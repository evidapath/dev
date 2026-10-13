#!/usr/bin/env python3
"""
Generalized A3 program generator. Creates new bachelor PROGRAMS (+ their sources,
admissions requirements, and residency-tiered cost profiles) in Sanity staging from
verified spec entries, cloning the schema shape of the existing verified programs.

One generator for the whole A3 expansion: add a verified PROGRAM spec, run with a
write token, and the app's program selector displays it. Every value here must be
primary-source verified (see fact-checks/ + docs/a3-program-offerings.md). Reuses the
university's shared applicant-category + admission-stage records (validated before write).

createOrReplace → idempotent (safe to re-run; already-created programs like Oxford E&M
are untouched if their spec isn't included).

Usage:
  python3 create_programs.py                         # dry run, all specs
  python3 create_programs.py --only oxford-eng        # dry run, one spec
  SANITY_TOKEN=<write> python3 create_programs.py --only oxford-eng --execute
"""
import json, os, sys, subprocess, tempfile, urllib.parse

PROJECT, DATASET, API = "jxwrtsiz", "staging", "2021-10-21"


def wref(ref, key=None):
    r = {"_ref": ref, "_type": "reference", "_weak": True}
    if key:
        r["_key"] = key
    return r


# ─────────────────────────────────────────────────────────────────────────────
# Verified program specs. uni = university slug (e.g. gb-university-of-oxford).
# cats/stage = reused existing record id suffixes under that uni.
# ─────────────────────────────────────────────────────────────────────────────
PROGRAMS = {
    "oxford-eng": {
        "uni": "gb-university-of-oxford",
        "prog_suffix": "meng-engineering-science",
        "program_name": "Engineering Science",
        "field_of_study": "Engineering",
        "degree_type": "MEng",
        "degree_type_local": "MEng in Engineering Science (4 years); specialise in Y3 into "
        "Biomedical/Chemical/Civil/Electrical/Information/Mechanical",
        "duration_value": 4, "duration_unit": "years", "language": ["en"],
        "faculty": "Department of Engineering Science",
        "url": "https://www.ox.ac.uk/admissions/undergraduate/courses/course-listing/engineering-science",
        "platform": "UCAS", "decision_year": "2027/2028 (Autumn 2027 entry)",
        "test_name": "Engineering and Science Admissions Test (ESAT)",
        "test_note": "Required admissions test for Engineering Science (distinct from CS's TMUA).",
        "ucas_code_note": "UCAS code H100.",
        "sources": {
            "adm": {
                "suffix": "src-eng-adm",
                "title": "Engineering Science: entry requirements -- University of Oxford",
                "url": "https://eng.ox.ac.uk/study/undergraduate/applications/entry-requirements",
                "excerpt": "A-Level A*A*A with the A*s in Maths and Further Maths or Physics; "
                "Maths and Physics required. IB 40 incl core with 776 at HL (7s in HL Maths and Physics). ESAT required.",
            },
            "fee": {
                "suffix": "src-eng-fee",
                "title": "Engineering Science -- course fees, University of Oxford",
                "url": "https://www.ox.ac.uk/admissions/undergraduate/courses/course-listing/engineering-science",
                "excerpt": "Home fee GBP 10,050 (2027/28). Overseas course fee GBP 66,580 (2027 entry).",
            },
        },
        "admissions": [
            {"suffix": "a-level", "cat": "curriculum-a-level", "curriculum": "A-Level",
             "threshold": "A*A*A, with the A*s in Maths, Further Maths or Physics; Mathematics and Physics are both required (Further Mathematics helpful but not required)",
             "subjects": ["Mathematics", "Physics", "Further Mathematics (helpful, not required)"]},
            {"suffix": "ib", "cat": "curriculum-ib", "curriculum": "International Baccalaureate",
             "threshold": "40 points including core points, with 776 at HL (7s in HL Mathematics and Physics)",
             "subjects": ["Mathematics (HL)", "Physics (HL)"]},
        ],
        "stage": "stage-interview",
        "costs": [
            {"suffix": "home", "cat": "residency-home", "tuition": 10050, "basis": "statutory",
             "year": "2027/28", "note": None},
            {"suffix": "overseas", "cat": "residency-overseas", "tuition": 66580, "basis": "institutional",
             "year": "2027/28", "note": "Engineering Science overseas rate (top band, same as CS)."},
        ],
        "living": {"min": 1475, "max": 2175, "currency": "GBP",
                   "desc": "Oxford-published living-cost estimate GBP 1,475-2,175/month (2027-28)."},
        "currency": "GBP",
        "lang_req": {
            "test_name": "IELTS Academic (or accepted equivalent) unless exempt",
            "min_score": "IELTS 7.5 overall, min 7.0 per component (TOEFL 110; C1 191); by 31 July of offer year, if not exempt.",
            "notes": "Oxford general ELR policy; exemptions for English-medium education/residency.",
        },
    },
}


def build_docs(key, s):
    uni, ps = s["uni"], s["prog_suffix"]
    prog_id = f"program-{uni}-{ps}"
    src_adm = f"sourceRecord-{uni}-{s['sources']['adm']['suffix']}"
    src_fee = f"sourceRecord-{uni}-{s['sources']['fee']['suffix']}"
    docs = []

    for which, sid in (("adm", src_adm), ("fee", src_fee)):
        sc = s["sources"][which]
        docs.append({
            "_id": sid, "_type": "sourceRecord", "id": sc["suffix"],
            "source_organization": "University of Oxford" if uni.startswith("gb-university-of-oxford") else uni,
            "source_type": "official_university", "title": sc["title"], "url": sc["url"],
            "excerpt": sc["excerpt"], "notes": "",
            "retrieval_method": "WebSearch/WebFetch (primary-source verification, EvidaPath A3)",
            "retrieved_at": "2026-10-13T00:00:00Z", "fields_supported": [],
        })

    docs.append({
        "_id": prog_id, "_type": "program", "id": f"{uni}-{ps}",
        "program_name": s["program_name"], "field_of_study": s["field_of_study"],
        "degree_type": s["degree_type"], "degree_type_local": s["degree_type_local"],
        "duration_value": s["duration_value"], "duration_unit": s["duration_unit"],
        "language_of_instruction": s["language"], "faculty_school": s["faculty"],
        "official_program_url": s["url"], "application_platform": s["platform"],
        "decision_context_academic_year": s["decision_year"], "record_status": "VERIFIED",
        "university_ref": wref(f"university-{uni}"),
        "application_requirements": [
            {"_key": "r1", "_type": "applicationRequirement", "name": "UCAS application",
             "necessity": "required", "requirement_type": "form", "description": "", "notes": s["ucas_code_note"]},
            {"_key": "r2", "_type": "applicationRequirement", "name": s["test_name"],
             "necessity": "required", "requirement_type": "standardized_test_score",
             "description": "", "notes": s["test_note"]},
            {"_key": "r3", "_type": "applicationRequirement", "name": "Interview (at least two colleges)",
             "necessity": "required", "requirement_type": "interview_or_evaluation_event",
             "description": "Shortlisted candidates interviewed by colleges in December.", "notes": ""},
        ],
        "source_refs": [wref(src_adm, "s1"), wref(src_fee, "s2")],
        "extension_metadata": {"_type": "extensionMetadata"},
    })

    for a in s["admissions"]:
        docs.append({
            "_id": f"admissionsRequirement-{uni}-admreq-{ps}-{a['suffix']}", "_type": "admissionsRequirement",
            "id": f"{uni}-admreq-{ps}-{a['suffix']}", "curriculum_type": a["curriculum"],
            "academic_threshold": a["threshold"], "academic_year": "2027 entry",
            "required_subjects": a["subjects"], "program_ref": wref(prog_id),
            "prior_curriculum_category_ref": wref(f"applicantCategory-{uni}-{a['cat']}"),
            "admission_stage_ref": wref(f"admissionStage-{uni}-{s['stage']}"),
            "record_status": "VERIFIED", "last_checked": "2026-10-13",
            "language_requirements": [{"_key": "lr1", "_type": "languageRequirement", "language": "English",
                **s["lang_req"]}],
            "standardized_tests": [{"_key": "st1", "_type": "testRequirement",
                "test_name": s["test_name"], "required": "required", "notes": s["test_note"]}],
            "source_refs": [wref(src_adm, "s1")],
        })

    for c in s["costs"]:
        docs.append({
            "_id": f"costProfile-{uni}-cost-{ps}-{c['suffix']}", "_type": "costProfile",
            "id": f"{uni}-cost-{ps}-{c['suffix']}", "academic_year": c["year"], "currency": s["currency"],
            "duration_years": s["duration_value"], "tuition_annual": c["tuition"], "tuition_basis": c["basis"],
            "program_ref": wref(prog_id), "residency_category_ref": wref(f"applicantCategory-{uni}-{c['cat']}"),
            "record_status": "VERIFIED", "verification_status": "VERIFIED", "last_checked": "2026-10-13",
            "mandatory_fees_breakdown": [], "other_material_costs": [],
            "estimated_living_costs_monthly_range": {"_type": "monthlyRange", "currency": s["living"]["currency"],
                "min": s["living"]["min"], "max": s["living"]["max"]},
            "living_cost_source_basis": {"_type": "livingCostSourceBasis",
                "kind": "genuine_cost_of_living_estimate", "administering_body": "University of Oxford",
                "description": s["living"]["desc"]},
            "source_refs": [wref(src_fee, "s1")],
            "extension_metadata": ({"_type": "extensionMetadata", "fields": [
                {"_key": "fee_note", "_type": "extensionMetadataFieldEntry", "key": "fee_note",
                 "value": c["note"], "value_type": "string"}]} if c["note"] else {"_type": "extensionMetadata"}),
        })

    reused = [f"university-{uni}", f"admissionStage-{uni}-{s['stage']}"] + \
             [f"applicantCategory-{uni}-{a['cat']}" for a in s["admissions"]] + \
             [f"applicantCategory-{uni}-{c['cat']}" for c in s["costs"]]
    return docs, sorted(set(reused))


def curl(args):
    p = subprocess.run(["curl", "-sS", "--fail-with-body", *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"curl failed ({p.returncode}): {p.stderr or p.stdout}")
    return p.stdout


def check_refs(reused, token):
    q = "*[_id in " + json.dumps(reused) + "]._id"
    url = f"https://{PROJECT}.api.sanity.io/v{API}/data/query/{DATASET}?query=" + urllib.parse.quote(q)
    found = json.loads(curl(["-H", f"Authorization: Bearer {token}", url]))["result"]
    return [r for r in reused if r not in found]


def main():
    execute = "--execute" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    keys = [only] if only else list(PROGRAMS)
    all_docs, all_reused = [], set()
    for k in keys:
        if k not in PROGRAMS:
            sys.exit(f"unknown spec: {k} (have: {list(PROGRAMS)})")
        d, r = build_docs(k, PROGRAMS[k])
        all_docs += d
        all_reused |= set(r)
        print(f"[{k}] {PROGRAMS[k]['program_name']} -> {len(d)} docs")
        for x in d:
            print(f"    {x['_type']:22} {x['_id']}")
    if not execute:
        print(f"\nDRY RUN — {len(all_docs)} docs total. Re-run with SANITY_TOKEN and --execute.")
        print(f"reused refs to validate: {sorted(all_reused)}")
        return
    token = os.environ.get("SANITY_TOKEN", "").strip()
    if not token:
        sys.exit("SANITY_TOKEN (write token) required for --execute.")
    missing = check_refs(sorted(all_reused), token)
    if missing:
        sys.exit(f"ABORT — reused reference targets missing: {missing}")
    print("reused references all exist ✓")
    body = json.dumps({"mutations": [{"createOrReplace": d} for d in all_docs]})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
        tf.write(body); payload = tf.name
    url = f"https://{PROJECT}.api.sanity.io/v2021-06-07/data/mutate/{DATASET}?returnIds=false"
    out = curl(["-X", "POST", "-H", f"Authorization: Bearer {token}",
                "-H", "Content-Type: application/json", "--data-binary", f"@{payload}", url])
    os.unlink(payload)
    print(f"\nCREATED {len(all_docs)} docs | transactionId {json.loads(out).get('transactionId')}")


if __name__ == "__main__":
    main()

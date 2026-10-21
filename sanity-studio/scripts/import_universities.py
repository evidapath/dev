#!/usr/bin/env python3
"""
Batch-2 university importer. Creates a NEW university's full scaffold in Sanity
staging **as DRAFTS** (never published) from a primary-source-verified spec:
university + city + applicantCategory + (optional) admissionStage + programs +
admissionsRequirements + residency-tiered costProfiles + scholarships + sources.

Per Suhail's Batch-2 doc (see memory batch2-import / docs/a3-program-offerings.md):
  - Do NOT auto-publish — every generated _id and every ref between generated docs
    carries the `drafts.` prefix, so these live only as unpublished drafts.
  - Reuse the existing published `country-<cc>` doc (weak ref, no prefix).
  - Program-specific requirements/costs, never university-wide substitutes.
  - Distinguish international vs domestic tuition; guaranteed vs competitive aid.
  - Store uncertain/unavailable AS SUCH (living kind="not_published"), never invent.

Usage:
  python3 import_universities.py                      # dry run, all specs
  python3 import_universities.py --only ae-aus         # dry run, one spec
  SANITY_TOKEN=<write> python3 import_universities.py --only ae-aus --execute
"""
import json, os, sys, subprocess, tempfile, urllib.parse

PROJECT, DATASET, API = "jxwrtsiz", "staging", "2021-10-21"
D = "drafts."  # all generated docs are drafts


def wref(ref, key=None, draft=True):
    r = {"_ref": (D + ref if draft else ref), "_type": "reference", "_weak": True}
    if key:
        r["_key"] = key
    return r


# ─────────────────────────────────────────────────────────────────────────────
# Verified university specs. slug = "<cc>-<name>" (e.g. ae-aus). Every value here
# must be primary-source verified; mark anything unverified as uncertain, never guess.
# ─────────────────────────────────────────────────────────────────────────────
UNIVERSITIES = {
    "ae-aus": {
        "canonical_name": "American University of Sharjah",
        "aliases": ["AUS"], "country_cc": "ae",
        "city": {"slug": "ae-sharjah", "name": "Sharjah"},
        "website": "https://www.aus.edu/", "institution_type": "private-nonprofit",
        "verified_at": "2026-10-21", "currency": "AED",
        "verification_note": "fact-checks/ae-aus-2026-10-21.md",
        # Shared sources (primary). Each program/cost/scholarship cites by key.
        "sources": {
            "main": {"suffix": "src-01", "title": "American University of Sharjah — official site (aus.edu)",
                "url": "https://www.aus.edu/",
                "excerpt": "AUS is a private, not-for-profit, coeducational, American-model university in University "
                "City, Sharjah, UAE; English medium of instruction. Colleges incl. College of Engineering (CEN) and "
                "School of Business Administration (SBA)."},
            "adm": {"suffix": "src-adm", "title": "Undergraduate Admission Requirements — AUS",
                "url": "https://www.aus.edu/admissions/bachelors-degrees/undergraduate-admission-requirements",
                "excerpt": "Subject minimums (grade equiv. B): Engineering & Data Science = Math + Physics; "
                "Science/Computer Science = Math + a Science; Business = Math. English: IELTS 6.5 / TOEFL iBT 80 / "
                "EmSAT Achieve English 1550 (Bridge Program for 4.5–6.0 IELTS). American/SABIS curriculum must submit "
                "SAT with Math section >= 450. Fall applications received after ~21 May may not be considered."},
            "fee": {"suffix": "src-fee", "title": "Undergraduate Tuition and Fees (2026-2027) — AUS",
                "url": "https://www.aus.edu/admissions/bachelors-degrees/undergraduate-tuition-and-fees",
                "excerpt": "Tuition for all majors AED 110,876 per academic year (AED 55,438/semester for 12–16 "
                "credits), 2026-2027, SAME for all students regardless of nationality (private university; no intl/"
                "domestic split). Student Activities Fee AED 422 + 5% VAT/semester; Health Insurance AED 300/sem (Plan "
                "II) or 600 + VAT (Plan I); Lab/Technology Fee AED 1,552–1,700 per course; one-time seat deposit AED "
                "5,000; application fee AED 400 + VAT. VAT not applied to tuition."},
            "schol": {"suffix": "src-schol", "title": "Financial Grants and Scholarships — AUS",
                "url": "https://www.aus.edu/admissions/financial-grants-and-scholarships",
                "excerpt": "President's Scholarship (competitive): 100% tuition + lab fees + stipend/housing/travel/"
                "insurance; IELTS 7.0/TOEFL 94; American curriculum 98% CGPA G10–11 + three AP grade-5 or SAT 1400; "
                "deadline Apr 1. Chancellor's Scholarship (competitive): full tuition + lab fees + housing/insurance; "
                "slightly lower (two AP grade-5 or SAT 1200). Merit Scholarships (automatic at admission, not "
                "competitive): 10–20% of tuition + lab fees, 95% average G10–11, transfers ineligible. Family Tuition "
                "Grant (need/guaranteed): 25% discount for second+ sibling enrolled simultaneously."},
        },
        # applicantCategory docs to create (dimension: prior_curriculum / residency).
        "curricula": [
            ("a-level", "GCE A-Level / IGCSE", "Applicants with GCE A-Level / IGCSE qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "American High School Diploma / SAT", "US-curriculum / SABIS applicants (SAT required)."),
            ("uae-shs", "UAE Secondary School Certificate", "UAE national secondary school certificate holders."),
        ],
        "residencies": [
            ("all-students", "All students (uniform tuition)",
             "AUS is private; tuition is uniform for all students regardless of nationality."),
        ],
        # Each program: pillar coverage CS / Engineering / Business / Economics.
        "programs": [
            {"suffix": "bscs", "program_name": "Computer Science", "field": "Computer Science",
             "degree": "BSc", "degree_local": "Bachelor of Science in Computer Science (BSCS), College of Engineering "
             "(Dept. of Computer Science and Engineering); ABET (CAC) accredited.",
             "faculty": "College of Engineering", "duration": 4,
             "url": "https://www.aus.edu/cen/department-of-computer-science-and-engineering",
             "subjects_note": "Math + a Science (min grade equiv. B)",
             "subjects": {"a-level": ["Mathematics", "a Science subject"], "ib": ["Mathematics", "a Science subject"],
                          "us-hs": ["Mathematics", "a Science subject"], "uae-shs": ["Mathematics", "a Science subject"]}},
            {"suffix": "bscoe", "program_name": "Computer Engineering", "field": "Engineering",
             "degree": "BSc", "degree_local": "Bachelor of Science in Computer Engineering (BSCoE), College of "
             "Engineering; ABET (EAC) accredited.",
             "faculty": "College of Engineering", "duration": 4,
             "url": "https://www.aus.edu/cen/department-of-computer-science-and-engineering",
             "subjects_note": "Math + Physics (min grade equiv. B); Physics by Grade 11 minimum",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics", "Physics"],
                          "us-hs": ["Mathematics", "Physics"], "uae-shs": ["Mathematics", "Physics"]}},
            {"suffix": "bsba", "program_name": "Business Administration", "field": "Business",
             "degree": "BSc", "degree_local": "Bachelor of Science in Business Administration (BSBA), School of "
             "Business Administration; AACSB accredited.",
             "faculty": "School of Business Administration", "duration": 4,
             "url": "https://www.aus.edu/sba/programs",
             "subjects_note": "Math (min grade equiv. B)",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"],
                          "us-hs": ["Mathematics"], "uae-shs": ["Mathematics"]}},
            {"suffix": "bae", "program_name": "Economics", "field": "Economics",
             "degree": "BA", "degree_local": "Bachelor of Arts in Economics (BAE), School of Business Administration "
             "(Dept. of Economics). AUS also offers a BSBA major in Economics.",
             "faculty": "School of Business Administration", "duration": 4,
             "url": "https://www.aus.edu/sba/undergraduate-degree/bachelor-of-arts-in-economics",
             "subjects_note": "Math (min grade equiv. B) — School of Business Administration requirement",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"],
                          "us-hs": ["Mathematics"], "uae-shs": ["Mathematics"]}},
        ],
        # Uniform cost (one residency tier). Tuition AED 110,876/yr; recurring mandatory fees
        # (activities + health Plan II) ~AED 1,486/yr (lab/tech per-course + one-time deposits excluded, noted).
        "cost": {"residency": "all-students", "tuition": 110876, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": 1486,
            "note": "Uniform tuition AED 110,876/yr for ALL students (private university; no intl/domestic split), "
            "2026-27. mandatory_fees_annual ~1,486 = Student Activities (422+VAT x2) + Health Insurance Plan II "
            "(300 x2); EXCLUDES per-course Lab/Technology fees (AED 1,552–1,700/course, variable) and one-time seat "
            "deposit AED 5,000 + application AED 400. Not residency-tiered."},
        # Admission is subject-based + English + (American/SABIS) SAT; no single committee stage -> omit stage.
        "lang_req": {"test_name": "IELTS Academic / TOEFL iBT / EmSAT Achieve English (unless exempt)",
            "min_score": "IELTS 6.5 overall, or TOEFL iBT 80, or EmSAT Achieve English 1550 (ITP TOEFL 550). "
            "Applicants scoring IELTS 4.5–6.0 (or iBT 32–79) may be admitted into the English Bridge Program.",
            "notes": "English is the medium of instruction at AUS."},
        "std_tests": [
            {"test_name": "SAT", "required": "conditional",
             "notes": "Required for American-curriculum / SABIS applicants: SAT Math section >= 450. Not required for "
             "all curricula."},
        ],
        "deadline_note": "Fall intake: applications received after ~21 May may not be considered (per AUS).",
        "living": None,  # No AUS program living estimate verified this pass; dorm charges exist but not captured. Not fabricated.
        "scholarships": [
            {"suffix": "presidents", "name": "President's Scholarship", "provider": "American University of Sharjah",
             "aid_type": "competitive_merit", "renewable": True, "deadline": "2027-04-01",
             "award_summary": "100% of tuition and lab fees, plus monthly stipend, housing, travel tickets and medical insurance.",
             "eligibility": "Highly competitive merit award. IELTS 7.0 / TOEFL iBT 94; e.g. American curriculum 98% CGPA "
             "(grades 10–11) + three AP grade-5 or SAT composite 1400. Requirements vary by curriculum."},
            {"suffix": "chancellors", "name": "Chancellor's Scholarship", "provider": "American University of Sharjah",
             "aid_type": "competitive_merit", "renewable": True, "deadline": "2027-04-01",
             "award_summary": "Full coverage of tuition and lab fees, plus application fee waiver, housing and medical insurance.",
             "eligibility": "Competitive merit award, slightly below President's. IELTS 7.0 / TOEFL iBT 94; e.g. American "
             "curriculum 98% CGPA (grades 10–11) + two AP grade-5 or SAT composite 1200."},
            {"suffix": "merit", "name": "Merit Scholarships", "provider": "American University of Sharjah",
             "aid_type": "automatic_merit", "renewable": True, "deadline": None,
             "award_summary": "10–20% of tuition and lab fees.",
             "eligibility": "Automatically offered at admission (no separate competitive application) to students with a "
             "95% minimum average in grades 10–11. Transfer students ineligible; award not guaranteed."},
            {"suffix": "family-grant", "name": "Family Tuition Grant", "provider": "American University of Sharjah",
             "aid_type": "guaranteed_need", "renewable": True, "deadline": None,
             "award_summary": "25% tuition discount for the second and subsequent siblings enrolled simultaneously.",
             "eligibility": "Need-based, guaranteed if eligible: multiple siblings enrolled at the same time; ineligible "
             "if a sibling holds a 100% scholarship."},
        ],
    },
}


def build_docs(slug, s):
    cc = s["country_cc"]
    uni_id = f"university-{slug}"
    city_id = f"city-{s['city']['slug']}"
    docs = []

    def src_id(key):
        return f"sourceRecord-{slug}-{s['sources'][key]['suffix']}"

    # Sources
    for key, sc in s["sources"].items():
        docs.append({"_id": D + src_id(key), "_type": "sourceRecord", "id": f"{slug}-{sc['suffix']}",
            "source_organization": s["canonical_name"], "source_type": "official_university",
            "title": sc["title"], "url": sc["url"], "excerpt": sc["excerpt"], "notes": "",
            "retrieval_method": "WebSearch/WebFetch (primary-source verification, EvidaPath Batch 2)",
            "retrieved_at": f"{s['verified_at']}T00:00:00Z", "fields_supported": []})

    # City (country reused from the already-published country-<cc>, weak ref, NO drafts prefix)
    docs.append({"_id": D + city_id, "_type": "city", "id": s["city"]["slug"], "name": s["city"]["name"],
        "country_ref": wref(f"country-{cc}", draft=False)})

    # University
    docs.append({"_id": D + uni_id, "_type": "university", "id": slug,
        "canonical_name": s["canonical_name"], "aliases": s.get("aliases", []),
        "country_ref": wref(f"country-{cc}", draft=False), "primary_city_ref": wref(city_id),
        "official_website": s["website"], "institution_type": s["institution_type"],
        "record_status": "VERIFIED", "evidapath_verified": True, "evidapath_verified_at": s["verified_at"],
        "last_verified": s["verified_at"], "last_researched": s["verified_at"],
        "evidapath_verification_note": s.get("verification_note", ""),
        "source_refs": [wref(src_id("main"), "sm")],
        "extension_metadata": {"_type": "extensionMetadata", "fields": [],
            "note": "Batch-2 import (DRAFT, unpublished). Program-specific data verified per primary sources."}})

    # applicantCategory (curriculum + residency)
    for cid, label, desc in s["curricula"]:
        docs.append({"_id": D + f"applicantCategory-{slug}-curriculum-{cid}", "_type": "applicantCategory",
            "id": f"{slug}-curriculum-{cid}", "dimension": "prior_curriculum", "label": label,
            "description": desc, "university_ref": wref(uni_id)})
    for rid, label, desc in s["residencies"]:
        docs.append({"_id": D + f"applicantCategory-{slug}-residency-{rid}", "_type": "applicantCategory",
            "id": f"{slug}-residency-{rid}", "dimension": "residency", "label": label,
            "description": desc, "university_ref": wref(uni_id)})

    cost, lang = s["cost"], s["lang_req"]
    living = s.get("living")
    for p in s["programs"]:
        ps, prog_id = p["suffix"], f"program-{slug}-{p['suffix']}"
        docs.append({"_id": D + prog_id, "_type": "program", "id": f"{slug}-{ps}",
            "program_name": p["program_name"], "field_of_study": p["field"], "degree_type": p["degree"],
            "degree_type_local": p["degree_local"], "duration_value": p["duration"], "duration_unit": "years",
            "language_of_instruction": ["en"], "faculty_school": p["faculty"], "official_program_url": p["url"],
            "application_platform": "AUS online application", "decision_context_academic_year": "2026-2027 (Fall 2027 entry)",
            "record_status": "VERIFIED", "university_ref": wref(uni_id),
            "application_requirements": [
                {"_key": "r1", "_type": "applicationRequirement", "name": "AUS online application",
                 "necessity": "required", "requirement_type": "form", "description": "", "notes": s.get("deadline_note", "")},
                {"_key": "r2", "_type": "applicationRequirement", "name": "Subject prerequisites",
                 "necessity": "required", "requirement_type": "other",
                 "description": f"{p['subjects_note']}.", "notes": ""},
                {"_key": "r3", "_type": "applicationRequirement", "name": "English proficiency",
                 "necessity": "required", "requirement_type": "standardized_test_score",
                 "description": lang["min_score"], "notes": lang["notes"]},
            ],
            "source_refs": [wref(src_id("adm"), "s1"), wref(src_id("fee"), "s2")],
            "extension_metadata": {"_type": "extensionMetadata"}})

        for cid, label, desc in s["curricula"]:
            req = {"_id": D + f"admissionsRequirement-{slug}-admreq-{ps}-{cid}", "_type": "admissionsRequirement",
                "id": f"{slug}-admreq-{ps}-{cid}", "curriculum_type": label,
                "academic_threshold": f"{p['subjects_note']} for {p['program_name']}.",
                "academic_year": "2027 entry", "required_subjects": p["subjects"][cid],
                "program_ref": wref(prog_id),
                "prior_curriculum_category_ref": wref(f"applicantCategory-{slug}-curriculum-{cid}"),
                "record_status": "VERIFIED", "last_checked": s["verified_at"],
                "language_requirements": [{"_key": "lr1", "_type": "languageRequirement", "language": "English", **lang}],
                "source_refs": [wref(src_id("adm"), "s1")]}
            if s.get("std_tests"):
                req["standardized_tests"] = [{"_key": f"st{i+1}", "_type": "testRequirement", **t}
                                             for i, t in enumerate(s["std_tests"])]
            docs.append(req)

        cp = {"_id": D + f"costProfile-{slug}-cost-{ps}-{cost['residency']}", "_type": "costProfile",
            "id": f"{slug}-cost-{ps}-{cost['residency']}", "academic_year": cost["year"], "currency": s["currency"],
            "duration_years": p["duration"], "tuition_annual": cost["tuition"], "tuition_basis": cost["basis"],
            "mandatory_fees_annual": cost["mandatory_fees_annual"],
            "program_ref": wref(prog_id), "residency_category_ref": wref(f"applicantCategory-{slug}-residency-{cost['residency']}"),
            "record_status": "VERIFIED", "verification_status": "VERIFIED", "last_checked": s["verified_at"],
            "mandatory_fees_breakdown": [], "other_material_costs": [],
            "living_cost_source_basis": ({"_type": "livingCostSourceBasis", "kind": "genuine_cost_of_living_estimate",
                "administering_body": s["canonical_name"], "description": living["desc"]} if living else
                {"_type": "livingCostSourceBasis", "kind": "not_published",
                 "description": "No official program living-cost estimate captured this pass; not fabricated."}),
            "source_refs": [wref(src_id("fee"), "s1")],
            "extension_metadata": {"_type": "extensionMetadata", "fields": [
                {"_key": "fee_note", "_type": "extensionMetadataFieldEntry", "key": "fee_note",
                 "value": cost["note"], "value_type": "string"}]}}
        if living:
            cp["estimated_living_costs_monthly_range"] = {"_type": "monthlyRange", "currency": living["currency"],
                "min": living["min"], "max": living["max"]}
        docs.append(cp)

    # Scholarships
    for sch in s.get("scholarships", []):
        doc = {"_id": D + f"scholarship-{slug}-{sch['suffix']}", "_type": "scholarship",
            "id": f"{slug}-{sch['suffix']}", "name": sch["name"], "provider": sch["provider"],
            "degree_levels": ["undergraduate"], "aid_type": sch["aid_type"], "renewable": sch["renewable"],
            "award_summary": sch["award_summary"], "eligibility_summary": sch["eligibility"],
            "university_ref": wref(uni_id), "record_status": "VERIFIED",
            "source_refs": [wref(src_id("schol"), "s1")]}
        if sch.get("deadline"):
            doc["deadline"] = sch["deadline"]
        docs.append(doc)

    reused = [f"country-{cc}"]  # published country must exist
    return docs, reused


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
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    keys = only.split(",") if only else list(UNIVERSITIES)
    all_docs, all_reused = [], set()
    for k in keys:
        if k not in UNIVERSITIES:
            sys.exit(f"unknown spec: {k} (have: {list(UNIVERSITIES)})")
        d, r = build_docs(k, UNIVERSITIES[k])
        all_docs += d
        all_reused |= set(r)
        print(f"[{k}] {UNIVERSITIES[k]['canonical_name']} -> {len(d)} DRAFT docs")
        for x in d:
            print(f"    {x['_type']:22} {x['_id']}")
    if not execute:
        print(f"\nDRY RUN — {len(all_docs)} draft docs total. Re-run with SANITY_TOKEN and --execute.")
        print(f"reused published refs to validate: {sorted(all_reused)}")
        return
    token = os.environ.get("SANITY_TOKEN", "").strip()
    if not token:
        sys.exit("SANITY_TOKEN (write token) required for --execute.")
    missing = check_refs(sorted(all_reused), token)
    if missing:
        sys.exit(f"ABORT — reused published reference targets missing: {missing}")
    print("reused references all exist ✓")
    body = json.dumps({"mutations": [{"createOrReplace": d} for d in all_docs]})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
        tf.write(body); payload = tf.name
    url = f"https://{PROJECT}.api.sanity.io/v2021-06-07/data/mutate/{DATASET}?returnIds=false"
    out = curl(["-X", "POST", "-H", f"Authorization: Bearer {token}",
                "-H", "Content-Type: application/json", "--data-binary", f"@{payload}", url])
    os.unlink(payload)
    print(f"\nCREATED {len(all_docs)} DRAFT docs | transactionId {json.loads(out).get('transactionId')}")


if __name__ == "__main__":
    main()

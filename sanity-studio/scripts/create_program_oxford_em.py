#!/usr/bin/env python3
"""
Create the Oxford Economics & Management (BA) program in Sanity (project jxwrtsiz,
dataset staging), cloning the schema shape of the existing verified Oxford CS program
and swapping in E&M's PRIMARY-SOURCE-VERIFIED data (see docs/a3-program-offerings.md).

This is the A3 TEMPLATE — one program built end-to-end to prove the pattern before
scaling to the other ~10. Creates:
  - 2 sourceRecords (E&M admissions criteria; E&M fees) with real official URLs
  - 1 program (Economics & Management, BA, 3yr, English, TARA test)
  - 2 costProfiles (Home GBP10,050 statutory; Overseas GBP43,600 institutional)
  - 2 admissionsRequirements (A-Level A*AA+TARA; IB 39/766+TARA)
Reuses existing university-level applicant categories (curriculum + residency) and the
interview admission stage — those are shared across programs (verified they exist).

evidapath_verified is NOT set here (programs beyond CS aren't on the student-facing
verified allowlist yet by design); record_status=VERIFIED reflects the primary-source
check. Does NOT publish anything new beyond writing to staging (Suhail's no-auto-publish
rule is about production; staging is the working set).

Usage:
  python3 create_program_oxford_em.py            # dry run (prints docs + ref check)
  SANITY_TOKEN=<write> python3 create_program_oxford_em.py --execute
"""
import json, os, sys, subprocess, tempfile

PROJECT, DATASET, API = "jxwrtsiz", "staging", "2021-10-21"
UNI = "university-gb-university-of-oxford"
PROG_ID = "program-gb-university-of-oxford-ba-economics-management"
SRC_ADM = "sourceRecord-gb-university-of-oxford-src-em-adm"
SRC_FEE = "sourceRecord-gb-university-of-oxford-src-em-fee"

# Reused (must already exist) — validated before execute.
CAT_ALEVEL = "applicantCategory-gb-university-of-oxford-curriculum-a-level"
CAT_IB = "applicantCategory-gb-university-of-oxford-curriculum-ib"
CAT_HOME = "applicantCategory-gb-university-of-oxford-residency-home"
CAT_OVERSEAS = "applicantCategory-gb-university-of-oxford-residency-overseas"
STAGE_INTERVIEW = "admissionStage-gb-university-of-oxford-stage-interview"

META = {"_type": "extensionMetadata"}  # minimal when nothing to carry


def wref(ref, key=None):
    r = {"_ref": ref, "_type": "reference", "_weak": True}
    if key:
        r["_key"] = key
    return r


def doc_sources():
    return [
        {
            "_id": SRC_ADM, "_type": "sourceRecord", "id": "src-em-adm",
            "source_organization": "University of Oxford",
            "source_type": "official_university",
            "title": "Economics and Management: Undergraduate Admissions Criteria -- University of Oxford",
            "url": "https://www.economics.ox.ac.uk/undergraduate-admissions-criteria",
            "excerpt": "A-Level: A*AA with Mathematics at A or above. IB: 39 points including core points, with 766 at HL. All applicants must take the TARA admissions test.",
            "retrieval_method": "WebSearch (primary-source verification, EvidaPath A3)",
            "retrieved_at": "2026-10-13T00:00:00Z", "notes": "",
            "fields_supported": [
                "AdmissionsRequirement.academic_threshold (A-Level, IB)",
                "Program.application_requirements (TARA)",
            ],
        },
        {
            "_id": SRC_FEE, "_type": "sourceRecord", "id": "src-em-fee",
            "source_organization": "University of Oxford",
            "source_type": "official_university",
            "title": "Economics and Management -- course listing / course fees, University of Oxford",
            "url": "https://www.ox.ac.uk/admissions/undergraduate/courses/course-listing/economics-and-management",
            "excerpt": "Home fee GBP 10,050 (2027/28 cap). Overseas course fee GBP 43,600 (2026/27; 2027 entry not yet published at time of verification).",
            "retrieval_method": "WebSearch (primary-source verification, EvidaPath A3)",
            "retrieved_at": "2026-10-13T00:00:00Z",
            "notes": "2027-entry overseas fee not yet published by Oxford; recorded 2026/27 figure, flagged pending.",
            "fields_supported": [
                "CostProfile.tuition_annual (home, overseas)",
            ],
        },
    ]


def doc_program():
    return {
        "_id": PROG_ID, "_type": "program", "id": "gb-university-of-oxford-ba-economics-management",
        "program_name": "Economics and Management", "field_of_study": "Economics and Management",
        "degree_type": "BA",
        "degree_type_local": "BA (Hons) in Economics and Management (3 years)",
        "duration_value": 3, "duration_unit": "years",
        "language_of_instruction": ["en"],
        "faculty_school": "Department of Economics / Saïd Business School",
        "official_program_url": "https://www.ox.ac.uk/admissions/undergraduate/courses/course-listing/economics-and-management",
        "application_platform": "UCAS",
        "decision_context_academic_year": "2027/2028 (Autumn 2027 undergraduate entry)",
        "record_status": "VERIFIED",
        "university_ref": wref(UNI),
        "application_requirements": [
            {"_key": "em01", "_type": "applicationRequirement", "name": "UCAS application",
             "necessity": "required", "requirement_type": "form", "description": "", "notes": "UCAS code L0V0."},
            {"_key": "em02", "_type": "applicationRequirement",
             "name": "Thinking Skills Assessment for Admissions / TARA", "necessity": "required",
             "requirement_type": "standardized_test_score",
             "description": "Required admissions test for Economics & Management.",
             "notes": "Distinct from CS's TMUA and Engineering's ESAT."},
            {"_key": "em03", "_type": "applicationRequirement", "name": "Interview (at least two colleges)",
             "necessity": "required", "requirement_type": "interview_or_evaluation_event",
             "description": "Shortlisted candidates interviewed by colleges in December.", "notes": ""},
        ],
        "source_refs": [wref(SRC_ADM, "s1"), wref(SRC_FEE, "s2")],
        "extension_metadata": META,
    }


def admreq(suffix, curriculum, cat_ref, threshold, subjects):
    return {
        "_id": f"admissionsRequirement-gb-university-of-oxford-admreq-em-{suffix}",
        "_type": "admissionsRequirement", "id": f"gb-university-of-oxford-admreq-em-{suffix}",
        "curriculum_type": curriculum, "academic_threshold": threshold,
        "academic_year": "2027 entry", "required_subjects": subjects,
        "program_ref": wref(PROG_ID), "prior_curriculum_category_ref": wref(cat_ref),
        "admission_stage_ref": wref(STAGE_INTERVIEW),
        "record_status": "VERIFIED", "last_checked": "2026-10-13",
        "language_requirements": [{
            "_key": "lr1", "_type": "languageRequirement", "language": "English",
            "test_name": "IELTS Academic (or accepted equivalent) unless exempt",
            "min_score": "IELTS 7.5 overall, min 7.0 per component (TOEFL 110; C1 191); by 31 July of offer year, if not exempt.",
            "notes": "Oxford general ELR policy; exemptions for English-medium education/residency.",
        }],
        "standardized_tests": [{
            "_key": "st1", "_type": "testRequirement",
            "test_name": "Thinking Skills Assessment for Admissions (TARA)",
            "required": "required", "notes": "E&M-specific admissions test.",
        }],
        "source_refs": [wref(SRC_ADM, "s1")],
    }


def costprofile(suffix, res_cat, tuition, basis, year, note):
    return {
        "_id": f"costProfile-gb-university-of-oxford-cost-em-{suffix}", "_type": "costProfile",
        "id": f"gb-university-of-oxford-cost-em-{suffix}", "academic_year": year,
        "currency": "GBP", "duration_years": 3, "tuition_annual": tuition, "tuition_basis": basis,
        "program_ref": wref(PROG_ID), "residency_category_ref": wref(res_cat),
        "record_status": "VERIFIED", "verification_status": "VERIFIED", "last_checked": "2026-10-13",
        "mandatory_fees_breakdown": [], "other_material_costs": [],
        "estimated_living_costs_monthly_range": {
            "_type": "monthlyRange", "currency": "GBP", "min": 1475, "max": 2175},
        "living_cost_source_basis": {
            "_type": "livingCostSourceBasis", "kind": "genuine_cost_of_living_estimate",
            "administering_body": "University of Oxford",
            "description": "Oxford-published living-cost estimate GBP 1,475-2,175/month (2027-28); same figure across programs. Overseas living cost not separately published."},
        "source_refs": [wref(SRC_FEE, "s1")],
        "extension_metadata": ({"_type": "extensionMetadata", "fields": [
            {"_key": "fee_year_note", "_type": "extensionMetadataFieldEntry",
             "key": "fee_year_note", "value": note, "value_type": "string"}]} if note else META),
    }


def all_docs():
    docs = doc_sources()
    docs.append(doc_program())
    docs += [
        admreq("a-level", "A-Level", CAT_ALEVEL,
               "A*AA, with Mathematics at A or A* (Maths required)", ["Mathematics"]),
        admreq("ib", "International Baccalaureate", CAT_IB,
               "39 points including core points, with 766 at HL", ["Mathematics (HL recommended)"]),
    ]
    docs.append(costprofile("home", CAT_HOME, 10050, "statutory", "2027/28", None))
    docs.append(costprofile("overseas", CAT_OVERSEAS, 43600, "institutional", "2026/27",
                "GBP 43,600 is the 2026/27 overseas rate; Oxford had not published the 2027-entry E&M overseas fee at verification (2026-10-13). Lower than CS's GBP 66,580 band."))
    return docs


def curl(args):
    p = subprocess.run(["curl", "-sS", "--fail-with-body", *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"curl failed ({p.returncode}): {p.stderr or p.stdout}")
    return p.stdout


def check_refs(token):
    reused = [UNI, CAT_ALEVEL, CAT_IB, CAT_HOME, CAT_OVERSEAS, STAGE_INTERVIEW]
    q = "*[_id in " + json.dumps(reused) + "]._id"
    url = f"https://{PROJECT}.api.sanity.io/v{API}/data/query/{DATASET}?query=" + \
          __import__("urllib.parse", fromlist=["quote"]).quote(q)
    found = json.loads(curl(["-H", f"Authorization: Bearer {token}", url]))["result"]
    missing = [r for r in reused if r not in found]
    return missing


def main():
    execute = "--execute" in sys.argv
    docs = all_docs()
    print(f"target: {PROJECT}/{DATASET} | new docs: {len(docs)}")
    for d in docs:
        print(f"  {d['_type']:22} {d['_id']}")
    if not execute:
        print("\nDRY RUN — no writes. Re-run with SANITY_TOKEN and --execute.")
        print("(execute will first verify the 6 reused reference targets exist.)")
        return
    token = os.environ.get("SANITY_TOKEN", "").strip()
    if not token:
        sys.exit("SANITY_TOKEN (write token) required for --execute.")
    missing = check_refs(token)
    if missing:
        sys.exit(f"ABORT — reused reference targets missing: {missing}")
    print("reused references all exist ✓")
    # createOrReplace so re-runs are idempotent.
    body = json.dumps({"mutations": [{"createOrReplace": d} for d in docs]})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
        tf.write(body); payload = tf.name
    url = f"https://{PROJECT}.api.sanity.io/v2021-06-07/data/mutate/{DATASET}?returnIds=false"
    out = curl(["-X", "POST", "-H", f"Authorization: Bearer {token}",
                "-H", "Content-Type: application/json", "--data-binary", f"@{payload}", url])
    os.unlink(payload)
    print(f"\nCREATED {len(docs)} docs | transactionId {json.loads(out).get('transactionId')}")


if __name__ == "__main__":
    main()

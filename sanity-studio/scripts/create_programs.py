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


# NYUAD admission is UNIVERSITY-WIDE and identical across majors (holistic, test-optional,
# single Common App decision; major declared AFTER entry). So all NYUAD majors share the same
# admission shape — only field/degree/major differ. These mirror the already-verified NYUAD CS record.
_NYUAD_CURRICULA = [
    ("a-level", "curriculum-a-level", "GCE A-Level"),
    ("ib", "curriculum-ib", "International Baccalaureate Diploma"),
    ("international-other", "curriculum-international-other", "General International Secondary Qualification"),
    ("us-hs", "curriculum-us-hs", "US High School Diploma"),
]
_NYUAD_LANG = {
    "test_name": "TOEFL iBT / Duolingo English Test / IELTS Academic / PTE Academic / Cambridge C1 Advanced or C2 Proficiency / iTEP",
    "min_score": "No formal minimum; competitive benchmarks: TOEFL 100+, Duolingo 130+, IELTS 7.5+, PTE 70+, Cambridge 191+, iTEP 4.5+",
    "notes": "Required for non-native English speakers unless 3+ consecutive years of study in an English-only curriculum "
             "immediately prior to application; most non-native-English applicants are still expected to submit a score.",
}
_NYUAD_TESTS = [
    {"test_name": "SAT", "required": "recommended",
     "notes": "Test-optional through the 2027-2028 cycle; NYU states no minimum score, only that submitted scores are 'an important criteria' when provided."},
    {"test_name": "ACT", "required": "recommended", "notes": "Same test-optional policy as SAT."},
]


def nyuad_adms(threshold, subjects=None):
    """Four-curriculum admissions list for a NYUAD major (identical holistic admission)."""
    return [{"suffix": sfx, "cat": cat, "curriculum": label,
             "threshold": threshold, "subjects": subjects or []}
            for sfx, cat, label in _NYUAD_CURRICULA]


_NYUAD_APPREQS = [
    {"_key": "r1", "_type": "applicationRequirement", "name": "Common Application (university-wide)",
     "necessity": "required", "requirement_type": "form",
     "description": "Apply to NYU Abu Dhabi via the Common Application; a single admission decision is issued.",
     "notes": "Admission is to the university, not to a specific major."},
    {"_key": "r2", "_type": "applicationRequirement", "name": "Major declared after admission (post-admission)",
     "necessity": "required", "requirement_type": "other",
     "description": "Not a direct-entry major. Students are admitted to NYUAD holistically and declare this major "
     "after entry; admission criteria do not vary by major.", "notes": ""},
]
# University-wide cost of attendance — identical for every major and residency (hence residency-uniform).
_NYUAD_COSTS = [
    {"suffix": "uniform", "cat": "residency-uniform", "tuition": 68576, "basis": "institutional",
     "year": "2026-2027", "mandatory_fees_annual": 15838,
     "note": "University-wide cost of attendance, identical for all majors and residencies. Tuition 68,576 + direct "
     "non-tuition (health 2,308 + books 1,730 + food 5,800 + housing 6,000 = 15,838) = 84,414 direct; + ~5,914 "
     "indirect => ~90,328 total COA (2026-27)."},
]
_NYUAD_SOURCES = {
    "adm": {"suffix": "src-nyuad-adm", "title": "Entry Requirements - NYU Abu Dhabi",
        "url": "https://nyuad.nyu.edu/en/apply/undergraduate/apply/entry-requirements.html",
        "excerpt": "NYU Abu Dhabi admission is university-wide and holistic via the Common Application (single decision). "
        "Test-optional (SAT/ACT) through the 2027-2028 cycle; no minimum scores. English proficiency "
        "(TOEFL/IELTS/Duolingo/PTE/Cambridge/iTEP) required for non-native speakers unless exempt (3+ yrs English-medium). "
        "Students are admitted to the university and declare a major after entry."},
    "fee": {"suffix": "src-nyuad-fee", "title": "Cost of Attendance | NYU Bulletins (Abu Dhabi, 2026-2027)",
        "url": "https://bulletins.nyu.edu/undergraduate/abu-dhabi/cost-attendance/",
        "excerpt": "Direct Costs: Tuition $68,576; Student Health Insurance $2,308; Books and Supplies $1,730; Food "
        "$5,800; Housing $6,000; Total Direct $84,414. Indirect ~$5,914. Total Cost of Attendance $90,328. Academic "
        "Year 2026-2027. University-wide (same for all majors)."},
}


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
    "toronto-eng": {
        "uni": "ca-university-of-toronto",
        "prog_suffix": "basc-engineering",
        "program_name": "Engineering (Applied Science)",
        "field_of_study": "Engineering",
        "degree_type": "BASc",
        "degree_type_local": "Bachelor of Applied Science (BASc), Faculty of Applied Science & Engineering; "
        "first-year common/stream entry (Core-8 programs, Engineering Science, TrackOne)",
        "duration_value": 4, "duration_unit": "years", "language": ["en"],
        "faculty": "Faculty of Applied Science & Engineering",
        "url": "https://discover.engineering.utoronto.ca/",
        "platform": "OUAC", "decision_year": "2026-27 cycle, Fall 2027 entry",
        # No standardized admissions test (Canada); provide explicit application_requirements.
        "application_requirements": [
            {"_key": "r1", "_type": "applicationRequirement", "name": "OUAC application",
             "necessity": "required", "requirement_type": "form", "description": "", "notes": "Ontario Universities' Application Centre."},
            {"_key": "r2", "_type": "applicationRequirement", "name": "Online Student Profile (OSP)",
             "necessity": "required", "requirement_type": "other",
             "description": "Mandatory supplementary profile (written + video components).", "notes": ""},
        ],
        "sources": {
            "adm": {
                "suffix": "src-eng-adm",
                "title": "Admission Requirements -- Faculty of Applied Science & Engineering, U of T",
                "url": "https://engineering.calendar.utoronto.ca/admission-requirements",
                "excerpt": "Prerequisites: senior-level Calculus, Physics and Chemistry (Ontario: MHF4U, MCV4U, "
                "SPH4U, SCH4U, ENG4U + one). Minimum 70% in each prerequisite; Online Student Profile required; no standardized test.",
            },
            "fee": {
                "suffix": "src-eng-fee",
                "title": "Finances -- Future Engineering Undergraduates, U of T (2026-27)",
                "url": "https://discover.engineering.utoronto.ca/finances/",
                "excerpt": "International tuition CAD 72,860 + 2,266.83 incidental + 948 UHIP (2026-27). "
                "Domestic Ontario tuition CAD 14,460 + 2,266.83 incidental.",
            },
        },
        "admissions": [
            {"suffix": "ontario-ossd", "cat": "curriculum-ontario-ossd", "curriculum": "Ontario Secondary School Diploma (OSSD), 4U/M",
             "threshold": "Six 4U/M courses; minimum 70% in each prerequisite (Faculty selects competitively on the whole profile)",
             "subjects": ["English (ENG4U)", "Advanced Functions (MHF4U)", "Calculus & Vectors (MCV4U)",
                          "Chemistry (SCH4U)", "Physics (SPH4U)", "one additional 4U/M"]},
            {"suffix": "a-level", "cat": "curriculum-a-level", "curriculum": "GCE A-Level",
             "threshold": "Senior-level Mathematics (with Calculus), Physics and Chemistry; competitive grades (prerequisite minimum 70% equivalent)",
             "subjects": ["Mathematics (Calculus)", "Physics", "Chemistry"]},
            {"suffix": "ib", "cat": "curriculum-ib", "curriculum": "International Baccalaureate",
             "threshold": "HL Mathematics, Physics and Chemistry; competitive grades",
             "subjects": ["Mathematics (HL)", "Physics (HL)", "Chemistry (HL)"]},
            {"suffix": "us", "cat": "curriculum-us", "curriculum": "US High School / AP",
             "threshold": "Senior-level Calculus, Physics and Chemistry (AP Calculus/Physics/Chemistry); competitive grades",
             "subjects": ["Calculus", "Physics", "Chemistry"]},
        ],
        # No single admission stage (Engineering admission differs from CS); omit stage.
        "costs": [
            {"suffix": "domestic-ontario", "cat": "residency-domestic-ontario", "tuition": 14460,
             "basis": "statutory", "year": "2026-27", "mandatory_fees_annual": 2266.83,
             "note": "Ontario-resident regulated Engineering tuition 2026-27 (markedly higher than Arts & Science's CAD 6,100)."},
            {"suffix": "international", "cat": "residency-international", "tuition": 72860,
             "basis": "institutional", "year": "2026-27", "mandatory_fees_annual": 3214.83,
             "note": "International Engineering tuition 2026-27: CAD 72,860 + 2,266.83 incidental + 948 UHIP. Higher than Arts & Science CS's CAD 66,110."},
        ],
        "living": {"min": 1500, "max": 2500, "currency": "CAD", "admin_body": "University of Toronto",
                   "desc": "U of T estimates ~CAD 2,000/month total living expenses (housing, food, transport, etc.); "
                   "first-year residence + meal plan CAD 15,167-24,910/yr. Source: studentlife/utm.utoronto.ca."},
        "currency": "CAD",
        "lang_req": {
            "test_name": "IELTS Academic (or accepted equivalent) unless exempt",
            "min_score": "IELTS Academic 6.5 overall, no band below 6.0 (per U of T English Language Requirements), unless exempt by English-medium schooling.",
            "notes": "U of T general English requirement; not Engineering-specific. Verified vs future.utoronto.ca/english-language-requirements.",
        },
    },
    "toronto-rotman": {
        "uni": "ca-university-of-toronto",
        "prog_suffix": "bcom-rotman-commerce",
        "program_name": "Commerce (Rotman Commerce)",
        "field_of_study": "Business",
        "degree_type": "BCom",
        "degree_type_local": "Bachelor of Commerce (BCom), Rotman Commerce within the Faculty of Arts & Science; "
        "specialist programs in Finance & Economics, Accounting, or Management",
        "duration_value": 4, "duration_unit": "years", "language": ["en"],
        "faculty": "Rotman Commerce (Faculty of Arts & Science)",
        "url": "https://rotmancommerce.utoronto.ca/future-students/",
        "platform": "OUAC", "decision_year": "2026-27 cycle, Fall 2027 entry",
        "application_requirements": [
            {"_key": "r1", "_type": "applicationRequirement", "name": "OUAC application",
             "necessity": "required", "requirement_type": "form", "description": "", "notes": "Ontario Universities' Application Centre."},
            {"_key": "r2", "_type": "applicationRequirement", "name": "Rotman Commerce Supplemental Application",
             "necessity": "required", "requirement_type": "other",
             "description": "Written + video responses considered with the academic record.",
             "notes": "Recommended by Dec 1, 2026; main application deadline Jan 15, 2027."},
        ],
        "sources": {
            "adm": {
                "suffix": "src-rotman-adm",
                "title": "Rotman Commerce -- Future Students admission requirements (Ontario / outside Ontario), U of T",
                "url": "https://rotmancommerce.utoronto.ca/future-students/ontario-applicants/",
                "excerpt": "Six Grade 12 U/M incl English (ENG4U) and Calculus & Vectors (MCV4U; special attention). "
                "Outside Ontario: senior English + a calculus course (incl AP Calculus). Overall grade 11/12 average in the mid-high 80s+ recommended. Rotman Commerce Supplemental Application required.",
            },
            "fee": {
                "suffix": "src-rotman-fee",
                "title": "Rotman Commerce -- tuition & fees for international students, U of T (2026-27)",
                "url": "https://rotmancommerce.utoronto.ca/current-students/international-student-welcome-guide/tuition-fees-scholarships-for-international-students/",
                "excerpt": "International first-year program fee CAD 66,110 + 2,100.29 incidental + 948 UHIP. "
                "From year two, Rotman Commerce charges a higher 'deregulated' program fee.",
            },
        },
        "admissions": [
            {"suffix": "ontario-ossd", "cat": "curriculum-ontario-ossd", "curriculum": "Ontario Secondary School Diploma (OSSD), 4U/M",
             "threshold": "Six 4U/M courses; overall grade 11/12 average in the mid-high 80s+ recommended; MCV4U weighted heavily",
             "subjects": ["English (ENG4U)", "Calculus & Vectors (MCV4U)", "four additional 4U/M"]},
            {"suffix": "a-level", "cat": "curriculum-a-level", "curriculum": "GCE A-Level",
             "threshold": "Senior-level English and a Calculus course; competitive grades (mid-high 80s+ equivalent)",
             "subjects": ["English", "Mathematics (Calculus)"]},
            {"suffix": "ib", "cat": "curriculum-ib", "curriculum": "International Baccalaureate",
             "threshold": "English and HL/SL Mathematics with calculus; competitive grades",
             "subjects": ["English", "Mathematics (with calculus)"]},
            {"suffix": "us", "cat": "curriculum-us", "curriculum": "US High School / AP",
             "threshold": "Senior English and a calculus course (e.g. AP Calculus); competitive grades",
             "subjects": ["English", "Calculus (e.g. AP Calculus)"]},
        ],
        "costs": [
            {"suffix": "international", "cat": "residency-international", "tuition": 66110,
             "basis": "institutional", "year": "2026-27", "mandatory_fees_annual": 3048.29,
             "note": "International FIRST-YEAR program fee (matches Arts & Science); + 2,100.29 incidental + 948 UHIP. "
             "From year two Rotman Commerce charges a higher 'deregulated' fee (not published here; verify per year)."},
        ],
        "living": {"min": 1500, "max": 2500, "currency": "CAD", "admin_body": "University of Toronto",
                   "desc": "U of T estimates ~CAD 2,000/month total living expenses; residence + meal CAD 15,167-24,910/yr."},
        "currency": "CAD",
        "lang_req": {
            "test_name": "IELTS Academic (or accepted equivalent) unless exempt",
            "min_score": "IELTS Academic 6.5 overall, no band below 6.0 (per U of T English Language Requirements), unless exempt.",
            "notes": "U of T general English requirement. Verified vs future.utoronto.ca/english-language-requirements.",
        },
    },
    "delft-aero": {
        "uni": "nl-tu-delft", "uni_name": "Delft University of Technology",
        "prog_suffix": "bsc-aerospace-engineering",
        "program_name": "Aerospace Engineering", "field_of_study": "Engineering",
        "degree_type": "BSc",
        "degree_type_local": "BSc Aerospace Engineering (English stream); numerus fixus (max 440 places 2026-27)",
        "duration_value": 3, "duration_unit": "years", "language": ["en"],
        "faculty": "Faculty of Aerospace Engineering",
        "url": "https://www.tudelft.nl/en/onderwijs/opleidingen/bachelors/ae/bsc-aerospace-engineering",
        "platform": "Studielink", "decision_year": "2027/2028 (Sept 2027 entry, numerus fixus)",
        "application_requirements": [
            {"_key": "r1", "_type": "applicationRequirement", "name": "Studielink registration",
             "necessity": "required", "requirement_type": "form",
             "description": "Register in Studielink before 15 January (numerus fixus).", "notes": ""},
            {"_key": "r2", "_type": "applicationRequirement", "name": "Matching & Selection (numerus fixus)",
             "necessity": "required", "requirement_type": "other",
             "description": "Ranked selection procedure; limited places (max 440 in 2026-27).", "notes": ""},
        ],
        "sources": {
            "adm": {"suffix": "src-aero-adm",
                "title": "Admission Requirements -- BSc Aerospace Engineering, TU Delft",
                "url": "https://www.tudelft.nl/en/onderwijs/opleidingen/bachelors/ae/bsc-aerospace-engineering/from-application-to-enrolment/admission-requirements",
                "excerpt": "A-Level: Mathematics + Physics (A-C). IB: Mathematics AA HL + Physics HL. US: Calculus A/B or B/C + Physics 1&2 or Physics C. Dutch VWO: Physics + Mathematics B. Numerus fixus, register before 15 January."},
            "fee": {"suffix": "src-aero-fee",
                "title": "Study Costs -- BSc Aerospace Engineering, TU Delft (2026-2027)",
                "url": "https://www.tudelft.nl/en/onderwijs/opleidingen/bachelors/ae/bsc-aerospace-engineering/from-application-to-enrolment/tuition-and-additional-fees",
                "excerpt": "Statutory tuition fee EUR 2,694 (EU/EEA/Swiss). Institutional tuition fee II EUR 19,906 (non-EU) for 2026-2027."},
        },
        "admissions": [
            {"suffix": "a-level", "cat": "curriculum-alevel", "curriculum": "GCE A-Levels",
             "threshold": "Mathematics and Physics at A-Level, grades A-C", "subjects": ["Mathematics (A-Level)", "Physics (A-Level)"]},
            {"suffix": "ib", "cat": "curriculum-ib", "curriculum": "International Baccalaureate Diploma Programme",
             "threshold": "Mathematics: Analysis & Approaches HL, and Physics HL", "subjects": ["Mathematics AA HL", "Physics HL"]},
            {"suffix": "us-hs-ap", "cat": "curriculum-us-hs-ap", "curriculum": "US High School Diploma + Advanced Placement",
             "threshold": "AP Calculus A/B or B/C (B/C preferred) and AP Physics 1&2 or Physics C: Mechanics",
             "subjects": ["AP Calculus A/B or B/C", "AP Physics 1&2 or Physics C"]},
            {"suffix": "dutch-vwo", "cat": "curriculum-dutch-vwo", "curriculum": "Dutch VWO / Gymnasium",
             "threshold": "VWO diploma including Physics and Mathematics B", "subjects": ["Physics (Natuurkunde)", "Mathematics B (Wiskunde B)"]},
        ],
        "stage": "stage-matching-selection",
        "costs": [
            {"suffix": "eu-efta", "cat": "residency-eu-efta", "tuition": 2694, "basis": "statutory",
             "year": "2026-2027", "note": None},
            {"suffix": "non-eu", "cat": "residency-non-eu", "tuition": 19906, "basis": "institutional",
             "year": "2026-2027", "note": "Institutional fee II for non-EU/EEA bachelor's (program-wide Dutch rate; = CSE)."},
        ],
        "living": None,  # TU Delft does not publish a program living-cost estimate; not fabricated.
        "currency": "EUR",
        "lang_req": {"test_name": "English proficiency (IELTS/TOEFL) unless exempt",
            "min_score": "Required for the English stream unless exempt (e.g. 3+ years English-medium education); see TU Delft language requirements.",
            "notes": "English-taught program; exemption rules per TU Delft."},
    },
    "tum-aero": {
        "uni": "de-tu-munich", "uni_name": "Technical University of Munich",
        "prog_suffix": "bsc-aerospace",
        "program_name": "Aerospace", "field_of_study": "Engineering",
        "degree_type": "BSc",
        "degree_type_local": "Aerospace B.Sc. (6 semesters), 100% English-taught, TUM School of Engineering and Design",
        "duration_value": 6, "duration_unit": "semesters", "language": ["en"],
        "faculty": "TUM School of Engineering and Design",
        "url": "https://www.tum.de/en/studies/degree-programs/detail/aerospace-bachelor-of-science-bsc",
        "platform": "TUMonline", "decision_year": "Winter Semester 2026/27",
        "application_requirements": [
            {"_key": "r1", "_type": "applicationRequirement", "name": "TUMonline online application",
             "necessity": "required", "requirement_type": "form", "description": "", "notes": ""},
            {"_key": "r2", "_type": "applicationRequirement", "name": "uni-assist Preliminary Documentation (VPD)",
             "necessity": "required", "requirement_type": "other",
             "description": "Credential pre-assessment for applicants with a non-German qualification.", "notes": ""},
            {"_key": "r3", "_type": "applicationRequirement", "name": "Aptitude assessment (Eignungsfeststellung)",
             "necessity": "required", "requirement_type": "interview_or_evaluation_event",
             "description": "Program aptitude assessment.", "notes": ""},
        ],
        "sources": {
            "adm": {"suffix": "src-aero-adm",
                "title": "Aerospace -- Bachelor of Science (B.Sc.), TUM",
                "url": "https://www.tum.de/en/studies/degree-programs/detail/aerospace-bachelor-of-science-bsc",
                "excerpt": "Aerospace B.Sc., 6 semesters, 100% English-taught, TUM School of Engineering and Design; aptitude assessment required."},
            "fee": {"suffix": "src-aero-fee",
                "title": "Tuition Fees for Students from Non-EU Countries, TUM",
                "url": "https://www.tum.de/en/studies/fees/tuition",
                "excerpt": "Non-EU bachelor tuition EUR 3,000/semester (2026-27). Student-union fee EUR 97/semester. EU/EEA: no tuition. Announced increase to EUR 3,400/semester for WS 2027/28 new entrants."},
        },
        "admissions": [
            {"suffix": "a-level", "cat": "curriculum-a-level", "curriculum": "British-patterned GCE A-Level",
             "threshold": "A-Level with mathematics and physics/science subjects; recognised as HZB; aptitude assessment",
             "subjects": ["Mathematics", "Physics"]},
            {"suffix": "ib", "cat": "curriculum-ib", "curriculum": "International Baccalaureate (IB) Diploma",
             "threshold": "IB Diploma recognised as HZB with Mathematics and Physics; aptitude assessment",
             "subjects": ["Mathematics", "Physics"]},
            {"suffix": "us-hs", "cat": "curriculum-us-hs", "curriculum": "U.S. High School Diploma / AP route",
             "threshold": "US HS diploma + AP (Calculus, Physics) to meet HZB; aptitude assessment",
             "subjects": ["AP Calculus", "AP Physics"]},
            {"suffix": "abitur", "cat": "curriculum-abitur", "curriculum": "German Abitur",
             "threshold": "Allgemeine Hochschulreife (Abitur) with mathematics and physics; aptitude assessment",
             "subjects": ["Mathematics", "Physics"]},
        ],
        "stage": "stage-aptitude-assessment",
        "costs": [
            {"suffix": "eu-eea", "cat": "residency-eu-eea", "tuition": 0, "basis": "statutory",
             "year": "2026-27 (Summer Semester 2026 basis)", "mandatory_fees_annual": 194,
             "note": "No tuition for EU/EEA; EUR 97/semester (EUR 194/yr) student-union fee applies."},
            {"suffix": "non-eu", "cat": "residency-non-eu", "tuition": 6000, "basis": "institutional",
             "year": "2026-27 (Summer Semester 2026 basis)", "mandatory_fees_annual": 194,
             "note": "EUR 3,000/semester (2026-27) + EUR 97/sem union fee. TUM has announced an increase to EUR 3,400/semester (EUR 6,800/yr) for engineering-tier NON-EU students entering WS 2027/28 (current students grandfathered)."},
        ],
        "living": None,  # Munich living estimate exists on the Informatics record but not re-verified here; omit rather than copy unverified.
        "currency": "EUR",
        "lang_req": {"test_name": "English proficiency (IELTS/TOEFL) unless exempt",
            "min_score": "Required for the English-taught program unless exempt; per TUM language certificate rules.",
            "notes": "Aerospace B.Sc. is English-taught (unlike TUM Informatics, which is German-taught)."},
    },
    "tum-mgt": {
        "uni": "de-tu-munich", "uni_name": "Technical University of Munich",
        "prog_suffix": "bsc-management-and-technology",
        "program_name": "Management and Technology", "field_of_study": "Business",
        "degree_type": "BSc",
        "degree_type_local": "Management and Technology B.Sc. (6 semesters, 180 ECTS), Campus Munich, "
        "TUM School of Management; ~70% management + a ~30% technology specialization "
        "(Chemistry, Mechanical Engineering, Informatics, Electrical & Information Technology, "
        "Computer Engineering, or Medicine). Bilingual English/German (Computer Engineering spec 100% English).",
        "duration_value": 6, "duration_unit": "semesters", "language": ["en", "de"],
        "faculty": "TUM School of Management",
        "url": "https://www.tum.de/en/studies/degree-programs/detail/management-and-technology-bachelor-of-science-bsc",
        "platform": "TUMonline", "decision_year": "Winter Semester 2026/27",
        "application_requirements": [
            {"_key": "r1", "_type": "applicationRequirement", "name": "TUMonline online application",
             "necessity": "required", "requirement_type": "form",
             "description": "", "notes": "Winter-semester application period 15 May - 15 July."},
            {"_key": "r2", "_type": "applicationRequirement", "name": "uni-assist Preliminary Documentation (VPD)",
             "necessity": "required", "requirement_type": "other",
             "description": "Credential pre-assessment for applicants with a non-German qualification.", "notes": ""},
            {"_key": "r3", "_type": "applicationRequirement", "name": "Aptitude assessment (Eignungsfeststellungsverfahren)",
             "necessity": "required", "requirement_type": "interview_or_evaluation_event",
             "description": "Two-part aptitude assessment. Scores the final Abitur/GPA plus four half-year grades "
             "in German or English, Mathematics, and an advanced natural science (including Informatics).", "notes": ""},
        ],
        "sources": {
            "adm": {"suffix": "src-mgt-adm",
                "title": "Management and Technology (Campus Munich) -- Bachelor of Science (B.Sc.), TUM",
                "url": "https://www.tum.de/en/studies/degree-programs/detail/management-and-technology-bachelor-of-science-bsc",
                "excerpt": "Management and Technology B.Sc., 6 semesters, 180 ECTS, TUM School of Management, "
                "English and German (Computer Engineering specialization 100% English). Two-part aptitude "
                "assessment scoring final grade/GPA plus half-year grades in German or English, Mathematics, "
                "and an advanced natural science including Informatics. Winter-semester application 15.05-15.07."},
            "fee": {"suffix": "src-mgt-fee",
                "title": "Bachelor in Management & Technology (Munich) -- tuition, TUM School of Management; TUM tuition for non-EU students",
                "url": "https://www.mgt.tum.de/programs/bachelor-management-technology/munich",
                "excerpt": "Non-EU/EEA tuition EUR 2,000/semester (the lower TUM bachelor tier; TUM engineering "
                "programs are EUR 3,000/semester). EU/EEA: no tuition. Munich student-union semester fee EUR 97 "
                "(SS 2026). TUM has announced bachelor non-EU fees rising to EUR 2,300/semester for WS 2027/28 "
                "new entrants (per tum.de/en/studies/fees/tuition)."},
        },
        "admissions": [
            {"suffix": "a-level", "cat": "curriculum-a-level", "curriculum": "British-patterned GCE A-Level",
             "threshold": "A-Level recognised as HZB; admission via the two-part aptitude assessment "
             "(final grade + half-year grades in German or English, Mathematics, and an advanced natural science incl. Informatics)",
             "subjects": ["Mathematics", "An advanced natural science (incl. Informatics)", "German or English"]},
            {"suffix": "ib", "cat": "curriculum-ib", "curriculum": "International Baccalaureate (IB) Diploma",
             "threshold": "IB Diploma recognised as HZB; admission via the two-part aptitude assessment "
             "(final grade + half-year grades in German or English, Mathematics, and an advanced natural science incl. Informatics)",
             "subjects": ["Mathematics", "An advanced natural science (incl. Informatics)", "German or English"]},
            {"suffix": "us-hs", "cat": "curriculum-us-hs", "curriculum": "U.S. High School Diploma / AP route",
             "threshold": "US HS diploma + AP as needed to meet HZB; admission via the two-part aptitude assessment "
             "(final grade/GPA + grades in German or English, Mathematics, and an advanced natural science incl. Informatics)",
             "subjects": ["Mathematics", "An advanced natural science (incl. Informatics)", "English"]},
            {"suffix": "abitur", "cat": "curriculum-abitur", "curriculum": "German Abitur",
             "threshold": "Allgemeine Hochschulreife (Abitur); admission via the two-part aptitude assessment "
             "(final grade + half-year grades in German or English, Mathematics, and an advanced natural science incl. Informatics)",
             "subjects": ["Mathematics", "An advanced natural science (incl. Informatics)", "German or English"]},
        ],
        "stage": "stage-aptitude-assessment",
        "costs": [
            {"suffix": "eu-eea", "cat": "residency-eu-eea", "tuition": 0, "basis": "statutory",
             "year": "2026-27", "mandatory_fees_annual": 194,
             "note": "No tuition for EU/EEA; EUR 97/semester (EUR 194/yr) Munich student-union fee applies."},
            {"suffix": "non-eu", "cat": "residency-non-eu", "tuition": 4000, "basis": "institutional",
             "year": "2026-27", "mandatory_fees_annual": 194,
             "note": "EUR 2,000/semester (2026-27) -- the LOWER TUM bachelor tier, not the EUR 3,000/sem engineering tier "
             "(e.g. Aerospace). + EUR 97/sem union fee. TUM announced an increase to EUR 2,300/semester for non-EU "
             "bachelor entrants in WS 2027/28 (current students grandfathered)."},
        ],
        "living": None,  # No official program living-cost estimate published; not fabricated (same as TUM Aerospace).
        "currency": "EUR",
        "lang_req": {"test_name": "German or English proficiency unless exempt",
            "min_score": "Sufficient German OR English language skills required (program is bilingual; the Computer "
            "Engineering specialization is 100% English). Certificate per TUM language rules unless exempt.",
            "notes": "Unlike TUM Aerospace (English-only), Management and Technology is bilingual English/German."},
    },
    "toronto-econ": {
        "uni": "ca-university-of-toronto", "uni_name": "University of Toronto",
        "prog_suffix": "ba-economics", "checked": "2026-10-20",
        "program_name": "Economics", "field_of_study": "Economics",
        "degree_type": "BA",
        "degree_type_local": "Bachelor of Arts in Economics, Faculty of Arts & Science (St. George). "
        "POST-ADMISSION: you apply to Arts & Science via the Social Sciences admission stream "
        "(OUAC code TAX), NOT to Economics directly. The Economics Major/Specialist/Minor is a "
        "Program of Study (POSt) enrolled after first year on meeting ECO101H1 + ECO102H1 "
        "(min 63% for Major, 70% for Specialist) or ECO105Y1 (80%), plus the required MAT course. "
        "A Financial Economics Specialist (BSc, Science program) also exists.",
        "duration_value": 4, "duration_unit": "years", "language": ["en"],
        "faculty": "Faculty of Arts & Science (Department of Economics)",
        "url": "https://www.economics.utoronto.ca/index.php/index/undergraduate/load/overview",
        "platform": "OUAC", "decision_year": "2026-27 cycle, Fall 2027 entry",
        "application_requirements": [
            {"_key": "r1", "_type": "applicationRequirement", "name": "OUAC application (Arts & Science, Social Sciences stream)",
             "necessity": "required", "requirement_type": "form",
             "description": "Apply to the Faculty of Arts & Science via the Social Sciences admission stream (OUAC code TAX).",
             "notes": "Admission is to Arts & Science, not to Economics directly."},
            {"_key": "r2", "_type": "applicationRequirement", "name": "Economics Program of Study (POSt) — post-admission",
             "necessity": "required", "requirement_type": "other",
             "description": "Not a direct-entry program. Enrol in the Economics Major/Specialist/Minor AFTER first year "
             "by meeting ECO101H1 + ECO102H1 (min 63% Major / 70% Specialist) or ECO105Y1 (80%), plus the required MAT course.",
             "notes": "Grade thresholds per economics.utoronto.ca (POSt enrolment)."},
        ],
        "sources": {
            "adm": {"suffix": "src-econ-adm",
                "title": "Economics (St. George) admission + Undergraduate POSt requirements, U of T",
                "url": "https://future.utoronto.ca/undergraduate-programs/economics/",
                "excerpt": "Economics is admitted via the Faculty of Arts & Science 'Social Sciences' stream "
                "(OUAC code TAX). Ontario prerequisites: English (ENG4U/EAE4U) and Calculus & Vectors (MCV4U). "
                "The Economics program is a post-admission Program of Study: enrol after first year via ECO101H1 + "
                "ECO102H1 (min 63% Major, 70% Specialist) or ECO105Y1 (80%) + MAT (per economics.utoronto.ca)."},
            "fee": {"suffix": "src-econ-fee",
                "title": "Tuition Explorer -- Arts & Science International Fees 2026-27 (Admission Streams Year 1)",
                "url": "https://tuitionexplorer.registrar.utoronto.ca/index.php?academicYear=2026-27&sessionType=1&studyLevel=UG&residency=INT&campus=UTSG&faculty=ARTSC-UG",
                "excerpt": "Admission Streams Year 1 (Commerce, Computer Science, Humanities, Life Sciences, "
                "Mathematical and Physical Sciences, Social Sciences) 2026/27 International: Program Fee CAD 66,110 + "
                "Incidental/System Access 2,100.29 + UHIP 948 = 69,158.29. Domestic Ontario-resident Year-1 A&S rate "
                "CAD 6,100 (Table B1). International tuition rises ~5%/yr for new cohorts."},
        },
        "admissions": [
            {"suffix": "ontario-ossd", "cat": "curriculum-ontario-ossd", "curriculum": "Ontario Secondary School Diploma (OSSD), 4U/M",
             "threshold": "Six 4U/M courses including English (ENG4U) and Calculus & Vectors (MCV4U); competitive admission to the Arts & Science Social Sciences stream",
             "subjects": ["English (ENG4U)", "Calculus & Vectors (MCV4U)", "four additional 4U/M"]},
            {"suffix": "a-level", "cat": "curriculum-a-level", "curriculum": "GCE A-Level",
             "threshold": "Senior-level English and a Calculus course; competitive grades for Social Sciences admission",
             "subjects": ["English", "Mathematics (Calculus)"]},
            {"suffix": "ib", "cat": "curriculum-ib", "curriculum": "International Baccalaureate",
             "threshold": "English and Mathematics (with calculus, e.g. Analysis & Approaches); competitive grades",
             "subjects": ["English", "Mathematics (with calculus)"]},
            {"suffix": "us", "cat": "curriculum-us", "curriculum": "US High School / AP",
             "threshold": "Senior English and a calculus course (e.g. AP Calculus); competitive grades",
             "subjects": ["English", "Calculus (e.g. AP Calculus)"]},
        ],
        # No single admission stage (admission is to Arts & Science; Economics is post-admission POSt). Omit stage.
        "costs": [
            {"suffix": "domestic-ontario", "cat": "residency-domestic-ontario", "tuition": 6100,
             "basis": "statutory", "year": "2026-27",
             "note": "Regulated Ontario-resident Year-1 Arts & Science rate (Table B1; division-wide, = CS Arts & Science)."},
            {"suffix": "international", "cat": "residency-international", "tuition": 66110,
             "basis": "institutional", "year": "2026-27", "mandatory_fees_annual": 3048.29,
             "note": "Arts & Science 'Social Sciences' admission-stream Year-1 international rate (= CS/Commerce/Humanities "
             "Year-1); + 2,100.29 incidental + 948 UHIP. Rises ~5%/yr for new cohorts. Unlike CS, Economics (Social "
             "Sciences) has NO upper-year deregulated jump."},
        ],
        "living": {"min": 1500, "max": 2500, "currency": "CAD", "admin_body": "University of Toronto",
                   "desc": "U of T estimates ~CAD 2,000/month total living expenses; residence + meal CAD 15,167-24,910/yr."},
        "currency": "CAD",
        "lang_req": {
            "test_name": "IELTS Academic (or accepted equivalent) unless exempt",
            "min_score": "IELTS Academic 6.5 overall, no band below 6.0 (per U of T English Language Requirements), unless exempt.",
            "notes": "U of T general English requirement. Verified vs future.utoronto.ca/english-language-requirements."},
    },
    "nyuad-eng": {
        "uni": "ae-nyu-abu-dhabi", "uni_name": "New York University Abu Dhabi",
        "prog_suffix": "bs-general-engineering", "checked": "2026-10-20",
        "program_name": "General Engineering (BS)", "field_of_study": "Engineering",
        "degree_type": "BSc",
        "degree_type_local": "Bachelor of Science, General Engineering (NYUAD Engineering division). "
        "POST-ADMISSION: admission is university-wide via the Common Application; students declare the Engineering "
        "major after entry. Disciplines: General Engineering, Bioengineering, Civil, Computer, Electrical, "
        "Mechanical Engineering.",
        "duration_value": 4, "duration_unit": "years", "language": ["en"],
        "faculty": "Engineering Division",
        "url": "https://nyuad.nyu.edu/en/academics/undergraduate/majors-and-minors/general-engineering-major.html",
        "platform": "Common Application (university-wide; campus preference for Abu Dhabi/NYC/Shanghai, single decision issued)",
        "decision_year": "2026-2027 (Fall 2027 entry)",
        "application_requirements": _NYUAD_APPREQS, "std_tests": _NYUAD_TESTS,
        "sources": _NYUAD_SOURCES,
        "admissions": nyuad_adms(
            "Holistic, whole-candidate admission to NYU Abu Dhabi (not to the major); highly selective, no fixed "
            "grade cutoff. Strong preparation in mathematics and physics is expected for the Engineering track."),
        "stage": "stage-university-entry",
        "costs": _NYUAD_COSTS, "living": None, "currency": "USD", "lang_req": _NYUAD_LANG,
    },
    "nyuad-econ": {
        "uni": "ae-nyu-abu-dhabi", "uni_name": "New York University Abu Dhabi",
        "prog_suffix": "ba-economics", "checked": "2026-10-20",
        "program_name": "Economics (BA)", "field_of_study": "Economics",
        "degree_type": "BA",
        "degree_type_local": "Bachelor of Arts, Economics (NYUAD Social Science division). "
        "POST-ADMISSION: admission is university-wide via the Common Application; students declare the Economics "
        "major after entry (admission criteria do not vary by major).",
        "duration_value": 4, "duration_unit": "years", "language": ["en"],
        "faculty": "Social Science Division",
        "url": "https://nyuad.nyu.edu/en/academics/undergraduate/majors-and-minors.html",
        "platform": "Common Application (university-wide; campus preference for Abu Dhabi/NYC/Shanghai, single decision issued)",
        "decision_year": "2026-2027 (Fall 2027 entry)",
        "application_requirements": _NYUAD_APPREQS, "std_tests": _NYUAD_TESTS,
        "sources": _NYUAD_SOURCES,
        "admissions": nyuad_adms(
            "Holistic, whole-candidate admission to NYU Abu Dhabi (not to the major); highly selective, no fixed "
            "grade cutoff. A strong quantitative/mathematics background is recommended for Economics."),
        "stage": "stage-university-entry",
        "costs": _NYUAD_COSTS, "living": None, "currency": "USD", "lang_req": _NYUAD_LANG,
    },
    "nyuad-bos": {
        "uni": "ae-nyu-abu-dhabi", "uni_name": "New York University Abu Dhabi",
        "prog_suffix": "ba-business-organizations-society", "checked": "2026-10-20",
        "program_name": "Business, Organizations and Society (BA)", "field_of_study": "Business",
        "degree_type": "BA",
        "degree_type_local": "Bachelor of Arts, Business, Organizations and Society (NYUAD Social Science division). "
        "POST-ADMISSION: admission is university-wide via the Common Application; students declare the major after "
        "entry (admission criteria do not vary by major).",
        "duration_value": 4, "duration_unit": "years", "language": ["en"],
        "faculty": "Social Science Division",
        "url": "https://nyuad.nyu.edu/en/academics/undergraduate/majors-and-minors/business-organizations-and-society-major.html",
        "platform": "Common Application (university-wide; campus preference for Abu Dhabi/NYC/Shanghai, single decision issued)",
        "decision_year": "2026-2027 (Fall 2027 entry)",
        "application_requirements": _NYUAD_APPREQS, "std_tests": _NYUAD_TESTS,
        "sources": _NYUAD_SOURCES,
        "admissions": nyuad_adms(
            "Holistic, whole-candidate admission to NYU Abu Dhabi (not to the major); highly selective, no fixed grade cutoff."),
        "stage": "stage-university-entry",
        "costs": _NYUAD_COSTS, "living": None, "currency": "USD", "lang_req": _NYUAD_LANG,
    },
}


def build_docs(key, s):
    uni, ps = s["uni"], s["prog_suffix"]
    prog_id = f"program-{uni}-{ps}"
    src_adm = f"sourceRecord-{uni}-{s['sources']['adm']['suffix']}"
    src_fee = f"sourceRecord-{uni}-{s['sources']['fee']['suffix']}"
    checked = s.get("checked", "2026-10-13")  # verification date (per-spec)
    docs = []

    for which, sid in (("adm", src_adm), ("fee", src_fee)):
        sc = s["sources"][which]
        docs.append({
            "_id": sid, "_type": "sourceRecord", "id": sc["suffix"],
            "source_organization": "University of Oxford" if uni.startswith("gb-university-of-oxford") else s.get("uni_name", uni),
            "source_type": "official_university", "title": sc["title"], "url": sc["url"],
            "excerpt": sc["excerpt"], "notes": "",
            "retrieval_method": "WebSearch/WebFetch (primary-source verification, EvidaPath A3)",
            "retrieved_at": f"{checked}T00:00:00Z", "fields_supported": [],
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
        "application_requirements": s.get("application_requirements") or [
            {"_key": "r1", "_type": "applicationRequirement", "name": "UCAS application",
             "necessity": "required", "requirement_type": "form", "description": "", "notes": s.get("ucas_code_note", "")},
            {"_key": "r2", "_type": "applicationRequirement", "name": s["test_name"],
             "necessity": "required", "requirement_type": "standardized_test_score",
             "description": "", "notes": s.get("test_note", "")},
            {"_key": "r3", "_type": "applicationRequirement", "name": "Interview (at least two colleges)",
             "necessity": "required", "requirement_type": "interview_or_evaluation_event",
             "description": "Shortlisted candidates interviewed by colleges in December.", "notes": ""},
        ],
        "source_refs": [wref(src_adm, "s1"), wref(src_fee, "s2")],
        "extension_metadata": {"_type": "extensionMetadata"},
    })

    has_test = bool(s.get("test_name"))
    stage = s.get("stage")  # optional; omit admission_stage_ref when absent
    living = s.get("living")  # optional; when absent, cost has no living estimate ("not_published")
    admin_body = (living or {}).get("admin_body", s.get("uni_name", ""))
    for a in s["admissions"]:
        req = {
            "_id": f"admissionsRequirement-{uni}-admreq-{ps}-{a['suffix']}", "_type": "admissionsRequirement",
            "id": f"{uni}-admreq-{ps}-{a['suffix']}", "curriculum_type": a["curriculum"],
            "academic_threshold": a["threshold"], "academic_year": "2027 entry",
            "required_subjects": a["subjects"], "program_ref": wref(prog_id),
            "prior_curriculum_category_ref": wref(f"applicantCategory-{uni}-{a['cat']}"),
            "record_status": "VERIFIED", "last_checked": checked,
            "language_requirements": [{"_key": "lr1", "_type": "languageRequirement", "language": "English",
                **s["lang_req"]}],
            "source_refs": [wref(src_adm, "s1")],
        }
        if stage:
            req["admission_stage_ref"] = wref(f"admissionStage-{uni}-{stage}")
        if s.get("std_tests"):  # explicit test list (e.g. NYUAD recommended/test-optional SAT/ACT)
            req["standardized_tests"] = [{"_key": f"st{i+1}", "_type": "testRequirement", **t}
                                         for i, t in enumerate(s["std_tests"])]
        elif has_test:
            req["standardized_tests"] = [{"_key": "st1", "_type": "testRequirement",
                "test_name": s["test_name"], "required": "required", "notes": s.get("test_note", "")}]
        docs.append(req)

    for c in s["costs"]:
        cp = {
            "_id": f"costProfile-{uni}-cost-{ps}-{c['suffix']}", "_type": "costProfile",
            "id": f"{uni}-cost-{ps}-{c['suffix']}", "academic_year": c["year"], "currency": s["currency"],
            "duration_years": s["duration_value"], "tuition_annual": c["tuition"], "tuition_basis": c["basis"],
            "program_ref": wref(prog_id), "residency_category_ref": wref(f"applicantCategory-{uni}-{c['cat']}"),
            "record_status": "VERIFIED", "verification_status": "VERIFIED", "last_checked": checked,
            "mandatory_fees_breakdown": c.get("mandatory_fees_breakdown", []), "other_material_costs": [],
            "living_cost_source_basis": ({"_type": "livingCostSourceBasis",
                "kind": "genuine_cost_of_living_estimate", "administering_body": admin_body,
                "description": living["desc"]} if living else {"_type": "livingCostSourceBasis",
                "kind": "not_published",
                "description": "No official living-cost estimate captured for this program; not fabricated."}),
            "source_refs": [wref(src_fee, "s1")],
            "extension_metadata": ({"_type": "extensionMetadata", "fields": [
                {"_key": "fee_note", "_type": "extensionMetadataFieldEntry", "key": "fee_note",
                 "value": c["note"], "value_type": "string"}]} if c["note"] else {"_type": "extensionMetadata"}),
        }
        if living:
            cp["estimated_living_costs_monthly_range"] = {"_type": "monthlyRange",
                "currency": living["currency"], "min": living["min"], "max": living["max"]}
        if c.get("mandatory_fees_annual") is not None:
            cp["mandatory_fees_annual"] = c["mandatory_fees_annual"]
        docs.append(cp)

    reused = [f"university-{uni}"] + \
             ([f"admissionStage-{uni}-{stage}"] if stage else []) + \
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
    keys = only.split(",") if only else list(PROGRAMS)
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

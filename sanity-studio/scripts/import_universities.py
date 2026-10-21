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
        # provider_type enum: institutional/government/external-private/university-fund.
        # award_type enum: full_tuition/partial_tuition/fixed_amount/stipend/living_cost_support/fee_waiver/mixed.
        # competitive-vs-guaranteed is captured in other_eligibility_criteria (schema has no such enum).
        "scholarships": [
            {"suffix": "presidents", "name": "President's Scholarship", "provider": "American University of Sharjah",
             "provider_type": "institutional", "award_type": "mixed", "renewable": True,
             "award_amount": "100% of tuition and lab fees, plus monthly stipend, housing, travel tickets and medical insurance.",
             "academic_criteria": "IELTS 7.0 / TOEFL iBT 94; e.g. American curriculum 98% CGPA (grades 10–11) + three AP "
             "grade-5 or SAT composite 1400 (requirements vary by curriculum).",
             "other_eligibility_criteria": "COMPETITIVE merit award (not guaranteed); separate application required.",
             "application_deadline": "April 1", "deadline_academic_year": "2027-2028"},
            {"suffix": "chancellors", "name": "Chancellor's Scholarship", "provider": "American University of Sharjah",
             "provider_type": "institutional", "award_type": "mixed", "renewable": True,
             "award_amount": "Full coverage of tuition and lab fees, plus application fee waiver, housing and medical insurance.",
             "academic_criteria": "IELTS 7.0 / TOEFL iBT 94; e.g. American curriculum 98% CGPA (grades 10–11) + two AP "
             "grade-5 or SAT composite 1200.",
             "other_eligibility_criteria": "COMPETITIVE merit award, just below President's; separate application required.",
             "application_deadline": "April 1", "deadline_academic_year": "2027-2028"},
            {"suffix": "merit", "name": "Merit Scholarships", "provider": "American University of Sharjah",
             "provider_type": "institutional", "award_type": "partial_tuition", "renewable": True,
             "award_amount": "10–20% of tuition and lab fees.",
             "academic_criteria": "95% minimum average in grades 10–11.",
             "other_eligibility_criteria": "AUTOMATIC at admission (no competitive application); not guaranteed; "
             "transfer students ineligible.", "application_deadline": None, "deadline_academic_year": None},
            {"suffix": "family-grant", "name": "Family Tuition Grant", "provider": "American University of Sharjah",
             "provider_type": "institutional", "award_type": "partial_tuition", "renewable": True,
             "award_amount": "25% tuition discount for the second and subsequent siblings enrolled simultaneously.",
             "academic_criteria": "",
             "other_eligibility_criteria": "Need-based, GUARANTEED if eligible: multiple siblings enrolled "
             "simultaneously; ineligible if a sibling holds a 100% scholarship.",
             "application_deadline": None, "deadline_academic_year": None},
        ],
    },
    "ae-uaeu": {
        "canonical_name": "United Arab Emirates University", "aliases": ["UAEU"], "country_cc": "ae",
        "city": {"slug": "ae-al-ain", "name": "Al Ain"},
        "website": "https://www.uaeu.ac.ae/", "institution_type": "public",
        "verified_at": "2026-10-21", "currency": "AED",
        "verification_note": "fact-checks/ae-uaeu-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "United Arab Emirates University — official site (uaeu.ac.ae)",
                "url": "https://www.uaeu.ac.ae/",
                "excerpt": "UAEU is the UAE's flagship public (federal) university, in Al Ain, Abu Dhabi emirate; "
                "English medium. Colleges incl. Information Technology (CIT), Engineering, and Business and Economics (CBE)."},
            "adm": {"suffix": "src-adm", "title": "Undergraduate Admissions / English requirements — UAEU",
                "url": "https://www.uaeu.ac.ae/en/admission/undergraduate-admissions-current-student.shtml",
                "excerpt": "International applicants: Grade 12 certificate or equivalent. English for direct admission: "
                "EmSAT Achieve English 1250, or TOEFL ITP 525 / iBT 70, or IELTS Academic 5.5; EmSAT English 1100–1225 "
                "may be conditionally admitted with foundation English. Deadlines: 1st semester May–Jul, 2nd semester Sep–Nov."},
            "fee": {"suffix": "src-fee", "title": "Program and Housing Rates — International Undergraduate Students (2026/27) — UAEU",
                "url": "https://www.uaeu.ac.ae/en/dvcsae/student_account_office/program-and-housing-rates-international-students-undergraduate-students.shtml",
                "excerpt": "International undergraduate rate AY 2026/27 onwards: AED 2,661 per credit hour. Computer Science "
                "120 cr = AED 319,320; Business/Economics programs 120 cr = AED 319,320; Engineering (College of "
                "Engineering) 132 cr = AED 351,252. These are INTERNATIONAL-student rates; UAE nationals are "
                "government-sponsored."},
            "schol": {"suffix": "src-schol", "title": "Undergraduate Scholarships (International Students) — UAEU",
                "url": "https://www.uaeu.ac.ae/en/admission/undergraduate-scholarships.shtml",
                "excerpt": "International-student tuition-waiver scholarships from AY 2025/26: Full Tuition Waiver — "
                "min 98% Grade-12 + TOEFL ITP 590 / iBT 105 / IELTS 7.5. 75% Tuition Waiver — min 95% Grade-12 + "
                "TOEFL ITP 550 / iBT 85 / IELTS 6.5."},
        },
        "curricula": [
            ("a-level", "GCE A-Level / IGCSE", "Applicants with GCE A-Level / IGCSE qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "American High School Diploma", "US-curriculum high school diploma holders."),
            ("uae-shs", "UAE Secondary School Certificate", "UAE national secondary school certificate holders."),
        ],
        "residencies": [
            ("international", "International students",
             "International (non-UAE-national) undergraduate students. UAE nationals are government-sponsored (national rate not separately published)."),
        ],
        # University default cost = 120-credit programs (CS / Business / Economics). Engineering overrides (132 cr).
        "cost": {"residency": "international", "tuition": 79830, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": 0,
            "note": "International rate AY2026/27: AED 2,661/credit × 120 credits = AED 319,320 total program fee "
            "(~AED 79,830/yr over 4 years). UAE nationals are government-sponsored (national rate not separately "
            "published). Excludes housing and other charges."},
        "lang_req": {"test_name": "EmSAT Achieve English / TOEFL / IELTS (unless exempt)",
            "min_score": "EmSAT Achieve English 1250, or TOEFL ITP 525 / iBT 70, or IELTS Academic 5.5 for direct "
            "admission. EmSAT English 1100–1225 may be conditionally admitted with foundation English courses.",
            "notes": "English is the medium of instruction at UAEU."},
        "std_tests": [
            {"test_name": "EmSAT Achieve (UAE)", "required": "required",
             "notes": "EmSAT Achieve English >= 1250 (or TOEFL/IELTS equivalent) for direct admission; EmSAT "
             "Mathematics is also required for STEM programs. International equivalents accepted."},
        ],
        "deadline_note": "Application deadlines: first semester May–July; second semester September–November.",
        "living": None,  # UAEU publishes housing rates but no program cost-of-living estimate captured; not fabricated.
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science",
             "degree": "BSc", "degree_local": "Bachelor of Science in Computer Science, College of Information Technology (CIT).",
             "faculty": "College of Information Technology", "duration": 4,
             "url": "https://www.uaeu.ac.ae/en/catalog/undergraduate/programs/bachelor-of-science-in-computer-science.shtml",
             "subjects_note": "Grade 12 certificate; strong mathematics (EmSAT Math for STEM); English per requirements",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "us-hs": ["Mathematics"], "uae-shs": ["Mathematics"]}},
            {"suffix": "bsc-eng", "program_name": "Engineering", "field": "Engineering",
             "degree": "BSc", "degree_local": "Bachelor of Science in Engineering, College of Engineering; "
             "specializations across the college (e.g. civil, electrical, mechanical, chemical).",
             "faculty": "College of Engineering", "duration": 4,
             "url": "https://www.uaeu.ac.ae/en/eng/",
             "subjects_note": "Grade 12 certificate; Mathematics and Physics (EmSAT Math for STEM); English per requirements",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics", "Physics"],
                          "us-hs": ["Mathematics", "Physics"], "uae-shs": ["Mathematics", "Physics"]},
             "cost": {"residency": "international", "tuition": 87813, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "International rate AY2026/27: AED 2,661/credit × 132 credits = AED 351,252 total program fee "
                 "(~AED 87,813/yr over 4 years) — higher than the 120-credit CS/Business/Economics programs. UAE "
                 "nationals government-sponsored. Excludes housing."}},
            {"suffix": "bba", "program_name": "Business Administration", "field": "Business",
             "degree": "BBA", "degree_local": "Bachelor of Business Administration, College of Business and Economics "
             "(CBE); majors incl. Marketing, Human Resources, Supply Chain & Logistics, Entrepreneurship.",
             "faculty": "College of Business and Economics", "duration": 4,
             "url": "https://www.uaeu.ac.ae/en/cbe/",
             "subjects_note": "Grade 12 certificate; Mathematics; English per requirements",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "us-hs": ["Mathematics"], "uae-shs": ["Mathematics"]}},
            {"suffix": "b-econ", "program_name": "Economics", "field": "Economics",
             "degree": "BSc", "degree_local": "Bachelor of Economics, College of Business and Economics (CBE).",
             "faculty": "College of Business and Economics", "duration": 4,
             "url": "https://www.uaeu.ac.ae/en/cbe/",
             "subjects_note": "Grade 12 certificate; Mathematics; English per requirements",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "us-hs": ["Mathematics"], "uae-shs": ["Mathematics"]}},
        ],
        "scholarships": [
            {"suffix": "full-waiver", "name": "Full Tuition Waiver (International Students)",
             "provider": "United Arab Emirates University", "provider_type": "institutional", "award_type": "full_tuition",
             "renewable": True, "award_amount": "100% tuition waiver.",
             "academic_criteria": "Minimum 98% in the General Secondary School Certificate (Grade 12) + English: "
             "TOEFL ITP 590 / iBT 105 / IELTS Academic 7.5.",
             "other_eligibility_criteria": "Merit-based scholarship for international students (from AY 2025/26); "
             "awarded on meeting the threshold.", "application_deadline": None, "deadline_academic_year": "2026-2027"},
            {"suffix": "partial-75", "name": "75% Tuition Waiver (International Students)",
             "provider": "United Arab Emirates University", "provider_type": "institutional", "award_type": "partial_tuition",
             "renewable": True, "award_amount": "75% tuition waiver.",
             "academic_criteria": "Minimum 95% in the General Secondary School Certificate (Grade 12) + English: "
             "TOEFL ITP 550 / iBT 85 / IELTS Academic 6.5.",
             "other_eligibility_criteria": "Merit-based scholarship for international students (from AY 2025/26).",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },
    "us-princeton": {
        "canonical_name": "Princeton University", "aliases": ["Princeton"], "country_cc": "us",
        "city": {"slug": "us-princeton", "name": "Princeton"},
        "website": "https://www.princeton.edu/", "institution_type": "private-nonprofit",
        "verified_at": "2026-10-21", "currency": "USD",
        "verification_note": "fact-checks/us-princeton-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "Princeton University — official site & Academics",
                "url": "https://www.princeton.edu/academics/areas-of-study",
                "excerpt": "Princeton offers A.B. (Bachelor of Arts) and B.S.E. (Bachelor of Science in Engineering) "
                "degrees. Computer Science offers BOTH A.B. and B.S.E.; Economics is an A.B.; B.S.E. is granted by six "
                "SEAS departments (CEE, CBE, CS, ECE, MAE, ORFE). Princeton offers NO standalone undergraduate business "
                "major (only a Finance minor and certificates)."},
            "adm": {"suffix": "src-adm", "title": "Standardized Testing & International Students — Princeton Admission",
                "url": "https://admission.princeton.edu/apply/standardized-testing",
                "excerpt": "Test-optional for fall 2026 and fall 2027 entry; standardized testing required again from "
                "fall 2028 entry (2027-28 cycle). International applicants whose native language is not English and who "
                "attend a school where English is not the language of instruction must submit TOEFL / IELTS Academic / "
                "Duolingo / PTE Academic."},
            "fee": {"suffix": "src-fee", "title": "Cost of Attendance 2026-27 — Princeton Admission",
                "url": "https://admission.princeton.edu/cost-aid/fees-payment-options",
                "excerpt": "2026-27 estimated cost of attendance $94,624: tuition $68,140; housing $13,010; food $9,110; "
                "fees $314; books/supplies $1,050; personal $3,000. Student Health Plan $4,220 if not otherwise insured. "
                "Same sticker price for all students; Princeton meets 100% of demonstrated need with grant aid."},
            "schol": {"suffix": "src-schol", "title": "How Princeton's Aid Program Works — Princeton Admission",
                "url": "https://admission.princeton.edu/cost-aid/how-princetons-aid-program-works",
                "excerpt": "Princeton meets 100% of demonstrated financial need with grant aid (no loans) for all admitted "
                "students; admission is need-blind including for international students (full need met the same as for US "
                "students). Average aid package 2026-27 > $83,000. Princeton offers NO academic or athletic merit scholarships."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "US High School Diploma", "US high school diploma / American curriculum applicants."),
            ("international-other", "General International Secondary Qualification", "Other international secondary qualifications."),
        ],
        "residencies": [
            ("all-students", "All students (uniform tuition)",
             "US private university: the same sticker tuition for domestic and international students (no residency split). Need-based aid differs by family need."),
        ],
        "cost": {"residency": "all-students", "tuition": 68140, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": 314,
            "note": "Sticker cost of attendance 2026-27 = $94,624 (tuition 68,140 + fees 314 + housing 13,010 + food "
            "9,110 + books 1,050 + personal 3,000). Student Health Plan $4,220 extra if uninsured. SAME sticker for all "
            "students; Princeton is need-blind and meets 100% of demonstrated need with GRANT aid (no loans), so most "
            "families pay far less — affordability depends on family need, not a published discount."},
        "lang_req": {"test_name": "TOEFL / IELTS Academic / Duolingo / PTE Academic (if required)",
            "min_score": "Required only if English is not your native language AND you attend a school where English is "
            "not the language of instruction; Princeton does not publish fixed minimum scores.",
            "notes": "Not required for applicants educated in English-medium schools."},
        "std_tests": [
            {"test_name": "SAT or ACT", "required": "recommended",
             "notes": "Test-optional for fall 2026 and fall 2027 entry; standardized testing REQUIRED again from fall "
             "2028 entry (2027-28 application cycle)."},
        ],
        "deadline_note": "Apply via the Common/Coalition Application (single-choice early action ~Nov 1; regular decision ~Jan 1).",
        "living": {"min": 2180, "max": 2910, "currency": "USD", "admin_body": "Princeton University",
            "desc": "Princeton COA 2026-27 non-tuition/fees: housing $13,010 + food $9,110 + books $1,050 + personal "
            "$3,000 = $26,170/yr (~$2,180–2,910/mo over 12 vs 9 months). Student Health Plan $4,220 extra if uninsured."},
        "programs": [
            {"suffix": "cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "Computer Science — offered as A.B. (Bachelor of Arts) or B.S.E. (Bachelor of Science in Engineering).",
             "faculty": "Department of Computer Science (School of Engineering & Applied Science)", "duration": 4,
             "url": "https://www.cs.princeton.edu/ugrad/undergraduate-degrees-requirements",
             "subjects_note": "Holistic whole-application review; strong preparation in mathematics and science expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "bse-engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BSc",
             "degree_local": "B.S.E. (Bachelor of Science in Engineering), School of Engineering & Applied Science; "
             "departments: Civil & Environmental, Chemical & Biological, Electrical & Computer, Mechanical & Aerospace, "
             "Operations Research & Financial Engineering (and Computer Science).",
             "faculty": "School of Engineering and Applied Science", "duration": 4,
             "url": "https://engineering.princeton.edu/undergraduate-studies/concentrations",
             "subjects_note": "Holistic whole-application review; strong preparation in mathematics and physics expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "ab-economics", "program_name": "Economics", "field": "Economics", "degree": "BA",
             "degree_local": "A.B. (Bachelor of Arts) in Economics. Prerequisites incl. ECO 100/101/202 + MAT 175 "
             "(calculus) by end of sophomore year (C or better).",
             "faculty": "Department of Economics", "duration": 4,
             "url": "https://economics.princeton.edu/undergraduate-program/concentration-requirements/",
             "subjects_note": "Holistic whole-application review; strong quantitative preparation (calculus) expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
        ],
        # Princeton has NO undergraduate Business major (verified) — omitted, not fabricated.
        "scholarships": [
            {"suffix": "need-based-aid", "name": "Need-Based Financial Aid (meets 100% of demonstrated need)",
             "provider": "Princeton University", "provider_type": "institutional", "award_type": "mixed", "renewable": True,
             "award_amount": "Grant aid meeting 100% of demonstrated financial need (no loans); average package 2026-27 > $83,000.",
             "academic_criteria": "Awarded solely on demonstrated financial need; admission is need-blind for all applicants, including international.",
             "other_eligibility_criteria": "GUARANTEED for every admitted student with demonstrated need, all four years. "
             "Princeton offers NO academic or athletic merit scholarships (aid is 100% need-based).",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },
    "us-mit": {
        "canonical_name": "Massachusetts Institute of Technology", "aliases": ["MIT"], "country_cc": "us",
        "city": {"slug": "us-cambridge-ma", "name": "Cambridge"},
        "website": "https://www.mit.edu/", "institution_type": "private-nonprofit",
        "verified_at": "2026-10-21", "currency": "USD",
        "verification_note": "fact-checks/us-mit-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "MIT — Degree Charts / undergraduate majors",
                "url": "https://catalog.mit.edu/degree-charts/",
                "excerpt": "MIT grants the S.B. (Bachelor of Science). Course 6-3 Computer Science and Engineering (EECS); "
                "Course 14-1 Economics (SHASS); Course 15 Management (Sloan: 15-1 Management, 15-2 Business Analytics, "
                "15-3 Finance); numerous engineering courses (2 Mechanical, 16 Aerospace, 6 Electrical, 10 Chemical, 1 Civil)."},
            "adm": {"suffix": "src-adm", "title": "MIT Admissions — testing & international English requirements",
                "url": "https://mitadmissions.org/apply/firstyear/tests-scores/",
                "excerpt": "SAT or ACT is REQUIRED (e.g. fall 2025 entrants SAT 1520–1570, ACT 34–35 mid-50%). "
                "International applicants who need to demonstrate English proficiency: minimum IELTS 7.0 or TOEFL iBT 100; "
                "applications without required English scores may not be reviewed."},
            "fee": {"suffix": "src-fee", "title": "Cost of Attendance 2026-2027 — MIT Student Financial Services",
                "url": "https://sfs.mit.edu/undergraduate-students/the-cost-of-attendance/coa/",
                "excerpt": "2026-27 total cost of attendance $92,760: tuition $66,720; student life fee $420; housing "
                "$14,090; food $8,104; books/materials $930; personal $2,496. Same sticker for all students; MIT meets "
                "full demonstrated need."},
            "schol": {"suffix": "src-schol", "title": "Making MIT Affordable / Financial Aid — MIT SFS",
                "url": "https://sfs.mit.edu/undergraduate-students/the-cost-of-attendance/making-mit-affordable/",
                "excerpt": "MIT is need-blind for ALL applicants incl. international and meets 100% of demonstrated need "
                "for all four years; no merit scholarships, no loans. Since fall 2025, families earning < $200,000 "
                "typically pay no tuition; families < $100,000 typically contribute nothing to cost of attendance."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "US High School Diploma", "US high school diploma / American curriculum applicants."),
            ("international-other", "General International Secondary Qualification", "Other international secondary qualifications."),
        ],
        "residencies": [
            ("all-students", "All students (uniform tuition)",
             "US private university: the same sticker tuition for domestic and international students (no residency split). Need-based aid differs by family need."),
        ],
        "cost": {"residency": "all-students", "tuition": 66720, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": 420,
            "note": "Sticker cost of attendance 2026-27 = $92,760 (tuition 66,720 + student-life fee 420 + housing 14,090 "
            "+ food 8,104 + books 930 + personal 2,496). SAME sticker for all students; MIT is need-blind (incl. "
            "international) and meets 100% of demonstrated need with grants (no loans). Since fall 2025, families earning "
            "< $200k typically pay no tuition and < $100k typically contribute nothing — net cost depends on family need."},
        "lang_req": {"test_name": "IELTS Academic / TOEFL iBT (if required)",
            "min_score": "IELTS Academic 7.0 or TOEFL iBT 100 minimum for international applicants required to demonstrate English proficiency.",
            "notes": "Applications may not be reviewed without required English scores."},
        "std_tests": [
            {"test_name": "SAT or ACT", "required": "required",
             "notes": "SAT or ACT is required (fall 2025 entrants: SAT 1520–1570, ACT 34–35 mid-50%)."},
        ],
        "deadline_note": "Apply via MIT's own application (early action ~Nov 1; regular action ~Jan 1).",
        "living": {"min": 2135, "max": 2850, "currency": "USD", "admin_body": "Massachusetts Institute of Technology",
            "desc": "MIT COA 2026-27 non-tuition/fees: housing $14,090 + food $8,104 + books $930 + personal $2,496 = "
            "$25,620/yr (~$2,135–2,850/mo over 12 vs 9 months)."},
        "programs": [
            {"suffix": "cs-6-3", "program_name": "Computer Science and Engineering", "field": "Computer Science", "degree": "BSc",
             "degree_local": "S.B. in Computer Science and Engineering (Course 6-3), Dept. of EECS / Schwarzman College of Computing.",
             "faculty": "Department of Electrical Engineering and Computer Science", "duration": 4,
             "url": "https://www.eecs.mit.edu/academics/undergraduate-programs/curriculum/6-3-computer-science-and-engineering/",
             "subjects_note": "Holistic whole-application review; strong preparation in mathematics and science expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BSc",
             "degree_local": "S.B. in engineering (e.g. Mechanical (2), Aerospace (16), Electrical (6-1/6-2), Chemical (10), Civil & Environmental (1)).",
             "faculty": "MIT School of Engineering", "duration": 4,
             "url": "https://catalog.mit.edu/degree-charts/",
             "subjects_note": "Holistic whole-application review; strong preparation in mathematics and physics expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "econ-14-1", "program_name": "Economics", "field": "Economics", "degree": "BSc",
             "degree_local": "S.B. in Economics (Course 14-1), School of Humanities, Arts & Social Sciences.",
             "faculty": "Department of Economics", "duration": 4,
             "url": "https://catalog.mit.edu/subjects/14/",
             "subjects_note": "Holistic whole-application review; strong quantitative preparation expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "mgmt-15", "program_name": "Management (Sloan)", "field": "Business", "degree": "BSc",
             "degree_local": "S.B. via MIT Sloan (Course 15): 15-1 Management, 15-2 Business Analytics, or 15-3 Finance.",
             "faculty": "MIT Sloan School of Management", "duration": 4,
             "url": "https://mitsloan.mit.edu/programs/undergraduate/undergraduate-programs",
             "subjects_note": "Holistic whole-application review; strong quantitative preparation expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
        ],
        "scholarships": [
            {"suffix": "need-based-aid", "name": "Need-Based Financial Aid (meets 100% of demonstrated need)",
             "provider": "Massachusetts Institute of Technology", "provider_type": "institutional", "award_type": "mixed",
             "renewable": True,
             "award_amount": "Grant aid meeting 100% of demonstrated need (no loans). Families < $200k income typically "
             "pay no tuition; < $100k typically contribute nothing (since fall 2025).",
             "academic_criteria": "Awarded solely on demonstrated financial need; admission is need-blind for all applicants, including international.",
             "other_eligibility_criteria": "GUARANTEED for every admitted student with demonstrated need, all four years. "
             "MIT offers NO merit scholarships (aid is 100% need-based).",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },
    "ae-khalifa": {
        "canonical_name": "Khalifa University of Science and Technology", "aliases": ["Khalifa University", "KU"],
        "country_cc": "ae", "city": {"slug": "ae-abu-dhabi", "name": "Abu Dhabi", "reuse_published": True},
        "website": "https://www.ku.ac.ae/", "institution_type": "public",
        "verified_at": "2026-10-21", "currency": "AED",
        "verification_note": "fact-checks/ae-khalifa-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "Undergraduate Degree Programs — Khalifa University",
                "url": "https://www.ku.ac.ae/academics/undergraduate-programs",
                "excerpt": "Khalifa University of Science and Technology (Abu Dhabi) is a STEM-focused public research "
                "university. Undergraduate B.Sc. programs: Computer Science (AI and Cybersecurity concentrations), "
                "Computer Engineering, Applied Mathematics/Statistics/Data Science, and Engineering (Aerospace, "
                "Biomedical, Chemical, Civil, Electrical, Industrial & Systems, Mechanical, Petroleum). No undergraduate "
                "Business or Economics programs."},
            "adm": {"suffix": "src-adm", "title": "Undergraduate Admissions / English requirements — Khalifa University",
                "url": "https://www.ku.ac.ae/undergraduate-admissions",
                "excerpt": "English (direct): IELTS Academic 6.0 / TOEFL iBT 79 / EmSAT English 1400; conditional "
                "IELTS 5.5 / iBT 70 / EmSAT 1250. Grade 12 within the last two years; strong grades (UAE stream 80% "
                "Advanced/Elite, 90% General). Computer Science requires Mathematics (a science optional). SAT Math >= "
                "700 may be considered."},
            "fee": {"suffix": "src-fee", "title": "Fee and Payment Guidelines — Khalifa University",
                "url": "https://www.ku.ac.ae/fee-and-payment-guidelines",
                "excerpt": "B.Sc. tuition AED 2,500 per credit hour; approximately AED 81,250 per year over a 4-year "
                "normal duration. Uniform across Engineering and Science colleges and across nationalities (no "
                "national/expat base-rate difference). Seat-holding deposit AED 5,000 (one-time). Year not explicitly stated."},
            "schol": {"suffix": "src-schol", "title": "Partial Scholarships for International Students — Khalifa University",
                "url": "https://www.ku.ac.ae/partial-scholarships-for-international-students",
                "excerpt": "Partial scholarships for international undergraduates (maintain CGPA 3.0+): College of Science "
                "75% tuition discount (net ~AED 25,000/yr); College of Engineering 50% discount (net ~AED 50,000/yr), "
                "against a stated base tuition of AED 100,000/yr. Excludes summer terms, dorms and transport."},
        },
        "curricula": [
            ("a-level", "GCE A-Level / IGCSE", "Applicants with GCE A-Level / IGCSE qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "American High School Diploma / SAT", "US-curriculum applicants (SAT Math may be considered)."),
            ("uae-shs", "UAE Secondary School Certificate", "UAE national secondary school certificate holders."),
        ],
        "residencies": [
            ("all-students", "All students (uniform base tuition)",
             "Khalifa charges the same base per-credit tuition for all students (no national/expat base-rate split); "
             "scholarships, not nationality, determine net cost."),
        ],
        "cost": {"residency": "all-students", "tuition": 81250, "basis": "institutional",
            "year": "2026-2027 (year not explicitly stated on KU fee page)", "mandatory_fees_annual": 0,
            "note": "SOURCE CONFLICT (shown, not reconciled): KU fee page = AED 2,500/credit ≈ AED 81,250/yr over 4 "
            "years; KU scholarship page states a 'base tuition AED 100,000/yr' against which discounts are computed "
            "(≈40-credit nominal load). Both from ku.ac.ae. tuition_annual uses the fee-page 81,250 basis; the "
            "scholarship net figures below use KU's 100,000 base. One-time seat-holding deposit AED 5,000. Dorms and "
            "transport are extra. Uniform across colleges and nationalities."},
        "lang_req": {"test_name": "IELTS Academic / TOEFL iBT / EmSAT English",
            "min_score": "Direct admission: IELTS 6.0 / TOEFL iBT 79 / EmSAT English 1400. Conditional: IELTS 5.5 / "
            "TOEFL iBT 70 / EmSAT English 1250.", "notes": "English is the medium of instruction."},
        "std_tests": [
            {"test_name": "EmSAT / SAT (as applicable)", "required": "required",
             "notes": "Admission requires EmSAT (or accepted equivalent); SAT Math >= 700 may be considered, especially "
             "for international / non-UAE-system applicants. Strong Grade-12 results required (UAE stream 80% Advanced/"
             "Elite, 90% General)."},
        ],
        "deadline_note": "Apply via the Khalifa University online admissions portal (ku.ac.ae/ug-apply).",
        "living": None,  # Dorms/transport are charged separately; no program cost-of-living estimate captured. Not fabricated.
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "Bachelor of Science in Computer Science (concentrations in Artificial Intelligence and "
             "Cybersecurity), College of Computing and Mathematical Sciences.",
             "faculty": "College of Computing and Mathematical Sciences", "duration": 4,
             "url": "https://www.ku.ac.ae/academics/undergraduate-programs",
             "subjects_note": "Grade 12 certificate; Mathematics required (a science optional); strong grades + EmSAT/English",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "us-hs": ["Mathematics"], "uae-shs": ["Mathematics"]}},
            {"suffix": "bsc-eng", "program_name": "Engineering", "field": "Engineering", "degree": "BSc",
             "degree_local": "Bachelor of Science in Engineering, College of Engineering; disciplines: Aerospace, "
             "Biomedical, Chemical, Civil, Electrical, Industrial & Systems, Mechanical, Petroleum, and Computer Engineering.",
             "faculty": "College of Engineering", "duration": 4,
             "url": "https://www.ku.ac.ae/academics/undergraduate-programs",
             "subjects_note": "Grade 12 certificate; Mathematics and Physics; strong grades + EmSAT/English",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics", "Physics"],
                          "us-hs": ["Mathematics", "Physics"], "uae-shs": ["Mathematics", "Physics"]}},
        ],
        # STEM-only university: NO Business or Economics undergraduate programs (verified absent) — omitted, not fabricated.
        "scholarships": [
            {"suffix": "sci-75", "name": "Partial Scholarship — College of Science (75%)",
             "provider": "Khalifa University", "provider_type": "institutional", "award_type": "partial_tuition",
             "renewable": True, "award_amount": "75% tuition discount (net ~AED 25,000/yr on KU's AED 100,000/yr base).",
             "academic_criteria": "Maintain a cumulative GPA of 3.0 or higher during studies.",
             "other_eligibility_criteria": "Partial scholarship for international undergraduates in College of Science "
             "programs (incl. Computer Science). Excludes summer terms, dorms and transport.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
            {"suffix": "eng-50", "name": "Partial Scholarship — College of Engineering (50%)",
             "provider": "Khalifa University", "provider_type": "institutional", "award_type": "partial_tuition",
             "renewable": True, "award_amount": "50% tuition discount (net ~AED 50,000/yr on KU's AED 100,000/yr base).",
             "academic_criteria": "Maintain a cumulative GPA of 3.0 or higher during studies.",
             "other_eligibility_criteria": "Partial scholarship for international undergraduates in College of "
             "Engineering programs. Excludes summer terms, dorms and transport.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
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

    # City. If reuse_published, point at an already-published city-<slug> (e.g. city-ae-abu-dhabi
    # from NYUAD) and do NOT create a duplicate; else create a draft city.
    reuse_city = s["city"].get("reuse_published", False)
    if not reuse_city:
        docs.append({"_id": D + city_id, "_type": "city", "id": s["city"]["slug"], "name": s["city"]["name"],
            "country_ref": wref(f"country-{cc}", draft=False)})
    city_ref = wref(city_id, draft=not reuse_city)

    # University
    docs.append({"_id": D + uni_id, "_type": "university", "id": slug,
        "canonical_name": s["canonical_name"], "aliases": s.get("aliases", []),
        "country_ref": wref(f"country-{cc}", draft=False), "primary_city_ref": city_ref,
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

    lang = s["lang_req"]
    living = s.get("living")
    for p in s["programs"]:
        cost = p.get("cost", s.get("cost"))  # per-program cost override; else university default
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

    # Scholarships — schema fields: provider_type, institutions_covered (uni id strings),
    # programs_covered, degree_levels, eligible_citizenships, award_type, award_amount,
    # academic_criteria, other_eligibility_criteria, official_source_url, verification_status, etc.
    schol_src = s["sources"]["schol"]
    for sch in s.get("scholarships", []):
        doc = {"_id": D + f"scholarship-{slug}-{sch['suffix']}", "_type": "scholarship",
            "id": f"{slug}-{sch['suffix']}", "name": sch["name"], "provider": sch["provider"],
            "provider_type": sch["provider_type"], "institutions_covered": [slug],
            "programs_covered": ["all-undergraduate-majors"], "degree_levels": ["undergraduate"],
            "eligible_citizenships": ["all"], "award_type": sch["award_type"],
            "award_amount": sch["award_amount"], "academic_criteria": sch.get("academic_criteria", ""),
            "other_eligibility_criteria": sch.get("other_eligibility_criteria", ""),
            "renewable": sch["renewable"], "official_source_url": schol_src["url"],
            "source_refs": [wref(src_id("schol"), "s1")], "last_checked": s["verified_at"],
            "verification_status": "VERIFIED", "record_status": "VERIFIED",
            "extension_metadata": {"_type": "extensionMetadata"}}
        if sch.get("application_deadline"):
            doc["application_deadline"] = sch["application_deadline"]
        if sch.get("deadline_academic_year"):
            doc["deadline_academic_year"] = sch["deadline_academic_year"]
        docs.append(doc)

    reused = [f"country-{cc}"]  # published country must exist
    if s["city"].get("reuse_published"):
        reused.append(city_id)  # reused published city must exist
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

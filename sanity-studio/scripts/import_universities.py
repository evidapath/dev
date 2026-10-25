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
    # Internal refs ALWAYS point to the BASE id (no drafts. prefix). Even though the docs live as
    # drafts (drafts.<id>), Sanity's "drafts" perspective overlays drafts onto base ids, so a weak
    # ref to the base id resolves to the draft in that perspective — and resolves to the published doc
    # after publishing (which strips the drafts. prefix). The `draft` arg is kept for call-site compat.
    r = {"_ref": ref, "_type": "reference", "_weak": True}
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
    "ae-university-of-sharjah": {
        "canonical_name": "University of Sharjah", "aliases": ["UOS"], "country_cc": "ae",
        "city": {"slug": "ae-sharjah", "name": "Sharjah"},
        "website": "https://www.sharjah.ac.ae/", "institution_type": "public",
        "verified_at": "2026-10-21", "currency": "AED",
        "verification_note": "fact-checks/ae-university-of-sharjah-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "University of Sharjah — Undergraduate Admissions",
                "url": "https://www.sharjah.ac.ae/Admissions/Undergraduate",
                "excerpt": "University of Sharjah (UOS) is a public university in Sharjah, UAE; English medium for its "
                "English-taught programs. Colleges incl. Computing & Informatics, Engineering, Business Administration. "
                "Undergraduate programs include Computer Science, Computer Engineering, Business Administration majors, "
                "and Economics (New)."},
            "adm": {"suffix": "src-adm", "title": "Undergraduate Admission Policy / English — University of Sharjah",
                "url": "https://www.sharjah.ac.ae/Admissions/Undergraduate-Admission-FAQs",
                "excerpt": "English proficiency for English-taught programs: TOEFL ITP 550 / Academic IELTS 6.0 / EmSAT "
                "English 1400 (IBT TOEFL and PTE Academic also accepted). Grade 12 with a minimum ~70% average (varies "
                "by program; some engineering programs higher)."},
            "fee": {"suffix": "src-fee", "title": "Undergraduate Tuition Fees (AED) — University of Sharjah",
                "url": "https://uosadmission.sharjah.ac.ae/assets/image/Tuition_Fees_En.pdf",
                "excerpt": "Per official UOS tuition schedule: Computer Science & Computing programs, Business "
                "Administration majors, Economics (New), and Electrical & Electronics / Computer Engineering = AED 2,529 "
                "per credit hour; AED 30,351 per semester (12–16 credits); ~AED 60,703 per year. (Mechanical ~2,772, "
                "Nuclear ~2,786 are higher.) Semester fee covers 12–16 credits."},
            "schol": {"suffix": "src-schol", "title": "Financial Aid & Scholarships — University of Sharjah",
                "url": "https://www.sharjah.ac.ae/Admissions/Financial-Aids/Student-Support-Fund",
                "excerpt": "New high-school graduates receive a 50% reduction in first-semester tuition (all colleges "
                "except Medicine & Dentistry). Full scholarships for the top five UAE high-school graduates (full tuition, "
                "entire duration). Student Support Fund (SSF): need-based aid for undergraduates, available after the "
                "first academic year."},
        },
        "curricula": [
            ("a-level", "GCE A-Level / IGCSE", "Applicants with GCE A-Level / IGCSE qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "American High School Diploma", "US-curriculum high school diploma holders."),
            ("uae-shs", "UAE Secondary School Certificate", "UAE national secondary school certificate holders."),
        ],
        "residencies": [
            ("all-students", "All students (uniform base tuition)",
             "UOS charges the same base per-credit tuition by program; scholarships (incl. the 50% new-grad reduction), not nationality, reduce net cost."),
        ],
        "cost": {"residency": "all-students", "tuition": 60703, "basis": "institutional",
            "year": "2026-2027 (per current UOS tuition schedule)", "mandatory_fees_annual": 0,
            "note": "AED 2,529/credit; AED 30,351/semester (covers 12–16 credits) => ~AED 60,703/yr for Computer "
            "Science, Business Administration, Economics (New) and Electrical/Computer Engineering. (Mechanical ~2,772/"
            "credit, Nuclear ~2,786 are higher — not modeled here.) University services fees and dorms additional. "
            "NOTE: an earlier web summary cited AED 2,347/credit; the official UOS tuition schedule says 2,529 — the "
            "schedule is used here."},
        "lang_req": {"test_name": "TOEFL ITP / Academic IELTS / EmSAT English / TOEFL iBT / PTE Academic",
            "min_score": "TOEFL ITP 550, or Academic IELTS 6.0, or EmSAT English 1400 (IBT TOEFL and PTE Academic also accepted).",
            "notes": "Required for English-taught programs."},
        "std_tests": [
            {"test_name": "EmSAT (or accepted equivalent)", "required": "required",
             "notes": "Admission testing per UOS; Grade-12 minimum ~70% average (varies by program; some engineering higher)."},
        ],
        "deadline_note": "Apply via the University of Sharjah online admissions portal (uosadmission.sharjah.ac.ae).",
        "living": None,  # UOS publishes dorm rates but no full cost-of-living estimate captured; not fabricated.
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "Bachelor of Science in Computer Science, College of Computing and Informatics.",
             "faculty": "College of Computing and Informatics", "duration": 4,
             "url": "https://www.sharjah.ac.ae/academics/degree/undergraduate/computer-engineering",
             "subjects_note": "Grade 12 (~70% min); Mathematics; English per requirements",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "us-hs": ["Mathematics"], "uae-shs": ["Mathematics"]}},
            {"suffix": "bsc-eng", "program_name": "Engineering", "field": "Engineering", "degree": "BSc",
             "degree_local": "Bachelor of Science in Engineering, College of Engineering (e.g. Electrical & Electronics, "
             "Computer, Civil, Industrial Engineering). Representative rate shown; Mechanical/Nuclear are higher.",
             "faculty": "College of Engineering", "duration": 4,
             "url": "https://www.sharjah.ac.ae/academics/degree/undergraduate/computer-engineering",
             "subjects_note": "Grade 12 (~70% min, some higher); Mathematics and Physics; English per requirements",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics", "Physics"],
                          "us-hs": ["Mathematics", "Physics"], "uae-shs": ["Mathematics", "Physics"]}},
            {"suffix": "bba", "program_name": "Business Administration", "field": "Business", "degree": "BBA",
             "degree_local": "Bachelor of Business Administration, College of Business Administration (majors incl. "
             "Management, Marketing, Human Resources, Finance, Supply Chain).",
             "faculty": "College of Business Administration", "duration": 4,
             "url": "https://www.sharjah.ac.ae/Admissions/Undergraduate",
             "subjects_note": "Grade 12 (~70% min); Mathematics; English per requirements",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "us-hs": ["Mathematics"], "uae-shs": ["Mathematics"]}},
            {"suffix": "b-econ", "program_name": "Economics", "field": "Economics", "degree": "BSc",
             "degree_local": "Bachelor in Economics (listed as 'Economics (New)'), College of Business Administration. "
             "Fee follows the Business college schedule.",
             "faculty": "College of Business Administration", "duration": 4,
             "url": "https://www.sharjah.ac.ae/Admissions/Undergraduate",
             "subjects_note": "Grade 12 (~70% min); Mathematics; English per requirements",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "us-hs": ["Mathematics"], "uae-shs": ["Mathematics"]}},
        ],
        "scholarships": [
            {"suffix": "new-grad-50", "name": "New High-School Graduate Scholarship (50% first semester)",
             "provider": "University of Sharjah", "provider_type": "institutional", "award_type": "partial_tuition",
             "renewable": False, "award_amount": "50% reduction in first-semester tuition fees.",
             "academic_criteria": "New high-school graduates.",
             "other_eligibility_criteria": "AUTOMATIC for new high-school graduates in all colleges except Medicine and "
             "Dentistry; first semester only (not renewed).", "application_deadline": None, "deadline_academic_year": "2026-2027"},
            {"suffix": "top5-full", "name": "Full Scholarship — Top 5 UAE High-School Graduates",
             "provider": "University of Sharjah", "provider_type": "institutional", "award_type": "full_tuition",
             "renewable": True, "award_amount": "Full tuition for the entire undergraduate duration.",
             "academic_criteria": "Among the top five high-school graduates in the UAE.",
             "other_eligibility_criteria": "COMPETITIVE and highly limited (top 5 nationally); accredited programs incl. "
             "engineering, business administration, computer science & engineering.", "application_deadline": None,
             "deadline_academic_year": "2026-2027"},
            {"suffix": "ssf", "name": "Student Support Fund (need-based)",
             "provider": "University of Sharjah", "provider_type": "institutional", "award_type": "partial_tuition",
             "renewable": True, "award_amount": "Need-based financial assistance (amount varies by need).",
             "academic_criteria": "",
             "other_eligibility_criteria": "NEED-BASED; undergraduate students only; cannot apply in the first semester "
             "(available after completing the first academic year).", "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },
    "ae-birmingham-dubai": {
        "canonical_name": "University of Birmingham Dubai", "aliases": ["Birmingham Dubai", "UoB Dubai"],
        "country_cc": "ae", "city": {"slug": "ae-dubai", "name": "Dubai"},
        "website": "https://www.birmingham.ac.uk/dubai", "institution_type": "private-nonprofit",
        "verified_at": "2026-10-21", "currency": "AED",
        "verification_note": "fact-checks/ae-birmingham-dubai-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "University of Birmingham Dubai — undergraduate courses",
                "url": "https://www.birmingham.ac.uk/dubai/study/courses/undergraduate",
                "excerpt": "UK branch campus in Dubai; English medium; UK degrees. Undergraduate courses incl. Computer "
                "Science BSc, Computer Engineering BSc/BEng, Business Management BSc, Economics BSc."},
            "adm": {"suffix": "src-adm", "title": "Entry requirements (Dubai campus) — University of Birmingham Dubai",
                "url": "https://www.birmingham.ac.uk/dubai/study/apply/entry-requirements",
                "excerpt": "A-level typical offers: Computer Science A*AA–ABB incl. A-level Mathematics grade A; Economics "
                "AAA–ABB; Business Management AAB–BBB. IELTS: Computer Science/Computer Engineering 6.0 overall (no band "
                "below 5.5); Business/Economics 6.5 overall (6.5 writing & speaking, 6.0 reading & listening)."},
            "fee": {"suffix": "src-fee", "title": "Undergraduate tuition fees — University of Birmingham Dubai",
                "url": "https://www.birmingham.ac.uk/dubai/study/fees",
                "excerpt": "Annual tuition (AED/yr): Computer Science BSc 156,718; Computer Engineering ~156,718; Business "
                "Management BSc 146,806; Economics BSc 128,695. Single fee per programme for all students (UK branch "
                "campus; no domestic/international split)."},
            "schol": {"suffix": "src-schol", "title": "Scholarships — University of Birmingham Dubai",
                "url": "https://www.birmingham.ac.uk/dubai/study/fees/scholarships",
                "excerpt": "Chancellor's Academic Merit Scholarship up to 30% per year (automatic consideration for all "
                "eligible applicants). Corporate Scholarship up to 30%/yr. Alumni Scholarship +AED 5,000 in year one. "
                "'Secure Your Spot' +10% in year one for UAE-based students who enrol early."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "American High School Diploma / AP", "US-curriculum applicants."),
            ("international-other", "General International Secondary Qualification", "Other international secondary qualifications."),
        ],
        "residencies": [
            ("all-students", "All students (single programme fee)",
             "UK branch campus: a single tuition fee per programme for all students (no domestic/international split)."),
        ],
        "cost": {"residency": "all-students", "tuition": 156718, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": 0,
            "note": "Annual programme fee (AED), Sept 2026 intake: Computer Science / Computer Engineering 156,718. "
            "Single fee per programme for all students. Dubai branch of the University of Birmingham (UK)."},
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "Computer Science / Computer Engineering: IELTS 6.0 overall (no band below 5.5). "
            "Business / Economics: IELTS 6.5 overall (6.5 writing & speaking, 6.0 reading & listening).",
            "notes": "English is the medium of instruction (UK branch campus)."},
        "deadline_note": "Apply via the University of Birmingham Dubai application (September and January intakes).",
        "living": None,
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "Computer Science BSc (University of Birmingham UK degree, Dubai campus).",
             "faculty": "University of Birmingham Dubai (Computer Science)", "duration": 3,
             "url": "https://www.birmingham.ac.uk/dubai/study/undergraduate/subjects/computer-science-courses/computer-science-bsc",
             "subjects_note": "A-level A*AA–ABB incl. Mathematics grade A (or equivalent); IELTS 6.0 (no band below 5.5)",
             "subjects": {"a-level": ["Mathematics (A)"], "ib": ["Mathematics (HL)"], "us-hs": ["Mathematics (AP/Calculus)"], "international-other": ["Mathematics"]}},
            {"suffix": "beng-computer-engineering", "program_name": "Computer Engineering", "field": "Engineering", "degree": "BEng",
             "degree_local": "Computer Engineering BEng/BSc (University of Birmingham UK degree, Dubai campus).",
             "faculty": "University of Birmingham Dubai (Engineering)", "duration": 3,
             "url": "https://www.birmingham.ac.uk/dubai/study/undergraduate/subjects/engineering-courses/computer-engineering-beng",
             "subjects_note": "A-level AAB–ABB incl. A-level Mathematics (or equivalent); IELTS 6.0 (no band below 5.5)",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics (HL)"], "us-hs": ["Mathematics (AP/Calculus)"], "international-other": ["Mathematics"]}},
            {"suffix": "bsc-business-management", "program_name": "Business Management", "field": "Business", "degree": "BSc",
             "degree_local": "Business Management BSc (University of Birmingham UK degree, Dubai campus).",
             "faculty": "Birmingham Business School (Dubai)", "duration": 3,
             "url": "https://www.birmingham.ac.uk/dubai/study/courses/undergraduate/business-management-bsc.aspx",
             "subjects_note": "A-level AAB–BBB (or equivalent); IELTS 6.5 (6.5 writing/speaking, 6.0 reading/listening)",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []},
             "cost": {"residency": "all-students", "tuition": 146806, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0, "note": "Business Management BSc annual fee AED 146,806 (Sept 2027 intake)."}},
            {"suffix": "bsc-economics", "program_name": "Economics", "field": "Economics", "degree": "BSc",
             "degree_local": "Economics BSc (University of Birmingham UK degree, Dubai campus).",
             "faculty": "Birmingham Business School (Dubai)", "duration": 3,
             "url": "https://www.birmingham.ac.uk/dubai/study/courses/undergraduate/economics-bsc.aspx",
             "subjects_note": "A-level AAA–ABB (or equivalent); IELTS 6.5 (6.5 writing/speaking, 6.0 reading/listening)",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []},
             "cost": {"residency": "all-students", "tuition": 128695, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0, "note": "Economics BSc annual fee AED 128,695 (Sept 2026 intake)."}},
        ],
        "scholarships": [
            {"suffix": "chancellors-merit", "name": "Chancellor's Academic Merit Scholarship",
             "provider": "University of Birmingham Dubai", "provider_type": "institutional", "award_type": "partial_tuition",
             "renewable": True, "award_amount": "Up to 30% of tuition per year.",
             "academic_criteria": "Academic merit.",
             "other_eligibility_criteria": "AUTOMATIC consideration for all eligible applicants as part of admissions.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
            {"suffix": "secure-your-spot", "name": "Secure Your Spot Scholarship",
             "provider": "University of Birmingham Dubai", "provider_type": "institutional", "award_type": "partial_tuition",
             "renewable": False, "award_amount": "Additional 10% award in year one.",
             "academic_criteria": "",
             "other_eligibility_criteria": "For UAE-based students who enrol early (year one only).",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },
    "ae-heriot-watt-dubai": {
        "canonical_name": "Heriot-Watt University Dubai", "aliases": ["Heriot-Watt Dubai", "HWU Dubai"],
        "country_cc": "ae", "city": {"slug": "ae-dubai", "name": "Dubai"},
        "website": "https://www.hw.ac.uk/dubai", "institution_type": "private-nonprofit",
        "verified_at": "2026-10-21", "currency": "AED",
        "verification_note": "fact-checks/ae-heriot-watt-dubai-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "Heriot-Watt University Dubai — undergraduate study",
                "url": "https://www.hw.ac.uk/dubai/study/undergraduate",
                "excerpt": "UK branch campus in Dubai; English medium; UK degrees. Undergraduate programmes incl. BSc "
                "(Hons) Computer Science (and Data Science / Software Engineering), BEng (Hons) Engineering (Electrical & "
                "Electronic, Civil, Mechanical, Chemical), BBA (Hons) Business Administration. No standalone Economics "
                "BSc listed at the Dubai campus."},
            "adm": {"suffix": "src-adm", "title": "International entry / English requirements — Heriot-Watt University Dubai",
                "url": "https://www.hw.ac.uk/dubai/study/apply/english-language-requirements",
                "excerpt": "Undergraduate English: IELTS Academic 6.0 overall with no band below 5.5. Entry via A-levels, "
                "IB, or recognised international qualifications (direct entry to year 1; foundation/degree-entry routes available)."},
            "fee": {"suffix": "src-fee", "title": "Undergraduate tuition fees — Heriot-Watt University Dubai",
                "url": "https://www.hw.ac.uk/dubai/study/fees-and-funding",
                "excerpt": "Annual tuition (AED/yr, Jan 2027 intake, incl. VAT): Computer Science 82,264; Engineering "
                "(Electrical & Electronic / Civil / Mechanical) 82,264; BBA Business Administration 78,650. Single fee per "
                "programme for all students (UK branch campus)."},
            "schol": {"suffix": "src-schol", "title": "Scholarships and discounts — Heriot-Watt University Dubai",
                "url": "https://www.hw.ac.uk/dubai/study/fees-and-funding/scholarships-and-discounts",
                "excerpt": "Undergraduate Merit Scholarship (based on net first-year tuition, spread across instalments); "
                "Undergraduate Engineering Merit Scholarship (direct entry to year 2); Future Made for Success Scholarship "
                "AED 8,000; GCC and UAE Regional Student Grant AED 7,000; advance-payment and corporate discounts."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "American High School Diploma / AP", "US-curriculum applicants."),
            ("international-other", "General International Secondary Qualification", "Other international secondary qualifications."),
        ],
        "residencies": [
            ("all-students", "All students (single programme fee)",
             "UK branch campus: a single tuition fee per programme for all students (no domestic/international split)."),
        ],
        "cost": {"residency": "all-students", "tuition": 82264, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": 0,
            "note": "Annual programme fee (AED, Jan 2027 intake, incl. VAT): Computer Science / Engineering 82,264. "
            "Single fee per programme for all students. Dubai branch of Heriot-Watt University (UK)."},
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "IELTS Academic 6.0 overall with no band below 5.5.",
            "notes": "English is the medium of instruction (UK branch campus)."},
        "deadline_note": "Apply via Heriot-Watt University Dubai (September and January intakes).",
        "living": None,
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "BSc (Hons) Computer Science (Heriot-Watt UK degree, Dubai campus); also Data Science and Software Engineering variants.",
             "faculty": "School of Mathematical and Computer Sciences (Dubai)", "duration": 4,
             "url": "https://www.hw.ac.uk/dubai/study/undergraduate/computer-science",
             "subjects_note": "A-level / IB / recognised qualification for direct entry; IELTS 6.0 (no band below 5.5)",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "us-hs": ["Mathematics"], "international-other": ["Mathematics"]}},
            {"suffix": "beng-engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BEng",
             "degree_local": "BEng (Hons) Engineering (Heriot-Watt UK degree, Dubai campus): Electrical & Electronic, Civil, or Mechanical & Energy Engineering.",
             "faculty": "School of Engineering and Physical Sciences (Dubai)", "duration": 4,
             "url": "https://www.hw.ac.uk/dubai/study/undergraduate/electronic-electrical-engineering",
             "subjects_note": "A-level / IB with Mathematics (and Physics for most engineering); IELTS 6.0 (no band below 5.5)",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics", "Physics"], "us-hs": ["Mathematics", "Physics"], "international-other": ["Mathematics", "Physics"]}},
            {"suffix": "bba", "program_name": "Business Administration", "field": "Business", "degree": "BBA",
             "degree_local": "BBA (Hons) Bachelor of Business Administration (Heriot-Watt UK degree, Dubai campus).",
             "faculty": "Edinburgh Business School (Dubai)", "duration": 4,
             "url": "https://www.hw.ac.uk/dubai/study/undergraduate/bachelor-business-administration",
             "subjects_note": "A-level / IB / recognised qualification; IELTS 6.0 (no band below 5.5)",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []},
             "cost": {"residency": "all-students", "tuition": 78650, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0, "note": "BBA annual fee AED 78,650 (Jan 2027 intake, incl. VAT)."}},
        ],
        # No standalone Economics undergraduate programme listed at the Dubai campus — omitted, not fabricated.
        "scholarships": [
            {"suffix": "ug-merit", "name": "Undergraduate Merit Scholarship",
             "provider": "Heriot-Watt University Dubai", "provider_type": "institutional", "award_type": "partial_tuition",
             "renewable": True, "award_amount": "Merit award based on net first-year tuition, spread across annual instalments.",
             "academic_criteria": "High academic performance.",
             "other_eligibility_criteria": "Merit-based; for high-performing undergraduate students.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
            {"suffix": "eng-merit", "name": "Undergraduate Engineering Merit Scholarship",
             "provider": "Heriot-Watt University Dubai", "provider_type": "institutional", "award_type": "partial_tuition",
             "renewable": True, "award_amount": "Merit award for high-achieving engineering students.",
             "academic_criteria": "High achievement; eligible for direct entry to year 2 of an engineering programme.",
             "other_eligibility_criteria": "Merit-based; engineering programmes.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
            {"suffix": "regional-grant", "name": "GCC and UAE Regional Student Grant",
             "provider": "Heriot-Watt University Dubai", "provider_type": "institutional", "award_type": "fixed_amount",
             "renewable": False, "award_amount": "AED 7,000.",
             "academic_criteria": "",
             "other_eligibility_criteria": "For undergraduate students currently studying in the UAE / GCC region.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },
    "ae-rit-dubai": {
        "canonical_name": "Rochester Institute of Technology — Dubai", "aliases": ["RIT Dubai"],
        "country_cc": "ae", "city": {"slug": "ae-dubai", "name": "Dubai"},
        "website": "https://www.rit.edu/dubai", "institution_type": "private-nonprofit",
        "verified_at": "2026-10-21", "currency": "AED",
        "verification_note": "fact-checks/ae-rit-dubai-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "RIT Dubai — undergraduate programs",
                "url": "https://www.rit.edu/dubai/undergraduate-admissions",
                "excerpt": "US (Rochester Institute of Technology) branch campus, Dubai Silicon Oasis; English medium; "
                "US degrees. Undergraduate B.S. programs incl. Computing and Information Technologies, Computer "
                "Engineering, Mechanical Engineering, and Global Business Management. No Economics undergraduate program."},
            "adm": {"suffix": "src-adm", "title": "Undergraduate Admissions / English — RIT Dubai",
                "url": "https://www.rit.edu/dubai/undergraduate-admissions",
                "excerpt": "English-taught. IELTS: full admission 6.5+ overall; conditional admission 5.0–6.0. High-school "
                "performance considered for admission and scholarships."},
            "fee": {"suffix": "src-fee", "title": "Tuition and Fees — RIT Dubai",
                "url": "https://www.rit.edu/dubai/tuition-and-fees",
                "excerpt": "Undergraduate B.S. tuition AED 68,000 per year for students admitted effective Fall 2023 — "
                "uniform across Computing and Information Technologies, Computer Engineering, Mechanical Engineering and "
                "Global Business Management. Non-refundable enrollment deposit AED 2,500 (credited toward tuition)."},
            "schol": {"suffix": "src-schol", "title": "Scholarships — RIT Dubai",
                "url": "https://www.rit.edu/dubai/scholarships",
                "excerpt": "Academic Scholarship up to 45% (tiered by high-school average: 5% at 80–84.99% up to 45% at "
                ">98%). Tiger Journey Scholarship: 20% flat for a limited 50 students (predicted 90%+). Global Tigers "
                "Scholarship: 40% first-year tuition for international students (10 seats/yr), maintainable. Need-based "
                "financial aid up to 50%."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "American High School Diploma / AP", "US-curriculum applicants."),
            ("uae-shs", "UAE Secondary School Certificate", "UAE national secondary school certificate holders."),
        ],
        "residencies": [
            ("all-students", "All students (uniform tuition)",
             "US branch campus: uniform AED tuition for all students (no domestic/international split); scholarships reduce net cost."),
        ],
        "cost": {"residency": "all-students", "tuition": 68000, "basis": "institutional", "year": "2026-2027 (rate effective Fall 2023)",
            "mandatory_fees_annual": 0,
            "note": "Uniform AED 68,000/yr for all B.S. programs (Computing & IT, Computer Engineering, Mechanical "
            "Engineering, Global Business Management), for students admitted effective Fall 2023. Non-refundable "
            "enrollment deposit AED 2,500 (credited toward tuition). NOTE: an earlier web summary cited AED 3,800–3,920/"
            "credit (~114k–118k) for some engineering — that is the pre-Fall-2023 rate; the official page says 68,000 uniform."},
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "IELTS 6.5+ overall for full admission; 5.0–6.0 for conditional admission.",
            "notes": "English is the medium of instruction (US branch campus)."},
        "deadline_note": "Apply via RIT Dubai undergraduate admissions.",
        "living": None,
        "programs": [
            {"suffix": "bs-computing-it", "program_name": "Computing and Information Technologies", "field": "Computer Science", "degree": "BSc",
             "degree_local": "B.S. in Computing and Information Technologies (RIT US degree, Dubai campus).",
             "faculty": "RIT Dubai — Computing", "duration": 4,
             "url": "https://www.rit.edu/dubai/undergraduate-admissions",
             "subjects_note": "High-school diploma; Mathematics; English per requirements",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "us-hs": ["Mathematics"], "uae-shs": ["Mathematics"]}},
            {"suffix": "bs-computer-engineering", "program_name": "Computer Engineering", "field": "Engineering", "degree": "BSc",
             "degree_local": "B.S. in Computer Engineering (RIT US degree, Dubai campus). Mechanical Engineering also offered.",
             "faculty": "RIT Dubai — Engineering", "duration": 4,
             "url": "https://www.rit.edu/dubai/bachelor-science-computer-engineering",
             "subjects_note": "High-school diploma; Mathematics and Physics; English per requirements",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics", "Physics"], "us-hs": ["Mathematics", "Physics"], "uae-shs": ["Mathematics", "Physics"]}},
            {"suffix": "bs-global-business", "program_name": "Global Business Management", "field": "Business", "degree": "BSc",
             "degree_local": "B.S. in Global Business Management (RIT US degree, Dubai campus).",
             "faculty": "RIT Dubai — Business", "duration": 4,
             "url": "https://www.rit.edu/business/study/global-business-management-bs",
             "subjects_note": "High-school diploma; English per requirements",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "uae-shs": []}},
        ],
        # RIT Dubai offers no Economics undergraduate program — omitted, not fabricated.
        "scholarships": [
            {"suffix": "academic", "name": "Academic Scholarship", "provider": "RIT Dubai",
             "provider_type": "institutional", "award_type": "partial_tuition", "renewable": True,
             "award_amount": "Up to 45% of tuition, tiered by high-school average (5% at 80–84.99% up to 45% at >98%).",
             "academic_criteria": "Based on high-school average.",
             "other_eligibility_criteria": "Merit-based; awarded on admission by high-school performance.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
            {"suffix": "global-tigers", "name": "Global Tigers Scholarship", "provider": "RIT Dubai",
             "provider_type": "institutional", "award_type": "partial_tuition", "renewable": True,
             "award_amount": "40% of first-year tuition (maintainable with outstanding achievement).",
             "academic_criteria": "Outstanding academic achievement.",
             "other_eligibility_criteria": "COMPETITIVE and limited (≈10 seats/yr) for international students.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
            {"suffix": "financial-aid", "name": "Need-Based Financial Aid", "provider": "RIT Dubai",
             "provider_type": "institutional", "award_type": "partial_tuition", "renewable": True,
             "award_amount": "Up to 50% of tuition, based on demonstrated financial need.",
             "academic_criteria": "",
             "other_eligibility_criteria": "NEED-BASED; packages awarded after review of financial status.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },
    "ae-canadian-university-dubai": {
        "canonical_name": "Canadian University Dubai", "aliases": ["CUD"], "country_cc": "ae",
        "city": {"slug": "ae-dubai", "name": "Dubai"},
        "website": "https://www.cud.ac.ae/", "institution_type": "private-nonprofit",
        "verified_at": "2026-10-21", "currency": "AED",
        "verification_note": "fact-checks/ae-canadian-university-dubai-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "Canadian University Dubai — undergraduate programs",
                "url": "https://www.cud.ac.ae/prospective-students/undergraduate",
                "excerpt": "Private university in Dubai (Canadian-inspired curriculum); English medium. Undergraduate "
                "programs incl. BSc Computer Science (and Software Design, Cyber Security), BSc Engineering (Mechatronics, "
                "Power & Renewable Energy), and BBA (Marketing, International Business, Accounting & Finance, Management)."},
            "adm": {"suffix": "src-adm", "title": "Admission Requirements (Undergraduate) — Canadian University Dubai",
                "url": "https://www.cud.ac.ae/prospective-students/undergraduate",
                "excerpt": "English: minimum IELTS Academic 5.0, TOEFL iBT 61, TOEFL ITP 500 or equivalent MoE-approved "
                "test. Grade 12 / high-school certificate required."},
            "fee": {"suffix": "src-fee", "title": "Fees — Canadian University Dubai",
                "url": "https://www.cud.ac.ae/fees",
                "excerpt": "Per-credit tuition (pre-VAT): Computer Science (and Software Design, Cyber Security) AED "
                "2,300.50/credit × 30 cr/yr = AED 72,465.90/yr; Engineering (Mechatronics, Power & Renewable Energy) AED "
                "2,300.50/credit × 34 cr/yr = AED 82,127.85/yr; BBA AED 2,247.00/credit × 30 cr/yr = AED 67,410/yr. Plus "
                "AED 2,236.50 incidental fees (VAT inclusive)."},
            "schol": {"suffix": "src-schol", "title": "Scholarships — Canadian University Dubai",
                "url": "https://www.cud.ac.ae/fees",
                "excerpt": "Scholarships incl. Academic Excellence, Sports, Financial Hardship, Special Needs (tuition "
                "reduction up to 40%), and Special Talent. Numbers limited; amounts depend on each scholarship's criteria."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "American High School Diploma", "US-curriculum applicants."),
            ("uae-shs", "UAE Secondary School Certificate", "UAE national secondary school certificate holders."),
        ],
        "residencies": [
            ("all-students", "All students (uniform base tuition)",
             "Private university: the same per-credit tuition by program for all students; scholarships reduce net cost."),
        ],
        "cost": {"residency": "all-students", "tuition": 72466, "basis": "institutional", "year": "2025-2026",
            "mandatory_fees_annual": 2237,
            "note": "Computer Science: AED 2,300.50/credit × 30 cr/yr = AED 72,465.90/yr (pre-VAT) + AED 2,236.50 "
            "incidental (VAT incl.). Rounded. Per-program rates differ (Engineering higher credits; BBA lower per-credit)."},
        "lang_req": {"test_name": "IELTS Academic / TOEFL iBT / TOEFL ITP (or MoE-approved equivalent)",
            "min_score": "IELTS Academic 5.0, or TOEFL iBT 61, or TOEFL ITP 500 (or equivalent MoE-approved test).",
            "notes": "English is the medium of instruction."},
        "deadline_note": "Apply via Canadian University Dubai admissions.",
        "living": None,
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "BSc Computer Science (also Software Design and Cyber Security), Canadian University Dubai.",
             "faculty": "Canadian University Dubai — Computing/IT", "duration": 4,
             "url": "https://www.cud.ac.ae/prospective-students/undergraduate",
             "subjects_note": "Grade 12; Mathematics; English per requirements",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "us-hs": ["Mathematics"], "uae-shs": ["Mathematics"]}},
            {"suffix": "bsc-eng", "program_name": "Engineering", "field": "Engineering", "degree": "BSc",
             "degree_local": "BSc Engineering — Mechatronics Engineering or Power & Renewable Energy Engineering, Canadian University Dubai.",
             "faculty": "Canadian University Dubai — Engineering & Applied Sciences", "duration": 4,
             "url": "https://www.cud.ac.ae/prospective-students/undergraduate",
             "subjects_note": "Grade 12; Mathematics and Physics; English per requirements",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics", "Physics"], "us-hs": ["Mathematics", "Physics"], "uae-shs": ["Mathematics", "Physics"]},
             "cost": {"residency": "all-students", "tuition": 82128, "basis": "institutional", "year": "2025-2026",
                 "mandatory_fees_annual": 2237,
                 "note": "Engineering: AED 2,300.50/credit × 34 cr/yr = AED 82,127.85/yr (pre-VAT) + AED 2,236.50 incidental."}},
            {"suffix": "bba", "program_name": "Business Administration", "field": "Business", "degree": "BBA",
             "degree_local": "BBA (Marketing, International Business, Accounting & Finance, Management), Canadian University Dubai.",
             "faculty": "Canadian University Dubai — School of Business", "duration": 4,
             "url": "https://www.cud.ac.ae/prospective-students/undergraduate",
             "subjects_note": "Grade 12; English per requirements",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "uae-shs": []},
             "cost": {"residency": "all-students", "tuition": 67410, "basis": "institutional", "year": "2025-2026",
                 "mandatory_fees_annual": 2237,
                 "note": "BBA: AED 2,247.00/credit × 30 cr/yr = AED 67,410/yr (pre-VAT) + AED 2,236.50 incidental."}},
        ],
        # CUD offers no standalone Economics undergraduate program — omitted, not fabricated.
        "scholarships": [
            {"suffix": "academic-excellence", "name": "Academic Excellence Scholarship", "provider": "Canadian University Dubai",
             "provider_type": "institutional", "award_type": "partial_tuition", "renewable": True,
             "award_amount": "Merit tuition reduction (amount per criteria; limited).",
             "academic_criteria": "High academic achievement.",
             "other_eligibility_criteria": "Merit-based; limited number.",
             "application_deadline": None, "deadline_academic_year": "2025-2026"},
            {"suffix": "special-needs", "name": "Special Needs Scholarship", "provider": "Canadian University Dubai",
             "provider_type": "institutional", "award_type": "partial_tuition", "renewable": True,
             "award_amount": "Tuition reduction of up to 40%.",
             "academic_criteria": "",
             "other_eligibility_criteria": "For students with special needs; limited.",
             "application_deadline": None, "deadline_academic_year": "2025-2026"},
            {"suffix": "financial-hardship", "name": "Financial Hardship Scholarship", "provider": "Canadian University Dubai",
             "provider_type": "institutional", "award_type": "partial_tuition", "renewable": True,
             "award_amount": "Need-based tuition assistance (amount per criteria; limited).",
             "academic_criteria": "",
             "other_eligibility_criteria": "NEED-BASED; limited number.",
             "application_deadline": None, "deadline_academic_year": "2025-2026"},
        ],
    },
    "us-harvard": {
        "canonical_name": "Harvard University", "aliases": ["Harvard", "Harvard College"], "country_cc": "us",
        "city": {"slug": "us-cambridge-ma", "name": "Cambridge"},
        "website": "https://www.harvard.edu/", "institution_type": "private-nonprofit",
        "verified_at": "2026-10-21", "currency": "USD",
        "verification_note": "fact-checks/us-harvard-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "Harvard College — Concentrations (fields of study)",
                "url": "https://college.harvard.edu/academics/liberal-arts-sciences/concentrations",
                "excerpt": "Harvard College offers ~50 concentrations incl. Computer Science, Engineering (Biomedical, "
                "Electrical, Environmental Science & Engineering, Mechanical) and Economics. Harvard offers NO "
                "undergraduate business concentration (business is graduate-only at HBS)."},
            "adm": {"suffix": "src-adm", "title": "International Applicants / testing — Harvard College",
                "url": "https://college.harvard.edu/admissions/apply/international-applicants",
                "excerpt": "Holistic admission. SAT or ACT required (reinstated for students entering fall 2025 onward). "
                "International applicants: English proficiency expected; TOEFL/IELTS/Duolingo may be submitted."},
            "fee": {"suffix": "src-fee", "title": "Cost of Attendance 2026-27 — Harvard College",
                "url": "https://college.harvard.edu/financial-aid/how-aid-works",
                "excerpt": "2026-27 billed costs $91,634: tuition $62,226; housing $14,250; food $8,942; student services "
                "fee $4,272; health services fee $1,944. Plus personal ~$2,500 and books ~$1,000. Health insurance $4,954 "
                "if not otherwise covered. Same sticker for all; Harvard meets 100% of demonstrated need."},
            "schol": {"suffix": "src-schol", "title": "How Aid Works / Affordability — Harvard College",
                "url": "https://college.harvard.edu/financial-aid/how-aid-works",
                "excerpt": "Need-based aid for all students regardless of nationality; need-blind admission including for "
                "international students; meets 100% of demonstrated need. No merit-based (or athletic) scholarships."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "US High School Diploma", "US high school diploma / American curriculum applicants."),
            ("international-other", "General International Secondary Qualification", "Other international secondary qualifications."),
        ],
        "residencies": [
            ("all-students", "All students (uniform tuition)",
             "US private university: same sticker tuition for domestic and international students. Need-based aid differs by family need."),
        ],
        "cost": {"residency": "all-students", "tuition": 62226, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": 6216,
            "note": "Billed cost of attendance 2026-27 = $91,634 (tuition 62,226 + housing 14,250 + food 8,942 + student "
            "services 4,272 + health services 1,944); mandatory_fees here = student-services + health-services fees "
            "(6,216). Personal ~2,500 + books ~1,000 unbilled. Health insurance $4,954 extra if uninsured. SAME sticker "
            "for all; Harvard is need-blind (incl. international) and meets 100% of demonstrated need — most pay far less."},
        "lang_req": {"test_name": "TOEFL / IELTS Academic / Duolingo (international, if applicable)",
            "min_score": "English proficiency expected of international applicants; Harvard does not publish a fixed minimum score.",
            "notes": "Context for non-native English speakers; not required where prior education was in English."},
        "std_tests": [
            {"test_name": "SAT or ACT", "required": "required",
             "notes": "Standardized testing required (reinstated for students entering fall 2025 onward)."},
        ],
        "deadline_note": "Apply via the Common/Coalition Application (restrictive early action ~Nov 1; regular ~Jan 1).",
        "living": {"min": 2224, "max": 2966, "currency": "USD", "admin_body": "Harvard University",
            "desc": "Harvard COA 2026-27 non-tuition/fees: housing $14,250 + food $8,942 + books $1,000 + personal "
            "$2,500 = $26,692/yr (~$2,224–2,966/mo over 12 vs 9 months). Health insurance $4,954 extra if uninsured."},
        "programs": [
            {"suffix": "cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "Computer Science concentration (A.B. or S.B.), Harvard John A. Paulson School of Engineering & Applied Sciences.",
             "faculty": "Harvard SEAS", "duration": 4,
             "url": "https://college.harvard.edu/academics/liberal-arts-sciences/concentrations",
             "subjects_note": "Holistic whole-application review; strong preparation in mathematics and science expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BSc",
             "degree_local": "Engineering concentrations (S.B./A.B.): Biomedical, Electrical, Environmental Science & Engineering, Mechanical (Harvard SEAS).",
             "faculty": "Harvard SEAS", "duration": 4,
             "url": "https://college.harvard.edu/academics/liberal-arts-sciences/concentrations",
             "subjects_note": "Holistic whole-application review; strong preparation in mathematics and physics expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "economics", "program_name": "Economics", "field": "Economics", "degree": "BA",
             "degree_local": "Economics concentration (A.B.), Harvard Faculty of Arts & Sciences.",
             "faculty": "Department of Economics", "duration": 4,
             "url": "https://www.economics.harvard.edu/concentrator-guide",
             "subjects_note": "Holistic whole-application review; strong quantitative preparation expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
        ],
        # Harvard has NO undergraduate business concentration (verified) — omitted, not fabricated.
        "scholarships": [
            {"suffix": "need-based-aid", "name": "Need-Based Financial Aid (meets 100% of demonstrated need)",
             "provider": "Harvard University", "provider_type": "institutional", "award_type": "mixed", "renewable": True,
             "award_amount": "Grant-based aid meeting 100% of demonstrated financial need (no loans).",
             "academic_criteria": "Awarded solely on demonstrated financial need; admission is need-blind for all applicants, including international.",
             "other_eligibility_criteria": "GUARANTEED for every admitted student with demonstrated need, all four years. "
             "Harvard offers NO merit-based or athletic scholarships.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },
    "us-stanford": {
        "canonical_name": "Stanford University", "aliases": ["Stanford"], "country_cc": "us",
        "city": {"slug": "us-stanford-ca", "name": "Stanford"},
        "website": "https://www.stanford.edu/", "institution_type": "private-nonprofit",
        "verified_at": "2026-10-21", "currency": "USD",
        "verification_note": "fact-checks/us-stanford-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "Stanford — undergraduate majors",
                "url": "https://majors.stanford.edu/majors/text-only-lists-majors-and-offerings",
                "excerpt": "Stanford offers Computer Science (B.S.), Engineering (School of Engineering, 10 departmental "
                "majors incl. EE, ME, Aero/Astro, Bioengineering, MS&E), and Economics (B.A.). Stanford offers NO "
                "undergraduate business degree (the GSB is graduate; undergrads may take GSB 'Pathfinder' courses only)."},
            "adm": {"suffix": "src-adm", "title": "International Applicants / testing — Stanford Admission",
                "url": "https://admission.stanford.edu/apply/international/index.html",
                "excerpt": "Holistic admission. SAT or ACT required (reinstated for the 2025-26 cycle onward). Admission "
                "is need-blind for US applicants but NEED-AWARE for international applicants. English proficiency expected."},
            "fee": {"suffix": "src-fee", "title": "Undergraduate Tuition & Student Budget 2026-27 — Stanford",
                "url": "https://financialaid.stanford.edu/undergrad/budget/index.html",
                "excerpt": "2026-27: tuition $67,731; standard room & board $22,944; total cost of attendance $97,545 "
                "(incl. fees, books, personal). Same sticker for all; Stanford meets full demonstrated need. Families "
                "earning < $100,000 typically pay no tuition, room or board; < $150,000 typically pay no tuition."},
            "schol": {"suffix": "src-schol", "title": "Afford / Financial Aid — Stanford Admission",
                "url": "https://admission.stanford.edu/afford/",
                "excerpt": "Need-based aid; meets full demonstrated need for admitted students. No merit scholarships "
                "(aside from a limited number of athletic scholarships). Need-blind for US applicants; need-aware for "
                "international applicants."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "US High School Diploma", "US high school diploma / American curriculum applicants."),
            ("international-other", "General International Secondary Qualification", "Other international secondary qualifications."),
        ],
        "residencies": [
            ("all-students", "All students (uniform tuition)",
             "US private university: same sticker tuition for domestic and international students. Need-based aid differs by family need."),
        ],
        "cost": {"residency": "all-students", "tuition": 67731, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": 0,
            "note": "Total cost of attendance 2026-27 = $97,545 (tuition 67,731 + room & board 22,944 + fees/books/"
            "personal). SAME sticker for all. Stanford meets full demonstrated need: families < $100k income typically "
            "pay no tuition/room/board; < $150k typically pay no tuition. NOTE: need-blind for US applicants but "
            "NEED-AWARE for international applicants — net cost and admission chances for internationals depend on need."},
        "lang_req": {"test_name": "TOEFL / IELTS Academic / Duolingo (international, if applicable)",
            "min_score": "English proficiency expected of international applicants; Stanford does not publish a fixed minimum score.",
            "notes": "Context for non-native English speakers."},
        "std_tests": [
            {"test_name": "SAT or ACT", "required": "required",
             "notes": "Standardized testing required (reinstated for the 2025-26 application cycle onward)."},
        ],
        "deadline_note": "Apply via the Common/Coalition Application (restrictive early action ~Nov 1; regular ~Jan 5).",
        "living": {"min": 2485, "max": 3313, "currency": "USD", "admin_body": "Stanford University",
            "desc": "Stanford COA 2026-27 non-tuition ≈ $29,814/yr (standard room & board $22,944 + fees, books, "
            "personal ≈ $6,870); ~$2,485–3,313/mo over 12 vs 9 months. Total COA $97,545."},
        "programs": [
            {"suffix": "cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "B.S. in Computer Science, Stanford School of Engineering.",
             "faculty": "Stanford School of Engineering", "duration": 4,
             "url": "https://bulletin.stanford.edu/programs/CS-BS",
             "subjects_note": "Holistic whole-application review; strong preparation in mathematics and science expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BSc",
             "degree_local": "B.S. engineering majors (e.g. Electrical, Mechanical, Aeronautics & Astronautics, Bioengineering, Management Science & Engineering), Stanford School of Engineering.",
             "faculty": "Stanford School of Engineering", "duration": 4,
             "url": "https://engineering.stanford.edu/students-academics/academics/undergraduate-degree-programs",
             "subjects_note": "Holistic whole-application review; strong preparation in mathematics and physics expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "economics", "program_name": "Economics", "field": "Economics", "degree": "BA",
             "degree_local": "B.A. in Economics, Stanford School of Humanities & Sciences.",
             "faculty": "Department of Economics", "duration": 4,
             "url": "https://bulletin.stanford.edu/programs/ECON-BA",
             "subjects_note": "Holistic whole-application review; strong quantitative preparation expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
        ],
        # Stanford has NO undergraduate business degree (verified) — omitted, not fabricated.
        "scholarships": [
            {"suffix": "need-based-aid", "name": "Need-Based Financial Aid (meets full demonstrated need)",
             "provider": "Stanford University", "provider_type": "institutional", "award_type": "mixed", "renewable": True,
             "award_amount": "Need-based aid meeting full demonstrated need. Families < $100k income typically pay no "
             "tuition/room/board; < $150k typically pay no tuition.",
             "academic_criteria": "Awarded on demonstrated financial need.",
             "other_eligibility_criteria": "Meets full need for admitted students. NO merit scholarships (aside from a "
             "limited number of athletic awards). Admission is need-blind for US applicants but NEED-AWARE for international applicants.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },
    "us-upenn": {
        "canonical_name": "University of Pennsylvania", "aliases": ["Penn", "UPenn"], "country_cc": "us",
        "city": {"slug": "us-philadelphia-pa", "name": "Philadelphia"},
        "website": "https://www.upenn.edu/", "institution_type": "private-nonprofit",
        "verified_at": "2026-10-21", "currency": "USD",
        "verification_note": "fact-checks/us-upenn-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "University of Pennsylvania — undergraduate schools",
                "url": "https://catalog.upenn.edu/undergraduate/",
                "excerpt": "Penn's four undergraduate schools incl. Arts & Sciences (Economics B.A.), the School of "
                "Engineering & Applied Science (Computer Science and engineering, B.S.E.), and the Wharton School "
                "(business, B.S. in Economics). Same tuition across all schools."},
            "adm": {"suffix": "src-adm", "title": "Undergraduate admissions / aid — University of Pennsylvania",
                "url": "https://catalog.upenn.edu/undergraduate/academic-resources/financial-aid/",
                "excerpt": "Holistic admission. Penn meets 100% of demonstrated need with grant-based aid and no loans. "
                "Need-blind for US applicants (and Canada/Mexico); need-aware for other international applicants. "
                "English proficiency expected of international applicants."},
            "fee": {"suffix": "src-fee", "title": "Undergraduate Cost of Attendance 2026-27 — Penn SRFS",
                "url": "https://srfs.upenn.edu/costs-budgeting/undergraduate-cost-attendance",
                "excerpt": "2026-27: tuition $65,670; fees $8,308; room $13,644; meal plan $6,960 (= $94,582 tuition/"
                "fees/room/board). On-campus total budget $99,082 (incl. books, transport, personal). Same tuition "
                "across Arts & Sciences, Wharton and Engineering."},
            "schol": {"suffix": "src-schol", "title": "Financial Aid (no-loan) — University of Pennsylvania",
                "url": "https://srfs.upenn.edu/costs-budgeting/undergraduate-cost-attendance",
                "excerpt": "Penn meets 100% of demonstrated need with grant-based aid and WITHOUT loans. Need-blind for "
                "US (and Canada/Mexico) applicants; need-aware for other international applicants. No merit scholarships."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "US High School Diploma", "US high school diploma / American curriculum applicants."),
            ("international-other", "General International Secondary Qualification", "Other international secondary qualifications."),
        ],
        "residencies": [
            ("all-students", "All students (uniform tuition)",
             "US private university: same sticker tuition for domestic and international students (same across all schools). Need-based aid differs by family need."),
        ],
        "cost": {"residency": "all-students", "tuition": 65670, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": 8308,
            "note": "2026-27: tuition 65,670 + fees 8,308 + room 13,644 + meal 6,960 = 94,582; on-campus total budget "
            "$99,082 (incl. books/transport/personal). SAME tuition across Arts & Sciences, Wharton and Engineering. "
            "Penn meets 100% of demonstrated need with grant aid and NO loans; need-blind for US/Canada/Mexico "
            "applicants, need-aware for other internationals — net cost depends on family need."},
        "lang_req": {"test_name": "TOEFL / IELTS Academic / Duolingo (international, if applicable)",
            "min_score": "English proficiency expected of international applicants; Penn does not publish a single fixed minimum score.",
            "notes": "Context for non-native English speakers."},
        "std_tests": [
            {"test_name": "SAT or ACT", "required": "recommended",
             "notes": "Penn's standardized-testing policy has varied by year (test-optional in recent cycles); verify the current requirement for your entry year."},
        ],
        "deadline_note": "Apply via the Common/Coalition Application (early decision ~Nov 1; regular ~Jan).",
        "living": {"min": 2092, "max": 2789, "currency": "USD", "admin_body": "University of Pennsylvania",
            "desc": "Penn COA 2026-27 non-tuition/fees: room $13,644 + meal $6,960 + books/transport/personal ≈ $4,500 "
            "= ~$25,104/yr (~$2,092–2,789/mo over 12 vs 9 months). Fees $8,308 billed separately."},
        "programs": [
            {"suffix": "cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "B.S.E. in Computer Science, School of Engineering & Applied Science (Dept. of CIS).",
             "faculty": "Penn Engineering (SEAS)", "duration": 4,
             "url": "https://catalog.upenn.edu/undergraduate/",
             "subjects_note": "Holistic whole-application review; strong preparation in mathematics and science expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BSc",
             "degree_local": "B.S.E. engineering majors (e.g. Mechanical, Electrical, Bioengineering, Chemical & Biomolecular), Penn Engineering.",
             "faculty": "Penn Engineering (SEAS)", "duration": 4,
             "url": "https://catalog.upenn.edu/undergraduate/",
             "subjects_note": "Holistic whole-application review; strong preparation in mathematics and physics expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "economics", "program_name": "Economics", "field": "Economics", "degree": "BA",
             "degree_local": "B.A. in Economics, School of Arts & Sciences.",
             "faculty": "Department of Economics (School of Arts & Sciences)", "duration": 4,
             "url": "https://catalog.upenn.edu/undergraduate/",
             "subjects_note": "Holistic whole-application review; strong quantitative preparation expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "wharton-business", "program_name": "Business (Wharton)", "field": "Business", "degree": "BSc",
             "degree_local": "B.S. in Economics (the Wharton School undergraduate business degree), with concentrations (Finance, Management, Marketing, etc.).",
             "faculty": "The Wharton School", "duration": 4,
             "url": "https://catalog.upenn.edu/undergraduate/",
             "subjects_note": "Holistic whole-application review; strong quantitative preparation expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
        ],
        "scholarships": [
            {"suffix": "need-based-aid", "name": "Need-Based Financial Aid (no-loan, meets 100% of need)",
             "provider": "University of Pennsylvania", "provider_type": "institutional", "award_type": "mixed", "renewable": True,
             "award_amount": "Grant-based aid meeting 100% of demonstrated financial need, with NO loans.",
             "academic_criteria": "Awarded on demonstrated financial need.",
             "other_eligibility_criteria": "Meets 100% of need for admitted students (grant-based, no loans). NO merit "
             "scholarships. Need-blind for US / Canada / Mexico applicants; need-aware for other international applicants.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },
    "us-cornell": {
        "canonical_name": "Cornell University", "aliases": ["Cornell"], "country_cc": "us",
        "city": {"slug": "us-ithaca-ny", "name": "Ithaca"},
        "website": "https://www.cornell.edu/", "institution_type": "private-nonprofit",
        "verified_at": "2026-10-21", "currency": "USD",
        "verification_note": "fact-checks/us-cornell-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "Cornell University — undergraduate colleges & programs",
                "url": "https://www.cornell.edu/academics/",
                "excerpt": "Cornell offers Computer Science (Bowers CIS; B.A. in Arts & Sciences or B.S. in Engineering), "
                "Engineering (College of Engineering, B.S.), Economics (Arts & Sciences, B.A.), and Applied Economics & "
                "Management (the Dyson School, B.S. — business). All four pillars present."},
            "adm": {"suffix": "src-adm", "title": "International applicants / financial aid — Cornell",
                "url": "https://finaid.cornell.edu/first-year-and-transfer-students-international",
                "excerpt": "Holistic admission; international admission is NEED-AWARE. English proficiency expected of "
                "international applicants. Standardized-testing policy varies by year — verify current requirement."},
            "fee": {"suffix": "src-fee", "title": "Cost to Attend — Cornell Office of Financial Aid",
                "url": "https://finaid.cornell.edu/cost-to-attend",
                "excerpt": "Endowed colleges (incl. CS, Engineering, Arts & Sciences, SC Johnson Business): tuition "
                "$73,946 (2026-27, board-approved). Most recent published breakdown: mandatory fees $1,024, housing "
                "$13,744, food $7,604, books $1,234, personal $2,182 (total ≈ $99,734). Dyson/AEM (contract college) is "
                "$49,816 for NY residents but $73,946 for non-residents/international."},
            "schol": {"suffix": "src-schol", "title": "Financial Aid — Cornell Office of Financial Aid",
                "url": "https://finaid.cornell.edu/grants-and-scholarships",
                "excerpt": "Meets 100% of demonstrated financial need for all admitted undergraduates (incl. "
                "international). Aid is a package of Cornell grants, work-study and reasonable student loans (NOT "
                "loan-free). Domestic: families up to $125,000 have tuition covered; up to $75,000 have full cost covered."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "US High School Diploma", "US high school diploma / American curriculum applicants."),
            ("international-other", "General International Secondary Qualification", "Other international secondary qualifications."),
        ],
        "residencies": [
            ("all-students", "International / non-NY-resident rate",
             "Modeled at the international (non-NY-resident) rate. NY residents pay less in the contract colleges (e.g. Dyson AEM $49,816). Need-based aid differs by family need."),
        ],
        "cost": {"residency": "all-students", "tuition": 73946, "basis": "institutional",
            "year": "2026-2027 (tuition board-approved; fees/living per most recent published breakdown)", "mandatory_fees_annual": 1024,
            "note": "Endowed-college (and international contract-college) tuition $73,946 for 2026-27 (board-approved). "
            "Fees $1,024 (activity $424 + health $600); living below. Total COA ≈ $99,734. Dyson/AEM & other contract "
            "colleges charge NY residents $49,816 but non-residents/international $73,946. Cornell meets 100% of need "
            "(package includes loans) — net cost depends on family need."},
        "lang_req": {"test_name": "TOEFL / IELTS Academic (international, if applicable)",
            "min_score": "English proficiency expected of international applicants; see Cornell's current minimums.",
            "notes": "Context for non-native English speakers."},
        "std_tests": [
            {"test_name": "SAT or ACT", "required": "recommended",
             "notes": "Cornell's standardized-testing policy varies by year/college; verify the current requirement for your entry year."},
        ],
        "deadline_note": "Apply via the Common Application (early decision ~Nov; regular decision ~Jan 2).",
        "living": {"min": 2064, "max": 2752, "currency": "USD", "admin_body": "Cornell University",
            "desc": "Cornell endowed-college non-tuition/fees (most recent published): housing $13,744 + food $7,604 + "
            "books $1,234 + personal $2,182 = $24,764/yr (~$2,064–2,752/mo over 12 vs 9 months). Total COA ≈ $99,734."},
        "programs": [
            {"suffix": "cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "Computer Science (Bowers CIS) — B.A. (Arts & Sciences) or B.S. (Engineering).",
             "faculty": "Bowers College of Computing and Information Science", "duration": 4,
             "url": "https://www.cornell.edu/academics/", "subjects_note": "Holistic review; strong preparation in mathematics and science expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BSc",
             "degree_local": "B.S. engineering majors (e.g. Mechanical, Electrical & Computer, Civil, Chemical, Operations Research), Cornell College of Engineering.",
             "faculty": "College of Engineering", "duration": 4,
             "url": "https://www.engineering.cornell.edu/", "subjects_note": "Holistic review; strong preparation in mathematics and physics expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "economics", "program_name": "Economics", "field": "Economics", "degree": "BA",
             "degree_local": "B.A. in Economics, College of Arts & Sciences.",
             "faculty": "Department of Economics (Arts & Sciences)", "duration": 4,
             "url": "https://www.cornell.edu/academics/", "subjects_note": "Holistic review; strong quantitative preparation expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "dyson-aem", "program_name": "Applied Economics & Management (Dyson)", "field": "Business", "degree": "BSc",
             "degree_local": "B.S. in Applied Economics & Management, the Charles H. Dyson School (SC Johnson College of Business).",
             "faculty": "Dyson School (SC Johnson College of Business)", "duration": 4,
             "url": "https://dyson.cornell.edu/programs/undergraduate/", "subjects_note": "Holistic review; strong quantitative preparation expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
        ],
        "scholarships": [
            {"suffix": "need-based-aid", "name": "Need-Based Financial Aid (meets 100% of demonstrated need)",
             "provider": "Cornell University", "provider_type": "institutional", "award_type": "mixed", "renewable": True,
             "award_amount": "Meets 100% of demonstrated need via Cornell grants, work-study and reasonable loans (NOT loan-free).",
             "academic_criteria": "Awarded on demonstrated financial need.",
             "other_eligibility_criteria": "Meets full need for all admitted students incl. international; admission is "
             "NEED-AWARE for international. NO merit scholarships. Domestic: tuition covered up to $125k family income, full cost up to $75k.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },
    "us-nyu": {
        "canonical_name": "New York University", "aliases": ["NYU"], "country_cc": "us",
        "city": {"slug": "us-new-york-ny", "name": "New York"},
        "website": "https://www.nyu.edu/", "institution_type": "private-nonprofit",
        "verified_at": "2026-10-21", "currency": "USD",
        "verification_note": "fact-checks/us-nyu-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "New York University — undergraduate schools",
                "url": "https://www.nyu.edu/academics.html",
                "excerpt": "NYU (New York campus) offers Computer Science (Courant, Arts & Science B.A.; also Tandon "
                "B.S.), Engineering (Tandon School of Engineering, B.S.), Economics (Arts & Science, B.A.), and Business "
                "(Leonard N. Stern School of Business, B.S. in Business). All four pillars."},
            "adm": {"suffix": "src-adm", "title": "Undergraduate admissions / aid — NYU",
                "url": "https://www.nyu.edu/admissions/financial-aid-and-scholarships.html",
                "excerpt": "Holistic admission (need-aware). English proficiency expected of international applicants. "
                "Standardized testing is test-flexible — verify the current policy for your entry year."},
            "fee": {"suffix": "src-fee", "title": "Cost of Attendance 2026-27 — NYU",
                "url": "https://www.nyu.edu/admissions/financial-aid-and-scholarships/cost-of-attendance.html",
                "excerpt": "2026-27: Arts & Science / Tandon Engineering tuition & fees $68,576, food & housing $26,438, "
                "total COA $100,998. Stern (Business) tuition & fees $70,464, total COA $102,886. Indirect (books/"
                "transport/personal) ≈ $5,984."},
            "schol": {"suffix": "src-schol", "title": "The NYU Promise / Financial Aid — NYU",
                "url": "https://www.nyu.edu/admissions/financial-aid-and-scholarships/applying-as-a-prospective-undergraduate-student/first-year-applicants/the-nyu-promise.html",
                "excerpt": "The NYU Promise (from 2024-25): every first-year undergraduate — domestic AND international — "
                "admitted to the New York campus has 100% of demonstrated need met through scholarships and grants. "
                "Families with income under $100,000 (typical assets) do not pay tuition."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "US High School Diploma", "US high school diploma / American curriculum applicants."),
            ("international-other", "General International Secondary Qualification", "Other international secondary qualifications."),
        ],
        "residencies": [
            ("all-students", "All students (uniform tuition per school)",
             "US private university: same tuition for domestic and international students (differs by school). Need-based aid differs by family need."),
        ],
        "cost": {"residency": "all-students", "tuition": 68576, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": 0,
            "note": "Arts & Science / Tandon Engineering: tuition & fees $68,576 (combined), food & housing $26,438, "
            "indirect ≈ $5,984 => total COA $100,998. (Stern Business is higher — see that program.) NYU meets 100% of "
            "demonstrated need for first-years incl. international (NYU Promise); families < $100k income pay no tuition."},
        "lang_req": {"test_name": "TOEFL / IELTS Academic / Duolingo (international, if applicable)",
            "min_score": "English proficiency expected of international applicants; see NYU's current minimums.",
            "notes": "Context for non-native English speakers."},
        "std_tests": [
            {"test_name": "SAT or ACT", "required": "recommended",
             "notes": "NYU is test-flexible (accepts several exams / test-optional in recent cycles); verify the current policy."},
        ],
        "deadline_note": "Apply via the Common Application (early decision I ~Nov 1; ED II / regular ~Jan).",
        "living": {"min": 2701, "max": 3602, "currency": "USD", "admin_body": "New York University",
            "desc": "NYU COA 2026-27 non-tuition: food & housing $26,438 + indirect (books/transport/personal) ≈ $5,984 "
            "= $32,422/yr (~$2,701–3,602/mo over 12 vs 9 months); NYC cost of living is high."},
        "programs": [
            {"suffix": "cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "Computer Science — B.A. (Courant, Arts & Science) or B.S. (Tandon School of Engineering).",
             "faculty": "Courant Institute / Tandon", "duration": 4,
             "url": "https://www.nyu.edu/academics.html", "subjects_note": "Holistic review; strong preparation in mathematics and science expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BSc",
             "degree_local": "B.S. engineering majors, NYU Tandon School of Engineering.",
             "faculty": "Tandon School of Engineering", "duration": 4,
             "url": "https://engineering.nyu.edu/", "subjects_note": "Holistic review; strong preparation in mathematics and physics expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "economics", "program_name": "Economics", "field": "Economics", "degree": "BA",
             "degree_local": "B.A. in Economics, College of Arts & Science.",
             "faculty": "Department of Economics (Arts & Science)", "duration": 4,
             "url": "https://www.nyu.edu/academics.html", "subjects_note": "Holistic review; strong quantitative preparation expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "stern-business", "program_name": "Business (Stern)", "field": "Business", "degree": "BSc",
             "degree_local": "B.S. in Business, Leonard N. Stern School of Business.",
             "faculty": "Stern School of Business", "duration": 4,
             "url": "https://www.stern.nyu.edu/programs-admissions/undergraduate", "subjects_note": "Holistic review; strong quantitative preparation expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []},
             "cost": {"residency": "all-students", "tuition": 70464, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "Stern (Business): tuition & fees $70,464 (combined) + food & housing $26,438 + indirect ≈ $5,984 "
                 "=> total COA $102,886 (higher than Arts & Science / Tandon). NYU Promise meets 100% of need."}},
        ],
        "scholarships": [
            {"suffix": "need-based-aid", "name": "Need-Based Financial Aid (the NYU Promise — meets 100% of need)",
             "provider": "New York University", "provider_type": "institutional", "award_type": "mixed", "renewable": True,
             "award_amount": "Meets 100% of demonstrated need via scholarships and grants. Families < $100k income pay no tuition.",
             "academic_criteria": "Awarded on demonstrated financial need.",
             "other_eligibility_criteria": "The NYU Promise (from 2024-25): full demonstrated need met for first-year "
             "undergraduates, domestic AND international, at the New York campus. Admission is need-aware.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },
    "us-usc": {
        "canonical_name": "University of Southern California", "aliases": ["USC"], "country_cc": "us",
        "city": {"slug": "us-los-angeles-ca", "name": "Los Angeles"},
        "website": "https://www.usc.edu/", "institution_type": "private-nonprofit",
        "verified_at": "2026-10-21", "currency": "USD",
        "verification_note": "fact-checks/us-usc-2026-10-21.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "USC — undergraduate schools & majors",
                "url": "https://www.usc.edu/academics/",
                "excerpt": "USC offers Computer Science (Viterbi School of Engineering, B.S.), Engineering (Viterbi, "
                "B.S.), Economics (Dornsife College, B.A.), and Business Administration (Marshall School of Business, "
                "B.S.). Undergraduate tuition is the same across all schools and the same for resident and nonresident students."},
            "adm": {"suffix": "src-adm", "title": "Financial Aid & Scholarships / admission — USC",
                "url": "https://admission.usc.edu/cost-and-financial-aid/financial-aid-and-scholarships/",
                "excerpt": "Holistic admission. English proficiency expected of international applicants. Standardized "
                "testing policy varies by year (test-optional in recent cycles) — verify current requirement."},
            "fee": {"suffix": "src-fee", "title": "Undergraduate Cost of Attendance 2026-27 — USC Financial Aid",
                "url": "https://financialaid.usc.edu/undergraduate-financial-aid/cost-of-attendance/",
                "excerpt": "2026-27 on-campus total $103,162: tuition (12–18 units) $75,384; mandatory fees $1,952; "
                "housing $13,510; food $8,442; books $670; transportation/personal $3,204. Tuition is the same across "
                "USC schools and the same for residents and nonresidents."},
            "schol": {"suffix": "src-schol", "title": "Scholarship Guide / Affordability — USC Admission",
                "url": "https://admission.usc.edu/scholarship-guide/",
                "excerpt": "USC meets USC-determined need via merit scholarships, need-based grants, work-study and "
                "loans. Families earning <= $80,000 (typical assets) attend tuition-free. Competitive MERIT scholarships: "
                "Trustee (full tuition), Presidential (half tuition), Deans (quarter tuition), plus full-ride Mork Family "
                "and Stamps; ~10% of the entering class receives a merit award."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "US High School Diploma", "US high school diploma / American curriculum applicants."),
            ("international-other", "General International Secondary Qualification", "Other international secondary qualifications."),
        ],
        "residencies": [
            ("all-students", "All students (uniform tuition)",
             "US private university: same tuition for residents, nonresidents and international students, across all schools. Need-based aid and merit scholarships reduce net cost."),
        ],
        "cost": {"residency": "all-students", "tuition": 75384, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": 1952,
            "note": "2026-27 on-campus total COA $103,162: tuition $75,384 (12–18 units) + fees $1,952 + housing $13,510 "
            "+ food $8,442 + books $670 + transport/personal $3,204. SAME tuition across schools and for residents/"
            "nonresidents. USC meets USC-determined need (incl. merit + grants + work-study + loans); < $80k income "
            "tuition-free. Competitive merit scholarships also available (see scholarships)."},
        "lang_req": {"test_name": "TOEFL / IELTS Academic / Duolingo (international, if applicable)",
            "min_score": "English proficiency expected of international applicants; see USC's current minimums.",
            "notes": "Context for non-native English speakers."},
        "std_tests": [
            {"test_name": "SAT or ACT", "required": "recommended",
             "notes": "USC's standardized-testing policy varies by year (test-optional in recent cycles); verify the current requirement."},
        ],
        "deadline_note": "Apply via the Common Application (scholarship consideration deadline ~Dec 1; regular ~Jan 15).",
        "living": {"min": 2152, "max": 2870, "currency": "USD", "admin_body": "University of Southern California",
            "desc": "USC COA 2026-27 non-tuition/fees: housing $13,510 + food $8,442 + books $670 + transport/personal "
            "$3,204 = $25,826/yr (~$2,152–2,870/mo over 12 vs 9 months)."},
        "programs": [
            {"suffix": "cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "B.S. in Computer Science, USC Viterbi School of Engineering.",
             "faculty": "Viterbi School of Engineering", "duration": 4,
             "url": "https://www.usc.edu/academics/", "subjects_note": "Holistic review; strong preparation in mathematics and science expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BSc",
             "degree_local": "B.S. engineering majors, USC Viterbi School of Engineering.",
             "faculty": "Viterbi School of Engineering", "duration": 4,
             "url": "https://viterbischool.usc.edu/", "subjects_note": "Holistic review; strong preparation in mathematics and physics expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "economics", "program_name": "Economics", "field": "Economics", "degree": "BA",
             "degree_local": "B.A. in Economics, USC Dornsife College of Letters, Arts & Sciences.",
             "faculty": "Department of Economics (Dornsife)", "duration": 4,
             "url": "https://www.usc.edu/academics/", "subjects_note": "Holistic review; strong quantitative preparation expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "marshall-business", "program_name": "Business Administration (Marshall)", "field": "Business", "degree": "BSc",
             "degree_local": "B.S. in Business Administration, USC Marshall School of Business.",
             "faculty": "Marshall School of Business", "duration": 4,
             "url": "https://www.marshall.usc.edu/programs/undergraduate-programs", "subjects_note": "Holistic review; strong quantitative preparation expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
        ],
        "scholarships": [
            {"suffix": "need-based-aid", "name": "Need-Based Financial Aid (meets USC-determined need)",
             "provider": "University of Southern California", "provider_type": "institutional", "award_type": "mixed", "renewable": True,
             "award_amount": "Meets USC-determined need via grants, work-study and loans. Families <= $80k income attend tuition-free.",
             "academic_criteria": "Awarded on demonstrated financial need.",
             "other_eligibility_criteria": "Need-based; international students may be considered but aid for internationals is limited relative to domestic.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
            {"suffix": "merit", "name": "Merit Scholarships (Trustee / Presidential / Deans)",
             "provider": "University of Southern California", "provider_type": "institutional", "award_type": "mixed", "renewable": True,
             "award_amount": "Trustee = full tuition; Presidential = half tuition; Deans = quarter tuition; plus full-ride Mork Family & Stamps.",
             "academic_criteria": "Highly competitive academic merit.",
             "other_eligibility_criteria": "COMPETITIVE merit awards (open to international applicants); ~10% of the "
             "entering class receives one. Scholarship-consideration application deadline ~Dec 1.",
             "application_deadline": "December 1", "deadline_academic_year": "2026-2027"},
        ],
    },
    "us-purdue": {
        "canonical_name": "Purdue University", "aliases": ["Purdue"], "country_cc": "us",
        "city": {"slug": "us-west-lafayette-in", "name": "West Lafayette"},
        "website": "https://www.purdue.edu/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "USD",
        "verification_note": "fact-checks/us-purdue-2026-10-25.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "Purdue University — Undergraduate Programs",
                "url": "https://www.purdue.edu/academics/",
                "excerpt": "Purdue University is a public land-grant research university in West Lafayette, Indiana; "
                "English medium. Colleges/schools offering the four target pillars: College of Science (Computer "
                "Science, AI, Data Science B.S.), College of Engineering (18+ B.S. engineering majors), and Mitch "
                "Daniels School of Business (B.S. in Management/Finance/Marketing/BAIM/SCM/Economics and others)."},
            "adm": {"suffix": "src-adm",
                "title": "International Admissions & English Proficiency — Purdue University",
                "url": "https://admissions.purdue.edu/become-student/international/",
                "excerpt": "Purdue recognizes A-level examinations and awards college credits; no specific A-level "
                "subject requirements (most applicants complete 3–4 A-levels). IB accepted; no overall IB minimum. "
                "SAT/ACT test-optional (scores evaluated if submitted). English proficiency: IELTS Academic 6.5 "
                "overall (min 6.0 each section); TOEFL iBT 88 overall min 20 per section (pre-Jan 21 2026 tests) / "
                "4.5 overall min 4.0 per section (new format, Jan 21 2026 onwards); Duolingo generally 115+ "
                "(min 110 subscores). Deadlines: Early Action Nov 1 (scholarship consideration, domestic only); "
                "Regular Decision Jan 15. Apply via Common App."},
            "fee": {"suffix": "src-fee",
                "title": "Undergraduate Tuition and Fees 2026-2027 — Purdue Finance / Bursar",
                "url": "https://www.purdue.edu/treasurer/finance/bursar-office/tuition/fee-rates-2026-2027/undergraduate-tuition-and-fees-2026-2027/",
                "excerpt": "2026-27 international undergraduate flat rate (8+ cr/semester): Nonresident Tuition "
                "$9,401 + International Student Tuition $1,655 + General Service $4,859 + Fitness/Wellness $117 + "
                "Activity Fee $20 = $16,052/semester ($32,104/yr). DIFFERENTIAL surcharges for international "
                "students: CS / Data Science / Engineering UG / Biological Engineering +$2,025/semester (+$4,050/yr) "
                "→ $36,154/yr total; Daniels School of Business UG + B.S./B.A. in Economics +$1,718/semester "
                "(+$3,436/yr) → $35,540/yr total. Estimated housing + food $8,367/semester ($16,734/yr). "
                "Indiana residents pay $9,992/yr (no nonresident or international surcharge)."},
            "schol": {"suffix": "src-schol",
                "title": "First-Year Scholarships — Purdue Admissions",
                "url": "https://admissions.purdue.edu/cost-financial-aid/scholarships/",
                "excerpt": "Purdue institutional merit scholarships (Trustees $10,000–$16,000/yr, Presidential "
                "$4,000–$10,000/yr, Lilly full-tuition, etc.) are DOMESTIC STUDENTS ONLY. Page explicitly states: "
                "'Only domestic students are eligible for the scholarships described above. International students "
                "who hold F, J and some other visa types are not eligible.' No institutional scholarship "
                "alternatives for international undergraduates are listed."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "US High School Diploma", "US high school diploma / American curriculum applicants."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications."),
        ],
        "residencies": [
            ("international", "International students (nonresident rate)",
             "International (non-US) undergraduate students pay nonresident + international student tuition. "
             "Purdue offers NO institutional scholarships for international undergraduates — this is explicitly "
             "stated on the admissions scholarships page."),
        ],
        # University-level cost = base international rate (no program differential). All programs override below.
        "cost": {"residency": "international", "tuition": 32104, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": 0,
            "note": "Base 2026-27 international rate: $32,104/yr (all fees bundled: General Service $9,718 + "
            "Nonresident Tuition $18,802 + International Student Tuition $3,310 + Fitness $234 + Activity $40). "
            "Program differentials APPLY on top (see per-program cost). Estimated housing+food $16,734/yr. "
            "Indiana residents pay $9,992/yr. NOTE: Purdue offers NO institutional scholarships for "
            "international undergraduates (explicitly verified)."},
        "lang_req": {"test_name": "IELTS Academic / TOEFL iBT / Duolingo (or accepted equivalent)",
            "min_score": "IELTS Academic 6.5 overall (min 6.0 in each section); TOEFL iBT 88 overall (min 20 per "
            "section) for tests before Jan 21 2026, OR 4.5 overall (min 4.0 per section) under new TOEFL format "
            "(tests on/after Jan 21 2026); Duolingo generally 115+ (min 110 in all subscores). Meeting the "
            "minimum does not guarantee admission.",
            "notes": "English is the medium of instruction at Purdue."},
        "std_tests": [
            {"test_name": "SAT or ACT", "required": "recommended",
             "notes": "Test-optional: scores evaluated as one factor if submitted; not required. No test preference; "
             "highest section scores across test dates accepted. SAT/ACT do not substitute for English proficiency."},
        ],
        "deadline_note": "Early Action: November 1 (scholarship consideration — domestic students only). Regular Decision: January 15. Apply via Common App.",
        "living": {"min": 1395, "max": 1860, "currency": "USD", "admin_body": "Purdue University",
            "desc": "Purdue estimated housing+food $8,367/semester = $16,734/yr (~$1,395–1,860/mo over 12 vs 9 "
            "months). Source: Purdue Bursar 2026-27 undergraduate rate schedule."},
        "programs": [
            {"suffix": "bscs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "Bachelor of Science in Computer Science, College of Science, Department of Computer "
             "Science. Related options: B.S. in Artificial Intelligence; B.S. in Data Science (same dept, same "
             "tuition differential).",
             "faculty": "College of Science, Department of Computer Science", "duration": 4,
             "url": "https://www.cs.purdue.edu/undergraduate/",
             "subjects_note": "Holistic review; strong preparation in mathematics and science expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []},
             "cost": {"residency": "international", "tuition": 36154, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "CS 2026-27 international: base $32,104 + CS/Data Science/Engineering differential "
                 "$4,050 = $36,154/yr. Source: Purdue Bursar 2026-27 differential fee schedule."}},
            {"suffix": "bs-engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BSc",
             "degree_local": "Bachelor of Science in Engineering, College of Engineering; 18+ majors including "
             "Electrical & Computer Engineering, Mechanical Engineering, Civil Engineering, Aerospace Engineering, "
             "Chemical Engineering, Computer Engineering, and others.",
             "faculty": "College of Engineering", "duration": 4,
             "url": "https://www.purdue.edu/futureengineers/engineeringmajors/",
             "subjects_note": "Holistic review; strong preparation in mathematics and physics expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []},
             "cost": {"residency": "international", "tuition": 36154, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "Engineering 2026-27 international: base $32,104 + Engineering UG differential $4,050 = "
                 "$36,154/yr. Source: Purdue Bursar 2026-27 differential fee schedule (same category as CS/Data Science)."}},
            {"suffix": "bs-management", "program_name": "Management", "field": "Business", "degree": "BSc",
             "degree_local": "Bachelor of Science in [Major], Mitch Daniels School of Business; majors include "
             "General Management, Accounting, Finance, Marketing, Business Analytics & Information Management, "
             "Supply Chain & Operations Management, Organizational Behavior & HRM, and others.",
             "faculty": "Mitch Daniels School of Business", "duration": 4,
             "url": "https://business.purdue.edu/undergraduate/",
             "subjects_note": "Holistic review; quantitative preparation expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []},
             "cost": {"residency": "international", "tuition": 35540, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "Daniels Business UG 2026-27 international: base $32,104 + Daniels Business/Economics "
                 "differential $3,436 = $35,540/yr. Source: Purdue Bursar 2026-27 differential fee schedule."}},
            {"suffix": "bs-economics", "program_name": "Economics", "field": "Economics", "degree": "BSc",
             "degree_local": "Bachelor of Science in Economics, Mitch Daniels School of Business. Also available: "
             "B.S. in Quantitative Business Economics (same school, same differential).",
             "faculty": "Mitch Daniels School of Business", "duration": 4,
             "url": "https://business.purdue.edu/undergraduate/academics/economics.php",
             "subjects_note": "Holistic review; strong quantitative preparation expected",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []},
             "cost": {"residency": "international", "tuition": 35540, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "Daniels Economics 2026-27 international: base $32,104 + Daniels Business/Economics "
                 "differential $3,436 = $35,540/yr. Source: Purdue Bursar 2026-27 differential fee schedule "
                 "(B.S. in Economics is grouped with Daniels Business UG for differential purposes)."}},
        ],
        # Purdue institutional scholarships are DOMESTIC-ONLY (F/J visa holders explicitly excluded).
        # No institutional aid alternatives for international undergraduates listed on Purdue's site.
        # Recording as empty — this is an honest, verified fact, not an omission.
        "scholarships": [],
    },
    "us-asu": {
        "canonical_name": "Arizona State University", "aliases": ["ASU"], "country_cc": "us",
        "city": {"slug": "us-tempe-az", "name": "Tempe"},
        "website": "https://www.asu.edu/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "USD",
        "verification_note": "fact-checks/us-asu-2026-10-25.md",
        "sources": {
            "main": {"suffix": "src-01", "title": "Arizona State University — Undergraduate Programs",
                "url": "https://www.asu.edu/academics/",
                "excerpt": "Arizona State University is a public research university with main campus in Tempe, "
                "Arizona; English medium. Key schools for the four target pillars: Ira A. Fulton Schools of "
                "Engineering (Computer Science, Engineering B.S. degrees); W. P. Carey School of Business (30+ B.S. "
                "business degrees including Management, Finance, Marketing, BAIM, SCM; also B.S. in Economics, "
                "STEM-designated). Direct admission to colleges available for first-year students meeting requirements."},
            "adm": {"suffix": "src-adm",
                "title": "International First-Year Admissions — Arizona State University",
                "url": "https://admission.asu.edu/apply/international/first-year",
                "excerpt": "International first-year admission: minimum 3.0 GPA (B or better, A=4.00); three years "
                "of secondary coursework; high school diploma required. Math: 4 years (Algebra I, Geometry, Algebra "
                "II + one advanced). Science: 3 lab years. SAT/ACT not required but may support higher merit award. "
                "English proficiency (if not native English): most majors IELTS 6.0/TOEFL iBT 61/Duolingo 95; "
                "Fulton Engineering IELTS 6.5/TOEFL iBT 79/Duolingo 105. Fall priority deadline January 15; "
                "Spring priority November 1. $90 application fee. Rolling admissions."},
            "fee": {"suffix": "src-fee",
                "title": "International Student Cost of College 2026-27 — ASU Admission",
                "url": "https://admission.asu.edu/cost-aid/international",
                "excerpt": "2026-27 international undergraduate COA (Tempe/Downtown Phoenix/Polytechnic/West Valley "
                "campus): base tuition $39,062; tuition surcharge $350; advanced technology fee $200; undergraduate "
                "college fees up to $2,190 (varies by program — $2,190 shown is the highest possible); "
                "student-initiated fees $807; international student fee $400. Living: on-campus housing+meals "
                "$18,819; books+supplies $1,320; travel $1,650; personal $2,343; health insurance $2,765 (2025-26 "
                "rate; 2026-27 pending update). Total COA $69,906 with max college fee and on-campus housing."},
            "schol": {"suffix": "src-schol",
                "title": "New American University Scholarship (International) — ASU",
                "url": "https://tuition.asu.edu/new-american-university/international",
                "excerpt": "New American University (NAMU) Scholarship for international undergraduate (F-1) "
                "students: automatically considered at admission — no separate application required. First-year "
                "award tiers: $17,500/yr (GPA 4.0+) down to $10,000/yr (GPA 3.01+). Renewable for up to 8 "
                "consecutive fall+spring semesters. Limited number of awards. Notifications on rolling basis "
                "~10 business days after admission (for admits on/after Oct 1). Submitting SAT/ACT may support "
                "higher award tier."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("us-hs", "US High School Diploma", "US high school diploma / American curriculum applicants."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications."),
        ],
        "residencies": [
            ("international", "International students",
             "International (non-US) undergraduate students. Base tuition $39,062/yr for international students at "
             "ASU's Tempe, Downtown Phoenix, Polytechnic, or West Valley campus. Arizona residents pay significantly less."),
        ],
        "cost": {"residency": "international", "tuition": 39062, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": 1757,
            "note": "2026-27 international: base tuition $39,062 + fixed mandatory fees $1,757 (tuition surcharge "
            "$350 + advanced technology $200 + student-initiated $807 + international student fee $400) = $40,819/yr "
            "before variable undergraduate college fee. College fee varies by program — up to $2,190 (the 'highest "
            "possible'; total COA figure of $69,906 uses this max). Living: on-campus housing+meals $18,819 + books "
            "$1,320 + travel $1,650 + personal $2,343 + health insurance $2,765 = $26,897/yr extra. Arizona "
            "residents pay ~$12,000–$13,000/yr base tuition."},
        "lang_req": {"test_name": "IELTS Academic / TOEFL iBT / Duolingo / PTE Academic / Cambridge English",
            "min_score": "Ira A. Fulton Schools of Engineering (CS, Engineering): IELTS 6.5 / TOEFL iBT 79 / "
            "Duolingo 105 / Cambridge 176. Other majors (Business, Economics): IELTS 6.0 / TOEFL iBT 61 / "
            "Duolingo 95 / Cambridge B2 (170). Minimums shown; Engineering minimum used as university default here.",
            "notes": "Conditional admission available for academically qualified applicants needing English "
            "improvement (up to 3 semesters). English is the medium of instruction."},
        "std_tests": [
            {"test_name": "SAT or ACT", "required": "recommended",
             "notes": "Not required for admission but may be submitted for course placement or as supplemental "
             "information. Submitting strong scores may support a higher NAMU scholarship award tier."},
        ],
        "deadline_note": "Fall priority deadline: January 15. Spring priority deadline: November 1. Apply via ASU application or Common App ($90 fee). Rolling admissions.",
        "living": {"min": 1568, "max": 2091, "currency": "USD", "admin_body": "Arizona State University",
            "desc": "ASU COA 2026-27 non-tuition/fees: on-campus housing+meals $18,819 + books+supplies $1,320 + "
            "personal $2,343 + travel $1,650 = $24,132/yr (~$1,568–2,091/mo over 12 vs 9 months). Health insurance "
            "$2,765 additional (2025-26 rate; 2026-27 pending)."},
        "programs": [
            {"suffix": "bscs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "Bachelor of Science in Computer Science, Ira A. Fulton Schools of Engineering; "
             "STEM-designated. Related programs in the same schools: B.S. in Software Engineering, B.S. in Computer "
             "Systems Engineering.",
             "faculty": "Ira A. Fulton Schools of Engineering", "duration": 4,
             "url": "https://engineering.asu.edu/undergraduate-programs/",
             "subjects_note": "Min 3.0 GPA; strong mathematics preparation; English IELTS 6.5/TOEFL 79 (Engineering minimum)",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "bs-engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BSc",
             "degree_local": "Bachelor of Science in Engineering (various majors), Ira A. Fulton Schools of "
             "Engineering; disciplines include Electrical Engineering, Mechanical Engineering, Civil Engineering, "
             "Aerospace Engineering, Chemical Engineering, Biomedical Engineering, Industrial Engineering, and others.",
             "faculty": "Ira A. Fulton Schools of Engineering", "duration": 4,
             "url": "https://engineering.asu.edu/undergraduate-programs/",
             "subjects_note": "Min 3.0 GPA; strong mathematics and physics preparation; English IELTS 6.5/TOEFL 79 (Engineering minimum)",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "bs-business", "program_name": "Business", "field": "Business", "degree": "BSc",
             "degree_local": "Bachelor of Science in [Major], W. P. Carey School of Business; 30+ degree programs "
             "including Management, Finance, Marketing, Business Data Analytics, Supply Chain Management, Financial "
             "Technology, and others. Direct admission to W. P. Carey from first year for qualifying students.",
             "faculty": "W. P. Carey School of Business", "duration": 4,
             "url": "https://wpcarey.asu.edu/undergraduate/",
             "subjects_note": "Min 3.0 GPA; W. P. Carey requires meeting both university and school admission requirements; English IELTS 6.0/TOEFL 61 (non-Engineering minimum)",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
            {"suffix": "bs-economics", "program_name": "Economics", "field": "Economics", "degree": "BSc",
             "degree_local": "Bachelor of Science in Economics, W. P. Carey School of Business; STEM-designated. "
             "Also available: B.S. in Economics via College of Liberal Arts and Sciences (CLAS).",
             "faculty": "W. P. Carey School of Business", "duration": 4,
             "url": "https://wpcarey.asu.edu/economics-degrees/undergraduate",
             "subjects_note": "Min 3.0 GPA; strong quantitative preparation expected; English IELTS 6.0/TOEFL 61 (non-Engineering minimum)",
             "subjects": {"a-level": [], "ib": [], "us-hs": [], "international-other": []}},
        ],
        "scholarships": [
            {"suffix": "namu", "name": "New American University Scholarship",
             "provider": "Arizona State University", "provider_type": "institutional",
             "award_type": "partial_tuition", "renewable": True,
             "award_amount": "$10,000–$17,500 per year (first-year students); award tier based on GPA: "
             "4.0+ → $17,500/yr; tiers down to 3.01+ for the minimum $10,000/yr award.",
             "academic_criteria": "High academic achievement; GPA-tiered award (4.0+ receives maximum $17,500; "
             "minimum award requires 3.01+ GPA). Submitting SAT/ACT may support a higher award tier.",
             "other_eligibility_criteria": "AUTOMATIC consideration at admission — no separate application needed. "
             "Limited number of awards for international (F-1) undergraduate students. Renewable for up to 8 "
             "consecutive fall+spring semesters (first-year admits).",
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

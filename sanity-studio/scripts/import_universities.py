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

    # ── UK BATCH (7 universities, Batch-2 slots 19–25) ──────────────────────────────────────
    # country-gb already published in Sanity staging. All 7 are DRAFTS.
    # Application platform: UCAS. Cambridge early deadline 15 Oct 2026; all others Jan 2027.
    # Tuition: international (overseas fee status) rates only — Home/domestic not shown.

    "uk-cambridge": {
        "canonical_name": "University of Cambridge", "aliases": ["Cambridge"], "country_cc": "gb",
        "city": {"slug": "uk-cambridge-gb", "name": "Cambridge"},
        "website": "https://www.cam.ac.uk/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "GBP",
        "verification_note": "fact-checks/uk-cambridge-2026-10-25.md",
        "application_platform_name": "UCAS Application",
        "decision_context_year": "2026-2027 (September 2027 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "Cambridge Undergraduate Study",
                "url": "https://www.undergraduate.study.cam.ac.uk/",
                "excerpt": "University of Cambridge, UK; collegiate research university; English medium. Undergraduate "
                "courses include Computer Science (BA, 3 years, Group 4 fee band), Engineering (MEng, 4 years, "
                "Group 4), and Economics (BA, 3 years, Group 1 fee band). No undergraduate Business programme. "
                "All applicants apply through UCAS by the early Oxbridge deadline (15 October 2026 for 2027 entry)."},
            "adm": {"suffix": "src-adm", "title": "International Students — Cambridge Undergraduate",
                "url": "https://www.undergraduate.study.cam.ac.uk/international-students",
                "excerpt": "All overseas applicants apply via UCAS by 15 October 2026 at 6pm UK time. English: "
                "IELTS Academic 7.5 overall, minimum 7.0 in each element (required unless previous education was "
                "entirely in English). Accepted qualifications: A-levels (typically A*A*A), IB (41-42 with 776 at HL). "
                "Cambridge admissions assessments: TMUA (Computer Science, Economics); ESAT (Engineering). "
                "Interview is part of the selection process for shortlisted applicants."},
            "fee": {"suffix": "src-fee", "title": "International Fees and Costs — Cambridge Undergraduate",
                "url": "https://www.undergraduate.study.cam.ac.uk/international-students/international-fees-and-costs",
                "excerpt": "2027 entry international (overseas) tuition: Group 4 (Computer Science, Engineering, "
                "Natural Sciences) £46,872/year; Group 1 (Arts, Humanities, Economics) £30,798/year. "
                "College fee is ADDITIONAL and varies by college — confirmed with individual college at offer stage. "
                "Living costs estimated £13,380–£20,520/year (excluding college fee)."},
            "schol": {"suffix": "src-schol", "title": "Scholarships and Bursaries — Cambridge Undergraduate",
                "url": "https://www.undergraduate.study.cam.ac.uk/fees-funding/scholarships-bursaries",
                "excerpt": "Cambridge Trust (Cambridge Commonwealth, European and International Trust) awards for "
                "overseas undergraduates with demonstrated financial need — applied for after receiving a college offer. "
                "Deadline: February for the following October entry. Cambridge does not offer merit-based undergraduate "
                "scholarships; institutional aid is need-based only."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications; Cambridge considers a wide range of qualifications."),
        ],
        "residencies": [
            ("international", "International (overseas fee status)",
             "Students classified as 'overseas' for UK fee purposes. UK Home students pay the lower Home fee rate."),
        ],
        # University-level cost is a placeholder; all three programmes override with their group-specific fee.
        "cost": {"residency": "international", "tuition": None, "basis": "institutional", "year": "2027 entry",
            "mandatory_fees_annual": None,
            "note": "Cambridge charges by course group: Group 4 (CS, Engineering) £46,872/yr; Group 1 (Economics) "
            "£30,798/yr (2027 entry). College fee is ADDITIONAL — varies by college, not published centrally, "
            "confirmed at offer stage. All per-programme costs stored on each programme record."},
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "IELTS 7.5 overall, with no element below 7.0.",
            "notes": "Required if first language is not English and previous education was not entirely in English. "
            "Test must be no more than two years old at course start."},
        "std_tests": [
            {"test_name": "UCAS Application", "required": "required",
             "notes": "Apply via UCAS (Institution code: CAM). Deadline: 15 October 2026 at 6pm UK time."},
        ],
        "deadline_note": "UCAS deadline: 15 October 2026 at 6pm UK (early Oxbridge deadline — NOT the standard January date). "
            "Institution code: CAM. Admissions assessments: TMUA for CS and Economics, ESAT for Engineering. "
            "Shortlisted applicants invited to interview in December.",
        "living": {"min": 1115, "max": 1710, "currency": "GBP", "admin_body": "University of Cambridge",
            "desc": "Cambridge estimated living costs (2027 entry): £13,380–£20,520/year (~£1,115–£1,710/month). "
            "Excludes college fee (separate, varies by college, confirmed at offer)."},
        "programs": [
            {"suffix": "ba-cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BA",
             "degree_local": "BA in Computer Science, University of Cambridge. 3-year honours course. Group 4 fee band. "
             "Covers algorithms, machine learning, systems, programming languages, and theory of computation. "
             "TMUA admissions assessment required.",
             "faculty": "Department of Computer Science and Technology", "duration": 3,
             "url": "https://www.undergraduate.study.cam.ac.uk/courses/computer-science",
             "subjects_note": "A*A*A at A-level; Mathematics required; TMUA admissions test required",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "std_tests": [
                 {"test_name": "TMUA (Test of Mathematics for University Admissions)", "required": "required",
                  "notes": "Required for Cambridge Computer Science applicants. Assesses mathematical thinking."},
             ],
             "cost": {"residency": "international", "tuition": 46872, "basis": "institutional", "year": "2027 entry",
                 "mandatory_fees_annual": None,
                 "note": "£46,872/yr (Group 4) for international students, Cambridge BA Computer Science, 2027 entry. "
                 "College fee additional (amount varies by college — not published centrally)."}},
            {"suffix": "meng-engineering", "program_name": "Engineering", "field": "Engineering", "degree": "MEng",
             "degree_local": "MEng in Engineering, University of Cambridge. 4-year integrated Master's. Group 4 fee band. "
             "General Engineering for first two years; specialise in Year 3 and 4 across Electrical, Mechanical, "
             "Civil, Chemical, Aerospace, Information, and Manufacturing Engineering. ESAT required.",
             "faculty": "Department of Engineering", "duration": 4,
             "url": "https://www.undergraduate.study.cam.ac.uk/courses/engineering",
             "subjects_note": "A*A*A at A-level; Mathematics and Physics expected; ESAT admissions test required",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics", "Physics"], "international-other": []},
             "std_tests": [
                 {"test_name": "ESAT (Engineering and Science Admissions Test)", "required": "required",
                  "notes": "Required for Cambridge Engineering applicants. Tests Mathematics and Physics at A-level standard."},
             ],
             "cost": {"residency": "international", "tuition": 46872, "basis": "institutional", "year": "2027 entry",
                 "mandatory_fees_annual": None,
                 "note": "£46,872/yr (Group 4) for international students, Cambridge MEng Engineering, 2027 entry. "
                 "College fee additional."}},
            {"suffix": "ba-economics", "program_name": "Economics", "field": "Economics", "degree": "BA",
             "degree_local": "BA in Economics, University of Cambridge. 3-year honours course. Group 1 fee band "
             "(lower rate than STEM courses). Microeconomics, macroeconomics, econometrics, and economic theory. "
             "TMUA admissions assessment required.",
             "faculty": "Faculty of Economics", "duration": 3,
             "url": "https://www.undergraduate.study.cam.ac.uk/courses/economics",
             "subjects_note": "A*A*A at A-level; strong Mathematics background expected; TMUA admissions test required",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "std_tests": [
                 {"test_name": "TMUA (Test of Mathematics for University Admissions)", "required": "required",
                  "notes": "Required for Cambridge Economics applicants. Assesses mathematical thinking and reasoning."},
             ],
             "cost": {"residency": "international", "tuition": 30798, "basis": "institutional", "year": "2027 entry",
                 "mandatory_fees_annual": None,
                 "note": "£30,798/yr (Group 1) for international students, Cambridge BA Economics, 2027 entry. "
                 "Significantly lower than Group 4 (CS/Engineering). College fee additional."}},
        ],
        # Cambridge has no undergraduate Business programme — omitted, not fabricated.
        "scholarships": [
            {"suffix": "cambridge-trust", "name": "Cambridge Trust International Award",
             "provider": "Cambridge Commonwealth, European and International Trust",
             "provider_type": "institutional", "award_type": "partial_tuition", "renewable": True,
             "award_amount": "Variable; assessed on financial need after receiving a college offer. Covers partial "
             "tuition and/or maintenance. Not a fixed amount — decided case by case.",
             "academic_criteria": "Must have received an offer of admission from a Cambridge college.",
             "other_eligibility_criteria": "NEED-BASED only — available to overseas students with demonstrated financial "
             "need. Application after receiving a college offer; deadline typically February for October entry. "
             "Cambridge does NOT offer merit-based undergraduate scholarships.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },

    "uk-imperial": {
        "canonical_name": "Imperial College London", "aliases": ["Imperial"], "country_cc": "gb",
        "city": {"slug": "uk-london-gb", "name": "London"},
        "website": "https://www.imperial.ac.uk/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "GBP",
        "verification_note": "fact-checks/uk-imperial-2026-10-25.md",
        "application_platform_name": "UCAS Application",
        "decision_context_year": "2026-2027 (September 2027 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "Imperial College London — Undergraduate Study",
                "url": "https://www.imperial.ac.uk/study/ug/",
                "excerpt": "Imperial College London; London research university; English medium. Undergraduate "
                "programmes: MEng Computing (4 years), MEng/BEng Engineering across departments (3/4 years), "
                "and BSc Economics, Finance and Data Science via Imperial Business School (3 years). Imperial has NO "
                "standalone undergraduate Business or Economics degree — BSc Economics, Finance and Data Science is "
                "the sole economics/business UG offering."},
            "adm": {"suffix": "src-adm", "title": "Applying to Imperial — Undergraduate",
                "url": "https://www.imperial.ac.uk/study/ug/apply/",
                "excerpt": "Apply via UCAS (Institution code: I50). Standard January 2027 deadline. English: "
                "most UG programmes require Higher Level — IELTS 7.0 overall, minimum 6.5 in all elements. "
                "MEng Computing: A*A*A (A* in Mathematics; A* in Further Mathematics also typical/expected). "
                "BSc Economics, Finance and Data Science: A*AA (A* in Mathematics). Engineering MEng: A*A*A "
                "(A* in Mathematics; Physics typically required by department)."},
            "fee": {"suffix": "src-fee", "title": "Undergraduate Tuition Fees — Imperial College London",
                "url": "https://www.imperial.ac.uk/study/fees-and-funding/undergraduate/tuition-fees/",
                "excerpt": "2026-27 international (overseas) undergraduate tuition: Engineering and Computing "
                "£45,500/year; Imperial Business School (BSc Economics, Finance and Data Science) £42,700/year. "
                "Fees set for the duration of the course for the 2026 entry cohort."},
            "schol": {"suffix": "src-schol",
                "title": "Undergraduate Scholarships — Imperial College London",
                "url": "https://www.imperial.ac.uk/study/fees-and-funding/scholarships-search/international-baccalaureate-excellence-scholarships-20262027.php",
                "excerpt": "IB Excellence Scholarships 2026-27: £5,000/year for duration of study; 23 scholarships "
                "across Faculty of Engineering, Faculty of Natural Sciences, and Imperial Business School. For IB "
                "Diploma holders entering autumn 2026. COMPETITIVE. GREAT Scholarships (£15,000 towards tuition, "
                "UK government funded, limited countries) also available. No general merit scholarship for all "
                "international UG applicants."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications accepted at equivalent standard."),
        ],
        "residencies": [
            ("international", "International (overseas fee status)",
             "Students classified as 'overseas' for UK fee purposes."),
        ],
        "cost": {"residency": "international", "tuition": None, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": None,
            "note": "Imperial charges by faculty: Engineering/Computing £45,500/yr; Business School £42,700/yr. "
            "Per-programme tuition stored on each record."},
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "IELTS 7.0 overall, with no element below 6.5 (Higher Level, most UG programmes).",
            "notes": "Higher Level English requirement for Engineering/Computing and Business School UG. "
            "TOEFL iBT equivalent accepted. Test must be no more than two years old."},
        "std_tests": [
            {"test_name": "UCAS Application", "required": "required",
             "notes": "Apply via UCAS (Institution code: I50). Standard January 2027 deadline."},
        ],
        "deadline_note": "Apply via UCAS by January 2027 (standard UCAS equal consideration deadline). Institution code: I50.",
        "living": None,
        "programs": [
            {"suffix": "meng-computing", "program_name": "Computing (Computer Science)", "field": "Computer Science",
             "degree": "MEng",
             "degree_local": "MEng Computing, Department of Computing, Imperial College London. 4-year integrated "
             "Master's. Streams: Artificial Intelligence, Machine Learning, Visual Computing, Software Engineering, "
             "and others. Related: MEng Computing (AI), MEng Computing (Software Engineering).",
             "faculty": "Department of Computing", "duration": 4,
             "url": "https://www.imperial.ac.uk/computing/prospective-students/courses/ug/",
             "subjects_note": "A*A*A with A* in Mathematics (A* in Further Mathematics also typical/expected)",
             "subjects": {"a-level": ["Mathematics", "Further Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 45500, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "£45,500/yr for international students, Imperial MEng Computing, 2026-2027."}},
            {"suffix": "meng-engineering", "program_name": "Engineering", "field": "Engineering", "degree": "MEng",
             "degree_local": "MEng Engineering, Imperial College London. 4-year integrated Master's. Departments: "
             "Aeronautics, Civil, Electrical & Electronic, Mechanical, Chemical, Bioengineering, Materials, "
             "and Earth Science & Engineering. 3-year BEng also available in some departments.",
             "faculty": "Faculty of Engineering", "duration": 4,
             "url": "https://www.imperial.ac.uk/study/ug/programmes/engineering/",
             "subjects_note": "A*A*A with A* in Mathematics (Physics or relevant science typically required by department)",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics", "Physics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 45500, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "£45,500/yr for international students, Imperial MEng Engineering, 2026-2027."}},
            {"suffix": "bsc-econ-finance-ds", "program_name": "Economics, Finance and Data Science",
             "field": "Economics", "degree": "BSc",
             "degree_local": "BSc Economics, Finance and Data Science, Imperial Business School. 3-year programme "
             "combining microeconomics, macroeconomics, quantitative finance, and data science. This is Imperial's "
             "sole undergraduate economics/business offering — there is NO standalone BSc Economics or BSc Business "
             "Management at Imperial.",
             "faculty": "Imperial Business School", "duration": 3,
             "url": "https://www.imperial.ac.uk/business-school/undergraduate/economics-finance-data-science/",
             "subjects_note": "A*AA with A* in Mathematics",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 42700, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "£42,700/yr for international students, Imperial BSc Economics Finance Data Science, 2026-2027."}},
        ],
        # Imperial has no standalone Business Management undergraduate degree.
        "scholarships": [
            {"suffix": "ib-excellence", "name": "International Baccalaureate Excellence Scholarship",
             "provider": "Imperial College London", "provider_type": "institutional",
             "award_type": "partial_tuition", "renewable": True,
             "award_amount": "£5,000 per year for the full duration of the degree.",
             "academic_criteria": "IB Diploma holder entering autumn 2026. Academic excellence required.",
             "other_eligibility_criteria": "COMPETITIVE — 23 scholarships across Faculty of Engineering, "
             "Faculty of Natural Sciences, and Imperial Business School. IB Diploma applicants only.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },

    "uk-ucl": {
        "canonical_name": "University College London", "aliases": ["UCL"], "country_cc": "gb",
        "city": {"slug": "uk-london-gb", "name": "London"},
        "website": "https://www.ucl.ac.uk/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "GBP",
        "verification_note": "fact-checks/uk-ucl-2026-10-25.md",
        "application_platform_name": "UCAS Application",
        "decision_context_year": "2026-2027 (September 2027 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "UCL — Undergraduate Study",
                "url": "https://www.ucl.ac.uk/prospective-students/undergraduate/",
                "excerpt": "University College London (UCL); Bloomsbury, London; English medium. Undergraduate "
                "programmes include: BSc Computer Science (3 years), BEng Engineering across departments "
                "(3 years, MEng 4 years), BSc Economics (3 years), and BSc Management/International Management "
                "(3 years, UCL School of Management). All applications via UCAS."},
            "adm": {"suffix": "src-adm", "title": "Entry Requirements — UCL Undergraduate",
                "url": "https://www.ucl.ac.uk/study/prospective-students/undergraduate/how-apply/entry-requirements",
                "excerpt": "UCL Computer Science BSc: A*A*A (A* in Mathematics or Further Mathematics); TARA "
                "admissions test required for all UCL CS UG programmes (Critical Thinking, Problem Solving, "
                "Writing Task modules). UCL Economics BSc: A*AA (A* in Mathematics); IELTS Level 4: 7.5/7.0. "
                "Engineering: typically A*A*A or A*AA depending on department (course pages returning 403 this "
                "research pass — verify per dept). UCL uses 5 English proficiency levels; Economics = Level 4 "
                "(7.5/7.0); most Engineering = Level 2 (7.0/6.5) — verify from programme page."},
            "fee": {"suffix": "src-fee", "title": "Tuition Fees — UCL Undergraduate 2026-27",
                "url": "https://www.ucl.ac.uk/students/fees",
                "excerpt": "2026-27 international (overseas) undergraduate tuition: BSc Computer Science "
                "£46,700/year; most BEng/MEng Engineering £42,700/year; BSc Economics £39,200/year; "
                "BSc Management/International Management £42,700/year."},
            "schol": {"suffix": "src-schol", "title": "Scholarships — UCL",
                "url": "https://www.ucl.ac.uk/scholarships/",
                "excerpt": "UCL offers various scholarships including the Telles Scholarship for Engineering. "
                "Most UCL UG scholarships are need-based or UK-focused; no general merit scholarship for all "
                "international UG applicants identified at this time."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications accepted at equivalent standard."),
        ],
        "residencies": [
            ("international", "International (overseas fee status)",
             "Students classified as 'overseas' for UK fee purposes."),
        ],
        "cost": {"residency": "international", "tuition": None, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": None,
            "note": "UCL fees vary by programme: CS £46,700/yr; Engineering £42,700/yr; Economics £39,200/yr; "
            "Management £42,700/yr. Per-programme tuition stored on each programme record."},
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "Varies by programme level. Economics BSc (Level 4): IELTS 7.5 overall, min 7.0 per "
            "element. Most UG programmes (Level 2): IELTS 7.0 overall, min 6.5 per element — verify from "
            "individual programme page.",
            "notes": "UCL uses 5 English proficiency levels. Economics confirmed Level 4 (7.5/7.0). CS and "
            "Engineering levels not verified from primary source this pass (course pages returned 403). "
            "TOEFL equivalent accepted."},
        "std_tests": [
            {"test_name": "UCAS Application", "required": "required",
             "notes": "Apply via UCAS (Institution code: U80). Standard January 2027 deadline."},
        ],
        "deadline_note": "Apply via UCAS by January 2027 (standard UCAS equal consideration deadline). Institution code: U80. "
            "CS applicants must also register for and sit the TARA admissions assessment.",
        "living": None,
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "BSc Computer Science, UCL Department of Computer Science. 3-year programme. "
             "TARA admissions test required for all UCL CS UG programmes.",
             "faculty": "UCL Department of Computer Science", "duration": 3,
             "url": "https://www.ucl.ac.uk/prospective-students/undergraduate/degrees/computer-science-bsc-2026",
             "subjects_note": "A*A*A with A* in Mathematics or Further Mathematics; TARA admissions test required",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "std_tests": [
                 {"test_name": "TARA (Test for Academic Reasoning for Admissions)", "required": "required",
                  "notes": "Required for all UCL CS UG programmes. Three modules: Critical Thinking, Problem Solving, Writing Task."},
             ],
             "cost": {"residency": "international", "tuition": 46700, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "£46,700/yr for international students, UCL BSc Computer Science, 2026-2027."}},
            {"suffix": "beng-engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BEng",
             "degree_local": "BEng Engineering, UCL Faculty of Engineering Sciences. 3-year BEng (4-year MEng "
             "also available). Departments: Chemical, Civil Environmental & Geomatic, Electronic & Electrical, "
             "Mechanical, Biochemical, and others. Most departments: £42,700/yr international.",
             "faculty": "UCL Faculty of Engineering Sciences", "duration": 3,
             "url": "https://www.ucl.ac.uk/engineering/",
             "subjects_note": "A-level offer typically A*A*A or A*AA depending on engineering dept (not verified from primary source this pass — course pages returned 403; verify per dept)",
             "subjects": {"a-level": [], "ib": [], "international-other": []},
             "cost": {"residency": "international", "tuition": 42700, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "£42,700/yr for international students, most UCL BEng Engineering, 2026-2027."}},
            {"suffix": "bsc-economics", "program_name": "Economics", "field": "Economics", "degree": "BSc",
             "degree_local": "BSc Economics (Econ), UCL Department of Economics. 3-year programme.",
             "faculty": "UCL Department of Economics", "duration": 3,
             "url": "https://www.ucl.ac.uk/prospective-students/undergraduate/degrees/economics-bsc-econ-2026",
             "subjects_note": "A*AA with A* in Mathematics; IELTS Level 4: 7.5 overall, min 7.0 per element",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 39200, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "£39,200/yr for international students, UCL BSc Economics, 2026-2027. "
                 "NOTE: Economics IELTS requirement is Level 4 (7.5/7.0) — higher than most UCL UG programmes."}},
            {"suffix": "bsc-management", "program_name": "Management", "field": "Business", "degree": "BSc",
             "degree_local": "BSc Management or BSc International Management, UCL School of Management. 3-year "
             "programme covering strategy, operations, finance, marketing, and organisational behaviour.",
             "faculty": "UCL School of Management", "duration": 3,
             "url": "https://www.ucl.ac.uk/school-of-management/study/undergraduate/",
             "subjects_note": "A-level offer not verified from primary source this pass (course pages returned 403)",
             "subjects": {"a-level": [], "ib": [], "international-other": []},
             "cost": {"residency": "international", "tuition": 42700, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "£42,700/yr for international students, UCL BSc Management/International Management, 2026-2027."}},
        ],
        "scholarships": [],
        # No general merit scholarship for all international UCL UG applicants identified at this time.
    },

    "uk-warwick": {
        "canonical_name": "University of Warwick", "aliases": ["Warwick"], "country_cc": "gb",
        "city": {"slug": "uk-coventry-gb", "name": "Coventry"},
        "website": "https://warwick.ac.uk/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "GBP",
        "verification_note": "fact-checks/uk-warwick-2026-10-25.md",
        "application_platform_name": "UCAS Application",
        "decision_context_year": "2026-2027 (September 2027 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "Warwick — Undergraduate Study",
                "url": "https://warwick.ac.uk/study/undergraduate/",
                "excerpt": "University of Warwick; Coventry, UK; English medium. Undergraduate programmes: "
                "BSc Computer Science (3 years), BEng/MEng Engineering (3/4 years), BA/BSc Economics (3 years), "
                "and Warwick Business School (WBS) degrees (3 years). International fee £35,530/year across all "
                "target programmes (2026-27)."},
            "adm": {"suffix": "src-adm", "title": "Undergraduate Entry Requirements — Warwick",
                "url": "https://warwick.ac.uk/study/undergraduate/applying/",
                "excerpt": "Apply via UCAS (Institution code: W20). Standard January 2027 deadline. A-level offers: "
                "CS BSc A*A*A (A* in Mathematics); Economics A*AA (A in Mathematics); Engineering BEng AAA "
                "(Maths + Physics); Engineering MEng A*AA (Maths + Physics). English language bands: "
                "Band A (CS) = IELTS 6.0 overall / min 5.5 per component; Band B = 6.5/6.0; Band C (Economics) = "
                "7.0 overall / min 6.5 per component. Engineering/WBS band not verified from primary source."},
            "fee": {"suffix": "src-fee", "title": "Undergraduate Fees — University of Warwick",
                "url": "https://warwick.ac.uk/study/undergraduate/fees/",
                "excerpt": "2026-27 international (overseas) undergraduate tuition: £35,530/year for most UG "
                "programmes including Computer Science, Engineering, Economics, and Warwick Business School. "
                "Uniform fee across all four target pillars."},
            "schol": {"suffix": "src-schol",
                "title": "Undergraduate Global Excellence Scholarship — Warwick",
                "url": "https://warwick.ac.uk/study/undergraduate/applying/scholarships/",
                "excerpt": "Warwick Undergraduate Global Excellence Scholarship: for international (overseas fee) "
                "self-funded students holding an offer. 2025 cohort awards: 6 full-fee, 148 half-fee, 103 25%-fee, "
                "6 at £2,000. Competitive — 547 scholars from 72 countries since 2021. Deadline for 2026/27 "
                "entry was 27 February 2026 (passed); check for 2027/28 entry dates."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications accepted at equivalent standard."),
        ],
        "residencies": [
            ("international", "International (overseas fee status)",
             "Students classified as 'overseas' for UK fee purposes."),
        ],
        # Warwick charges a uniform £35,530/yr across all four target programmes.
        "cost": {"residency": "international", "tuition": 35530, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": 0,
            "note": "£35,530/yr for international students, 2026-27. Uniform across CS, Engineering, Economics, "
            "and Warwick Business School programmes."},
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "Varies by programme band. CS (Band A): IELTS 6.0 overall, min 5.5 per component. "
            "Economics (Band C): IELTS 7.0 overall, min 6.5 per component. Engineering/WBS bands not verified.",
            "notes": "Warwick assigns each programme to an English language band. Band A = 6.0/5.5; Band B = 6.5/6.0; "
            "Band C = 7.0/6.5 (tests taken on/after 1 September 2024). Verify your programme's band at "
            "warwick.ac.uk/study/undergraduate/applying/english-language-requirements/."},
        "std_tests": [
            {"test_name": "UCAS Application", "required": "required",
             "notes": "Apply via UCAS (Institution code: W20). Standard January 2027 deadline."},
        ],
        "deadline_note": "Apply via UCAS by January 2027 (standard UCAS equal consideration deadline). Institution code: W20.",
        "living": None,
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "BSc Computer Science, Department of Computer Science, University of Warwick. 3-year "
             "programme. English language Band A: IELTS 6.0/5.5.",
             "faculty": "Department of Computer Science", "duration": 3,
             "url": "https://warwick.ac.uk/study/undergraduate/courses/bsc-computer-science/",
             "subjects_note": "A*A*A with A* in Mathematics; Band A English: IELTS 6.0 overall, min 5.5 per component",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []}},
            {"suffix": "beng-engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BEng",
             "degree_local": "BEng Engineering, School of Engineering, University of Warwick. 3-year BEng (4-year "
             "MEng also available — MEng offer A*AA). Disciplines: Civil, Electrical, Mechanical, Manufacturing, "
             "Biomedical, Systems Engineering. BEng offer: AAA (Maths + Physics).",
             "faculty": "School of Engineering", "duration": 3,
             "url": "https://warwick.ac.uk/study/undergraduate/courses/beng-engineering/",
             "subjects_note": "BEng: AAA (Mathematics + Physics); MEng: A*AA (Mathematics + Physics); IELTS band not verified from primary source this pass",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics", "Physics"], "international-other": []}},
            {"suffix": "ba-economics", "program_name": "Economics", "field": "Economics", "degree": "BA",
             "degree_local": "BA Economics, Department of Economics, University of Warwick. 3-year programme. "
             "Strong quantitative focus. English language Band C: IELTS 7.0/6.5.",
             "faculty": "Department of Economics", "duration": 3,
             "url": "https://warwick.ac.uk/study/undergraduate/courses/bsc-economics/",
             "subjects_note": "A*AA with A in Mathematics (A* overall grade, A in Maths); Band C English: IELTS 7.0 overall, min 6.5 per component",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []}},
            {"suffix": "bsc-business", "program_name": "Business", "field": "Business", "degree": "BSc",
             "degree_local": "Warwick Business School (WBS) undergraduate degree. Programmes include: "
             "BSc Accounting & Finance, BSc Management, BSc International Business (3 years). "
             "A-level offer and English language band not verified from primary source this pass.",
             "faculty": "Warwick Business School", "duration": 3,
             "url": "https://www.wbs.ac.uk/courses/undergraduate/",
             "subjects_note": "A-level offer and English language band not verified from primary source this pass — verify from wbs.ac.uk",
             "subjects": {"a-level": [], "ib": [], "international-other": []}},
        ],
        "scholarships": [
            {"suffix": "global-excellence", "name": "Warwick Undergraduate Global Excellence Scholarship",
             "provider": "University of Warwick", "provider_type": "institutional",
             "award_type": "partial_tuition", "renewable": True,
             "award_amount": "Variable and competitive: full-fee, half-fee, 25%-fee, or £2,000 (2025 cohort: "
             "6 full-fee, 148 half-fee, 103 25%-fee, 6 at £2,000 — across all international applicants).",
             "academic_criteria": "Exceptional academic achievement; must hold an offer to study at Warwick.",
             "other_eligibility_criteria": "COMPETITIVE — available to international self-funded students. "
             "Application separate from UCAS; 2026/27 deadline was 27 February 2026 (passed). "
             "Award renewable for duration of course.",
             "application_deadline": None, "deadline_academic_year": "2027-2028"},
        ],
    },

    "uk-manchester": {
        "canonical_name": "University of Manchester", "aliases": ["Manchester", "UoM"], "country_cc": "gb",
        "city": {"slug": "uk-manchester-gb", "name": "Manchester"},
        "website": "https://www.manchester.ac.uk/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "GBP",
        "verification_note": "fact-checks/uk-manchester-2026-10-25.md",
        "application_platform_name": "UCAS Application",
        "decision_context_year": "2026-2027 (September 2027 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "University of Manchester — Undergraduate Study",
                "url": "https://www.manchester.ac.uk/study/undergraduate/",
                "excerpt": "University of Manchester; Russell Group; English medium. Target UG programmes: "
                "BSc Computer Science (3 years, £39,700/yr international), BEng Mechanical Engineering (3 years, "
                "£35,700/yr), BSc Management via Alliance MBS (3 years, £33,100/yr), BSc Economics (3 years, "
                "£33,100/yr). All via UCAS (Institution code: M20)."},
            "adm": {"suffix": "src-adm", "title": "Entry Requirements — University of Manchester UG 2026",
                "url": "https://www.manchester.ac.uk/study/undergraduate/courses/2026/",
                "excerpt": "BSc Computer Science (2026): A*AA including A* in Mathematics and one science "
                "(Biology, Chemistry, CS, Further Maths, Physics, Statistics). BEng Mechanical Engineering "
                "(2026): A*A*A including Mathematics, Physics, and one further subject. BSc Economics: AAA "
                "including Mathematics. BSc Management: A-level offer not verified this pass — verify from "
                "Alliance MBS. IELTS: 6.5 overall, no sub-test below 6.5 (verified for CS and Engineering)."},
            "fee": {"suffix": "src-fee", "title": "International Fees — University of Manchester",
                "url": "https://www.manchester.ac.uk/study/international/finance-and-scholarships/fees/",
                "excerpt": "2026-27 international (overseas) undergraduate tuition: BSc Computer Science "
                "£39,700/year; BEng Mechanical Engineering £35,700/year; BSc Management £33,100/year; "
                "BSc Economics £33,100/year."},
            "schol": {"suffix": "src-schol", "title": "Global Futures Scholarships — University of Manchester 2026",
                "url": "https://www.manchester.ac.uk/study/international/finance-and-scholarships/",
                "excerpt": "Global Futures Scholarships 2026: 330+ awards, >£6 million total. UAE: up to £36,000 "
                "(£12,000/year over 3 years), merit-based. Assessed on academic excellence and application "
                "responses (form emailed to eligible offer-holders). Self-funded applicants, direct first-year "
                "entry 2026, A-level/IB/French Bac/Indian Standard XII. Country-specific deadlines."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications accepted at equivalent standard."),
        ],
        "residencies": [
            ("international", "International (overseas fee status)",
             "Students classified as 'overseas' for UK fee purposes."),
        ],
        "cost": {"residency": "international", "tuition": None, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": None,
            "note": "Manchester fees vary: CS £39,700/yr; Engineering £35,700/yr; Management £33,100/yr; "
            "Economics £33,100/yr. Per-programme tuition stored on each programme record."},
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "IELTS 6.5 overall, no sub-test below 6.5.",
            "notes": "IELTS 6.5/6.5 verified for CS (2026) and Mechanical Engineering (2026). Economics and "
            "Management IELTS not separately confirmed this pass — likely same standard; verify from programme."},
        "std_tests": [
            {"test_name": "UCAS Application", "required": "required",
             "notes": "Apply via UCAS (Institution code: M20). Standard January 2027 deadline."},
        ],
        "deadline_note": "Apply via UCAS by January 2027 (standard UCAS equal consideration deadline). Institution code: M20.",
        "living": None,
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "BSc Computer Science, Department of Computer Science, University of Manchester. "
             "3-year programme.",
             "faculty": "Department of Computer Science", "duration": 3,
             "url": "https://www.manchester.ac.uk/study/undergraduate/courses/2026/00560/bsc-computer-science/",
             "subjects_note": "A*AA including A* in Mathematics and one science subject (Biology, Chemistry, CS, Further Maths, Physics, or Statistics)",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 39700, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "£39,700/yr for international students, Manchester BSc Computer Science, 2026-2027."}},
            {"suffix": "beng-mechanical-eng", "program_name": "Engineering (Mechanical)", "field": "Engineering",
             "degree": "BEng",
             "degree_local": "BEng Mechanical Engineering, Dept of Mechanical Aerospace & Civil Engineering, "
             "University of Manchester. 3-year BEng (4-year MEng also available). Other engineering disciplines "
             "(Electrical, Civil, Chemical, Aerospace) offered at comparable fees.",
             "faculty": "Faculty of Science and Engineering", "duration": 3,
             "url": "https://www.manchester.ac.uk/study/undergraduate/courses/2026/03389/beng-mechanical-engineering/",
             "subjects_note": "A*A*A including Mathematics, Physics, and one further subject",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics", "Physics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 35700, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "£35,700/yr for international students, Manchester BEng Mechanical Engineering, 2026-2027."}},
            {"suffix": "bsc-management", "program_name": "Management", "field": "Business", "degree": "BSc",
             "degree_local": "BSc Management, Alliance Manchester Business School (Alliance MBS), University "
             "of Manchester. 3-year programme. Related: BSc International Management, BSc Accounting.",
             "faculty": "Alliance Manchester Business School", "duration": 3,
             "url": "https://www.manchester.ac.uk/study/undergraduate/courses/2026/",
             "subjects_note": "A-level offer not verified from primary source this pass — verify from alliancembs.manchester.ac.uk",
             "subjects": {"a-level": [], "ib": [], "international-other": []},
             "cost": {"residency": "international", "tuition": 33100, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "£33,100/yr for international students, Manchester BSc Management, 2026-2027."}},
            {"suffix": "bsc-economics", "program_name": "Economics", "field": "Economics", "degree": "BSc",
             "degree_local": "BSc Economics, School of Social Sciences, University of Manchester. 3-year "
             "programme. Optional industrial placement (4 years).",
             "faculty": "School of Social Sciences — Economics", "duration": 3,
             "url": "https://www.manchester.ac.uk/study/undergraduate/courses/2026/01066/bsc-economics/",
             "subjects_note": "AAA including Mathematics",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 33100, "basis": "institutional", "year": "2026-2027",
                 "mandatory_fees_annual": 0,
                 "note": "£33,100/yr for international students, Manchester BSc Economics, 2026-2027."}},
        ],
        "scholarships": [
            {"suffix": "global-futures-uae", "name": "Global Futures Scholarship (UAE)",
             "provider": "University of Manchester", "provider_type": "institutional",
             "award_type": "partial_tuition", "renewable": True,
             "award_amount": "Up to £12,000/year (£36,000 over 3 years) for UAE-based applicants.",
             "academic_criteria": "Merit-based — academic excellence (grades) and scholarship application responses.",
             "other_eligibility_criteria": "COMPETITIVE — one of 330+ global awards. UAE applicants: direct "
             "first-year 2026 entry, self-funded, with A-level/IB/French Bac/Indian Standard XII qualifications. "
             "Application form emailed to eligible offer-holders. UAE deadline — check manchester.ac.uk/uae.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },

    "uk-birmingham": {
        "canonical_name": "University of Birmingham", "aliases": ["Birmingham", "UoB"], "country_cc": "gb",
        "city": {"slug": "uk-birmingham-gb", "name": "Birmingham"},
        "website": "https://www.birmingham.ac.uk/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "GBP",
        "verification_note": "fact-checks/uk-birmingham-2026-10-25.md",
        "application_platform_name": "UCAS Application",
        "decision_context_year": "2026-2027 (September 2027 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "University of Birmingham — Undergraduate Study",
                "url": "https://www.birmingham.ac.uk/study/undergraduate/",
                "excerpt": "University of Birmingham; Russell Group; English medium. Target UG programmes: "
                "BSc Computer Science, BEng Engineering, BSc Business Management (Birmingham Business School), "
                "BSc Economics. International tuition fees are NOT published per programme — they are communicated "
                "individually in the offer letter, per Birmingham's own fees page."},
            "adm": {"suffix": "src-adm", "title": "Entry Requirements — University of Birmingham UG",
                "url": "https://www.birmingham.ac.uk/study/undergraduate/",
                "excerpt": "BSc Computer Science: A*AA including Mathematics (grade A required); IELTS 6.0 overall, "
                "no band below 5.5. BSc Economics: AAA including Mathematics; IELTS 6.5 overall (component "
                "minimum not confirmed this pass — verify from programme page). BEng Engineering and BSc Business "
                "Management: A-level and IELTS not verified from primary source this pass."},
            "fee": {"suffix": "src-fee", "title": "Tuition Fees (International) — University of Birmingham",
                "url": "https://www.birmingham.ac.uk/international/students/finance/fees",
                "excerpt": "IMPORTANT: University of Birmingham does not publish programme-specific international "
                "fees publicly. From their fees page: 'Confirmation of your exact tuition fee will be included "
                "with your offer letter.' Fee not publicly listed = stored as null, not estimated."},
            "schol": {"suffix": "src-schol", "title": "Scholarships — University of Birmingham",
                "url": "https://www.birmingham.ac.uk/study/scholarships-funding/",
                "excerpt": "Birmingham international UG scholarships are region-specific: High Fliers (£5,000) "
                "for Europe, China, Turkey only. GEES Global Futures (£2,000) for India/Bangladesh only. "
                "No general merit scholarship open to UAE/GCC UG applicants was identified at this time."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications accepted at equivalent standard."),
        ],
        "residencies": [
            ("international", "International (overseas fee status)",
             "Students classified as 'overseas' for UK fee purposes. International fees not published per "
             "programme — amount confirmed in individual offer letter."),
        ],
        # Birmingham does not publish international fees per programme — null is correct and honest.
        "cost": {"residency": "international", "tuition": None, "basis": "institutional", "year": "2026-2027",
            "mandatory_fees_annual": None,
            "note": "University of Birmingham does not publicly disclose per-programme international tuition fees. "
            "Their fees page states: 'Confirmation of your exact tuition fee will be included with your offer letter.' "
            "Stored as null — not estimated. Student must obtain the confirmed fee from the offer letter."},
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "CS: IELTS 6.0 overall, no band below 5.5. Economics: IELTS 6.5 overall (component "
            "minimum verify from programme page). Engineering/Business Management: not verified this pass.",
            "notes": "IELTS 6.0/5.5 confirmed for BSc Computer Science. IELTS 6.5 for Economics from prior "
            "research pass — verify from birmingham.ac.uk. Engineering and Business IELTS not confirmed."},
        "std_tests": [
            {"test_name": "UCAS Application", "required": "required",
             "notes": "Apply via UCAS (Institution code: B32). Standard January 2027 deadline."},
        ],
        "deadline_note": "Apply via UCAS by January 2027 (standard UCAS equal consideration deadline). Institution code: B32.",
        "living": None,
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "BSc Computer Science, School of Computer Science, University of Birmingham. "
             "3-year programme. A-level: A*AA including Mathematics (grade A). IELTS: 6.0/5.5.",
             "faculty": "School of Computer Science", "duration": 3,
             "url": "https://www.birmingham.ac.uk/study/undergraduate/subjects/computer-science-courses/computer-science-bsc",
             "subjects_note": "A*AA including Mathematics (grade A required); IELTS 6.0 overall, no band below 5.5",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []}},
            {"suffix": "beng-engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BEng",
             "degree_local": "BEng Engineering, School of Engineering, University of Birmingham. 3-year BEng "
             "(MEng 4-year also available). Disciplines: Mechanical, Electrical, Chemical, Civil, Materials. "
             "A-level offer not verified from primary source this pass.",
             "faculty": "School of Engineering", "duration": 3,
             "url": "https://www.birmingham.ac.uk/study/undergraduate/subjects/engineering-courses/",
             "subjects_note": "A-level offer not verified from primary source this pass — verify from programme page at birmingham.ac.uk",
             "subjects": {"a-level": [], "ib": [], "international-other": []}},
            {"suffix": "bsc-business", "program_name": "Business Management", "field": "Business", "degree": "BSc",
             "degree_local": "BSc Business Management (or BSc Commerce), Birmingham Business School, University "
             "of Birmingham. 3-year programme. A-level and IELTS not verified this pass.",
             "faculty": "Birmingham Business School", "duration": 3,
             "url": "https://www.birmingham.ac.uk/study/undergraduate/subjects/business-courses/",
             "subjects_note": "A-level offer not verified from primary source this pass — verify from programme page",
             "subjects": {"a-level": [], "ib": [], "international-other": []}},
            {"suffix": "bsc-economics", "program_name": "Economics", "field": "Economics", "degree": "BSc",
             "degree_local": "BSc Economics, Department of Economics, University of Birmingham. 3-year programme. "
             "A-level: AAA including Mathematics. IELTS: 6.5 overall.",
             "faculty": "Department of Economics", "duration": 3,
             "url": "https://www.birmingham.ac.uk/study/undergraduate/subjects/economics-courses/",
             "subjects_note": "AAA including Mathematics; IELTS 6.5 overall (component minimum verify from programme page)",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []}},
        ],
        # No scholarship applicable for UAE/GCC undergraduate applicants found at this time.
        "scholarships": [],
    },

    "uk-nottingham": {
        "canonical_name": "University of Nottingham", "aliases": ["Nottingham", "UoN"], "country_cc": "gb",
        "city": {"slug": "uk-nottingham-gb", "name": "Nottingham"},
        "website": "https://www.nottingham.ac.uk/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "GBP",
        "verification_note": "fact-checks/uk-nottingham-2026-10-25.md",
        "application_platform_name": "UCAS Application",
        "decision_context_year": "2026-2027 (September 2027 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "University of Nottingham — Undergraduate Study",
                "url": "https://www.nottingham.ac.uk/ugstudy/",
                "excerpt": "University of Nottingham; Russell Group; English medium. Target UG programmes: "
                "BSc Computer Science (3 years), BEng Engineering (3 years), BSc Economics (3 years), "
                "BSc Business Management via NUBS (3 years). Fees below are 2027/28 figures (best available "
                "proxy — 2026/27 international fees not yet published at time of research)."},
            "adm": {"suffix": "src-adm", "title": "International Applicants — University of Nottingham UG",
                "url": "https://www.nottingham.ac.uk/studywithus/ugstudy/international-applicants/",
                "excerpt": "Apply via UCAS (Institution code: N84). Standard January 2027 deadline. English: "
                "IELTS 6.5 overall, no band below 6.0 (most programmes). BSc Computer Science (2027/28): "
                "typically AAA at A-level (or AAB with A in Computer Science). A-level offers for Engineering, "
                "Economics, and Business not verified from primary source this pass."},
            "fee": {"suffix": "src-fee", "title": "International Tuition Fees — University of Nottingham",
                "url": "https://www.nottingham.ac.uk/studywithus/ugstudy/international-applicants/tuition-fees.aspx",
                "excerpt": "2027/28 entry international (overseas) tuition (proxy — 2026/27 not yet published): "
                "Computer Science BSc £33,500/year; Engineering BEng £33,000/year; Economics BSc £26,800/year; "
                "Business Management BSc £24,700/year. Fees may increase for 2026/27 — verify from Nottingham."},
            "schol": {"suffix": "src-schol",
                "title": "International Undergraduate Excellence Scholarship — Nottingham",
                "url": "https://www.nottingham.ac.uk/studywithus/international-applicants/scholarships-funding-finance/international-undergraduate-excellence-scholarships.aspx",
                "excerpt": "International Undergraduate Excellence Scholarship: £5,000 deducted from first-year "
                "tuition. AUTOMATIC at admission — no separate application. For students achieving AAA at "
                "A-level or international equivalent. International fee-paying students, Year 1 full-time UG "
                "at Nottingham UK campus (BA/BSc/BEng/MEng etc.). Excludes Medicine, Pharmacy, Vet Medicine, "
                "Architecture, Foundation Year."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications accepted at equivalent standard."),
        ],
        "residencies": [
            ("international", "International (overseas fee status)",
             "Students classified as 'overseas' for UK fee purposes."),
        ],
        "cost": {"residency": "international", "tuition": None, "basis": "institutional",
            "year": "2027-2028 (proxy; 2026-27 not yet published)",
            "mandatory_fees_annual": None,
            "note": "Nottingham fees vary: CS £33,500/yr; Engineering £33,000/yr; Economics £26,800/yr; "
            "Business £24,700/yr — all 2027/28 proxy figures. 2026/27 fees not yet published. "
            "Per-programme tuition stored on each record. Verify from nottingham.ac.uk once published."},
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "IELTS 6.5 overall, no band below 6.0.",
            "notes": "IELTS 6.5/6.0 applies to most Nottingham UG programmes. Verify from individual programme page. "
            "TOEFL and PTE equivalents accepted."},
        "std_tests": [
            {"test_name": "UCAS Application", "required": "required",
             "notes": "Apply via UCAS (Institution code: N84). Standard January 2027 deadline."},
        ],
        "deadline_note": "Apply via UCAS by January 2027 (standard UCAS equal consideration deadline). Institution code: N84.",
        "living": None,
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science", "degree": "BSc",
             "degree_local": "BSc Computer Science, School of Computer Science, University of Nottingham. "
             "3-year programme. Related: MSci Computer Science (4 years).",
             "faculty": "School of Computer Science", "duration": 3,
             "url": "https://www.nottingham.ac.uk/ugstudy/courses/computer-science/g400-computer-science-bsc-hons.aspx",
             "subjects_note": "Typically AAA (or AAB with A in Computer Science); IELTS 6.5 overall, no band below 6.0",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 33500, "basis": "institutional",
                 "year": "2027-2028 (proxy)",
                 "mandatory_fees_annual": 0,
                 "note": "£33,500/yr, Nottingham BSc Computer Science (2027/28 proxy — 2026/27 not yet published)."}},
            {"suffix": "beng-engineering", "program_name": "Engineering", "field": "Engineering", "degree": "BEng",
             "degree_local": "BEng Engineering, Faculty of Engineering, University of Nottingham. 3-year BEng "
             "(MEng 4-year also available). Disciplines: Mechanical, Electrical, Civil, Chemical, Aerospace. "
             "A-level offer not verified from primary source this pass.",
             "faculty": "Faculty of Engineering", "duration": 3,
             "url": "https://www.nottingham.ac.uk/ugstudy/subjects/engineering/",
             "subjects_note": "A-level offer not verified from primary source this pass (typically AAA with Maths and Physics); IELTS 6.5/6.0",
             "subjects": {"a-level": [], "ib": [], "international-other": []},
             "cost": {"residency": "international", "tuition": 33000, "basis": "institutional",
                 "year": "2027-2028 (proxy)",
                 "mandatory_fees_annual": 0,
                 "note": "£33,000/yr, Nottingham BEng Engineering (2027/28 proxy)."}},
            {"suffix": "bsc-economics", "program_name": "Economics", "field": "Economics", "degree": "BSc",
             "degree_local": "BSc Economics, School of Economics, University of Nottingham. 3-year programme. "
             "A-level offer not verified from primary source this pass.",
             "faculty": "School of Economics", "duration": 3,
             "url": "https://www.nottingham.ac.uk/ugstudy/subjects/economics/",
             "subjects_note": "A-level offer not verified from primary source this pass (typically AAA including Maths); IELTS 6.5/6.0",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 26800, "basis": "institutional",
                 "year": "2027-2028 (proxy)",
                 "mandatory_fees_annual": 0,
                 "note": "£26,800/yr, Nottingham BSc Economics (2027/28 proxy)."}},
            {"suffix": "bsc-business", "program_name": "Business", "field": "Business", "degree": "BSc",
             "degree_local": "BSc Business Management, Nottingham University Business School (NUBS). 3-year "
             "programme. A-level offer not verified from primary source this pass.",
             "faculty": "Nottingham University Business School", "duration": 3,
             "url": "https://www.nottingham.ac.uk/ugstudy/subjects/business-economics/",
             "subjects_note": "A-level offer not verified from primary source this pass; IELTS 6.5/6.0",
             "subjects": {"a-level": [], "ib": [], "international-other": []},
             "cost": {"residency": "international", "tuition": 24700, "basis": "institutional",
                 "year": "2027-2028 (proxy)",
                 "mandatory_fees_annual": 0,
                 "note": "£24,700/yr, Nottingham BSc Business Management (2027/28 proxy)."}},
        ],
        "scholarships": [
            {"suffix": "excellence", "name": "International Undergraduate Excellence Scholarship",
             "provider": "University of Nottingham", "provider_type": "institutional",
             "award_type": "fixed_amount", "renewable": False,
             "award_amount": "£5,000 deducted from first-year tuition fees.",
             "academic_criteria": "AAA grades at A-level or international equivalent, assessed at admission.",
             "other_eligibility_criteria": "AUTOMATIC at admission — no separate application required. "
             "International fee-paying students, Year 1 full-time UG at Nottingham UK campus "
             "(BA/BSc/BEng/MEng etc.). Excludes Medicine, Pharmacy, Veterinary Medicine, Architecture, "
             "Foundation Year.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },

    # ── CANADA BATCH (5 universities, Batch-2 slots 26–30) ──────────────────────────────────────
    # country-ca is already published in Sanity staging.
    # Application platforms: OUAC for Ontario schools (Waterloo, McMaster); direct portals for UBC, McGill, Alberta.
    # All Canadian schools: no SAT/ACT required for A-level or IB applicants.
    # decision_context_year: "2026-2027 (Fall 2027 entry)" — applications in 2026-27 for September 2027 start.
    "ca-waterloo": {
        "canonical_name": "University of Waterloo",
        "aliases": ["Waterloo", "UWaterloo", "UW"],
        "country_cc": "ca",
        "city": {"slug": "ca-waterloo-on", "name": "Waterloo"},
        "website": "https://uwaterloo.ca/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "CAD",
        "verification_note": "fact-checks/ca-waterloo-2026-10-25.md",
        "application_platform_name": "OUAC Application",
        "decision_context_year": "2026-2027 (Fall 2027 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "University of Waterloo — Future Students",
                "url": "https://uwaterloo.ca/future-students/",
                "excerpt": "University of Waterloo, Waterloo, Ontario, Canada; public research university. Globally "
                "recognised co-op (cooperative education) programme with mandatory paid work terms integrated into "
                "CS, Engineering, and AFM degrees. Faculty of Mathematics (incl. CS), Faculty of Engineering, "
                "School of Accounting and Finance (AFM), and Faculty of Arts (Economics)."},
            "adm": {"suffix": "src-adm",
                "title": "Computer Science A-Level Admission Requirements — University of Waterloo",
                "url": "https://uwaterloo.ca/future-students/admissions/admission-requirements/computer-science/"
                "high-school/international-system/british-system",
                "excerpt": "A-Level requirements for CS: A Level Mathematics (minimum final grade A); two other "
                "academic A Level courses (minimum final grade A each); English at GCSE, AS, or A Level. "
                "Admission Information Form (AIF) is mandatory for all CS applicants. "
                "Computer Engineering additionally requires A Level Physics (min A) and Chemistry at GCSE (min B/5). "
                "IELTS Academic 6.5 overall (min 6.5 writing and speaking; min 6.0 reading and listening) required "
                "if four most recent years of full-time education were not in English. Application deadline: OUAC "
                "January 31, 2027 for Fall 2027 entry."},
            "fee": {"suffix": "src-fee",
                "title": "Fee Schedule — International Undergraduate Students Fall 2026 — University of Waterloo",
                "url": "https://uwaterloo.ca/finance/fee-schedule-international-undergraduate-students-fall-2026",
                "excerpt": "International UG maximum per-term tuition Fall 2026: Computer Science (Mathematics "
                "faculty) $34,942.00/term; Engineering $34,942.00/term; Accounting and Financial Management "
                "(co-op terms 2A–3B) $27,673.00/term, (terms 4A–4B) $27,029.00/term; Arts (regular) $27,010.00/term. "
                "Figures are maximum tuition per academic term (Fall or Winter). Co-op work terms have a "
                "separate co-op fee of $836 per work term. Student incidental fees ~$665–$1,400/term additional."},
            "schol": {"suffix": "src-schol",
                "title": "International Student Entrance Scholarship — University of Waterloo",
                "url": "https://uwaterloo.ca/future-students/financing/entrance-scholarships",
                "excerpt": "International Student Entrance Scholarship: CAD $10,000 one-time automatic award "
                "for all new international fee-paying students admitted to full-time, first-year degree programs "
                "at Waterloo starting September 2026. No application required — automatically applied in April "
                "via the Waterloo Applicant Portal. Stackable with faculty-specific scholarships."},
        },
        "curricula": [
            ("a-level", "GCE A-Level / IGCSE", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications (CBSE, Canadian equivalent, etc.)."),
        ],
        "residencies": [
            ("international", "International (non-Canadian) students",
             "Students classified as international (non-Canadian citizens/PRs) for fee purposes. "
             "Canadian citizens and permanent residents pay significantly lower domestic tuition (~$10,000–$18,000/yr)."),
        ],
        "cost": None,  # All programmes have per-programme costs below (fees differ by faculty)
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "IELTS 6.5 overall; minimum 6.5 in writing and speaking; minimum 6.0 in reading and listening.",
            "notes": "Required if four most recent years of full-time education were not in English. Also accepts "
            "TOEFL iBT 90 (25 writing and speaking), PTE Academic 63, Duolingo 120. Waterloo A-Level students "
            "with English as a subject may be exempt — confirm with Waterloo admissions."},
        "std_tests": [],  # No SAT/ACT or subject tests required for A-Level/IB applicants at Waterloo
        "deadline_note": "OUAC application deadline: January 31, 2027 for Fall 2027 entry. "
            "CS AND Engineering require completion of the Admission Information Form (AIF) — a mandatory online "
            "questionnaire about academic background, interests, and activities; must be submitted as part of the "
            "OUAC application. No standardised admission tests (SAT/ACT) required for A-Level or IB applicants.",
        "living": None,  # Official Waterloo program living-cost estimate not captured this pass; not fabricated.
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science",
             "degree": "BSc",
             "degree_local": "BSc (Honours) Computer Science, University of Waterloo, Faculty of Mathematics. "
             "5-year co-op programme (alternating academic and 6 paid work terms of 4 months each). "
             "Non-co-op 4-year option also available. Strong focus on algorithms, systems, AI, and theory. "
             "Consistently ranked among top CS programmes globally. AIF and OUAC required.",
             "faculty": "Faculty of Mathematics", "duration": 5,
             "url": "https://uwaterloo.ca/future-students/programs/computer-science",
             "subjects_note": "A Level Mathematics (min A); two other academic A Levels (min A each). "
             "AIF (Admission Information Form) mandatory.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics HL"], "international-other": []},
             "cost": {"residency": "international", "tuition": 69884, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD $69,884/yr (2 academic terms × $34,942/term maximum) for international students "
                 "in the Mathematics faculty (CS category), UWaterloo Fall 2026 fee schedule (primary source). "
                 "Co-op work-term fee ~$836/work term additional. Student incidental fees ~$665–$1,400/term "
                 "additional. Non-co-op stream has same academic-term fee."}},
            {"suffix": "basc-engineering", "program_name": "Engineering", "field": "Engineering",
             "degree": "BASc",
             "degree_local": "BASc (Bachelor of Applied Science) in Engineering, University of Waterloo, "
             "Faculty of Engineering. 5-year co-op programme (mandatory for most Engineering disciplines). "
             "Disciplines: Electrical, Computer, Mechanical, Software, Civil, Chemical, Environmental, "
             "Mechatronics Engineering, Systems Design Engineering. AIF and online interview for some programs.",
             "faculty": "Faculty of Engineering", "duration": 5,
             "url": "https://uwaterloo.ca/future-students/programs?faculty=Engineering",
             "subjects_note": "A Level Mathematics (min A) and A Level Physics (min A); one additional A Level "
             "(min B); Chemistry at GCSE-level (min B/5). AIF mandatory; online interview for selected programs.",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics HL", "Physics HL"],
                          "international-other": []},
             "cost": {"residency": "international", "tuition": 69884, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD $69,884/yr (2 academic terms × $34,942/term maximum) for international students "
                 "in the Engineering faculty, UWaterloo Fall 2026 fee schedule (primary source). "
                 "Co-op fee ~$836/work term additional."}},
            {"suffix": "bafm", "program_name": "Accounting and Financial Management", "field": "Business",
             "degree": "BAcc",
             "degree_local": "BAcc (Honours) Accounting and Financial Management (AFM), University of Waterloo, "
             "School of Accounting and Finance. 5-year co-op programme. Highly selective — direct route to "
             "CPA (Chartered Professional Accountant) and CFA (Chartered Financial Analyst) designations. "
             "Note: Waterloo does NOT offer a traditional undergraduate BBA/Business Administration degree on the "
             "main campus; AFM is the primary business-adjacent programme. Separate double-degree with Wilfrid "
             "Laurier (BBA+BMath) exists but requires separate application to Laurier.",
             "faculty": "School of Accounting and Finance (Faculty of Arts)", "duration": 5,
             "url": "https://uwaterloo.ca/future-students/programs/accounting-and-financial-management",
             "subjects_note": "A-level specific requirements not separately published for AFM; strong Mathematics "
             "expected (AFM is quantitative). Competitive academic average comparable to CS/Engineering required.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 55346, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD $55,346/yr (2 academic terms × $27,673/term for AFM co-op terms 2A–3B) "
                 "for international students in AFM, UWaterloo Fall 2026 fee schedule (primary source). "
                 "Slightly higher than general Arts ($54,020/yr) due to AFM-specific fee category. "
                 "Co-op fee ~$836/work term additional."}},
            {"suffix": "ba-economics", "program_name": "Economics", "field": "Economics",
             "degree": "BA",
             "degree_local": "BA (Honours) Economics, University of Waterloo, Faculty of Arts. "
             "4-year Honours programme (5-year co-op stream available). Covers micro, macro, econometrics, "
             "and mathematical economics. Mathematics-heavy relative to most Arts programmes.",
             "faculty": "Faculty of Arts", "duration": 4,
             "url": "https://uwaterloo.ca/future-students/programs/economics",
             "subjects_note": "A-level specific requirements not separately published for Economics; "
             "Mathematics strongly recommended. Competitive academic average required.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 54020, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD $54,020/yr (2 academic terms × $27,010/term) for international students "
                 "in the Arts faculty, UWaterloo Fall 2026 fee schedule (primary source). "
                 "Economics falls under the general Arts fee category (no Economics-specific surcharge)."}},
        ],
        "scholarships": [
            {"suffix": "ises", "name": "International Student Entrance Scholarship",
             "provider": "University of Waterloo", "provider_type": "institutional",
             "award_type": "fixed_amount", "renewable": False,
             "award_amount": "CAD $10,000 one-time, credited in first year.",
             "academic_criteria": "Admission as a full-time international fee-paying first-year student starting "
             "September 2026 or later. No separate application required.",
             "other_eligibility_criteria": "AUTOMATIC — every eligible international student receives this award. "
             "Applied automatically from mid-April via the Waterloo Applicant Portal. "
             "Stackable with faculty-specific Waterloo scholarships.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },

    "ca-ubc": {
        "canonical_name": "University of British Columbia",
        "aliases": ["UBC"],
        "country_cc": "ca",
        "city": {"slug": "ca-vancouver-bc", "name": "Vancouver"},
        "website": "https://www.ubc.ca/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "CAD",
        "verification_note": "fact-checks/ca-ubc-2026-10-25.md",
        "application_platform_name": "UBC Online Application",
        "decision_context_year": "2026-2027 (Fall 2027 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "University of British Columbia — Undergraduate Admissions",
                "url": "https://you.ubc.ca/",
                "excerpt": "University of British Columbia (Vancouver campus), British Columbia, Canada; "
                "public research university. Programmes: BSc Computer Science (Faculty of Science), "
                "BASc Applied Science/Engineering (Faculty of Applied Science), BCom (Sauder School of Business), "
                "BA Economics (Faculty of Arts). All fees are per credit; international undergraduate rates approved "
                "by the UBC Board of Governors for 2026/27."},
            "adm": {"suffix": "src-adm", "title": "Admission Requirements — University of British Columbia",
                "url": "https://you.ubc.ca/applying-ubc/requirements/",
                "excerpt": "A-Level: standing in at least five academic subject areas incl. English, with at least "
                "three UBC-approved academic A Levels (or six AS Levels). Minimum grades AAA–A*AA for competitive "
                "programmes; English required. Engineering (BASc): A-Level Maths and Physics required; competitive "
                "averages 92–95%. Commerce (BCom Sauder): A-Level Maths required; competitive 93–96%. "
                "IB: minimum 24 points (diploma), at least 3 HL courses; IB Math AA or AI HL required for "
                "Engineering and Commerce. English: IELTS 6.5 overall, no band below 6.0. "
                "UBC requires a Personal Profile (personal statement equivalent) for all applicants — submit "
                "online by January 15, 2027."},
            "fee": {"suffix": "src-fee",
                "title": "Undergraduate Tuition Fees 2026/27 — University of British Columbia",
                "url": "https://students.ubc.ca/finances/tuition-fees/undergraduate-tuition-fees/",
                "excerpt": "2026/27 international undergraduate tuition rates (per credit, Board-approved Dec 2025): "
                "BSc Computer Science (Faculty of Science) $1,769.40/credit (~$53,082/yr for 30 credits); "
                "BASc Applied Science (Engineering) $1,789.18/credit (~$53,675/yr for 30 credits); "
                "BCom Sauder School of Business $2,222.61/credit ($66,678/yr for 30 credits); "
                "BA Economics (Faculty of Arts) $1,717.68/credit (~$51,530/yr for 30 credits). "
                "Tuition guaranteed to increase by no more than 3%/yr for 4 years from start of degree. "
                "Note: actual annual cost may vary with credit load; Engineering typically 30–36 credits/yr."},
            "schol": {"suffix": "src-schol",
                "title": "Scholarships and Awards — International Students — UBC",
                "url": "https://you.ubc.ca/financial-planning/scholarships-awards-international-students/",
                "excerpt": "International Major Entrance Scholarship (IMES): $10,000–$25,000/yr, renewable up to "
                "3 additional years; competitive merit-based; automatic consideration for all applicants who apply "
                "by January 15, 2027 — no separate application required; assessed on academic achievement AND "
                "extracurricular/community involvement. Outstanding International Student Award (OIS): "
                "$10,000–$25,000 one-time; awarded on admission for strong academics and extracurricular record. "
                "UBC devotes over $35 million annually to international undergraduate awards."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications."),
        ],
        "residencies": [
            ("international", "International students (studying on Canadian study permit)",
             "Non-Canadian students on a study permit. Canadian citizens/PRs pay lower domestic tuition rates."),
        ],
        "cost": None,  # All programmes have per-programme costs (fees differ significantly by faculty at UBC)
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "IELTS 6.5 overall; no band below 6.0.",
            "notes": "Only IELTS Academic accepted (not IELTS General, IELTS Indicator, or IELTS One Skill Retake). "
            "Also accepts TOEFL iBT 90, Duolingo 120, or IB Group 1 English grade 5+. UBC A-Level English "
            "may satisfy the requirement — confirm with UBC admissions."},
        "std_tests": [],  # No SAT/ACT required for A-Level/IB applicants
        "deadline_note": "UBC application deadline: January 15, 2027 for Fall 2027 entry (Vancouver campus). "
            "UBC Personal Profile (online personal statement) must be submitted with the application — this is "
            "a key component of the admissions process, not optional. No SAT/ACT required for A-Level/IB applicants.",
        "living": None,  # Official UBC program living-cost estimate not captured this pass; not fabricated.
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science",
             "degree": "BSc",
             "degree_local": "BSc Computer Science, University of British Columbia, Faculty of Science. "
             "4-year programme. Strong research environment; specialisations in AI, machine learning, software "
             "engineering, algorithms, and vision. Top-ranked CS programme in Canada.",
             "faculty": "Faculty of Science", "duration": 4,
             "url": "https://www.cs.ubc.ca/undergraduate/programs/bachelor-of-science-computer-science",
             "subjects_note": "A-Level: three academic A Levels incl. Mathematics; competitive grades AAA–A*AA. "
             "IB: Math AA SL/HL or Math AI HL required; typically 33+ points competitive.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 53082, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD $53,082/yr ($1,769.40/credit × 30 credits) for international students in BSc CS, "
                 "UBC Vancouver, 2026/27 (secondary sources summarising Board-approved rates; UBC fees page "
                 "returned 403 during this verification pass). Actual annual cost varies with credit load. "
                 "3%/yr increase cap guaranteed for 4 years from degree start."}},
            {"suffix": "basc-engineering", "program_name": "Engineering", "field": "Engineering",
             "degree": "BASc",
             "degree_local": "BASc (Bachelor of Applied Science) in Engineering, University of British Columbia, "
             "Faculty of Applied Science. 4-year programme. Disciplines: Electrical, Mechanical, Civil, "
             "Chemical, Computer, Materials, and others. Highly competitive admission.",
             "faculty": "Faculty of Applied Science", "duration": 4,
             "url": "https://apsc.ubc.ca/",
             "subjects_note": "A-Level: Maths and Physics required; typically A*AA competitive. "
             "IB: Math AA or AI HL, Chemistry HL, and Physics HL required; 35+ competitive. "
             "UBC Personal Profile required.",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics HL", "Physics HL"],
                          "international-other": []},
             "cost": {"residency": "international", "tuition": 53675, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD $53,675/yr ($1,789.18/credit × 30 credits) for international students in BASc "
                 "Engineering, UBC Vancouver, 2026/27 (secondary sources summarising Board-approved rates; "
                 "UBC fees page returned 403 during this verification pass). Engineering typically requires "
                 "30–36+ credits/yr in later years — annual cost may be higher. 3%/yr cap guaranteed."}},
            {"suffix": "bcom", "program_name": "Commerce (Sauder)", "field": "Business",
             "degree": "BCom",
             "degree_local": "BCom (Bachelor of Commerce), Sauder School of Business, University of British Columbia. "
             "4-year programme. One of Canada's top business schools. Specialisations: accounting, finance, "
             "marketing, operations, OBHR, and more. Requires UBC Personal Profile.",
             "faculty": "Sauder School of Business", "duration": 4,
             "url": "https://www.sauder.ubc.ca/programs/bcom",
             "subjects_note": "A-Level: Maths required; typically AAA–A*AA competitive. "
             "IB: Math AA SL/HL or Math AI HL required; 35–38+ competitive. "
             "UBC Personal Profile a key admission component.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 66678, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD $66,678/yr ($2,222.61/credit × 30 credits) for international students in BCom, "
                 "Sauder School of Business, UBC Vancouver, 2026/27 (secondary sources summarising Board-approved "
                 "rates). Sauder BCom is priced significantly higher than Science/Arts at UBC. 3%/yr cap guaranteed."}},
            {"suffix": "ba-economics", "program_name": "Economics", "field": "Economics",
             "degree": "BA",
             "degree_local": "BA Economics, University of British Columbia, Faculty of Arts. "
             "4-year programme. Covers micro, macro, econometrics, and economic theory. "
             "Also available: BSc Economics (higher fee, under Science faculty) and "
             "Bachelor of International Economics (separate, higher fee ~$62,338/yr).",
             "faculty": "Faculty of Arts", "duration": 4,
             "url": "https://economics.ubc.ca/programs/undergraduate-programs/",
             "subjects_note": "A-Level: Maths typically required/expected; competitive AAA grades. "
             "IB: Math AA SL/HL or Math AI HL recommended.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 51530, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD $51,530/yr ($1,717.68/credit × 30 credits) for international students in BA "
                 "Economics (Arts faculty), UBC Vancouver, 2026/27 (secondary sources summarising Board-approved "
                 "rates). BA Economics (Arts) is the most affordable of UBC's economics routes. 3%/yr cap guaranteed."}},
        ],
        "scholarships": [
            {"suffix": "imes", "name": "International Major Entrance Scholarship (IMES)",
             "provider": "University of British Columbia", "provider_type": "institutional",
             "award_type": "fixed_amount", "renewable": True,
             "award_amount": "CAD $10,000–$25,000/yr, renewable for up to 3 additional years (4 years total). "
             "Amount within range determined by selection committee.",
             "academic_criteria": "Exceptional academic achievement and intellectual promise. Automatic "
             "consideration for all applicants who submit UBC application by January 15, 2027 — no separate "
             "scholarship application required. Extracurricular and community involvement also assessed.",
             "other_eligibility_criteria": "COMPETITIVE — not guaranteed. Must be new to UBC, entering directly "
             "from secondary school, as an international student on a Canadian study permit. "
             "Renewable if enrolled full-time and maintaining good academic standing.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },

    "ca-mcgill": {
        "canonical_name": "McGill University",
        "aliases": ["McGill"],
        "country_cc": "ca",
        "city": {"slug": "ca-montreal-qc", "name": "Montreal"},
        "website": "https://www.mcgill.ca/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "CAD",
        "verification_note": "fact-checks/ca-mcgill-2026-10-25.md",
        "application_platform_name": "McGill Online Application",
        "decision_context_year": "2026-2027 (Fall 2027 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "McGill University — Undergraduate Admissions",
                "url": "https://www.mcgill.ca/undergraduate-admissions/",
                "excerpt": "McGill University, Montreal, Quebec, Canada; public English-language research university. "
                "Undergraduate programmes: BSc Computer Science (Faculty of Science), BEng (Faculty of Engineering), "
                "BCom (Desautels Faculty of Management), BA Economics (Faculty of Arts). "
                "IMPORTANT: Students studying in Quebec require a Certificat d'acceptation du Québec (CAQ) "
                "in addition to the federal Canadian Study Permit. McGill's international tuition is deregulated "
                "under Quebec provincial policy — fees are significantly higher than domestic/Quebec rates. "
                "Rolling admissions — earlier applications receive earlier decisions."},
            "adm": {"suffix": "src-adm", "title": "A-Level Requirements — McGill University",
                "url": "https://www.mcgill.ca/undergraduate-admissions/apply/requirements/international/advanced-levels",
                "excerpt": "A-Level requirements: minimum three A-Levels in three different subjects (or two A-level "
                "and two AS subjects in three subjects). Admission is competitive; meeting minimum does NOT guarantee "
                "admission. Engineering: A-Level Maths and Sciences expected; competitive A*A*A–A*AA. "
                "Management (BCom): A-Level Maths expected; competitive A*AA–AAA. "
                "IB: 34–38+ points; no subject grade below 5; HL Maths required for Engineering and Management. "
                "English: IELTS 6.5 overall (min 6.0 each band) for most programmes; "
                "Management requires IELTS 7.0 (min 6.5 each band). "
                "McGill processes applications on a rolling basis — apply early for best consideration."},
            "fee": {"suffix": "src-fee",
                "title": "International Tuition and Fees 2026-27 — McGill University",
                "url": "https://www.mcgill.ca/student-accounts/files/student-accounts/"
                "new_intl_ugrad_degree_students_admitted_2026-27_0.pdf",
                "excerpt": "McGill 2026-27 international undergraduate annual tuition (PDF; figures from secondary "
                "sources summarising official McGill 2026-27 fee schedule — PDF was binary-compressed and could "
                "not be directly read during this verification pass; cross-checked across multiple independent "
                "sources citing the McGill fee tables): BSc (Science, incl. CS) ~CAD $64,786/yr; "
                "BEng (Engineering) CAD $65,167.50/yr; BCom (Management/Desautels) CAD $71,687.40/yr; "
                "BA (Arts, incl. Economics) ~CAD $54,000/yr. McGill offers GUARANTEED tuition rates — the "
                "rate set at admission applies for the full degree (no increases while enrolled). "
                "Note: CONFIDENCE IS MEDIUM — primary source PDF not directly readable; figures from "
                "secondary sources summarising official McGill document. Verify from mcgill.ca before go-live."},
            "schol": {"suffix": "src-schol",
                "title": "Entrance Scholarships for Future Undergraduates — McGill",
                "url": "https://www.mcgill.ca/studentaid/scholarships-aid/future-undergrads/entrance-scholarships",
                "excerpt": "McGill entrance scholarships for international undergraduate students: "
                "(1) Basic Entrance Award: $3,000 one-time, automatic based on top-percentile high school "
                "transcripts — no separate application required. "
                "(2) Major Entrance Scholarship: $3,000–$12,000/yr renewable up to 4 years (total $12,000–$48,000); "
                "competitive merit-based; requires separate scholarship application; rolling consideration."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications."),
        ],
        "residencies": [
            ("international", "International (non-Canadian) students",
             "Students classified as international (non-Quebec residents) under Quebec's deregulated tuition model. "
             "Quebec-resident and Canadian out-of-province rates are significantly lower. "
             "All international students studying in Quebec must also obtain a CAQ "
             "(Certificat d'acceptation du Québec) in addition to the federal Canadian Study Permit."),
        ],
        "cost": None,  # Per-programme costs below (significant fee variation by faculty at McGill)
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "IELTS 6.5 overall; minimum 6.0 in each band. Management (BCom Desautels): "
            "IELTS 7.0 overall; minimum 6.5 in each band.",
            "notes": "Also accepts TOEFL iBT 90, Cambridge C1 Advanced, and other tests. "
            "Tests submitted electronically only (paper TRFs not accepted). "
            "IELTS One Skill Retake not accepted. IB Group 1 English grade 5 may satisfy requirement."},
        "std_tests": [],  # No SAT/ACT required for A-Level/IB applicants at McGill
        "deadline_note": "McGill application deadline: approximately January 15, 2027 for Fall 2027 entry. "
            "Rolling admissions — earlier applications receive earlier decisions and better scholarship consideration. "
            "IMPORTANT: International students in Quebec require a CAQ (Certificat d'acceptation du Québec) "
            "in addition to the Canadian Study Permit. CAQ application must be submitted to the Quebec government "
            "after receiving a McGill conditional offer. No SAT/ACT required for A-Level/IB applicants.",
        "living": None,  # Official McGill program living-cost estimate not captured this pass; not fabricated.
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science",
             "degree": "BSc",
             "degree_local": "BSc Computer Science, McGill University, Faculty of Science. "
             "3-year Major or 3/4-year Honours programme. Joint Honours with Mathematics and Statistics available. "
             "Top-ranked CS programme; strong research output in AI and machine learning.",
             "faculty": "School of Computer Science (Faculty of Science)", "duration": 3,
             "url": "https://www.cs.mcgill.ca/academic/undergraduate/",
             "subjects_note": "A-Level: three A-Levels with competitive grades; Mathematics and Science subjects "
             "expected. IB: 34–38+ points with HL Maths; no subject below 5.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics HL"], "international-other": []},
             "cost": {"residency": "international", "tuition": 64786, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD ~$64,786/yr for international students in BSc (Science faculty), McGill, 2026-27. "
                 "SOURCE CONFIDENCE: MEDIUM — figures from secondary sources summarising official McGill 2026-27 "
                 "fees PDF (PDF was binary-compressed and could not be directly read this pass). Cross-checked "
                 "across multiple independent sources. Verify from mcgill.ca/student-accounts before go-live. "
                 "McGill guarantees this rate for the full degree duration (no annual increases)."}},
            {"suffix": "beng", "program_name": "Engineering", "field": "Engineering",
             "degree": "BEng",
             "degree_local": "BEng (Bachelor of Engineering), McGill University, Faculty of Engineering. "
             "4-year programme. Disciplines: Electrical, Mechanical, Civil, Chemical, Computer, Software, "
             "Biomedical, and Mining Engineering. Research-intensive with strong industry connections.",
             "faculty": "Faculty of Engineering", "duration": 4,
             "url": "https://www.mcgill.ca/engineering/future-students/undergraduate/",
             "subjects_note": "A-Level: Maths and Physics/Chemistry expected; competitive A*A*A–A*AA. "
             "IB: 34–40+ points with HL Maths and Sciences; no subject below 5.",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics HL", "Physics HL"],
                          "international-other": []},
             "cost": {"residency": "international", "tuition": 65168, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD $65,167.50/yr for international students in BEng, McGill, 2026-27. "
                 "SOURCE CONFIDENCE: MEDIUM — consistent across multiple secondary sources summarising McGill's "
                 "official 2026-27 fees PDF. Verify from mcgill.ca/student-accounts before go-live. "
                 "McGill guarantees this rate for the full degree."}},
            {"suffix": "bcom", "program_name": "Commerce (Desautels)", "field": "Business",
             "degree": "BCom",
             "degree_local": "BCom (Bachelor of Commerce), Desautels Faculty of Management, McGill University. "
             "3-year programme (full-time). One of Canada's top business schools. Concentrations: accounting, "
             "finance, international business, marketing, information systems, and more.",
             "faculty": "Desautels Faculty of Management", "duration": 3,
             "url": "https://www.mcgill.ca/desautels/undergraduate",
             "subjects_note": "A-Level: Maths expected; competitive A*AA–AAA. "
             "IB: HL Maths required; 35–38+ points competitive.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics HL"], "international-other": []},
             "cost": {"residency": "international", "tuition": 71687, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD $71,687.40/yr for international students in BCom, Desautels Faculty of Management, "
                 "McGill, 2026-27. SOURCE CONFIDENCE: MEDIUM — consistent across multiple secondary sources "
                 "summarising McGill's official fees PDF. Highest faculty rate at McGill for UG. "
                 "IELTS 7.0/6.5 required for Management (higher than general McGill threshold). "
                 "Verify from mcgill.ca/student-accounts before go-live."}},
            {"suffix": "ba-economics", "program_name": "Economics", "field": "Economics",
             "degree": "BA",
             "degree_local": "BA Economics, McGill University, Faculty of Arts. "
             "3-year programme (Major) or 4-year Honours. Covers micro, macro, econometrics, and policy. "
             "Joint Honours with Mathematics and Political Science available.",
             "faculty": "Faculty of Arts", "duration": 3,
             "url": "https://www.mcgill.ca/economics/undergraduate",
             "subjects_note": "A-Level: three A-Levels; Mathematics expected for Economics. Competitive grades.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 54000, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD ~$54,000/yr for international students in BA (Arts faculty), McGill, 2026-27. "
                 "SOURCE CONFIDENCE: MEDIUM — figures from secondary sources summarising official McGill 2026-27 "
                 "fees PDF. Arts faculty fee is significantly lower than Science/Engineering/Management at McGill. "
                 "Verify from mcgill.ca/student-accounts before go-live."}},
        ],
        "scholarships": [
            {"suffix": "basic-entrance", "name": "McGill Basic Entrance Award",
             "provider": "McGill University", "provider_type": "institutional",
             "award_type": "fixed_amount", "renewable": False,
             "award_amount": "CAD $3,000 one-time (non-renewable).",
             "academic_criteria": "Top-percentile high school academic record at admission. "
             "No separate application required — automatic consideration at admission.",
             "other_eligibility_criteria": "AUTOMATIC — awarded to qualifying new undergraduates at admission "
             "based on academic transcript. International students eligible.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
            {"suffix": "major-entrance", "name": "McGill Major Entrance Scholarship",
             "provider": "McGill University", "provider_type": "institutional",
             "award_type": "fixed_amount", "renewable": True,
             "award_amount": "CAD $3,000–$12,000/yr, renewable for up to 4 years (total $12,000–$48,000).",
             "academic_criteria": "Exceptional academic merit and achievement. Requires a separate scholarship "
             "application — not automatically awarded at admission.",
             "other_eligibility_criteria": "COMPETITIVE — requires separate application. Available to international "
             "students. Rolling consideration — apply as early as possible alongside admissions application. "
             "Renewal requires maintaining satisfactory academic standing.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },

    "ca-mcmaster": {
        "canonical_name": "McMaster University",
        "aliases": ["McMaster"],
        "country_cc": "ca",
        "city": {"slug": "ca-hamilton-on", "name": "Hamilton"},
        "website": "https://www.mcmaster.ca/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "CAD",
        "verification_note": "fact-checks/ca-mcmaster-2026-10-25.md",
        "application_platform_name": "OUAC Application",
        "decision_context_year": "2026-2027 (Fall 2027 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "McMaster University — Future Students",
                "url": "https://future.mcmaster.ca/",
                "excerpt": "McMaster University, Hamilton, Ontario, Canada; public research university. "
                "Programmes: BSc/BASc Computer Science (Faculty of Science), BEng Engineering (Faculty of "
                "Engineering), BCom (DeGroote School of Business), BA Social Sciences (Economics). "
                "Known for problem-based learning and health sciences. OUAC application for Ontario universities."},
            "adm": {"suffix": "src-adm", "title": "International Admission Requirements — McMaster University",
                "url": "https://future.mcmaster.ca/apply/curriculum-requirements/",
                "excerpt": "A-Level requirements: minimum three A-Levels; competitive grades typically A*AA–AAA "
                "depending on programme. Engineering and CS require A-Level Mathematics; Engineering also "
                "requires Physics. IB: 30–38+ points; HL Mathematics required for Engineering and CS. "
                "English: IELTS 6.5 overall (no band below 6.0). TOEFL iBT 80 also accepted. "
                "Application deadline: OUAC January 31, 2027 for Fall 2027 entry."},
            "fee": {"suffix": "src-fee", "title": "Undergraduate Fees — McMaster University",
                "url": "https://registrar.mcmaster.ca/fees/undergraduate/",
                "excerpt": "McMaster 2026-27 international undergraduate full-year tuition estimates "
                "(from McMaster's official cost estimator for Level I students; exact published fee schedule "
                "requires SharePoint access — figures are from the McMaster cost estimator tool and should be "
                "treated as approximate/unofficial until confirmed from the published schedule): "
                "Engineering I CAD $69,353.54; Computer Science CAD $56,232.60; "
                "Business (DeGroote) CAD $50,003.40; Social Sciences (incl. Economics) CAD $45,158.40. "
                "SOURCE CONFIDENCE: LOW-MEDIUM — cost estimator figures, not from the published fee schedule PDF. "
                "Verify from registrar.mcmaster.ca before go-live."},
            "schol": {"suffix": "src-schol",
                "title": "International Undergraduate Entrance Awards — McMaster University",
                "url": "https://future.mcmaster.ca/internationalawards/",
                "excerpt": "McMaster international undergraduate entrance awards by faculty (all AUTOMATIC, "
                "no separate application required): Engineering and CS: $10,000 CAD one-time (Level 1). "
                "DeGroote Business: tiered automatic awards — Scholars ($15,000 + $5,000/yr × 3 for <90% avg), "
                "Distinction ($20,000 + $10,000/yr × 3 for 90–95% avg), Dean's Global Excellence "
                "($25,000 + $20,000/yr × 3 for ≥95% avg). Social Sciences/Humanities: $10,000 (Level 1) + "
                "$5,000/yr × 3 renewal for ≥85% avg. Award of Excellence: up to $200,000 over 4 years, "
                "competitive with application required; deadline February 2027."},
        },
        "curricula": [
            ("a-level", "GCE A-Level", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications."),
        ],
        "residencies": [
            ("international", "International (non-Canadian) students",
             "Students classified as international for fee purposes. Canadian citizens/PRs pay domestic rates."),
        ],
        "cost": None,  # All programmes have per-programme costs below
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "IELTS 6.5 overall; no band below 6.0.",
            "notes": "Also accepts TOEFL iBT 80–90. McMaster may waive the language requirement for applicants "
            "educated entirely in English for four years at secondary level."},
        "std_tests": [],  # No SAT/ACT required for A-Level/IB applicants at McMaster
        "deadline_note": "OUAC application deadline: January 31, 2027 for Fall 2027 entry. "
            "No standardised admission tests (SAT/ACT) required for A-Level or IB applicants. "
            "DeGroote Business (BCom) is directly competitive and may require supplemental materials.",
        "living": None,  # Official McMaster program living-cost estimate not captured this pass; not fabricated.
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science",
             "degree": "BSc",
             "degree_local": "BSc Computer Science, McMaster University, Faculty of Science. "
             "4-year programme. Covers algorithms, systems, AI, data science, and software engineering. "
             "Problem-based learning pedagogy distinctive to McMaster.",
             "faculty": "Faculty of Science", "duration": 4,
             "url": "https://www.eng.mcmaster.ca/cas/",
             "subjects_note": "A-Level: Mathematics required; typically AAA–A*AA competitive. "
             "IB: HL Mathematics; 35+ competitive.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics HL"], "international-other": []},
             "cost": {"residency": "international", "tuition": 56233, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD ~$56,233/yr for international students in BSc CS, McMaster, 2026-27. "
                 "SOURCE CONFIDENCE: LOW-MEDIUM — from McMaster's cost estimator tool (unofficial). "
                 "Published fee schedule requires SharePoint access. Verify from registrar.mcmaster.ca before go-live."}},
            {"suffix": "beng", "program_name": "Engineering", "field": "Engineering",
             "degree": "BEng",
             "degree_local": "BEng (Bachelor of Engineering), McMaster University, Faculty of Engineering. "
             "4-year programme. Disciplines: Electrical, Mechanical, Civil, Chemical, Materials, "
             "iBioMed Engineering. Co-op streams available.",
             "faculty": "Faculty of Engineering", "duration": 4,
             "url": "https://www.eng.mcmaster.ca/future-students/future-undergraduate-students/",
             "subjects_note": "A-Level: Mathematics and Physics required; typically A*AA–AAA. "
             "IB: HL Mathematics and Physics; 35–38 competitive.",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics HL", "Physics HL"],
                          "international-other": []},
             "cost": {"residency": "international", "tuition": 69354, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD ~$69,354/yr for international students in BEng, McMaster, 2026-27. "
                 "SOURCE CONFIDENCE: LOW-MEDIUM — from McMaster's cost estimator tool (unofficial). "
                 "Engineering I is the highest-cost programme at McMaster. Verify before go-live."}},
            {"suffix": "bcom", "program_name": "Commerce (DeGroote)", "field": "Business",
             "degree": "BCom",
             "degree_local": "BCom (Bachelor of Commerce), DeGroote School of Business, McMaster University. "
             "4-year programme. One of Canada's prominent business schools. Streams: accounting, finance, "
             "marketing, human resources, information systems, and entrepreneurship.",
             "faculty": "DeGroote School of Business", "duration": 4,
             "url": "https://business.mcmaster.ca/undergraduate/",
             "subjects_note": "A-Level: competitive grades; Mathematics expected. "
             "IB: 30–35 competitive. Strong extracurriculars recommended.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 50003, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD ~$50,003/yr for international students in BCom (DeGroote), McMaster, 2026-27. "
                 "SOURCE CONFIDENCE: LOW-MEDIUM — from McMaster's cost estimator tool (unofficial). "
                 "Verify from registrar.mcmaster.ca before go-live. Note DeGroote has generous automatic tiered "
                 "scholarships for high-achieving international students."}},
            {"suffix": "ba-economics", "program_name": "Economics", "field": "Economics",
             "degree": "BA",
             "degree_local": "BA Economics, McMaster University, Faculty of Social Sciences. "
             "4-year Honours programme. Covers micro, macro, econometrics, and economic policy. "
             "McMaster's Economics department is research-active with health economics specialisation.",
             "faculty": "Faculty of Social Sciences", "duration": 4,
             "url": "https://socialsciences.mcmaster.ca/economics/",
             "subjects_note": "A-Level: competitive grades; Mathematics expected. IB: 30–35 competitive.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 45158, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD ~$45,158/yr for international students in BA Economics (Social Sciences), "
                 "McMaster, 2026-27. SOURCE CONFIDENCE: LOW-MEDIUM — from McMaster's cost estimator tool "
                 "(unofficial). Verify from registrar.mcmaster.ca before go-live."}},
        ],
        "scholarships": [
            {"suffix": "cs-entrance", "name": "Computer Science International Entrance Award",
             "provider": "McMaster University (Faculty of Science)", "provider_type": "institutional",
             "award_type": "fixed_amount", "renewable": False,
             "award_amount": "CAD $10,000 one-time (Level 1).",
             "academic_criteria": "Admission as a Level 1 international student in Computer Science.",
             "other_eligibility_criteria": "AUTOMATIC — no separate application. Awarded at admission.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
            {"suffix": "eng-entrance", "name": "Engineering International Entrance Award",
             "provider": "McMaster University (Faculty of Engineering)", "provider_type": "institutional",
             "award_type": "fixed_amount", "renewable": False,
             "award_amount": "CAD $10,000 one-time (Level 1).",
             "academic_criteria": "Admission as a Level 1 international student in Engineering.",
             "other_eligibility_criteria": "AUTOMATIC — no separate application. Awarded at admission.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
            {"suffix": "degroote-auto", "name": "DeGroote International Merit Award (tiered)",
             "provider": "DeGroote School of Business, McMaster University", "provider_type": "institutional",
             "award_type": "fixed_amount", "renewable": True,
             "award_amount": "Tiered by admission average: < 90% avg → $15,000 (Year 1) + $5,000/yr × 3; "
             "90–94.99% → $20,000 (Year 1) + $10,000/yr × 3; ≥ 95% → $25,000 (Year 1) + $20,000/yr × 3. "
             "(Amounts in CAD; renewal each year in good standing.)",
             "academic_criteria": "Assessed at admission based on admission average. Enrolled in DeGroote BCom.",
             "other_eligibility_criteria": "AUTOMATIC — no separate application. Tiered by admission average. "
             "Renewal requires continued full-time BCom enrolment in good standing.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
            {"suffix": "social-sci-auto", "name": "Social Sciences International Scholars Award",
             "provider": "McMaster University (Faculty of Social Sciences)", "provider_type": "institutional",
             "award_type": "fixed_amount", "renewable": True,
             "award_amount": "CAD $10,000 (Level 1) + $5,000/yr renewable for Levels 2–4 (≥ 85% avg required). "
             "Total up to CAD $25,000 over four years.",
             "academic_criteria": "Admission average ≥ 85% in Social Sciences Honours programme.",
             "other_eligibility_criteria": "AUTOMATIC — no separate application. Renewal requires ≥ 85% average "
             "and full-time Honours enrolment. Applies to Economics (Social Sciences faculty).",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },

    "ca-alberta": {
        "canonical_name": "University of Alberta",
        "aliases": ["UAlberta", "U of A"],
        "country_cc": "ca",
        "city": {"slug": "ca-edmonton-ab", "name": "Edmonton"},
        "website": "https://www.ualberta.ca/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "CAD",
        "verification_note": "fact-checks/ca-alberta-2026-10-25.md",
        "application_platform_name": "UAlberta Online Application",
        "decision_context_year": "2026-2027 (Fall 2027 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "University of Alberta — International Admissions",
                "url": "https://www.ualberta.ca/en/admissions/",
                "excerpt": "University of Alberta, Edmonton, Alberta, Canada; public research university and "
                "member of the U15 Group of Canadian Research Universities. Programmes: BSc Computing Science "
                "(Faculty of Science), BASc Engineering (Faculty of Engineering), BCom (Alberta School of Business), "
                "BA Economics (Faculty of Arts). DISTINCTIVE FEATURE: international undergraduate students receive "
                "a guaranteed tuition rate in their offer letter valid for the full degree duration plus one year — "
                "fees do not increase after admission. Edmonton provides affordable cost of living relative to "
                "Toronto/Vancouver."},
            "adm": {"suffix": "src-adm",
                "title": "Admission Requirements — University of Alberta",
                "url": "https://www.ualberta.ca/en/admissions/how-to-apply/ib-students/index.html",
                "excerpt": "A-Level requirements: competitive grades typically AAB–AAA depending on programme; "
                "minimum BBC for most faculties. Engineering and Computing Science require Mathematics. "
                "IB: minimum 30–37 points; competitive scores 34–37 for STEM; no individual subject grade below 4. "
                "English: IELTS 6.5 overall (no band below 6.0). IB English A grade 5 satisfies the requirement. "
                "Application deadline: March 1, 2027 for Fall 2027 entry (later than Ontario schools). "
                "Scholarship application deadline: January 10, 2027."},
            "fee": {"suffix": "src-fee",
                "title": "International Undergraduate Tuition — University of Alberta",
                "url": "https://www.ualberta.ca/en/registrar/costs-tuition-fees/undergraduate-tuition/"
                "spring-summer-tuition-for-international-students-fall.html",
                "excerpt": "Fall 2026 annual international undergraduate tuition rates cited from UAlberta search "
                "results (secondary sources summarising ualberta.ca data; direct fee page redirects to cost "
                "calculator — primary source confirmation recommended): Faculty of Engineering $49,952.40/yr; "
                "Alberta School of Business (Commerce) $46,546.80/yr; Faculty of Science (Computing Science) "
                "$39,792.00/yr. Faculty of Arts (Economics) annual rate not separately confirmed — estimated "
                "similar to or slightly below Science; stored as null pending primary-source verification. "
                "TUITION GUARANTEE: rate fixed in offer letter for full degree duration + 1 year. "
                "PROPOSED CHANGE (Fall 2027 entry): BSc Computing Science fee proposed to harmonise with "
                "Engineering (~26% increase) — Fall 2026 students locked at $39,792."},
            "schol": {"suffix": "src-schol",
                "title": "International Undergraduate Scholarships — University of Alberta",
                "url": "https://www.ualberta.ca/en/admissions/tuition-and-scholarships/scholarships.html",
                "excerpt": "Automatic entrance scholarships (no application required, assessed at admission): "
                "International Admission Scholarship up to CAD $10,000. Application-based awards (deadline "
                "January 10, 2027): President's International Distinction Scholarship CAD $120,000 over 4 years "
                "(top 5–10 students annually); International Leader Scholarship CAD $15,000 (community service "
                "required). Over CAD $52 million awarded annually; 1 in 5 first-year students receives a scholarship."},
        },
        "curricula": [
            ("a-level", "GCE A-Level / IGCSE", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma Programme."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications (CBSE, etc.)."),
        ],
        "residencies": [
            ("international", "International (non-Canadian) students",
             "Students classified as international for fee purposes. TUITION GUARANTEE: rate fixed in offer "
             "letter for full degree duration + 1 year — no annual increases after admission."),
        ],
        "cost": None,  # Per-programme costs below; Economics/Arts fee stored as null (not confirmed)
        "lang_req": {"test_name": "IELTS Academic (or accepted equivalent)",
            "min_score": "IELTS 6.5 overall; no band below 6.0.",
            "notes": "Also accepts TOEFL iBT 90. IB English A grade 5 satisfies the requirement. "
            "Some programmes may have higher requirements — confirm with UAlberta admissions."},
        "std_tests": [],  # No SAT/ACT required for A-Level/IB applicants at Alberta
        "deadline_note": "UAlberta application deadline: March 1, 2027 for Fall 2027 entry "
            "(later than Ontario schools; OUAC not used). Application-based scholarship deadline: January 10, 2027 "
            "(earlier than general admission deadline). No SAT/ACT required for A-Level or IB applicants. "
            "Tuition guarantee valid for program duration + 1 year from admission offer.",
        "living": None,  # Official UAlberta program living-cost estimate not captured this pass; not fabricated.
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computing Science", "field": "Computer Science",
             "degree": "BSc",
             "degree_local": "BSc Computing Science, University of Alberta, Faculty of Science. "
             "4-year programme. Strong research in AI, machine learning, and game theory. "
             "Note: For Fall 2027 entry, a proposed 26% fee increase is under review to harmonise CS with "
             "Engineering tuition — students admitted Fall 2026 are locked at the lower $39,792 rate.",
             "faculty": "Faculty of Science (Computing Science)", "duration": 4,
             "url": "https://www.ualberta.ca/en/computing-science/undergraduate/",
             "subjects_note": "A-Level: Mathematics required; competitive AAB–AAA. "
             "IB: HL Mathematics; 32–37 competitive.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics HL"], "international-other": []},
             "cost": {"residency": "international", "tuition": 39792, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD $39,792/yr for international students in BSc Computing Science, UAlberta, "
                 "Fall 2026 (cited from secondary sources summarising ualberta.ca search results; direct fee "
                 "page redirects to cost calculator). Tuition GUARANTEED at this rate for program duration + 1 yr. "
                 "For Fall 2027 entry, ~$50,000 rate proposed (26% harmonisation increase). Verify from ualberta.ca."}},
            {"suffix": "basc-engineering", "program_name": "Engineering", "field": "Engineering",
             "degree": "BASc",
             "degree_local": "BASc (Bachelor of Applied Science) in Engineering, University of Alberta, "
             "Faculty of Engineering. 4-year programme. Disciplines: Civil, Mechanical, Electrical, Chemical, "
             "Computing, Petroleum, Materials, Mining, and Geotechnical Engineering.",
             "faculty": "Faculty of Engineering", "duration": 4,
             "url": "https://www.ualberta.ca/en/engineering/undergraduate/",
             "subjects_note": "A-Level: Mathematics required; Physics strongly recommended; competitive AAB–AAA. "
             "IB: HL Mathematics and Physics; 34–37 competitive.",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics HL", "Physics HL"],
                          "international-other": []},
             "cost": {"residency": "international", "tuition": 49952, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD $49,952.40/yr for international students in Engineering, UAlberta, Fall 2026 "
                 "(from secondary sources summarising ualberta.ca data; consistent across sources). "
                 "Tuition GUARANTEED at this rate for program duration + 1 year. Verify from ualberta.ca."}},
            {"suffix": "bcom", "program_name": "Commerce (Alberta School of Business)", "field": "Business",
             "degree": "BCom",
             "degree_local": "BCom (Bachelor of Commerce), Alberta School of Business, University of Alberta. "
             "4-year programme. One of Canada's largest and most well-established business schools. "
             "Majors: accounting, finance, marketing, operations, strategy, and MIS.",
             "faculty": "Alberta School of Business", "duration": 4,
             "url": "https://www.ualberta.ca/en/business/programs/undergraduate/",
             "subjects_note": "A-Level: competitive grades; Mathematics expected. IB: 30–34 competitive.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 46547, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "CAD $46,546.80/yr for international students in BCom (Alberta School of Business), "
                 "UAlberta, Fall 2026 (from secondary sources summarising ualberta.ca data). "
                 "Tuition GUARANTEED at this rate for program duration + 1 year. Verify from ualberta.ca."}},
            {"suffix": "ba-economics", "program_name": "Economics", "field": "Economics",
             "degree": "BA",
             "degree_local": "BA Economics, University of Alberta, Faculty of Arts. "
             "4-year programme. Covers micro, macro, econometrics, and applied policy. "
             "Also available as BSc Economics with quantitative/science focus.",
             "faculty": "Faculty of Arts", "duration": 4,
             "url": "https://www.ualberta.ca/en/economics/undergraduate/",
             "subjects_note": "A-Level: Mathematics expected; competitive AAB–AAA. IB: 30–34 competitive.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": None, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "Economics annual fee (Arts faculty) NOT CONFIRMED from primary source — UAlberta direct "
                 "fee page redirects to cost calculator and no Arts-specific annual figure was confirmed in this "
                 "pass. Likely similar to or slightly below Science (~$39,000–$40,000/yr based on faculty "
                 "structure). DO NOT display to students; verify from ualberta.ca before go-live."}},
        ],
        "scholarships": [
            {"suffix": "intl-admission", "name": "International Admission Scholarship",
             "provider": "University of Alberta", "provider_type": "institutional",
             "award_type": "fixed_amount", "renewable": False,
             "award_amount": "Up to CAD $10,000 (one-time).",
             "academic_criteria": "Assessed at admission based on high school admission average. "
             "No separate scholarship application required.",
             "other_eligibility_criteria": "AUTOMATIC — assessed at admission. International fee-paying students. "
             "Amount within the 'up to $10,000' range depends on admission average.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
            {"suffix": "presidents-distinction", "name": "President's International Distinction Scholarship",
             "provider": "University of Alberta", "provider_type": "institutional",
             "award_type": "fixed_amount", "renewable": True,
             "award_amount": "CAD $120,000 over 4 years ($30,000/yr), renewable annually in good standing.",
             "academic_criteria": "Top-performing new international undergraduate students (typically top 5–10 "
             "students per year). Competitive application required.",
             "other_eligibility_criteria": "COMPETITIVE — application required by January 10, 2027. "
             "Outstanding academic record and demonstrated leadership/community service. "
             "Very limited number of awards.",
             "application_deadline": "2027-01-10", "deadline_academic_year": "2026-2027"},
        ],
    },

    # ── GERMANY BATCH (5 universities, Batch-2 slots 36–40) ─────────────────────────────────────
    # country-de is already published in Sanity staging.
    # CRITICAL: All 5 German universities teach Bachelor programmes PRIMARILY in German.
    # Exception: KIT Carl Benz School BSc Mechanical Engineering International is English-medium.
    # Primary language requirement = German C1 (TestDaF TDN 4-4-4-4 or DSH-2) — NOT English.
    # Application platform: uni-assist.de (VPD document) for most; Carl Benz has own KIT portal.
    # Standard deadline: July 15 for Winter Semester 2027/28. Carl Benz: April 30.
    # Fee tiers:
    #   Baden-Württemberg state law: Heidelberg + KIT charge €1,500/semester non-EU tuition.
    #   NRW (RWTH) + Berlin (TU Berlin) + Bavaria-LMU: FREE for non-EU, semester contribution only.
    #   LMU Munich confirmed NO non-EU tuition despite Bavaria's 2024/25 fee introduction (TUM only).
    # decision_context_year: "2026-2027 (Winter Semester 2027/28 entry)".
    # build_docs changes applied: lang_req["language"], lang_req["req_name"], per-programme lang_instruction.

    "de-rwth-aachen": {
        "canonical_name": "RWTH Aachen University",
        "aliases": ["RWTH", "RWTH Aachen", "Rheinisch-Westfälische Technische Hochschule Aachen"],
        "country_cc": "de",
        "city": {"slug": "de-aachen", "name": "Aachen"},
        "website": "https://www.rwth-aachen.de/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "EUR",
        "verification_note": "fact-checks/de-rwth-aachen-2026-10-25.md",
        "application_platform_name": "uni-assist + RWTH Application Portal",
        "decision_context_year": "2026-2027 (Winter Semester 2027/28 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "RWTH Aachen University — Official Website",
                "url": "https://www.rwth-aachen.de/",
                "excerpt": "RWTH Aachen University, Aachen, North Rhine-Westphalia, Germany; public technical "
                "university. Faculties include: Mathematics/Computer Science/Natural Sciences (Faculty 1), "
                "Mechanical Engineering (Faculty 4), and Business and Economics (Faculty 8). Tuition-free for "
                "all students (EU and non-EU); semester contribution ~€358/semester (2026) applies. NRW state "
                "does not impose non-EU tuition fees."},
            "adm": {"suffix": "src-adm",
                "title": "RWTH Aachen — International Admission Requirements",
                "url": "https://www.rwth-aachen.de/cms/root/studium/vor-dem-studium/"
                "internationale-studieninteressierte/organisation-des-studienaufenthaltes/"
                "~bqmn/internationale-studierende/?lidx=1",
                "excerpt": "International students apply via uni-assist for Vorprüfungsdokumentation (VPD / "
                "preliminary review document). German C1 proficiency required: TestDaF TDN 4 in all four "
                "sections or DSH-2. A-level qualifications assessed via Anabin database by uni-assist; at "
                "least three A-level subjects including Mathematics for CS/Engineering. Application deadline "
                "for Winter Semester: July 15. BSc Computer Science is admission-restricted (NC); ~8–10% of "
                "places reserved for international students."},
            "fee": {"suffix": "src-fee",
                "title": "RWTH Aachen — Semester Contributions",
                "url": "https://www.rwth-aachen.de/cms/root/studium/Im-Studium/~blsb/Semesterbeitraege/?lidx=1",
                "excerpt": "Semester contribution (Summer Semester 2026): €358.34 total = student body "
                "contribution €13.77 + Semesterticket (Deutschlandticket/NRW) €216.57 + Studierendenwerk "
                "€128.00. No tuition fees for any Bachelor or consecutive Master programme — identical for "
                "EU and non-EU students. Annual cost two semesters: approximately €716."},
            "schol": {"suffix": "src-schol",
                "title": "RWTH Aachen — Deutschlandstipendium",
                "url": "https://www.rwth-aachen.de/cms/root/transfer/spenden-sponsoring/"
                "deutschlandstipendium/~emd/bewerben/?lidx=1",
                "excerpt": "Deutschlandstipendium at RWTH: €300/month for at least two semesters, renewable. "
                "Funded 50% by Federal Ministry of Education and Research, 50% by private sponsors. Open to "
                "all nationalities enrolled or newly enrolling at RWTH. Next application period: June 2027 "
                "for WS 2027/28. Selection on academic merit, talent, engagement. Not automatic."},
        },
        "curricula": [
            ("a-level", "GCE A-Level / IGCSE", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications assessed via uni-assist."),
        ],
        "residencies": [
            ("international", "International (non-EU/non-German) students",
             "Students from outside the EU/EEA. RWTH charges NO separate non-EU tuition — all students pay "
             "the same semester contribution (~€358/semester). Fees are purely administrative/service-based."),
        ],
        "cost": None,
        "lang_req": {
            "language": "German",
            "req_name": "German language proficiency (C1)",
            "test_name": "TestDaF or DSH (German C1 proficiency)",
            "min_score": "TestDaF: TDN 4 in each of 4 sections (Lesen, Hören, Schreiben, Sprechen — TDN 4-4-4-4). "
                         "Alternatively: DSH-2 or DSH-3.",
            "notes": "All RWTH Bachelor programmes are taught in German. German C1 is the primary language "
                     "requirement — English proficiency is not separately tested (A-levels/IB demonstrate "
                     "English competency). UAE students typically need 1–2 years of dedicated German study to "
                     "reach C1 from A2 level. TestDaF test centres are available in the UAE and worldwide. "
                     "Note: Kombiniertes Zertifikat digitaler TestDaF is NOT accepted by some universities — "
                     "check RWTH's current accepted certificates list before registering.",
        },
        "std_tests": [],
        "deadline_note": "Apply via uni-assist.de well before the deadline — VPD processing takes several weeks. "
            "Winter Semester 2027/28 deadline: July 15, 2027 (some NC programmes may have earlier cut-offs). "
            "After receiving VPD, submit to RWTH's online application portal. German TestDaF/DSH certificate "
            "required at enrolment (not at application stage in most cases). "
            "CS (Informatik) is admission-restricted; apply by early June for maximum consideration.",
        "living": None,
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science",
             "degree": "BSc", "lang_instruction": ["de"],
             "degree_local": "Bachelor of Science in Informatik (Computer Science), Faculty of Mathematics, "
             "Computer Science and Natural Sciences (Faculty 1), RWTH Aachen University. Standard study period: "
             "6 semesters (3 years). TAUGHT IN GERMAN — German C1 (TestDaF/DSH) required. Admission restricted "
             "(NC); ~8–10% international student quota applies.",
             "faculty": "Faculty of Mathematics, Computer Science and Natural Sciences", "duration": 3,
             "url": "https://www.rwth-aachen.de/cms/root/studium/vor-dem-studium/studiengaenge/"
                    "liste-aktuelle-studiengaenge/studiengangbeschreibung/~bnzs/informatik-b-sc-/?lidx=1",
             "subjects_note": "Mathematics at A-level required. Grade threshold assessed holistically via "
                              "uni-assist based on overall A-level profile (no published per-subject minimum "
                              "grade). German C1 (TestDaF/DSH) mandatory. Programme taught entirely in German.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 716, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "€716/year (€358.34/semester × 2). No tuition fee — semester contribution only "
                 "(student body + Studierendenwerk + NRW Deutschlandticket). Identical for EU and non-EU."}},
            {"suffix": "bsc-mech-eng", "program_name": "Mechanical Engineering", "field": "Engineering",
             "degree": "BSc", "lang_instruction": ["de"],
             "degree_local": "Bachelor of Science in Maschinenbau (Mechanical Engineering), Faculty of "
             "Mechanical Engineering (Faculty 4), RWTH Aachen University. Standard study period: 7 semesters "
             "(3.5 years; displayed as 4 years here for field compatibility). TAUGHT IN GERMAN. "
             "RWTH Engineering is internationally highly ranked.",
             "faculty": "Faculty of Mechanical Engineering", "duration": 4,
             "url": "https://www.rwth-aachen.de/cms/root/studium/vor-dem-studium/studiengaenge/"
                    "liste-aktuelle-studiengaenge/studiengangbeschreibung/~bnev/maschinenbau-b-sc-/?lidx=1",
             "subjects_note": "Mathematics and Physics at A-level required. Grade threshold assessed via "
                              "uni-assist holistically. German C1 mandatory. Programme taught in German.",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics", "Physics"],
                          "international-other": []},
             "cost": {"residency": "international", "tuition": 716, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "€716/year. Same semester contribution as all RWTH programmes. No tuition fee."}},
        ],
        "scholarships": [
            {"suffix": "deutschlandstipendium", "name": "Deutschlandstipendium (Germany Scholarship)",
             "provider": "RWTH Aachen University / Federal Ministry of Education and Research",
             "provider_type": "institutional",
             "award_type": "monthly_stipend", "renewable": True,
             "award_amount": "€300/month for at least 2 semesters (starting Winter Semester), renewable. "
             "50% funded by Federal Government, 50% by private sponsors.",
             "academic_criteria": "Excellent academic achievement or strong evidence of future potential. "
             "Social engagement, talent, and individual circumstances also considered.",
             "other_eligibility_criteria": "COMPETITIVE — application required. Open to all nationalities "
             "enrolled or newly enrolling at RWTH Aachen. Next application period: June 2027 for WS 2027/28.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },

    "de-heidelberg": {
        "canonical_name": "Heidelberg University",
        "aliases": ["Heidelberg", "Uni Heidelberg", "Ruprecht-Karls-Universität Heidelberg",
                    "Ruprecht-Karls-Universität"],
        "country_cc": "de",
        "city": {"slug": "de-heidelberg", "name": "Heidelberg"},
        "website": "https://www.uni-heidelberg.de/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "EUR",
        "verification_note": "fact-checks/de-heidelberg-2026-10-25.md",
        "application_platform_name": "Heidelberg University Application Portal",
        "decision_context_year": "2026-2027 (Winter Semester 2027/28 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "Heidelberg University — Official Website",
                "url": "https://www.uni-heidelberg.de/",
                "excerpt": "Heidelberg University (founded 1386), Heidelberg, Baden-Württemberg, Germany; oldest "
                "university in Germany and one of Europe's most prestigious research universities. Strong in "
                "natural sciences (incl. Computer Science), social sciences, medicine, and humanities. "
                "Baden-Württemberg state law: non-EU international students pay €1,500/semester tuition fee in "
                "addition to the semester administrative fee (~€189.80/semester as of 2026/27)."},
            "adm": {"suffix": "src-adm",
                "title": "Heidelberg — Application for Bachelor Programmes (Mathematics and Computer Science Faculty)",
                "url": "https://www.mathinf.uni-heidelberg.de/en/studies/application-bachelor-programs",
                "excerpt": "Admission to Bachelor Computer Science (100%) requires passing a university entrance "
                "exam (Hochschuleignungsprüfung / internal selection procedure). Application portal opens June 1 "
                "each year; deadline July 15. International qualifications (A-level, IB) assessed under ZAB "
                "evaluation recommendations. German proficiency: DSH-2 minimum (must be proven at enrolment); "
                "TestDaF TDN 4 in all sections accepted. Language of instruction: German. ~8–10% international "
                "student quota for NC programmes."},
            "fee": {"suffix": "src-fee",
                "title": "Heidelberg University — Semester Fees and Non-EU Tuition",
                "url": "https://www.uni-heidelberg.de/en/study/management-of-studies/semester-fees",
                "excerpt": "Semester fee (2026/27 Winter Semester): €189.80 per semester for all students. "
                "Non-EU international students additionally pay €1,500/semester tuition fee under "
                "Baden-Württemberg Landeshochschulgebührengesetz (LHGebG). Total per semester (non-EU): "
                "€1,689.80. Annual total for two semesters (non-EU): €3,379.60 (tuition €3,000 + admin fees "
                "€379.60). EU/EEA students pay only the €189.80/semester admin fee."},
            "schol": {"suffix": "src-schol",
                "title": "Heidelberg University — Deutschlandstipendium",
                "url": "https://www.uni-heidelberg.de/en/friends-supporters/germany-scholarship/how-can-i-apply",
                "excerpt": "Deutschlandstipendium at Heidelberg: €300/month for two semesters, renewable. Open "
                "to all nationalities enrolled at Heidelberg. Applications accepted August 1–31 each year for "
                "the funding period starting Winter Semester. Income-independent. Selection based on academic "
                "excellence and engagement."},
        },
        "curricula": [
            ("a-level", "GCE A-Level / IGCSE", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications assessed by Heidelberg admissions."),
        ],
        "residencies": [
            ("international", "International (non-EU/non-German) students",
             "Students from outside EU/EEA paying the non-EU tuition fee under Baden-Württemberg state law. "
             "Total: €1,689.80/semester (€1,500 non-EU fee + €189.80 admin). EU/EEA students pay €189.80/semester only."),
        ],
        "cost": None,
        "lang_req": {
            "language": "German",
            "req_name": "German language proficiency (C1)",
            "test_name": "TestDaF or DSH (German C1 proficiency)",
            "min_score": "DSH-2 (minimum) or DSH-3. TestDaF: TDN 4 in all 4 sections (TDN 4-4-4-4). "
                         "Certificate must be presented at enrolment.",
            "notes": "All Heidelberg Bachelor programmes are taught in German. German proficiency at C1 level "
                     "is required — English is not separately tested for German-medium programmes. "
                     "Heidelberg's International Study Centre (ISZ) offers DSH preparation courses. "
                     "BSc CS 100% requires an entrance examination in addition to language proof. "
                     "UAE A-level/IB students: plan 1–2 years for German C1 preparation.",
        },
        "std_tests": [],
        "deadline_note": "Application portal opens June 1, 2027. Deadline: July 15, 2027 for Winter Semester "
            "2027/28. Apply directly via Heidelberg's online application portal (not uni-assist). "
            "BSc Computer Science (100%) requires an internal entrance examination — check dates once the "
            "portal opens. German language certificate required at enrolment.",
        "living": None,
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science",
             "degree": "BSc", "lang_instruction": ["de"],
             "degree_local": "Bachelor of Science in Informatik (Computer Science) 100%, Faculty of "
             "Mathematics and Computer Science, Heidelberg University. Standard period: 6 semesters (3 years). "
             "TAUGHT IN GERMAN. Admission requires an internal entrance examination (Hochschuleignungsprüfung) "
             "in addition to language proof and university entrance qualification. ~8–10% places for "
             "international applicants.",
             "faculty": "Faculty of Mathematics and Computer Science", "duration": 3,
             "url": "https://www.informatik.uni-heidelberg.de/studium/bachelor/bsc100?lang=en",
             "subjects_note": "Mathematics at A-level required. Internal entrance examination required for CS "
                              "admission. Grade threshold assessed via ZAB framework. German C1 mandatory. "
                              "Programme taught in German.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 3000, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": 380,
                 "note": "Non-EU students: €1,500/semester non-EU tuition (BW state law) + €189.80/semester "
                 "admin fee. Annual total (non-EU): approx. €3,380 (€3,000 tuition + €380 admin). "
                 "EU/EEA students pay €380/year admin fee only."}},
            {"suffix": "bsc-economics", "program_name": "Economics", "field": "Economics",
             "degree": "BSc", "lang_instruction": ["de"],
             "degree_local": "Bachelor of Science in Volkswirtschaftslehre (Economics) 100%, Faculty of "
             "Economics and Social Sciences, Heidelberg University. Standard period: 6 semesters (3 years). "
             "TAUGHT IN GERMAN. Admission not restricted (no NC for some intakes) — check current admissions "
             "status at application time.",
             "faculty": "Faculty of Economics and Social Sciences", "duration": 3,
             "url": "https://www.uni-heidelberg.de/en/study/all-subjects/economics/economics-bachelor-100",
             "subjects_note": "Mathematics at A-level recommended; assessed holistically via ZAB framework. "
                              "German C1 mandatory. Programme taught in German.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 3000, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": 380,
                 "note": "Non-EU students: €1,500/semester + €189.80/semester. Same fee structure as all "
                 "Heidelberg programmes under BW state law. Annual total: approx. €3,380."}},
        ],
        "scholarships": [
            {"suffix": "deutschlandstipendium", "name": "Deutschlandstipendium (Germany Scholarship)",
             "provider": "Heidelberg University / Federal Ministry of Education and Research",
             "provider_type": "institutional",
             "award_type": "monthly_stipend", "renewable": True,
             "award_amount": "€300/month for two semesters, renewable. Income-independent.",
             "academic_criteria": "Outstanding academic achievement and evidence of future potential. "
             "Social commitment and individual circumstances also considered.",
             "other_eligibility_criteria": "COMPETITIVE — application required August 1–31 each year. "
             "Open to all nationalities enrolled at Heidelberg.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },

    "de-tu-berlin": {
        "canonical_name": "Technical University of Berlin",
        "aliases": ["TU Berlin", "Technische Universität Berlin", "TU Berlin (Technische Universität)"],
        "country_cc": "de",
        "city": {"slug": "de-berlin", "name": "Berlin"},
        "website": "https://www.tu.berlin/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "EUR",
        "verification_note": "fact-checks/de-tu-berlin-2026-10-25.md",
        "application_platform_name": "uni-assist VPD + TU Berlin Application Portal",
        "decision_context_year": "2026-2027 (Winter Semester 2027/28 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "TU Berlin — Official Website",
                "url": "https://www.tu.berlin/",
                "excerpt": "Technische Universität Berlin, Berlin, Germany; major public technical university "
                "and one of Germany's top engineering and CS schools. Schools include Electrical Engineering "
                "and Computer Science (EECS) and several engineering and science faculties. "
                "Berlin (state) does not impose non-EU tuition fees — all students pay only the standard "
                "semester fee (€379.06 for WS 2026/27, includes Berlin semester ticket)."},
            "adm": {"suffix": "src-adm",
                "title": "TU Berlin — Admission Requirements for International Students (Bachelor)",
                "url": "https://www.tu.berlin/en/studierendensekretariat/bachelors-application-enrollment/"
                "prospective-students-with-an-international-higher-education-entrance-qualification/"
                "admission-requirements/language-skills",
                "excerpt": "German language requirement for all TU Berlin Bachelor programmes: C1 level. "
                "Accepted certificates: TestDaF with TDN 4 or higher in all modules (4-4-4-4); DSH-2 or "
                "DSH-3 (recognised by German HRK); Goethe C2; telc Deutsch C1 Hochschule. NOTE: Kombiniertes "
                "Zertifikat für den digitalen TestDaF is specifically NOT recognised by TU Berlin. "
                "International students must submit a VPD (Vorprüfungsdokumentation) from uni-assist. "
                "BSc Computer Science is being redesigned from WS 2026/27 but remains in German."},
            "fee": {"suffix": "src-fee",
                "title": "TU Berlin — Semester Fees",
                "url": "https://www.tu.berlin/en/studierendensekretariat/topics-a-z/semester-fees",
                "excerpt": "Winter Semester 2026/27 semester fee: €379.06. Includes the Berlin semester ticket "
                "(public transport). No tuition fees for any Bachelor programme at TU Berlin. Berlin state "
                "policy: no non-EU tuition fee; all students (German, EU, non-EU) pay identical semester "
                "contribution. Annual cost (2 semesters): €758.12."},
            "schol": {"suffix": "src-schol",
                "title": "TU Berlin — Financing Your Studies",
                "url": "https://www.tu.berlin/en/studying/organizing-your-studies/financing-your-studies",
                "excerpt": "TU Berlin participates in the national Deutschlandstipendium programme. Awards "
                "€300/month for at least 2 semesters, renewable. Open to all enrolled students of any "
                "nationality. Applications typically in summer for Winter Semester start. Competitive selection "
                "based on academic merit and engagement."},
        },
        "curricula": [
            ("a-level", "GCE A-Level / IGCSE", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications assessed via uni-assist VPD."),
        ],
        "residencies": [
            ("international", "International (non-EU/non-German) students",
             "TU Berlin charges NO non-EU tuition — all students pay identical semester fee (€379.06/semester, "
             "WS 2026/27). Fees are purely administrative/transport-based. No differentiation by nationality."),
        ],
        "cost": None,
        "lang_req": {
            "language": "German",
            "req_name": "German language proficiency (C1)",
            "test_name": "TestDaF or DSH (German C1 proficiency)",
            "min_score": "TestDaF: TDN 4 in all 4 modules (4-4-4-4). DSH-2 or DSH-3. Also accepted: Goethe "
                         "Zertifikat C2, telc Deutsch C1 Hochschule. NOTE: Kombiniertes Zertifikat digitaler "
                         "TestDaF is NOT accepted by TU Berlin.",
            "notes": "ALL TU Berlin Bachelor programmes are taught in German (98%+ German-medium). German C1 "
                     "is the primary language requirement. English proficiency not separately required "
                     "(A-levels/IB demonstrate this). UAE students need 1–2 years of German preparation to "
                     "reach C1. TestDaF is available at test centres in UAE and globally. "
                     "Apply via uni-assist for VPD before applying to TU Berlin directly.",
        },
        "std_tests": [],
        "deadline_note": "Apply via uni-assist.de for VPD (allow several weeks processing time). "
            "TU Berlin application deadline for Winter Semester 2027/28: June 1 – July 15, 2027 "
            "(restricted programmes like CS may close June 1). Apply via TU Berlin's online application "
            "portal after receiving VPD. German language certificate required at enrolment.",
        "living": None,
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science",
             "degree": "BSc", "lang_instruction": ["de"],
             "degree_local": "Bachelor of Science in Informatik (Computer Science), School of Electrical "
             "Engineering and Computer Science (EECS), TU Berlin. Standard period: 6 semesters (3 years). "
             "TAUGHT IN GERMAN. Admission restricted (NC). Programme redesigned from WS 2026/27 — remains "
             "German-medium. Applications via uni-assist VPD + TU Berlin portal.",
             "faculty": "School of Electrical Engineering and Computer Science (EECS)", "duration": 3,
             "url": "https://www.tu.berlin/en/studying/study-programs/all-programs-offered/study-course/"
                    "computer-science-b-sc",
             "subjects_note": "Mathematics at A-level required. Grade threshold assessed holistically via "
                              "uni-assist VPD. German C1 (TestDaF/DSH) mandatory. All teaching in German.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 758, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "€758/year (€379.06/semester × 2). Semester fee includes Berlin public transport "
                 "ticket. No tuition fee — same for all students regardless of nationality."}},
            {"suffix": "bsc-electrical-eng", "program_name": "Electrical Engineering",
             "field": "Engineering", "degree": "BSc", "lang_instruction": ["de"],
             "degree_local": "Bachelor of Science in Elektrotechnik (Electrical Engineering), School of "
             "Electrical Engineering and Computer Science (EECS), TU Berlin. Standard period: 6 semesters "
             "(3 years). TAUGHT IN GERMAN. TU Berlin EECS is one of Germany's strongest EE schools.",
             "faculty": "School of Electrical Engineering and Computer Science (EECS)", "duration": 3,
             "url": "https://www.tu.berlin/en/eecs/academics-teaching/study-offer/bachelors-programs",
             "subjects_note": "Mathematics and Physics at A-level required. Grade threshold assessed via "
                              "uni-assist VPD holistically. German C1 mandatory. Programme in German.",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics", "Physics"],
                          "international-other": []},
             "cost": {"residency": "international", "tuition": 758, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "€758/year. Same semester fee as all TU Berlin programmes. No tuition fee."}},
        ],
        "scholarships": [
            {"suffix": "deutschlandstipendium", "name": "Deutschlandstipendium (Germany Scholarship)",
             "provider": "TU Berlin / Federal Ministry of Education and Research",
             "provider_type": "institutional",
             "award_type": "monthly_stipend", "renewable": True,
             "award_amount": "€300/month for at least 2 semesters, renewable.",
             "academic_criteria": "Academic excellence, talent, and engagement. Open to all nationalities.",
             "other_eligibility_criteria": "COMPETITIVE — application required. Enrolled TU Berlin students. "
             "Application timing: typically summer each year for Winter Semester start.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },

    "de-kit": {
        "canonical_name": "Karlsruhe Institute of Technology",
        "aliases": ["KIT", "Karlsruher Institut für Technologie", "Universität Karlsruhe"],
        "country_cc": "de",
        "city": {"slug": "de-karlsruhe", "name": "Karlsruhe"},
        "website": "https://www.kit.edu/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "EUR",
        "verification_note": "fact-checks/de-kit-2026-10-25.md",
        "application_platform_name": "uni-assist + KIT Portal (German programmes); KIT Online Application Portal (Carl Benz School)",
        "decision_context_year": "2026-2027 (Winter Semester 2027/28 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "KIT — Official Website",
                "url": "https://www.kit.edu/",
                "excerpt": "Karlsruhe Institute of Technology (KIT), Karlsruhe, Baden-Württemberg, Germany; "
                "major public technical university. Faculties include Informatics, Mechanical Engineering, "
                "and Economics and Management. Baden-Württemberg state law: non-EU students pay €1,500/semester "
                "tuition. Carl Benz School of Engineering offers ONE English-medium Bachelor: BSc Mechanical "
                "Engineering International — all other KIT Bachelor programmes are in German."},
            "adm": {"suffix": "src-adm",
                "title": "KIT — International Students: Tuition Fees and Admission",
                "url": "https://www.intl.kit.edu/istudies/3363.php",
                "excerpt": "Non-EU international students pay €1,500/semester tuition under BW state law plus "
                "semester contributions (~€184/semester: admin €80 + Studierendenwerk €92 + students union €12). "
                "Total: €1,684/semester. German programmes: TestDaF TDN 4 or DSH-2 required. Apply via "
                "uni-assist for VPD; deadline July 15 for Winter Semester. "
                "Carl Benz School (English programme): IELTS 6.5 overall (no section below 5.5); A-level "
                "Mathematics and Physics (grade C minimum); deadline April 30. Apply via KIT online portal "
                "(not uni-assist). A-level English grade B or higher waives IELTS requirement."},
            "fee": {"suffix": "src-fee",
                "title": "KIT — Charges and Fees for Students",
                "url": "https://www.sle.kit.edu/english/imstudium/703.php",
                "excerpt": "Non-EU student fees per semester: tuition €1,500 + admin €80 + Studierendenwerk "
                "€92 + students union €12 = €1,684 total. EU/EEA students: semester contribution only (~€184). "
                "Annual cost (non-EU, 2 semesters): €3,368 (tuition €3,000 + fees €368)."},
            "schol": {"suffix": "src-schol",
                "title": "KIT — Deutschlandstipendium and Scholarships",
                "url": "https://www.intl.kit.edu/istudies/12591.php",
                "excerpt": "KIT offers the Deutschlandstipendium (€300/month, competitive, all nationalities) "
                "and other scholarships for international students. Some international students may be exempt "
                "from the non-EU tuition fee — details on KIT's dedicated tuition fees page. "
                "Carl Benz School has a separate scholarship programme."},
        },
        "curricula": [
            ("a-level", "GCE A-Level / IGCSE", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications (CBSE, national diplomas, etc.)."),
        ],
        "residencies": [
            ("international", "International (non-EU/non-German) students",
             "Non-EU students pay €1,500/semester tuition (BW state law) + ~€184/semester admin fees. "
             "Total: €1,684/semester, €3,368/year. EU/EEA pay only ~€184/semester admin fees."),
        ],
        "cost": None,
        "lang_req": {
            "language": "German",
            "req_name": "Language proficiency (German or English depending on programme)",
            "test_name": "TestDaF/DSH (German programmes) OR IELTS Academic (Carl Benz School English programme)",
            "min_score": "German programmes (BSc CS): TestDaF TDN 4 in all 4 sections or DSH-2. "
                         "Carl Benz School BSc Mechanical Engineering International (English-medium): "
                         "IELTS Academic 6.5 overall, no individual section below 5.5.",
            "notes": "KIT OFFERS BOTH: (1) German-medium programmes (BSc CS, most engineering) requiring "
                     "German C1 (TestDaF/DSH). (2) ONE English-medium Bachelor at Carl Benz School: BSc "
                     "Mechanical Engineering International — requires IELTS 6.5, NOT German. "
                     "UAE A-level students with English medium education and A-level English grade B or higher "
                     "may be EXEMPT from IELTS for the Carl Benz School programme. "
                     "Deadline for Carl Benz School: April 30 (not July 15). Apply via KIT's own portal "
                     "(not uni-assist) for Carl Benz.",
        },
        "std_tests": [],
        "deadline_note": "Two distinct application routes depending on programme: "
            "(1) German-medium programmes (BSc CS): apply via uni-assist.de for VPD, then KIT portal. "
            "Deadline: July 15, 2027 for Winter Semester 2027/28. German TestDaF/DSH required. "
            "(2) Carl Benz School (BSc Mechanical Engineering International, English): apply via KIT Online "
            "Application Portal — deadline April 30, 2027. IELTS 6.5 required (waived if A-level English ≥ B). "
            "A-level Mathematics and Physics required with grade C minimum.",
        "living": None,
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science",
             "degree": "BSc", "lang_instruction": ["de"],
             "degree_local": "Bachelor of Science in Informatik (Computer Science), Faculty of Informatics, "
             "KIT. Standard period: 6 semesters (3 years). TAUGHT IN GERMAN. Apply via uni-assist VPD + KIT "
             "portal by July 15. Non-EU tuition €1,500/semester (BW law).",
             "faculty": "Faculty of Informatics", "duration": 3,
             "url": "https://www.sle.kit.edu/english/vorstudium/bachelor-computer-science.php",
             "subjects_note": "Mathematics at A-level required. Grade threshold assessed via uni-assist. "
                              "German C1 (TestDaF/DSH) mandatory. Programme in German.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 3000, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": 368,
                 "note": "Non-EU: €1,500/semester tuition (BW state law) + €184/semester admin fees. "
                 "Annual: €3,000 tuition + €368 admin = €3,368. EU/EEA pay €368/year admin only."}},
            {"suffix": "bsc-mech-eng-intl", "program_name": "Mechanical Engineering (International)",
             "field": "Engineering", "degree": "BSc", "lang_instruction": ["en"],
             "degree_local": "Bachelor of Science in Mechanical Engineering (International), Carl Benz School "
             "of Engineering, KIT. Standard period: 7 semesters (3.5 years; shown as 4 years here). "
             "TAUGHT ENTIRELY IN ENGLISH — German language NOT required. Unique among KIT Bachelor programmes. "
             "Apply via KIT Online Application Portal (not uni-assist); deadline April 30, 2027.",
             "faculty": "Carl Benz School of Engineering, KIT", "duration": 4,
             "url": "https://www.sle.kit.edu/english/vorstudium/bachelor-mechanical-engineering-international.php",
             "subjects_note": "A-level Mathematics and Physics required (grade C minimum for enrollment). "
                              "IELTS 6.5 overall, no section below 5.5 (WAIVED if A-level English grade B or "
                              "higher — UAE students on English-medium A-levels typically qualify for waiver). "
                              "English-medium programme — no German language required.",
             "subjects": {"a-level": ["Mathematics", "Physics"], "ib": ["Mathematics", "Physics"],
                          "international-other": []},
             "cost": {"residency": "international", "tuition": 3000, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": 368,
                 "note": "Non-EU: same fee structure as all KIT programmes — €1,500/semester non-EU tuition "
                 "(BW law) + €184/semester admin. Annual: €3,368. Carl Benz English programme has same fee "
                 "as German-medium KIT programmes (no premium for English delivery)."}},
        ],
        "scholarships": [
            {"suffix": "deutschlandstipendium", "name": "Deutschlandstipendium (Germany Scholarship)",
             "provider": "KIT / Federal Ministry of Education and Research",
             "provider_type": "institutional",
             "award_type": "monthly_stipend", "renewable": True,
             "award_amount": "€300/month for at least 2 semesters, renewable.",
             "academic_criteria": "Academic excellence, talent, social engagement. Open to all nationalities.",
             "other_eligibility_criteria": "COMPETITIVE — application required. Enrolled KIT students. "
             "Application timing typically summer for Winter Semester start.",
             "application_deadline": None, "deadline_academic_year": "2026-2027"},
        ],
    },

    "de-lmu": {
        "canonical_name": "LMU Munich",
        "aliases": ["LMU", "Ludwig-Maximilians-Universität München", "Ludwig Maximilian University of Munich"],
        "country_cc": "de",
        "city": {"slug": "de-munich", "name": "Munich"},
        "website": "https://www.lmu.de/", "institution_type": "public",
        "verified_at": "2026-10-25", "currency": "EUR",
        "verification_note": "fact-checks/de-lmu-2026-10-25.md",
        "application_platform_name": "LMU Online Application Portal",
        "decision_context_year": "2026-2027 (Winter Semester 2027/28 entry)",
        "sources": {
            "main": {"suffix": "src-01", "title": "LMU Munich — Official Website",
                "url": "https://www.lmu.de/",
                "excerpt": "Ludwig-Maximilians-Universität München (LMU Munich), Munich, Bavaria, Germany; "
                "one of Germany's elite research universities. Offers programmes in natural sciences, "
                "social sciences, humanities, law, and medicine. Strong Computer Science (Faculty of "
                "Mathematics, Computer Science and Statistics) and Economics (Faculty of Economics). "
                "Bavaria introduced non-EU tuition from WS 2024/25 for TUM; LMU has NOT adopted this fee — "
                "confirmed: no non-EU tuition at LMU. Semester service fee: €97/semester (as of 2026)."},
            "adm": {"suffix": "src-adm",
                "title": "LMU Munich — Prerequisites for International Applicants",
                "url": "https://www.lmu.de/en/study/degree-students/prerequisites/",
                "excerpt": "International applicants need a recognised university entrance qualification and "
                "German language proficiency. For application: minimum B2 level in German. For registration "
                "(enrolment): TestDaF with TDN 4 in all sections (4-4-4-4) or DSH-2 required. "
                "Computer Science: NC (admission-restricted), A-level applicants assessed via Anabin. "
                "BSc Economics: predominantly English-language curriculum with selected modules in German; "
                "German proficiency still required for registration."},
            "fee": {"suffix": "src-fee",
                "title": "LMU Munich — Semester Fees",
                "url": "https://www.lmu.de/en/workspace-for-students/abc-study-guide/semester-fees-for-the-munich-student-union/",
                "excerpt": "LMU semester service fee: €97/semester (Summer Semester 2026; same for all "
                "students). LMU does NOT charge tuition fees for regular degree programmes, including for "
                "students from non-EU countries. Annual cost (2 semesters): €194. "
                "Note: Bavaria introduced non-EU fees for TUM (Technical University of Munich) from "
                "WS 2024/25 but LMU has not adopted this policy as of 2026."},
            "schol": {"suffix": "src-schol",
                "title": "LMU Munich — Deutschlandstipendium",
                "url": "https://www.lmu.de/en/workspace-for-students/student-support-services/finance-your-studies/scholarships/deutschlandstipendium/application/",
                "excerpt": "LMU Deutschlandstipendium: €300/month for up to the standard programme duration. "
                "Half funded by Federal Ministry of Education and Research, half by private sponsors. "
                "Application period 2026: March 16 – April 5. Open to all nationalities. First-year "
                "applicants assessed on university entrance qualification grades in relevant subjects. "
                "Competitive — not automatic. Over 6,000 scholarships awarded in 15 years at LMU."},
        },
        "curricula": [
            ("a-level", "GCE A-Level / IGCSE", "Applicants with GCE A-Level qualifications."),
            ("ib", "International Baccalaureate (IB) Diploma", "Applicants completing the IB Diploma."),
            ("international-other", "General International Secondary Qualification",
             "Other international secondary qualifications assessed via LMU admissions."),
        ],
        "residencies": [
            ("international", "International (non-EU/non-German) students",
             "LMU charges NO non-EU tuition (confirmed 2026). All students pay only the €97/semester service "
             "fee regardless of nationality. Exceptional value versus other German and European universities."),
        ],
        "cost": None,
        "lang_req": {
            "language": "German",
            "req_name": "German language proficiency (B2 for application; C1/TestDaF for registration)",
            "test_name": "German proficiency: B2 (application) → TestDaF TDN 4-4-4-4 or DSH-2 (enrolment)",
            "min_score": "Application: minimum B2 German proficiency proof required. "
                         "Enrolment/registration: TestDaF TDN 4 in all 4 sections (4-4-4-4) or DSH-2. "
                         "BSc Economics: same German requirement, though teaching is predominantly English.",
            "notes": "Two-stage German language requirement at LMU: B2 to apply, C1 (TestDaF/DSH) to enrol. "
                     "BSc Economics has a predominantly English-language curriculum with some German modules — "
                     "German proficiency is still required at registration. BSc CS is taught primarily in "
                     "German. LMU offers intensive 8-week German courses with DSH preparation. "
                     "UAE students: plan for B2 at application time (12–18 months preparation from A2).",
        },
        "std_tests": [],
        "deadline_note": "Apply via LMU's online application portal. "
            "Restricted programmes (BSc CS): apply by July 15, 2027 for Winter Semester 2027/28. "
            "Unrestricted programmes: may have later deadlines — check current LMU portal. "
            "German B2 certificate required at application stage; TestDaF/DSH (C1) required at enrolment. "
            "Note: LMU does not use uni-assist — apply directly via LMU portal.",
        "living": None,
        "programs": [
            {"suffix": "bsc-cs", "program_name": "Computer Science", "field": "Computer Science",
             "degree": "BSc", "lang_instruction": ["de"],
             "degree_local": "Bachelor of Science in Informatik (Computer Science), Faculty of Mathematics, "
             "Computer Science and Statistics, LMU Munich. Standard period: 6 semesters (3 years). "
             "TAUGHT IN GERMAN. NC admission-restricted. Apply directly via LMU portal by July 15.",
             "faculty": "Faculty of Mathematics, Computer Science and Statistics", "duration": 3,
             "url": "https://www.lmu.de/en/study/degree-students/applications-for-admission/",
             "subjects_note": "Mathematics at A-level required. Grade assessed via Anabin. German B2 at "
                              "application; TestDaF TDN 4-4-4-4 or DSH-2 at enrolment. Taught in German.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 194, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "€194/year (€97/semester × 2). No tuition fee — semester service fee only. "
                 "LMU has NOT adopted Bavaria's non-EU tuition policy (unlike TUM). Exceptional value."}},
            {"suffix": "bsc-economics", "program_name": "Economics", "field": "Economics",
             "degree": "BSc", "lang_instruction": ["de", "en"],
             "degree_local": "Bachelor of Science in Volkswirtschaftslehre (Economics), Faculty of Economics "
             "(Volkswirtschaftliche Fakultät), LMU Munich. Standard period: 6 semesters (3 years). "
             "PREDOMINANTLY ENGLISH curriculum (selected modules in German). Unique among German university "
             "Economics programmes. German C1 still required for registration despite English-medium teaching.",
             "faculty": "Faculty of Economics", "duration": 3,
             "url": "https://www.econ.lmu.de/en/study/bachelor-economics/",
             "subjects_note": "Mathematics at A-level recommended; assessed holistically. German B2 at "
                              "application; TestDaF/DSH at enrolment. Programme predominantly in English "
                              "with some German modules.",
             "subjects": {"a-level": ["Mathematics"], "ib": ["Mathematics"], "international-other": []},
             "cost": {"residency": "international", "tuition": 194, "basis": "institutional",
                 "year": "2026-2027",
                 "mandatory_fees_annual": None,
                 "note": "€194/year. Same minimal fee as all LMU programmes. No non-EU tuition."}},
        ],
        "scholarships": [
            {"suffix": "deutschlandstipendium", "name": "Deutschlandstipendium (Germany Scholarship)",
             "provider": "LMU Munich / Federal Ministry of Education and Research",
             "provider_type": "institutional",
             "award_type": "monthly_stipend", "renewable": True,
             "award_amount": "€300/month up to the standard programme duration.",
             "academic_criteria": "Outstanding academic grades in university entrance qualification (relevant "
             "subject grades weighted). Social engagement, talent, personal circumstances also considered.",
             "other_eligibility_criteria": "COMPETITIVE — application required March–April each year. Open to "
             "all nationalities enrolled at LMU Munich. First-year applicants use entrance qualification grades.",
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
            "language_of_instruction": p.get("lang_instruction", ["en"]), "faculty_school": p["faculty"], "official_program_url": p["url"],
            "application_platform": s.get("application_platform_name", "AUS online application"),
            "decision_context_academic_year": s.get("decision_context_year", "2026-2027 (Fall 2027 entry)"),
            "record_status": "VERIFIED", "university_ref": wref(uni_id),
            "application_requirements": [
                {"_key": "r1", "_type": "applicationRequirement",
                 "name": s.get("application_platform_name", "AUS online application"),
                 "necessity": "required", "requirement_type": "form", "description": "", "notes": s.get("deadline_note", "")},
                {"_key": "r2", "_type": "applicationRequirement", "name": "Subject prerequisites",
                 "necessity": "required", "requirement_type": "other",
                 "description": f"{p['subjects_note']}.", "notes": ""},
                {"_key": "r3", "_type": "applicationRequirement", "name": lang.get("req_name", "Language proficiency"),
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
                "language_requirements": [{"_key": "lr1", "_type": "languageRequirement", "language": lang.get("language", "English"), **{k: v for k, v in lang.items() if k not in ("language", "req_name")}}],
                "source_refs": [wref(src_id("adm"), "s1")]}
            prog_tests = p.get("std_tests", s.get("std_tests"))  # per-programme override, else university default
            if prog_tests:
                req["standardized_tests"] = [{"_key": f"st{i+1}", "_type": "testRequirement", **t}
                                             for i, t in enumerate(prog_tests)]
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

"""University of Pisa: base records + Management for Business and Economics (BSc, English) (written 2026-11-25).

Sources, all unipi.it:
  - Tuition fees for international students: 2026-2027 maximum annual all-inclusive fee EUR 2,900 within the
    standard duration (reducible on request); first-year non-EU students requiring a visa pay the regional
    tax (EUR 140) + stamp duty (EUR 16) as the first instalment;
  - Management for Business and Economics course page: "Admission: Local programmed Duration: 3 years English Pisa";
    the English TOLC-E, SAT, ACT and GMAT are accepted admission tests.
Held: International Programme in Humanities (has its own separate IPH fee). No living costs.
  python3 -I scripts/research/gen/it_unipi.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "University of Pisa"
FEES = src("bad2fc6f9653", "Tuition Fees for International Students | University of Pisa", ORG, [
    "For the 2026-2027 academic year , the maximum annual all-inclusive tuition fee for students enrolled within the standard duration of their programme is €2,900 .",
    "This amount may be reduced by applying for a tuition fee reduction .",
    "First-year non-EU students requiring a study visa Instalment Deadline Amount 1 st 31/12/2026 Regional Tax (€140) + Stamp duty (€16)"])
COURSE = src("fa15c222752c", "Management for Business and Economics | University of Pisa", ORG, [
    "Department: ECONOMICS AND MANAGEMENT Admission: Local programmed Duration: 3 years English Pisa",
    "There is no OFA1 for those who have taken the ENGLISH TOLC-E, the SAT, the ACT, and the GMAT regardless of the score.",
    "Support the University of Pisa"])
spec("it-unipi", ORG, ["UniPi", "Università di Pisa"], "public", "https://www.unipi.it/en/", ("it", "Italy", "EUR"), ("it-pisa", "Pisa"),
     {"main": COURSE, "fees": FEES},
     [("international", "International students (maximum fee)", "University of Pisa maximum annual all-inclusive fee within the standard duration; reductions on request.", "fees")])
TH = ("Management for Business and Economics: limited places (local programmed admission) with an admission test; "
      "the English TOLC-E, SAT, ACT and GMAT are accepted. No school-grade cut-off published.")
prog("it-unipi", "bsc-management-for-business-and-economics", {"course": COURSE, "fees": FEES},
     {"name": "Management for Business and Economics", "degree_type": "Bachelor's", "field": "Business", "faculty": "", "duration_years": 3,
      "duration_source": "course", "languages": ["en"], "entry_year": "2026-2027", "platform": "University of Pisa enrolment for international students",
      "source": "course", "summary": "Management for Business and Economics, University of Pisa; 3 years, taught in English.", "application_requirements": []},
     [{"residency": "international", "currency": "EUR", "tuition_annual": 2900, "mandatory_fees_annual": 140, "academic_year": "2026-2027", "source": "fees",
       "note": "2026-2027 maximum annual all-inclusive fee EUR 2,900 (reducible on request). Compulsory: regional tax EUR 140 (shown); stamp duty EUR 16 is also due with the first instalment for first-year non-EU students needing a visa."}],
     adm_all({c: TH for c in ("ib", "a-level", "us-hs", "cbse", "international-other")}, "course",
             tests=[{"name": "English TOLC-E, SAT, ACT or GMAT", "required": "required"}]))
print("wrote MBE")

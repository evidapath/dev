"""Sapienza University of Rome: base records + two English-taught BSc (written 2026-11-25).

Sources, all uniroma1.it:
  - International admissions (2026-2027): "Full tuition for our Bachelor's and Master's programmes is
    € 300-1500/year, according to country of residence";
  - Standard registration fee amounts (Art. 38.2): students with income abroad pay a fixed contribution by
    country band: A EUR 300, B EUR 700, C EUR 1500 (Board resolution of 30 May 2023), with the country lists;
  - Online pre-selection 2026-2027 (PDF): programme descriptions ("a three-year degree program entirely taught
    in English"), mandatory entry tests, minimum GPA, English B2.
Default shown: Band C (EUR 1,500), the highest foreign-income band; A and B are separate fee groups.
Held: Applied Computer Science and AI, Business Sciences, Economics and Finance, Classics, Global
Humanities, Sustainable Building Engineering (length not stated in the pre-selection PDF). No living costs.
  python3 -I scripts/research/gen/it_sapienza.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "Sapienza University of Rome"
ADM = src("abd406546300", "Programmes in English: admissions | Sapienza University of Rome", ORG, [
    "Full tuition for our Bachelor's and Master's programmes is € 300-1500/year, according to country of residence",
    "International Student Office 2026-2027 Pre-selection deadlines"])
FEES = src("0ae24a9523be", "Standard registration fee amounts | Sapienza Università di Roma", ORG, [
    "If you earn income in foreign countries and therefore cannot submit the ISEE declaration",
    "you pay a fixed contribution of a different amount depending on the country of origin, as illustrated below (Board of Directors' resolution of 30 May 2023).",
    "Countries in Band A Total €300", "Countries in Band B Total €700", "Countries in Band C Total €1500",
    "Countries in Band A Afghanistan; Albania; Algeria;", "India; Indonesia;", "Nigeria; Pakistan;",
    "Countries in Band B Antigua and Barbuda; Argentina;", "Malaysia;", "Countries in Band C Andorra;", "United Arab Emirates;"])
REQ_URL_PAGE = "sapienza-req-2627"
spec("it-sapienza", ORG, ["Sapienza", "Sapienza Università di Roma"], "public", "https://www.uniroma1.it/en",
     ("it", "Italy", "EUR"), ("it-rome", "Rome"),
     {"main": src(REQ_URL_PAGE, "Online pre-selection for international students 2026-2027 (PDF) | Sapienza", ORG,
                  ["The Master of Science Program in Economics at Sapienza University of Rome", "ONLINE PRE-SELECTION FOR INTERNATIONAL STUDENTS"]),
      "fees": FEES},
     [("band-c", "Income abroad, Band C countries (e.g. UAE, UK, US, Saudi Arabia)", "Sapienza fixed contribution for students with income in Band C countries.", "fees"),
      ("band-b", "Income abroad, Band B countries (e.g. Malaysia, Türkiye, Argentina)", "Sapienza fixed contribution for students with income in Band B countries.", "fees"),
      ("band-a", "Income abroad, Band A countries (e.g. India, Pakistan, Nigeria)", "Sapienza fixed contribution for students with income in Band A countries.", "fees")])

ENG = {"test_name": "English B2 (IELTS / TOEFL / Cambridge recommended)", "source": "req",
       "min_score": "B2 (CEFR). Exempt with an IB, GCE or GCSE, an English-taught diploma from listed countries, or English native-speaker status."}
P = [("Bioinformatics", "Bioinformatics", "The Degree Course in Bioinformatics is a three-year degree program entirely taught in English.",
      "CEnT-S (CISIA English Test-Sciences): an overall converted score higher than zero", "MINIMUM GPA: 75/100",
      "Bioinformatics: high school diploma after at least 12 years of schooling; minimum GPA 75/100; mandatory CEnT-S test (any converted score above zero). Pre-selection is followed by Sapienza's admission procedure."),
     ("Molecular Biology, Medicinal Chemistry and Computer Science for Pharmaceutical Applications", "Pharmacology",
      "The Degree Course in Molecular Biology, Medicinal Chemistry and Computer Science for Pharmaceutical Applications is a three-year degree program entirely taught in English.",
      "SAT (College Board), acquired from the 1st of January 2025, an overall converted score higher than zero.", "MINIMUM GPA: 60/100",
      "Molecular Biology, Medicinal Chemistry and Computer Science for Pharmaceutical Applications: high school diploma after at least 12 years of schooling; minimum GPA 60/100; SAT or CEnT-S (any score above zero). Pre-selection is followed by Sapienza's admission procedure.")]
COMMON = ["earned after no less than 12 years of studies is required.", "The student must have adequate knowledge of the English language (level B2).",
          "An International Baccalaureate, GCE or GCSE."]
for name, field, dur_q, test_q, gpa_q, th in P:
    req = src(REQ_URL_PAGE, "Online pre-selection for international students 2026-2027 (PDF) | Sapienza", ORG, [dur_q, test_q, gpa_q] + COMMON)
    slug = "bsc-" + ("bioinformatics" if name == "Bioinformatics" else "molecular-biology-medicinal-chemistry-pharma")
    costs = [{"residency": r, "currency": "EUR", "tuition_annual": amt, "academic_year": "2026-2027", "source": ["fees", "adm"],
              "note": f"Fixed contribution of EUR {amt:,} a year for students whose income is in {lab} (Sapienza, resolution of 30 May 2023); "
                      "Sapienza's 2026-2027 admissions page gives EUR 300-1500 a year by country of residence."}
             for r, amt, lab in (("band-c", 1500, "Band C countries"), ("band-b", 700, "Band B countries"), ("band-a", 300, "Band A countries"))]
    prog("it-sapienza", slug, {"req": req, "fees": FEES, "adm": ADM},
         {"name": name, "degree_type": "BSc", "field": field, "faculty": "", "duration_years": 3, "duration_source": "req", "languages": ["en"],
          "entry_year": "2026-2027 pre-selection", "platform": "Sapienza MoveIn pre-selection platform", "source": "req",
          "summary": f"BSc {name}, Sapienza University of Rome; three-year degree taught in English.", "application_requirements": []},
         costs, adm_all({c: th for c in ("ib", "a-level", "us-hs", "cbse", "international-other")}, "req", english=ENG))
    print("wrote", name[:40])

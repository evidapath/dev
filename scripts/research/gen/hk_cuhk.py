"""The Chinese University of Hong Kong: base records + Computer Science and Engineering (written 2026-11-26). THE queue #14.

Sources:
  - admission.cuhk.edu.hk/programme/bcsen: "JUPAS Code JS4412 Programme Code BCSEN Faculty Engineering Study Period 4 Years",
    address "The Chinese University of Hong Kong, Shatin, NT, Hong Kong";
  - admission.cuhk.edu.hk fees page: "2027-2028 annual tuition fees for non-local students HK$230,000 per annum";
  - Reference Scores for Major International Qualifications (PDF, October 2025, compiled from 2023-2025 entries):
    "Computer Science & Engineering 33-35 ABB to AAB" (lowest reference score ranges; for reference only).
Living costs not stored: the fees page (accommodation about HK$17,000 + living about HK$45,000) and the
FAQ ("around HK$48,500 per academic year") give different bases.
  python3 -I scripts/research/gen/hk_cuhk.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "The Chinese University of Hong Kong"
PROG = src("b8a84d742fb8", "Computer Science and Engineering | CUHK Undergraduate Admissions", ORG,
           ["JUPAS Code JS4412 Programme Code BCSEN Faculty Engineering Study Period 4 Years",
            "The Chinese University of Hong Kong, Shatin, NT, Hong Kong", "Computer Science and Engineering - CUHK Undergraduate Admissions"])
spec("hk-cuhk", ORG, ["CUHK", "Chinese University of Hong Kong"], "public", "https://www.cuhk.edu.hk", ("hk", "Hong Kong", "HKD"), ("hk-hong-kong", "Hong Kong"),
     {"main": PROG}, [("international", "Non-local students", "CUHK annual tuition fee for non-local students.", "main")])
prog("hk-cuhk", "bsc-computer-science-and-engineering",
     {"course": PROG,
      "fees": src("389d559a5a1e", "Fees | CUHK Undergraduate Admissions", ORG,
                  ["2027-2028 annual tuition fees for non-local students HK$230,000 per annum",
                   "Any yearly fee adjustment for the 2027 cohort will be capped at 3%."]),
      "ref": src("cuhk-reference-scores-oct2025", "Reference Scores for Major International Qualifications (October 2025) | CUHK", ORG,
                 ["Computer Science & Engineering 33-35 ABB to AAB", "Reference scores are compiled with reference to admission statistics in 2023, 2024 and 2025 entries.",
                  "The lowest reference score ranges of undergraduate programmes based on admission statistics in the same period are summarized below."])},
     {"name": "Computer Science and Engineering", "degree_type": "Bachelor", "field": "Computer Science", "faculty": "Faculty of Engineering",
      "duration_years": 4, "duration_source": "course", "languages": [], "entry_year": "2027-2028", "platform": "", "source": "course",
      "summary": "Computer Science and Engineering (JS4412 / BCSEN), The Chinese University of Hong Kong; study period 4 years.",
      "application_requirements": []},
     [{"residency": "international", "currency": "HKD", "tuition_annual": 230000, "academic_year": "2027-2028", "source": "fees",
       "note": "Non-local students: HK$230,000 per annum (2027-2028); any yearly adjustment for the 2027 cohort capped at 3%."}],
     adm_all({"ib": "Computer Science & Engineering: lowest reference score range 33-35 for the IB Diploma (2023-2025 entries; for reference only).",
              "a-level": "Computer Science & Engineering: lowest reference score range ABB to AAB at GCE AL / IAL (2023-2025 entries; for reference only)."},
             "ref"))
print("wrote cuhk")

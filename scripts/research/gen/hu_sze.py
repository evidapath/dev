"""Széchenyi István University, Győr: base records + four English-taught BSc (written 2026-11-25).

Source: programme pages on admissions.sze.hu: "<qualification> (BSc) N semesters – full time programme
... credits N EUR / semester", B2 English (IELTS Academic 6.0, TOEFL iBT 72...). The academic year of the
fee isn't stated on the pages. Admission beyond English not read. No living costs.
  python3 -I scripts/research/gen/hu_sze.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "Széchenyi István University"
P = [("8e4e6adc4aef", "International Business Economics", "Economics",
      "Economist in International Business Economics (BSc) 8 semesters – full time programme 180 + 60 credits 1,700 EUR / semester", 1700, 8),
     ("a5d009373394", "Business Administration and Management", "Business",
      "Economist in Business Administration and Management (BSc) 7 semesters – full time programme 210 credits 1,700 EUR / semester", 1700, 7),
     ("c6ed899fba22", "Logistics Engineering", "Engineering",
      "Logistics Engineer (BSc) 7 semesters – full time programme 210 credits 2,600 EUR / semester", 2600, 7),
     ("4388dd6337ec", "Agricultural Engineering", "Agriculture",
      "Agricultural Engineer (BSc) 7 semesters – full time programme 210 credits 1,700 EUR / semester", 1700, 7)]
ENG_Q = ["Applicants must have at least B2-level English language proficiency. Minimum accepted requirements: IELTS Academic: minimum overall score of 6.0 TOEFL iBT: minimum score of 72"]
spec("hu-sze", ORG, ["SZE", "Széchenyi István Egyetem"], "public", "https://uni.sze.hu/en_GB", ("hu", "Hungary", "HUF"), ("hu-gyor", "Győr"),
     {"main": src(P[0][0], "International Business Economics BSc | Széchenyi István University", ORG,
                  ["International Business Economics BSc programme at Széchenyi István University", "H-9026 Győr, Egyetem tér 1. Hungary"])},
     [("international", "International students (programme page fee)", "The per-semester tuition on each English-taught programme page of Széchenyi István University.", "main")])

ENG = {"test_name": "IELTS Academic / TOEFL iBT (B2)", "min_score": "B2: IELTS Academic 6.0 overall, TOEFL iBT 72, or another B2 certificate.", "source": "course"}
TH = "{name}: no grade cut-off on the programme page read; English B2 is required."
for page, name, field, row, fee, sem in P:
    prog("hu-sze", f"bsc-{slugify(name)}",
         {"course": src(page, f"{name} BSc | Széchenyi István University", ORG, [row] + ENG_Q)},
         {"name": name, "degree_type": "BSc", "field": field, "faculty": "", "duration_years": sem / 2, "duration_source": "course", "languages": ["en"],
          "entry_year": "Programme page (year not stated)", "platform": "Széchenyi István University admissions", "source": "course",
          "summary": f"{name} (BSc), Széchenyi István University, Győr; taught in English.", "application_requirements": []},
         [{"residency": "international", "currency": "EUR", "tuition_per_semester": fee, "semesters_quote": f"{sem} semesters", "semesters_source": "course",
           "academic_year": "Programme page (year not stated)", "source": "course",
           "note": f"EUR {fee:,} per semester (programme page; the academic year isn't stated). Yearly figure our calculation."}],
         adm_all({c: TH.format(name=name) for c in ("ib", "a-level", "us-hs", "cbse", "international-other")}, "course", english=ENG))
    print("wrote", name)

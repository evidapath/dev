"""The University of Sheffield: base records + two computing BSc (written 2026-11-26). THE queue #46.

Source: each 2027 course page on sheffield.ac.uk (rendered with bfetch.sh for the fee): "A Levels AAA; AAB
UCAS code ... Duration 3 years", "£34,670 Overseas students 2027-28 tuition fee for year one", IB offers,
IELTS 6.5 (6.0 each). No living costs read.
  python3 -I scripts/research/gen/gb_sheffield.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "University of Sheffield"
COMMON = ["£34,670 Overseas students 2027-28 tuition fee for year one",
          "International Baccalaureate 36, with 6 in HL Maths; 34, with 6 in HL Maths, and A in the Extended Essay; 34, with 6 in HL Maths and 5 in HL Computer Science",
          "IELTS grade of 6.5 with a minimum of 6.0 in each component"]
P = [("91a8dd988571", "Computer Science", "G402"), ("5ec5ff599c53", "Computer Science (Artificial Intelligence)", "GG74")]
spec("gb-sheffield", ORG, ["Sheffield", "The University of Sheffield"], "public", "https://www.sheffield.ac.uk", ("gb", "United Kingdom", "GBP"), ("gb-sheffield", "Sheffield"),
     {"main": src(P[0][0], "Computer Science BSc | The University of Sheffield", ORG, ["Computer science programmes at the University of Sheffield will empower you"])},
     [("international", "Overseas students", "The University of Sheffield's overseas tuition fee for year one.", "main")])
ENG = {"test_name": "IELTS", "min_score": "IELTS 6.5 with a minimum of 6.0 in each component.", "source": "course"}
for page, name, code in P:
    q = COMMON + [f"A Levels AAA; AAB UCAS code {code} Duration 3 years", f"{name} BSc School of Computer"]
    prog("gb-sheffield", slugify(f"bsc {name}"), {"course": src(page, f"{name} BSc | The University of Sheffield", ORG, q)},
         {"name": name, "degree_type": "BSc", "field": "Computer Science", "faculty": "", "duration_years": 3, "duration_source": "course", "languages": [],
          "entry_year": "2027-28", "platform": "UCAS", "source": "course", "summary": f"{name} BSc ({code}), The University of Sheffield; 3 years.",
          "application_requirements": []},
         [{"residency": "international", "currency": "GBP", "tuition_annual": 34670, "academic_year": "2027-28", "source": "course",
           "note": "Overseas students, 2027-28 tuition fee for year one: £34,670 (course page)."}],
         adm_all({"a-level": f"{name}: A Levels AAA (or AAB with the conditions on the course page).",
                  "ib": f"{name}: IB 36 with 6 in HL Maths (or 34 with 6 in HL Maths plus an A in the Extended Essay or 5 in HL Computer Science)."},
                 "course", english=ENG))
    print("wrote", name)

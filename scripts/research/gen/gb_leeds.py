"""University of Leeds: base records + two computing BSc (written 2026-11-26). THE queue #31.

Source: each course page on courses.leeds.ac.uk (Year of entry 2027): "Duration 3 Years (Full time)",
"Fees UK: £10,050 International: £33,700 (per year)", A-level and IB entry, IELTS 6.0 (5.5 each).
No living costs read.
  python3 -I scripts/research/gen/gb_leeds.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "University of Leeds"
FEE_Q = "Fees UK: £10,050 International: £33,700 (per year)"
IB_Q = "International Baccalaureate 18 points at Higher level to include 5 in HL Mathematics: Analysis and Approaches or 6 in HL Mathematics: Applications and Interpretation."
IELTS_Q = "IELTS 6.0 overall, with no less than 5.5 in each section."
COMMON = [FEE_Q, "Delivery type On campus Duration 3 Years (Full time)", "Year of entry 2027", IB_Q, IELTS_Q]
P = [("4c009f3c32c7", "Computer Science", "A-level: AAA including Mathematics.", "AAA including Mathematics"),
     ("96c7c976e42f", "Computer Science (Artificial Intelligence)", "A-level: AAA (specific subject requirements)", "AAA (with specific subject requirements; IB route requires HL Mathematics)")]
spec("gb-leeds", ORG, ["Leeds"], "public", "https://www.leeds.ac.uk", ("gb", "United Kingdom", "GBP"), ("gb-leeds", "Leeds"),
     {"main": src(P[0][0], "Computer Science BSc | University of Leeds", ORG, ["Computer Science BSc | University of Leeds", FEE_Q])},
     [("international", "International students", "University of Leeds international tuition fee (per year, fixed for the course).", "main")])
ENG = {"test_name": "IELTS", "min_score": "IELTS 6.0 overall, with no less than 5.5 in each section.", "source": "course"}
for page, name, al_q, al_txt in P:
    prog("gb-leeds", slugify(f"bsc {name}"), {"course": src(page, f"{name} BSc | University of Leeds", ORG, COMMON + [al_q, f"{name} BSc | University of Leeds"])},
         {"name": name, "degree_type": "BSc", "field": "Computer Science", "faculty": "", "duration_years": 3, "duration_source": "course", "languages": [],
          "entry_year": "2027", "platform": "UCAS", "source": "course", "summary": f"{name} BSc, University of Leeds; 3 years full time.", "application_requirements": []},
         [{"residency": "international", "currency": "GBP", "tuition_annual": 33700, "academic_year": "2027 entry", "source": "course",
           "note": "International: £33,700 per year for 2027 entry (course page)."}],
         adm_all({"a-level": f"{name}: A-level {al_txt}.",
                  "ib": f"{name}: IB 18 points at Higher level, including 5 in HL Mathematics: Analysis and Approaches or 6 in HL Mathematics: Applications and Interpretation."},
                 "course", english=ENG))
    print("wrote", name)

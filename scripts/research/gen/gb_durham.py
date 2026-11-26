"""Durham University: base records + two computing BSc (written 2026-11-26). THE queue #33.

Source: each course page on durham.ac.uk/study/courses (September 2027): "Course length 3 years full-time",
"International (full-time): £35,000 per year", A level and IB requirements, IELTS 6.5-7.0 (no element below 6.0).
No living costs read.
  python3 -I scripts/research/gen/gb_durham.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "Durham University"
P = [("c07cdd9b9f8f", "Computer Science", "G400",
      "Entry requirements Entry requirements A*AA including A in Mathematics.",
      "IB diploma score IB diploma score 37 with 766 in higher level subjects, including Mathematics.",
      "A*AA including A in Mathematics (contextual offer AAB including A in Mathematics).", "37 points with 766 at Higher Level, including Mathematics",
      "Contextual offer Contextual offer AAB including A in Mathematics."),
     ("ad1c2b8e5290", "Computer Science and Mathematics", "G411",
      "Entry requirements Entry requirements A*AA including either A*A in any order in Maths and Further Maths at A level",
      "IB diploma score IB diploma score 37 including 7 in Higher Level Mathematics (Analysis & Approaches) and 66 in two other Higher Level subjects.",
      "A*AA including A*A in Maths and Further Maths (or the alternative on the course page).", "37 points including 7 in HL Mathematics (Analysis & Approaches) and 6, 6 in two other HL subjects",
      None)]
spec("gb-durham", ORG, ["Durham"], "public", "https://www.durham.ac.uk", ("gb", "United Kingdom", "GBP"), ("gb-durham", "Durham"),
     {"main": src(P[0][0], "Computer Science G400 | Durham University", ORG, ["Computer Science G400 - Durham University"])},
     [("international", "International students (full-time)", "Durham University's international full-time tuition fee per year.", "main")])
ENG = {"test_name": "IELTS", "min_score": "IELTS band 6.5-7.0 (no element below 6.0), or equivalent.", "source": "course"}
for page, name, code, al_q, ib_q, al_txt, ib_txt, ctx in P:
    q = [f"{name} {code} September 2027", "Course length 3 years full-time", "International (full-time): £35,000 per year", al_q, ib_q,
         "IELTS score of band 6.5 – 7.0 (no element below band 6.0) or equivalent."] + ([ctx] if ctx else [])
    prog("gb-durham", slugify(f"bsc {name}"), {"course": src(page, f"{name} {code} | Durham University", ORG, q)},
         {"name": name, "degree_type": "BSc (Hons)", "field": "Computer Science", "faculty": "", "duration_years": 3, "duration_source": "course", "languages": [],
          "entry_year": "September 2027", "platform": "UCAS", "source": "course", "summary": f"BSc (Hons) {name} ({code}), Durham University; 3 years full-time.",
          "application_requirements": []},
         [{"residency": "international", "currency": "GBP", "tuition_annual": 35000, "academic_year": "September 2027 entry", "source": "course",
           "note": "International (full-time): £35,000 per year (course page, September 2027)."}],
         adm_all({"a-level": f"{name}: A level {al_txt}", "ib": f"{name}: IB Diploma {ib_txt}."}, "course", english=ENG))
    print("wrote", name)

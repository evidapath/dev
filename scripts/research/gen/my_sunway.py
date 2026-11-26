"""Sunway University, Bandar Sunway (Selangor): base records + four computing degrees (written 2026-11-26).

Source: each course page on sunwayuniversity.edu.my: "Estimated Annual Course Fee (Year 2026) ... USDn for
international students" (paid in RM equivalent; USD indicative), "Duration 3 Years (full-time)", entry
(A-Level minimum 12 points with at least Grade D in 2 subjects; IB 28 points excluding bonus), English
(IELTS or equivalent 6.0). The 2027 fee isn't published; the 2026 estimate is stored and labelled.
  python3 -I scripts/research/gen/my_sunway.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "Sunway University"
P = [("029a68b6cd45", "Computer Science", "BSc (Hons)", "Computer Science", 9779, "RM39,800"),
     ("159dd3ebfac0", "Information Technology", "BSc (Hons)", "Information Technology", 9779, "RM39,800"),
     ("7c2d8bf98ca4", "Software Engineering", "Bachelor (Hons)", "Computer Science", 10058, "RM41,000"),
     ("a6a409918b60", "Information Systems (Data Analytics)", "Bachelor (Hons)", "Information Technology", 10058, "RM41,000")]
spec("my-sunway", ORG, ["Sunway"], "private", "https://sunwayuniversity.edu.my", ("my", "Malaysia", "MYR"), ("my-bandar-sunway", "Bandar Sunway"),
     {"main": src(P[0][0], "Computer Science | Sunway University", ORG, ["Computer Science | Sunway University", "Bandar Sunway , 47500 Selangor Darul Ehsan Malaysia"])},
     [("international", "International students", "Sunway University's estimated annual course fee for international students (paid in RM equivalent).", "main")])
ENG = {"test_name": "IELTS (or equivalent)", "min_score": "IELTS or equivalent 6.0 (or MUET Band 4, O-Level English credit and others Sunway lists).", "source": "course"}
for page, name, deg, field, usd, rm in P:
    q = [f"Estimated Annual Course Fee (Year 2026) {rm} for Malaysian students USD{usd:,} for international students International students must pay their fees in RM equivalent.",
         "Duration 3 Years (full-time)", "A-Level Minimum 12 points (Minimum Grade D in at least 2 subjects)", "For A-Level points calculation A = 10 points B = 8 points C = 6 points D = 4 points E = 2 points",
         "International Baccalaureate (IB) Completed with minimum 28 points (excluding bonus points)",
         "English Language Requirements IELTS or equivalent 6.0", name.split(" (")[0]]
    prog("my-sunway", slugify(f"{deg} {name}"), {"course": src(page, f"{name} | Sunway University", ORG, q)},
         {"name": name, "degree_type": deg, "field": field, "faculty": "", "duration_years": 3, "duration_source": "course", "languages": ["en"],
          "entry_year": "2026 fee estimate (2027 not published)", "platform": "Sunway University online application", "source": "course",
          "summary": f"{name}, Sunway University; 3 years full-time.", "application_requirements": []},
         [{"residency": "international", "currency": "USD", "tuition_annual": usd, "academic_year": "Year 2026 (estimated)", "source": "course",
           "note": f"Estimated annual course fee for Year 2026: USD {usd:,} for international students, paid in RM equivalent (the USD is indicative)."}],
         adm_all({"a-level": f"{name}: A-Level minimum 12 points (A=10, B=8, C=6, D=4, E=2) with at least Grade D in 2 subjects.",
                  "ib": f"{name}: IB Diploma completed with at least 28 points (excluding bonus points)."}, "course", english=ENG))
    print("wrote", name)

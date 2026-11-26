"""The University of Queensland: base records + Bachelor of Computer Science (written 2026-11-26). THE queue #39.

Sources:
  - St Lucia campus page (campuses.uq.edu.au/st-lucia): name and city ("Located 7 kilometres from Brisbane’s city centre");
  - study.uq.edu.au program 2559: "Duration 3 Years", international "Approximate yearly cost of tuition (16 units)
    ... AUD $60,952 2027", IB 32 as the lowest adjusted score offered in Semester 1, 2026, IELTS 6.5 (6 each).
No living costs read.
  python3 -I scripts/research/gen/au_uq.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "The University of Queensland"
spec("au-uq", ORG, ["UQ", "University of Queensland"], "public", "https://www.uq.edu.au", ("au", "Australia", "AUD"), ("au-brisbane", "Brisbane"),
     {"main": src("d6298bf952e0", "St Lucia Campus | UQ", ORG,
                  ["© The University of Queensland ABN", "Located 7 kilometres from Brisbane’s city centre"])},
     [("international", "International students", "UQ approximate yearly international tuition (16 units).", "main")])
Q = ["Location St Lucia Duration 3 Years (or part time equivalent) Start Semester Semester 1 (22 Feb, 2027)",
     "Approximate yearly cost of tuition (16 units). Your fees will vary according to your study load. Fees are reviewed each year and may increase. AUD $60,952 2027",
     "Entry score threshold ATAR / Rank IB 84 32 These are the lowest adjusted scores we made an offer to in Semester 1, 2026.",
     "IELTS overall 6.5; reading 6; writing 6; speaking 6; listening 6.", "of Computer Science - Study - The University of Queensland"]
prog("au-uq", "bachelor-of-computer-science", {"course": src("85e449918913", "Bachelor of Computer Science (2559) | The University of Queensland", ORG, Q)},
     {"name": "Bachelor of Computer Science", "degree_type": "Bachelor", "field": "Computer Science", "faculty": "",
      "duration_years": 3, "duration_source": "course", "languages": [], "entry_year": "2027", "platform": "", "source": "course",
      "summary": "Bachelor of Computer Science, The University of Queensland (St Lucia); 3 years.", "application_requirements": []},
     [{"residency": "international", "currency": "AUD", "tuition_annual": 60952, "academic_year": "2027", "source": "course",
       "note": "Approximate yearly cost of tuition (16 units): AUD $60,952 (2027); fees are reviewed each year and may increase."}],
     adm_all({"ib": "Bachelor of Computer Science: IB 32 was the lowest adjusted score offered a place in Semester 1, 2026 (not a guarantee)."},
             "course", english={"test_name": "IELTS", "min_score": "IELTS overall 6.5; reading, writing, speaking and listening 6 each.", "source": "course"}))
print("wrote uq")

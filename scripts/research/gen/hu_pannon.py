"""University of Pannonia, Veszprém: base records + one English-taught BSc (written 2026-11-25).

Source: the BSc in Data Science in Business page (Faculty of Business and Economics, gtk.uni-pannon.hu):
Veszprém; non-EU EUR 4000 per academic year (2 semesters); English, full time, 8 semesters; finished
secondary school and B2 English. The year of the fee isn't stated on the page.
Held: International Business Economics (length "6+1+1 semesters"), Business Administration and Management
(non-EU fee printed as "40 00 EUR"), Water Operation Engineering (Nagykanizsa campus), Sustainable and
Circular Economy-based Tourism ("8 semester" doesn't pass the length check as written).
  python3 -I scripts/research/gen/hu_pannon.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "University of Pannonia"
Q = ["BSc in Data Science in Business - University of Pannonia", "Place of training Veszprém, Hungary",
     "The tuition fee for NON EU Students is 4000 EUR /Academic year (2 semesters) Language and form of training English Full time Study duration 8 semesters",
     "Entry requirements Finished secondary school studies. Language requirements: B2 level English language certificate"]
COURSE = src("f7a71f928ce2", "BSc in Data Science in Business | University of Pannonia", ORG, Q)
spec("hu-pannon", ORG, ["Pannon Egyetem"], "public", "https://uni-pannon.hu/en", ("hu", "Hungary", "HUF"), ("hu-veszprem", "Veszprém"),
     {"main": COURSE}, [("non-eu", "Non-EU students", "University of Pannonia's per-year tuition for non-EU students on the programme page.", "main")])
prog("hu-pannon", "bsc-data-science-in-business", {"course": COURSE},
     {"name": "Data Science in Business", "degree_type": "BSc", "field": "Computer Science", "faculty": "", "duration_years": 4, "duration_source": "course",
      "languages": ["en"], "entry_year": "Programme page (year not stated)", "platform": "University of Pannonia application", "source": "course",
      "summary": "BSc in Data Science in Business, University of Pannonia, Veszprém; taught in English.", "application_requirements": []},
     [{"residency": "non-eu", "currency": "EUR", "tuition_annual": 4000, "academic_year": "Programme page (year not stated)", "source": "course",
       "note": "Non-EU: EUR 4000 per academic year (2 semesters), programme page; the academic year isn't stated."}],
     adm_all({c: "Data Science in Business: finished secondary school studies and B2 English; no grade cut-off published."
              for c in ("ib", "a-level", "us-hs", "cbse", "international-other")}, "course",
             english={"test_name": "B2 English certificate", "min_score": "B2 level certificate (TOEFL, IELTS, Cambridge and others), or proof of studies in English.", "source": "course"}))
print("wrote Data Science in Business")

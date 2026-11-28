"""Tel Aviv University (THE #141): BA in Liberal Arts, its English-taught bachelor's with a stated length (written
2026-11-28). Left out: BA in Management and Liberal Arts (its page states no length), the Columbia dual degree
(part of the fee is Columbia's), and the BMus (tuition shown as "Free Tuition"; not added until checked).
  python3 -I scripts/research/gen/il_tau.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog

ORG = "Tel Aviv University"
LA = src("794188b28f57", "BA in Liberal Arts in Israel | Tel Aviv University", ORG,
         ["BA in Liberal Arts in Israel | Tel Aviv University",
          "Registration is open for: Fall 2027 Application Deadlines : TBA Program Length : 3 Years Language of Instruction : English Tuition : $15,500 / Year",
          "Available tracks to choose from: Data Science Psychology Middle Eastern Studies Philosophy Literature Jewish & Israel Studies Digital Culture & Media Entrepreneurship & Innovation"])
OV = src("96a8931e558a", "Undergraduate Degrees in English at Tel Aviv University", ORG,
         ["Location: Tel Aviv University campus, Israel"])
spec("il-tau", ORG, ["TAU"], "public", "https://english.tau.ac.il", ("il", "Israel", "ILS"), ("il-tel-aviv", "Tel Aviv"), {"main": OV, "la": LA},
     [("international", "International students", "Tuition for the English-taught international BA programme.", "la")])
prog("il-tau", "ba-liberal-arts", {"course": LA},
     {"name": "Liberal Arts", "degree_type": "BA", "field": "Liberal Arts", "faculty": "", "duration_years": 3, "duration_source": "course",
      "languages": ["en"], "entry_year": "Fall 2027", "platform": "", "source": "course",
      "summary": "BA in Liberal Arts, Tel Aviv University; 3 years, taught in English; a major, a minor and two further fields from tracks including Data Science, Psychology, Philosophy and Entrepreneurship & Innovation.",
      "application_requirements": []},
     [{"residency": "international", "currency": "USD", "tuition_annual": 15500, "academic_year": "Fall 2027", "source": "course",
       "note": "Tuition $15,500 a year (Fall 2027 entry)."}], [])
print("wrote il-tau")

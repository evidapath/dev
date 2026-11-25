"""Corvinus University of Budapest: base records + two English-only bachelor's degrees (written 2026-11-25).

Source: programme landing pages on uni-corvinus.hu: "Start date September 2027", "Tuition fee (Non-EEA)
N EUR/semester M EUR/year", "Duration N semesters (Y years)", "This programme is available only in English."
Held: Business and Management (Hungarian and English; length not given in the same form). Admission
requirements not read. No living costs.
  python3 -I scripts/research/gen/hu_corvinus.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "Corvinus University of Budapest"
P = [("af6ed255189e", "International Business", "BSc", "Business", "Tuition fee (Non-EEA) 3 500 EUR/semester 7 000 EUR/year", 7000, 4, "Duration 8 semesters (4 years)"),
     ("443b84b5c362", "International Relations", "BA", "Politics", "Tuition fee (Non-EEA) 3 300 EUR/semester 6 600 EUR/year", 6600, 3, "Duration 6 semesters (3 years)")]
spec("hu-corvinus", ORG, ["Corvinus", "Budapesti Corvinus Egyetem"], "public", "https://www.uni-corvinus.hu/?lang=en", ("hu", "Hungary", "HUF"), ("hu-budapest", "Budapest"),
     {"main": src(P[0][0], "International Business BSc | Corvinus University of Budapest", ORG, ["Corvinus University of Budapest Jump to main content", "Budapest"])},
     [("non-eea", "Non-EEA students", "Corvinus University of Budapest's tuition for non-EEA students on each programme page.", "main")])

TH = "{name}: admission requirements aren't on the programme page read; see Corvinus's Admissions Requirements page."
for page, name, deg, field, fee_q, annual, years, dur_q in P:
    q = [f"Programme name {name}", dur_q, "Start date September 2027", fee_q, "This programme is available only in English."]
    prog("hu-corvinus", f"{deg.lower()}-{slugify(name)}", {"course": src(page, f"{name} {deg} | Corvinus University of Budapest", ORG, q)},
         {"name": name, "degree_type": deg, "field": field, "faculty": "", "duration_years": years, "duration_source": "course", "languages": ["en"],
          "entry_year": "September 2027", "platform": "Corvinus online application", "source": "course",
          "summary": f"{name} ({deg}), Corvinus University of Budapest; taught only in English.", "application_requirements": []},
         [{"residency": "non-eea", "currency": "EUR", "tuition_annual": annual, "academic_year": "September 2027 start", "source": "course",
           "note": f"Non-EEA: EUR {annual:,} a year (EUR {annual // 2:,} per semester) for the September 2027 start; the official price list is in Corvinus's fee regulation."}],
         adm_all({c: TH.format(name=name) for c in ("ib", "a-level", "us-hs", "cbse", "international-other")}, "course"))
    print("wrote", name)

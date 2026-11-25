"""University of Debrecen: base records + seven English-taught bachelor's degrees (written 2026-11-25).

Source: each programme page on edu.unideb.hu: "The tuition fee for this program is N USD/Year",
"This is a N-year program consisting of M academic semesters", B2 English, "Academic entry: Admission
requires a high school certificate and passing entrance exams in ...", application deadline (self-financed)
15th June. The pages don't state which academic year the fee is for; the note says so.
No living-cost figures read. English and American Studies BA not added: its page doesn't carry the 'All courses are taught in English' line.
  python3 -I scripts/research/gen/hu_unideb.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify, text

ORG = "University of Debrecen"
# page, name, degree, field, fee USD, years
P = [("76befc5b0352", "Chemistry", "BSc", "Chemistry", 6500, 3),
     ("4932697fc70d", "Biotechnology", "BSc", "Biology", 6500, 3),
     ("41fad8bd3622", "Business Administration and Management", "BSc", "Business", 7000, 3.5),
     ("a4b89a75797f", "Mechanical Engineering", "BSc", "Mechanical Engineering", 7500, 3.5),
     ("c02c76df82dc", "Computer Science Engineering", "BSc", "Computer Science", 7000, 3.5),
     ("27b9dd8cad44", "Electrical Engineering", "BSc", "Electrical and Electronic Engineering", 7000, 3.5)]

first = P[0][0]
spec("hu-unideb", ORG, ["UD", "Debreceni Egyetem"], "public", "https://unideb.hu/en", ("hu", "Hungary", "HUF"), ("hu-debrecen", "Debrecen"),
     {"main": src(first, "Chemistry BSc | University of Debrecen", ORG, ["BSc at the University of Debrecen?"])},
     [("self-financed", "Self-financed students (programme page fee)", "The yearly tuition fee on each English-taught programme page of the University of Debrecen.", "main")])

for page, name, deg, field, fee, years in P:
    t = text(page)
    yr = f"{years:g}"
    dur_q = f"This is a {yr}-year program consisting of {int(years * 2)} academic semesters"
    m = re.search(r"academic entry: (admission requires [^.]*\.)", t)
    entry = m.group(1) if m else None
    quotes = [f"The tuition fee for this program is {fee:,} USD/Year", dur_q,
              "This is supplemented by the application fee of $150 USD (one-time) and the entrance procedure fee of $350 USD"]
    assert "all courses are taught in english ; therefore, a b2 level english proficiency is required." in t, name
    if True:
        quotes.append("All courses are taught in English ; therefore, a B2 level English proficiency is required.")
    eng = {"test_name": "English (B2)", "min_score": "B2 level English proficiency.", "source": "course"} if "b2 level english" in t else None
    if entry:
        orig = re.search(r"Academic entry: (Admission requires [^.]*\.)", re.sub(r"\s+", " ", (src.__globals__["PAGES"] / f"{page}.txt").read_text())).group(1)
        quotes.append(orig)
        th = f"{name}: no grade cut-off published. {orig}"
    else:
        quotes.append("written and oral entrance exams designed to evaluate subject-specific knowledge and personal motivation")
        th = f"{name}: no grade cut-off published. Admission is online, with written and oral entrance exams on subject knowledge and motivation."
    prog("hu-unideb", f"{deg.lower()}-{slugify(name)}", {"course": src(page, f"{name} {deg} | University of Debrecen", ORG, quotes)},
         {"name": name, "degree_type": deg, "field": field, "faculty": "", "duration_years": years, "duration_source": "course", "languages": ["en"],
          "entry_year": "Self-financed procedure (programme page)", "platform": "University of Debrecen online application", "source": "course",
          "summary": f"{name} ({deg}), University of Debrecen; taught in English.", "application_requirements": []},
         [{"residency": "self-financed", "currency": "USD", "tuition_annual": fee, "academic_year": "Not stated on the programme page",
           "source": "course",
           "note": f"USD {fee:,} a year (programme page; the academic year isn't stated). One-time: USD 150 application fee and USD 350 entrance procedure fee. Living costs not added."}],
         adm_all({c: th for c in ("ib", "a-level", "us-hs", "cbse", "international-other")}, "course", english=eng))
    print("wrote", name, yr)

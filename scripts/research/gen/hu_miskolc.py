"""University of Miskolc: base records + eight English-taught bachelor's degrees (written 2026-11-25).

Source: course pages on apply.uni-miskolc.hu: "<name> - University of Miskolc", "Study location Hungary,
Miskolc", "Nominal duration N semesters", "Study language English", "Tuition fee €N per semester", entry
qualification and English requirement where stated. The academic year isn't stated. No living costs.
  python3 -I scripts/research/gen/hu_miskolc.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify, text, norm

ORG = "University of Miskolc"
# page, portal name, display name, degree, field, fee, semesters
P = [("0dc2adca26bf", "[BSc] Business Administration and Management", "Business Administration and Management", "BSc", "Business", 2400, 7),
     ("c9c15a8aa3f3", "[BSc] Computer Science Engineering", "Computer Science Engineering", "BSc", "Computer Engineering", 3000, 7),
     ("447f248c5ce4", "[BSc] Mechanical Engineering", "Mechanical Engineering", "BSc", "Mechanical Engineering", 3000, 7),
     ("09a87aab0078", "[BSc] Logistics Engineering", "Logistics Engineering", "BSc", "Engineering", 3000, 7),
     ("2abcbbcd203c", "[BSc] Materials Engineering", "Materials Engineering", "BSc", "Materials Science", 3000, 7),
     ("7fc0676c7f5c", "[BSc] Chemical Engineering", "Chemical Engineering", "BSc", "Chemical Engineering", 3000, 7),
     ("c483a0323e29", "[BA] International Relations", "International Relations", "BA", "Politics", 2400, 6),
     ("8f1ce7ba926e", "[BA] English and American Studies", "English and American Studies", "BA", "Humanities", 2500, 6)]
spec("hu-miskolc", ORG, ["Miskolci Egyetem"], "public", "https://www.uni-miskolc.hu/en/", ("hu", "Hungary", "HUF"), ("hu-miskolc", "Miskolc"),
     {"main": src(P[1][0], "Computer Science Engineering BSc | University of Miskolc", ORG, [f"{P[1][1]} - {ORG}", "Study location Hungary, Miskolc"])},
     [("international", "International students (course page fee)", "The tuition fee on each University of Miskolc course page of its application portal.", "main")])

ENG_LINE = "a demonstrated proficiency in English (B2 level or equivalent: IELTS 6.0, TOEFL 72, GCSE English, Duolingo 100)"
for page, portal, name, deg, field, fee, sem in P:
    q = [f"{portal} - {ORG}", "Study location Hungary, Miskolc", f"Nominal duration {sem} semesters", "Study language English",
         f"Tuition fee €{fee:,} per semester", "Entry qualification High school / secondary education (or higher)"]
    eng = None
    if norm(ENG_LINE) in text(page):
        q.append(ENG_LINE)
        eng = {"test_name": "IELTS / TOEFL / Duolingo (B2)", "min_score": "B2: IELTS 6.0, TOEFL 72, GCSE English or Duolingo 100.", "source": "course"}
    th = f"{name}: no grade cut-off published; a completed secondary education is required (see the course page for the documents and any entry exam)."
    prog("hu-miskolc", f"{deg.lower()}-{slugify(name)}", {"course": src(page, f"{name} {deg} | University of Miskolc", ORG, q)},
         {"name": name, "degree_type": deg, "field": field, "faculty": "", "duration_years": sem / 2, "duration_source": "course", "languages": ["en"],
          "entry_year": "Course page (year not stated)", "platform": "University of Miskolc application portal (apply.uni-miskolc.hu)", "source": "course",
          "summary": f"{name} ({deg}), University of Miskolc; taught in English.", "application_requirements": []},
         [{"residency": "international", "currency": "EUR", "tuition_per_semester": fee, "semesters_quote": f"Nominal duration {sem} semesters",
           "semesters_source": "course", "academic_year": "Course page (year not stated)", "source": "course",
           "note": f"EUR {fee:,} per semester (course page; the academic year isn't stated). Yearly figure our calculation."}],
         adm_all({c: th for c in ("ib", "a-level", "us-hs", "cbse", "international-other")}, "course", english=eng))
    print("wrote", name, "english" if eng else "")

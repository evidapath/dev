"""Harbin Institute of Technology (THE #216): every major in the "2027/2028 Bachelor's Degree Program Major Lists &
CSCA Subjects" spreadsheet attached to HIT's bachelor's admission page (written 2026-11-28). The .xlsx is converted
to text at .research-cache/pages/hit-majors-2027.txt (one line per row; the school cell is merged, so it is carried
down from the row that names it). Fees from the admission page: Chinese-taught CNY 20,000/year, English-taught
CNY 26,000/year; English-taught programmes run only with at least 20 students.
  python3 -I scripts/research/gen/cn_hit.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES
from us_fields import field_for

ORG = "Harbin Institute of Technology"
FQ = ["Tuition Chinese-taught CNY 20,000/year (approximately USD 3,000) English-taught CNY 26,000/year (approximately USD 3,900)",
      "Insurance CNY 10 00/year", "Accommodation Fee CNY 800-1,000/month/bed",
      "English-taught undergraduate programs require a minimum of 20 students. Programs that do not reach this number will not run.",
      "Address:No.92 West Dazhi Street,Nangang District,Harbin 150001, P.R. China"]
F = src("904a4e29e8ce", "Bachelor | Study at HIT | Harbin Institute of Technology", ORG, FQ + ["HIT International Student Application Portal"])
M = src("f44c60566243", "Harbin Institute of Technology (English site)", ORG, ["Copyright Harbin Institute of Technology All Rights Reserved No. 92 Xidazhi Street, Nangang District, Harbin"])
lines = (PAGES / "hit-majors-2027.txt").read_text().splitlines()
TITLE = lines[0].split(" | ")[0]
spec("cn-hit", ORG, ["HIT", "Harbin Inst. of Technology"], "public", "https://en.hit.edu.cn", ("cn", "China", "CNY"), ("cn-harbin", "Harbin"),
     {"main": M, "fees": F}, [("international", "International students", "HIT tuition for international undergraduates (CNY/year).", "fees")])
school, seen = "", set()
for l in lines[2:]:
    c = l.split(" | ")
    if len(c) < 5 or not c[2]:
        continue
    school = c[1] or school
    zh_en, lang, dur = c[2], c[3], c[4]
    en = zh_en.split(" ", 1)[1] if " " in zh_en else zh_en
    eng = lang.endswith("English")
    sch_en = school.split(" ", 1)[1] if " " in school else school
    C = src("hit-majors-2027", "2027/2028 Bachelor's Degree Program Major Lists | Harbin Institute of Technology", ORG, [TITLE, l.strip(" |")])
    slug = slugify(f"{'en' if eng else 'zh'} {en}")[:70].rstrip("-")
    if slug in seen:
        continue
    seen.add(slug)
    fee = 26000 if eng else 20000
    prog("cn-hit", slug, {"course": C, "fees": F},
         {"name": f"{en} ({'English' if eng else 'Chinese'}-taught)", "degree_type": "Bachelor", "field": field_for(en), "faculty": "",
          "duration_years": float(dur), "duration_source": "course", "languages": ["en" if eng else "zh"], "entry_year": "2027/2028", "platform": "", "source": "course",
          "summary": f"{en}, {sch_en}, Harbin Institute of Technology; {'English' if eng else 'Chinese'}-taught, {dur.rstrip('0').rstrip('.')} years.",
          "application_requirements": []},
         [{"residency": "international", "currency": "CNY", "tuition_annual": fee, "academic_year": "2027/2028 intake", "source": "fees",
           "note": (f"English-taught tuition CNY 26,000/year; English-taught undergraduate programs require a minimum of 20 students." if eng
                    else "Chinese-taught tuition CNY 20,000/year.")}], [])
print("cn-hit", len(seen))

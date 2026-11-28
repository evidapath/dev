"""Tianjin University (THE #189): every programme in its "Catalog of Undergraduate Programs" for international
students (spreadsheet linked from the 2027 undergraduate admissions page, application period to May 31, 2027),
with each row's length (学制), teaching language and tuition (written 2026-11-28). The .xls is converted to text at
.research-cache/pages/tju-catalog-2027.txt (one line per row) so every quote can be checked. Left out: the
Chinese-taught Clinical Medicine row, listed as 4Y (a likely sheet error; to check).
  python3 -I scripts/research/gen/cn_tju.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES
from us_fields import field_for

ORG = "Tianjin University"
G = src("8f2a842786e3", "Undergraduate admissions (2027) | International School of Education, Tianjin University", ORG,
        ["The standard duration is 4 years (5 years for Architecture).",
         "Bachelor's general programs: 20,000 RMB/year; Other programs: 26,000 RMB/year (programs in the School of Architecture / Software Engineering)",
         "Tianjin University"])
rows = [l.rstrip("\n").split(" | ") for l in (PAGES / "tju-catalog-2027.txt").read_text().splitlines()[2:]]
first, seen = None, set()
for r in rows:
    zh, en, _, _, school, _, _, dur, _, deg, _, lang, fee = r[:13]
    if en == "Clinical Medicine" and lang == "Chinese":
        continue
    y = int(dur.rstrip("Y"))
    line = " | ".join(r)
    C = src("tju-catalog-2027", "Catalog of Undergraduate Programs (2027) | Tianjin University", ORG,
            ["Tianjin University Catalog of Undergraduate Programs (international students, 2027)", line])
    if first is None:
        spec("cn-tju", ORG, ["TJU", "Tianjin Univ."], "public", "https://www.tju.edu.cn", ("cn", "China", "CNY"), ("cn-tianjin", "Tianjin"), {"main": G},
             [("international", "International students", "Tianjin University tuition for international undergraduates (RMB/year).", "main")])
        first = True
    slug = slugify(f"{lang[:2]} {en} {school}")[:70].rstrip("-")
    if slug in seen:
        continue
    seen.add(slug)
    prog("cn-tju", slug, {"course": C},
         {"name": f"{en} ({lang}-taught)", "degree_type": deg, "field": field_for(en), "faculty": school, "duration_years": y, "duration_source": "course",
          "languages": ["en" if lang == "English" else "zh"], "entry_year": "2027", "platform": "", "source": "course",
          "summary": f"{en} ({zh}), {school}, Tianjin University; {lang}-taught, {y} years.", "application_requirements": []},
         [{"residency": "international", "currency": "CNY", "tuition_annual": int(fee), "academic_year": "2027 entry", "source": "course",
           "note": f"Tuition {int(fee):,} RMB a year (programme catalogue); application fee 500 RMB."}], [])
print("cn-tju", len(seen))

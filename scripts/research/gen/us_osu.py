"""The Ohio State University, Columbus (THE #149): every bachelor's major offered on the Columbus campus in
Undergraduate Admissions' "Majors and degrees" list (written 2026-11-28). Left out: associate degrees, regional-
campus-only majors, and completion programmes for licensed practitioners (RN to BSN, dental hygiene completion).
Costs: Student Financial Aid, International Students, "Cost of Attendance 2026-2027 Academic Year", Columbus campus,
non-Ohio resident living on campus (includes the International Student Fee). Length: Office of Undergraduate
Education, "Academic Progress to Degree" (121 credit hours, planned to complete in four years).
  python3 -I scripts/research/gen/us_osu.py
"""
import os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES
from us_fields import field_for

H = (PAGES / "b0ecf10f1204.html").read_text(errors="replace")
T = re.sub(r"\s+", " ", (PAGES / "b0ecf10f1204.txt").read_text(errors="replace"))
tab = H[H.find("stacktable"):]
cell = r'</a></th></tr><tr class=""><th class="st-head-row" colspan="2">Degree</th></tr><tr class=""><td class="st-key"></td><td class="st-val st-val ">([^<]*)</td></tr><tr class=""><th class="st-head-row" colspan="2">Campus</th></tr><tr class=""><td class="st-key"></td><td class="st-val st-val ">([^<]*)</td></tr><tr class=""><th class="st-head-row" colspan="2">College/School</th></tr><tr class=""><td class="st-key"></td><td class="st-val st-val ">([^<]*)</td>'
ents = {}
for m in re.finditer(r'majors/detail/(\d+)">([^<]+)' + cell, tab):
    ents.setdefault(m.group(1), tuple(html.unescape(x).strip() for x in m.groups()[1:]))
DEG = {"BS": "B.S.", "BA": "B.A.", "BFA": "B.F.A.", "BM": "B.M.", "BME": "B.M.E.", "BSD": "B.S.D.", "BSEd": "B.S.Ed."}
items, quotes = [], []
for name, degs, campus, col in ents.values():
    if "Columbus" not in campus or "RN to BSN" in name or "completion program" in name:
        continue
    degs_l = [d.strip() for d in degs.split(",")]
    if not all(d in DEG for d in degs_l):
        continue
    q = re.search(rf"Degree: {re.escape(degs)} (?:College|School|Center): {re.escape(col)} Campus: [A-Za-z ,]*?Columbus", T)
    if not q or name not in T:
        print("noquote", name); continue
    quotes += [name, q.group(0)]
    for d in degs_l:
        items.append((name, DEG[d], col))

ORG = "The Ohio State University"
ML = src("b0ecf10f1204", "Majors and degrees | Undergraduate Admissions | The Ohio State University", ORG,
         ["Undergraduate Admissions The Ohio State University"] + list(dict.fromkeys(quotes)))
MY = src("979c1c8dc0ba", "Academic Progress to Degree | Office of Undergraduate Education | The Ohio State University", ORG,
         ["Most baccalaureate degrees require 121 semester credit hours, so to complete these requirements in four years, careful planning is required."])
MF = src("70797df164e7", "Cost of attendance, International Students | Student Financial Aid | The Ohio State University", ORG,
         ["Cost of Attendance 2026-2027 Academic Year Ohio State University full-time, two semester academic year costs reflected below may vary by program",
          "Non-Ohio resident: Living on campus Category Estimated Cost Direct Costs Tuition and fees $14,034 Non-resident fees $30,220",
          "International Student Fee $3,104", "Living expenses: housing and food $15,630",
          "The Ohio State University © 2026, Office of Strategic Enrollment Management | Student Financial Aid Student Academic Services Building | 281 W Lane Ave, Columbus, OH 43210"])
spec("us-osu", ORG, ["Ohio State", "Ohio State University", "OSU"], "public", "https://www.osu.edu", ("us", "United States", "USD"), ("us-columbus-oh", "Columbus"),
     {"main": MF, "coa": MF}, [("international", "International students (Columbus, non-Ohio resident)", "Ohio State 2026-2027 cost of attendance for international undergraduates.", "coa")])
COST = {"residency": "international", "currency": "USD", "tuition_formula": "4*(14034+30220+3104)/4", "academic_year": "2026-2027", "source": "coa",
        "note": "International students, Columbus, 2026-2027: tuition and fees $14,034 + non-resident fees $30,220 + International Student Fee $3,104 = $47,358 (our calculation); costs may vary by program.",
        "living": {"monthly": [], "months": 9, "yearly": [15630], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                   "note": "Living on campus, 2026-2027: housing and food $15,630."}}
seen = set()
for name, deg, col in items:
    slug = slugify(f"{deg} {name}")[:60].rstrip("-")
    if slug in seen:
        continue
    seen.add(slug)
    prog("us-osu", slug, {"course": ML, "y": MY, "coa": MF},
         {"name": name, "degree_type": deg, "field": field_for(name.split(" – ")[0]), "faculty": "", "duration_years": 4, "duration_source": "y",
          "languages": ["en"], "entry_year": "2026-2027", "platform": "", "source": "course",
          "summary": f"{name} ({deg}), {col}, The Ohio State University (Columbus); Ohio State plans bachelor's degrees to be completed in four years.",
          "application_requirements": []},
         [COST], [])
print("us-osu", len(seen))

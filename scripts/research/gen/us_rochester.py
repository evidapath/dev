"""University of Rochester (THE #92 =): every bachelor's programme in the 2026-2027 Undergraduate Bulletin's
inventory of registered programmes for the School of Arts & Sciences and the Hajim School of Engineering & Applied
Sciences (written 2026-11-28). Combined bachelor's/master's entries (BS/MS, BA/MS) are left out; "BS, BS/MS" is
stored as the BS. Eastman School of Music and the School of Nursing have their own costs and are not added here.
Costs: Financial Aid "2026-2027 Cost of Attendance", residential students (flat tuition for full-time students).
  python3 -I scripts/research/gen/us_rochester.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES
from us_fields import field_for

T = re.sub(r"\s+", " ", (PAGES / "90502b75f247.txt").read_text(errors="replace"))
a = T.index("School of Arts & Sciences Program Code Hegis Code Program Name Degree")
h = T.index("Edmund A. Hajim School of Engineering & Applied Sciences Program Code Hegis Code Program Name Degree")
e = T.index("Report a Digital Accessibility Barrier")
items, quotes = [], []
for blk, school in ((T[a:h], "School of Arts & Sciences"), (T[h:e], "Hajim School of Engineering & Applied Sciences")):
    for m in re.finditer(r"\d{5} [\d./]+(?:/ [\d.]+)? +(.+?) (BS, BS/MS|BA/MS|BS/MS|BA|BS)(?= \d{5}| Edmund| Report|$)", blk):
        name, deg = m.group(1).strip(), m.group(2)
        if deg in ("BA/MS", "BS/MS"):
            continue
        items.append((name, "BS" if deg.startswith("BS") else deg, school)); quotes.append(f"{name} {deg}")

ORG = "University of Rochester"
ML = src("90502b75f247", "Programs: SAS, Hajim, and Simon | Undergraduate Bulletin | University of Rochester", ORG,
         ["The New York State Education Department has authorized the University of Rochester to offer the undergraduate-level programs which appear in the following inventory of registered programs.",
          "2026-2027 Printable Undergraduate Bulletin (pdf)", "University of Rochester 127 Lattimore Hall P.O. Box 270038 Rochester, NY 14627"] + quotes)
MY = src("5815ce29fbc1", "Bachelor's Degree Requirements | Undergraduate Studies | University of Rochester", ORG,
         ["Eight semesters of approved coursework (normally 128 credits) with an average of \"C\" or better."])
MF = src("c9a5f03f6429", "Undergraduate Tuition & Expenses | Financial Aid & Scholarships | University of Rochester", ORG,
         ["Undergraduate tuition is assessed at a flat rate for all full-time students",
          "2026-2027 Cost of Attendance Item Residential Students Off-Campus Students Students Living with Parents Tuition $71,750 $71,750 $71,750 Mandatory Fees $1,622 $1,622 $1,622 Housing $12,822 $5,716 $1,500 Food $8,506 $6,670 $5,170"])
spec("us-rochester", ORG, ["UR", "U of R"], "private", "https://www.rochester.edu", ("us", "United States", "USD"), ("us-rochester-ny", "Rochester"),
     {"main": ML, "coa": MF}, [("international", "All full-time undergraduates", "University of Rochester flat full-time undergraduate tuition, 2026-2027.", "coa")])
COST = {"residency": "international", "currency": "USD", "tuition_annual": 71750, "mandatory_fees_annual": 1622, "academic_year": "2026-2027", "source": "coa",
        "note": "2026-2027: tuition $71,750 (flat rate for full-time students) plus mandatory fees $1,622.",
        "living": {"monthly": [], "months": 9, "yearly": [12822, 8506], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                   "note": "Residential students 2026-2027: housing $12,822 + food $8,506 = $21,328 (our calculation)."}}
seen = set()
for name, deg, school in items:
    slug = slugify(f"{deg} {name}")[:60].rstrip("-")
    if slug in seen:
        continue
    seen.add(slug)
    prog("us-rochester", slug, {"course": ML, "y": MY, "coa": MF},
         {"name": name, "degree_type": deg, "field": field_for(name.split(":")[0] if ":" in name and name.startswith(("English", "Dance", "Chemistry")) else name),
          "faculty": school, "duration_years": 4, "duration_source": "y", "languages": ["en"], "entry_year": "2026-2027", "platform": "", "source": "course",
          "summary": f"{name} ({deg}), {school}, University of Rochester; bachelor's degrees require eight semesters of approved coursework.",
          "application_requirements": []},
         [COST], [])
print("us-rochester", len(seen))

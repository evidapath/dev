"""Columbia University, Columbia College (THE #68): every major on Columbia College's "Majors, Concentrations, and
Programs of Study" page (written 2026-11-28). Columbia Engineering (SEAS) has its own programme list and is not
added here. Costs: Columbia undergraduate admissions "2026-2027 Cost of Attendance" (Columbia College). The
Bulletin's fee table gives mandatory fees of $3,430 against $4,160 on the admissions page; the admissions figure is
stored (the higher one) and the Bulletin is not used for fees.
  python3 -I scripts/research/gen/us_columbia.py
"""
import os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES
from us_fields import field_for

H = (PAGES / "b2cb702e0474.html").read_text(errors="replace")
a = H.index("can choose a major in one of the following subjects"); b = H.index("Minors", a)
majors = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip() for x in re.findall(r"<a[^>]*>(.*?)</a>", H[a:b], re.S)]
majors = [m for m in majors if m and m not in ("Bulletin", "Columbia College Bulletin")]
T = re.sub(r"\s+", " ", (PAGES / "b2cb702e0474.txt").read_text(errors="replace"))
blk = T[T.index("Columbia College students can choose a major in one of the following subjects"):T.index("Minors Most students")]
missing = [m for m in majors if m not in blk]
assert not missing, missing

ORG = "Columbia University"
ML = src("b2cb702e0474", "Majors, Concentrations, and Programs of Study | Columbia College", ORG,
         ["All Columbia College students must complete a major.",
          "a student pursuing a special program must also complete a major in order to earn the B.A. degree."] + majors)
MD = src("8ce8dfba4c1a", "Departments, Programs, and Courses | Columbia College Bulletin 2026-2027", ORG,
         ["Columbia College Columbia University in the City of New York 208 Hamilton Hall , Mail Code 2805 1130 Amsterdam Avenue New York, NY 10027",
          "© 2026-2027 Columbia University"])
MY = src("9cb9474912f1", "Academic Requirements | Columbia College Bulletin 2026-2027", ORG,
         ["Students are expected to fulfill their degree requirements in eight semesters"])
MF = src("d806c05d7695", "Cost & Aid | Columbia Undergraduate Admissions", ORG,
         ["2026-2027 Cost of Attendance Tuition $72,800 Fees $4,160 Food $7,128 Housing $12,522 Books and supplies $1,320",
          "First-year students are required to live on campus."])
spec("us-columbia", ORG, ["Columbia", "Columbia College", "Columbia University in the City of New York"], "private", "https://www.columbia.edu",
     ("us", "United States", "USD"), ("us-new-york-ny", "New York"), {"main": MD, "coa": MF},
     [("international", "All undergraduates (Columbia College)", "Columbia College cost of attendance, 2026-2027.", "coa")])
COST = {"residency": "international", "currency": "USD", "tuition_annual": 72800, "mandatory_fees_annual": 4160, "academic_year": "2026-2027", "source": "coa",
        "note": "2026-2027: tuition $72,800; fees $4,160.",
        "living": {"monthly": [], "months": 9, "yearly": [12522, 7128], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                   "note": "Columbia College 2026-2027 budget: housing $12,522 + food $7,128 = $19,650 (our calculation); first-years live on campus."}}
seen = set()
for name in majors:
    slug = slugify(f"ba {name}")[:60].rstrip("-")
    if slug in seen:
        continue
    seen.add(slug)
    prog("us-columbia", slug, {"course": ML, "y": MY, "coa": MF},
         {"name": name, "degree_type": "B.A.", "field": field_for(name.split(" — ")[0]), "faculty": "Columbia College",
          "duration_years": 4, "duration_source": "y", "languages": ["en"], "entry_year": "2026-2027", "platform": "", "source": "course",
          "summary": f"{name} major, Columbia College, Columbia University (B.A.); students are expected to complete the degree in eight semesters.",
          "application_requirements": []},
         [COST], [])
print("us-columbia", len(seen))

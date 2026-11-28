"""University of Maryland, College Park (THE #167 =): every major in the 2026-2027 Undergraduate Catalog's
"Programs" navigation (links ending "-major/") (written 2026-11-28). Costs: catalog "Undergraduate Tuition and Fees",
2026-2027, residents of other states and other countries. The differential tuition for full-time juniors and seniors
majoring in Business, Engineering or Computer Science is added for two of the four years (our calculation); it is
applied to Smith School and Clark School majors and the Computer Science major (not to the AI or Immersive Media Design majors). Length: Student Success Office
advising policies ("To complete most curricula in four academic years ...").
  python3 -I scripts/research/gen/us_umd.py
"""
import os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES
from us_fields import field_for

H = (PAGES / "ee9f0022a260.html").read_text(errors="replace")
T = re.sub(r"\s+", " ", (PAGES / "ee9f0022a260.txt").read_text(errors="replace"))
COL = {"agriculture-natural-resources": "College of Agriculture and Natural Resources", "architecture-planning-preservation": "School of Architecture, Planning, and Preservation",
       "arts-humanities": "College of Arts and Humanities", "behavioral-social-sciences": "College of Behavioral and Social Sciences",
       "business": "The Robert H. Smith School of Business", "computer-mathematical-natural-sciences": "College of Computer, Mathematical, and Natural Sciences",
       "education": "College of Education", "engineering": "A. James Clark School of Engineering", "information-studies": "College of Information",
       "journalism": "Philip Merrill College of Journalism", "public-health": "School of Public Health", "public-policy": "School of Public Policy"}
items = {}
for path, txt in re.findall(r'<a href="(/undergraduate/colleges-schools/[^"]+-major/)">([^<]+)</a>', H):
    name = re.sub(r"\s+", " ", html.unescape(txt)).replace("​", "").strip()
    if not name.endswith(")") and not name.endswith("Major"):
        continue
    seg = path.split("/")
    col = seg[3]
    diff = col in ("business", "engineering") or name == "Computer Science Major"
    items.setdefault(path, (name, COL.get(col, ""), diff))

ORG = "University of Maryland"
names = sorted({n for n, _, _ in items.values()})
miss = [n for n in names if n not in T]
assert not miss, miss
ML = src("ee9f0022a260", "Programs | University of Maryland Undergraduate Catalog 2026-2027", ORG, names + ["The Flagship Institution of the University System of Maryland College Park, MD 20742, USA"])
MY = src("4f70bdcd1d1f", "Advising Policies | Student Success Office | University of Maryland", ORG,
         ["To complete most curricula in four academic years, students must average 15 credits per semester toward the degree."])
FQ = ("2026-2027 Residents of the District of Columbia, Other States, and Other Countries Tuition and Fees-Academic Year Fee Total Academic Year Cost (fall and spring semesters) Tuition $42,266.00 "
      "Additional Differential Tuition for full-time juniors and seniors who are majoring in Business, Engineering, or Computer Science (regardless of residency classification) $3,375.00 "
      "Mandatory Fees (includes Tech fee). Maximum charged to all students registered for 9 or more credits $1,820.00 Board Contract (Resident Dining Plan - Base Plan) $6,820.00 "
      "Room (Standard 2-person w/AC, includes Telecom fee) $10,290.00")
MF = src("ef3045952fde", "Undergraduate Tuition and Fees | University of Maryland Undergraduate Catalog 2026-2027", ORG,
         [FQ, "Undergraduate Tuition and Fees | University of Maryland Catalog"])
MA = src("ee9f0022a260", "Programs | University of Maryland Undergraduate Catalog 2026-2027", ORG,
         ["Undergraduate Programs | University of Maryland Catalog", "The Flagship Institution of the University System of Maryland College Park, MD 20742, USA"])
spec("us-umd", ORG, ["University of Maryland, College Park", "UMD", "Maryland"], "public", "https://umd.edu", ("us", "United States", "USD"), ("us-college-park-md", "College Park"),
     {"main": MA, "coa": MF}, [("nonresident", "Out-of-state and international students", "UMD tuition and fees for residents of other states and other countries, 2026-2027.", "coa")])
seen = set()
for name, col, diff in items.values():
    base = re.sub(r" Major(?: \([A-Z]+\))?$| \((B\.A\.|B\.S\.)[^)]*\)$", "", name).strip()
    slug = slugify(name)[:60].rstrip("-")
    if slug in seen:
        continue
    seen.add(slug)
    cost = {"residency": "nonresident", "currency": "USD", "tuition_formula": "(2*42266+2*(42266+3375))/4" if diff else "4*42266/4",
            "mandatory_fees_annual": 1820, "academic_year": "2026-2027", "source": "coa",
            "note": ("2026-2027 out-of-state: tuition $42,266; plus differential tuition $3,375 a year for full-time juniors and seniors in Business, Engineering or Computer Science (averaged over four years, our calculation); mandatory fees $1,820."
                     if diff else "2026-2027 out-of-state: tuition $42,266; mandatory fees $1,820."),
            "living": {"monthly": [], "months": 9, "yearly": [10290, 6820], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                       "note": "Standard 2-person room $10,290 + base dining plan $6,820 = $17,110 (our calculation), 2026-2027."}}
    prog("us-umd", slug, {"course": ML, "y": MY, "coa": MF},
         {"name": base, "degree_type": "Bachelor's (major)", "field": field_for(base), "faculty": "", "duration_years": 4, "duration_source": "y",
          "languages": ["en"], "entry_year": "2026-2027", "platform": "", "source": "course",
          "summary": f"{name}, {col or 'University of Maryland'}, University of Maryland (College Park); most curricula are completed in four academic years.",
          "application_requirements": []},
         [cost], [])
print("us-umd", len(seen))

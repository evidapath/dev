"""Northwestern University (THE #115 =): every program offered as a "Major" in Undergraduate Admissions' "Majors
and Minors" table (written 2026-11-28). Adjunct majors (taken only alongside another major) and minors are left
out. Costs: Northwestern Now, "Northwestern sets tuition and fees for the 2026-2027 academic year" (tuition,
standard room and board, fees). Length: Academic Catalog 2026-2027, Undergraduate Registration Requirement
("a four-year degree program"); dual bachelor's degrees take longer and are not stored.
  python3 -I scripts/research/gen/us_northwestern.py
"""
import os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES
from us_fields import field_for

SCHOOL = {"WCAS": "Weinberg College of Arts and Sciences", "Communication": "School of Communication", "SESP": "School of Education and Social Policy",
          "McCormick": "McCormick School of Engineering", "Medill": "Medill School of Journalism, Media, Integrated Marketing Communications",
          "Music": "Bienen School of Music", "Kellogg": "Kellogg School of Management"}
H = (PAGES / "b5a966d6380c.html").read_text(errors="replace")
T = re.sub(r"\s+", " ", (PAGES / "b5a966d6380c.txt").read_text(errors="replace"))
items = []
for row in re.findall(r"<tr[^>]*>(.*?)</tr>", H, re.S):
    m = re.search(r'<div class="program">(.*?)</div>', row)
    if not m:
        continue
    name = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))).strip()
    opts = [re.sub(r"\s+", " ", html.unescape(o)).strip() for o in re.findall(r"</span>([^<]+)</a>", row)]
    sch = re.findall(r'<td style="display:none;">([^<;]*)</td>', row)
    if "Major" not in opts:
        continue
    q = f"{name} {name} Major"
    assert q in T, q
    fac = SCHOOL.get(sch[-1].strip(), "") if sch else ""
    items.append((name, fac, q))

ORG = "Northwestern University"
ML = src("b5a966d6380c", "Majors and Minors | Undergraduate Admissions | Northwestern University", ORG,
         ["Majors and Minors: Undergraduate Admissions - Northwestern University", "633 Clark Street, Suite G547 Evanston, IL 60208"] + [q for _, _, q in items])
MY = src("3721adcbc544", "Undergraduate Registration Requirement | Northwestern University Academic Catalog 2026-2027", ORG,
         ["A student entering as a first-year student in a four-year degree program must be registered at Northwestern for at least 9 quarters"])
MF = src("e8b9c3331e65", "Northwestern sets tuition and fees for the 2026-2027 academic year | Northwestern Now", ORG,
         ["Northwestern University announced a 3.5% increase in undergraduate tuition for the 2026-2027 school year. Undergraduate tuition will be $71,802; standard room and board will be $22,941; and fees will be $1,260."])
spec("us-northwestern", ORG, ["Northwestern", "NU"], "private", "https://www.northwestern.edu", ("us", "United States", "USD"), ("us-evanston-il", "Evanston"),
     {"main": ML, "coa": MF}, [("international", "All undergraduates", "Northwestern undergraduate tuition and fees, 2026-2027.", "coa")])
COST = {"residency": "international", "currency": "USD", "tuition_annual": 71802, "mandatory_fees_annual": 1260, "academic_year": "2026-2027", "source": "coa",
        "note": "2026-2027: undergraduate tuition $71,802; fees $1,260.",
        "living": {"monthly": [], "months": 9, "yearly": [22941], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                   "note": "Standard room and board 2026-2027: $22,941."}}
seen = set()
for name, fac, _ in items:
    slug = slugify(f"major {name}")[:60].rstrip("-")
    if slug in seen:
        continue
    seen.add(slug)
    prog("us-northwestern", slug, {"course": ML, "y": MY, "coa": MF},
         {"name": name, "degree_type": "Bachelor's (major)", "field": field_for(name), "faculty": fac, "duration_years": 4, "duration_source": "y",
          "languages": ["en"], "entry_year": "2026-2027", "platform": "", "source": "course",
          "summary": f"{name} major, {fac or 'Northwestern University'}, Northwestern University; a four-year degree programme.",
          "application_requirements": []},
         [COST], [])
print("us-northwestern", len(seen))

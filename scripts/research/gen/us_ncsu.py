"""North Carolina State University (THE #140): every bachelor's major in the 2026-2027 Undergraduate Catalog
"Majors" index (written 2026-11-28). Concentrations are folded into their major ("Animal Science (BS): Industry
Concentration" -> Animal Science (BS)). Left out: associate degrees (AAS), online-only entries, "Engineering First
Year" (no degree), and "Architecture (Bachelor): One-Year Professional Degree" (a fifth-year degree).
Costs: Undergraduate Student Estimated Cost of Attendance, Academic Year 2026-27, living on campus, out-of-state.
Length: catalog "Length of Time to Graduation" (four years); the catalog notes "designated five-year programs"
without naming them, so the summary says so.
  python3 -I scripts/research/gen/us_ncsu.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES
from us_fields import field_for

T = re.sub(r"\s+", " ", (PAGES / "98520311626a.txt").read_text(errors="replace"))
blk = T[T.index("Majors # A B C D E F G H I J K L M N O P Q R S T U V W X Y Z") :]
blk = blk[: blk.index("Minors", 100)] if "Minors" in blk[100:] else blk
DEG = {"BS": "B.S.", "BA": "B.A.", "Bachelor": "Bachelor", "BFA": "B.F.A.", "BSW": "B.S.W.", "BSE": "B.S.E."}
items, quotes = {}, set()
# a major's name starts right after the previous entry, a "... Concentration", or an index letter ("B Biochemistry")
for m in re.finditer(r"(?:(?<=\) )|(?<=Concentration )|(?<=Concentrations )|(?<=Z )|(?<= [A-Z] ))([A-Z][A-Za-z ,&/'’\-]+?) \((BS|BA|BFA|BSW|BSE|Bachelor)\)(: Online)?", blk):
    name, deg, online = m.group(1).strip(), m.group(2), m.group(3)
    name = re.sub(r"^(?:[A-Z] )+", "", re.split(r" [A-Z] ", " " + name)[-1].strip())  # text after the last index letter
    if online or name.startswith("Inter-College") or name.startswith("Architecture") or "Concentration" in name or "First Year" in name:
        continue
    key = (name, deg)
    if key not in items:
        items[key] = f"{name} ({deg})"; quotes.add(f"{name} ({deg})")

ORG = "NC State University"
ML = src("98520311626a", "Undergraduate | North Carolina State University Catalog 2026-2027", ORG,
         ["Catalog 2026-2027 Home Department of Registration and Records 2831 Thurman Drive Harris Hall, Room 1000 Campus Box 7313 Raleigh, NC 27695"] + sorted(quotes))
MY = src("ba471d6a3aa5", "Graduation Requirements | North Carolina State University Catalog", ORG,
         ["The normal and expected length of time to graduation for a baccalaureate degree is four years (average of eight semesters)",
          "exceptions include designated five-year programs, and programs in certain colleges."])
MF = src("8eaa61045269", "Undergraduate Student Estimated Cost of Attendance | NC State Student Services Center", ORG,
         ["Academic Year 2026-27 Academic Year 2026-27 North Carolina Residents Out-of-State Residents Tuition & Fees $9,247 $34,961 Books & Supplies $642 $642 Housing $8,738 $8,738 Food $6,684 $6,684",
          "The figures below are for full-time fall and spring semester enrollment",
          "Harris Hall 2831 Thurman Drive Raleigh, North Carolina 27695", "© 2026 NC State University. All rights reserved."])
spec("us-ncsu", ORG, ["North Carolina State University", "NC State", "NCSU"], "public", "https://www.ncsu.edu", ("us", "United States", "USD"), ("us-raleigh-nc", "Raleigh"),
     {"main": MF, "coa": MF, "list": ML}, [("nonresident", "Out-of-state residents", "NC State estimated cost of attendance for out-of-state undergraduates.", "coa")])
COST = {"residency": "nonresident", "currency": "USD", "tuition_annual": 34961, "academic_year": "2026-27", "source": "coa",
        "note": "Out-of-state tuition & fees $34,961 a year (full-time fall and spring semesters; estimate).",
        "living": {"monthly": [], "months": 9, "yearly": [8738, 6684], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                   "note": "Living on campus, 2026-27: housing $8,738 + food $6,684 = $15,422 (our calculation)."}}
seen = set()
for (name, deg), q in items.items():
    slug = slugify(f"{deg} {name}")[:60].rstrip("-")
    if slug in seen:
        continue
    seen.add(slug)
    prog("us-ncsu", slug, {"course": ML, "y": MY, "coa": MF},
         {"name": name, "degree_type": DEG[deg], "field": field_for(name), "faculty": "", "duration_years": 4, "duration_source": "y",
          "languages": ["en"], "entry_year": "2026-2027 catalog", "platform": "", "source": "course",
          "summary": f"{name} ({deg}), NC State University (Raleigh); the catalog's normal time to a bachelor's degree is four years, with some designated five-year programmes.",
          "application_requirements": []},
         [COST], [])
print("us-ncsu", len(seen))

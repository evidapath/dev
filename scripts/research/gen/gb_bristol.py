"""University of Bristol: base records + three computing BSc (written 2026-11-26). THE queue #44.

Source: each 2027 course page on bristol.ac.uk/study/undergraduate/2027: "Programme duration 3 year(s) full-time",
"International students Year Year 1 fee 2027/28 £N", A-level standard and contextual offers, IB Diploma.
English requirement: the page lists IELTS among options but the band isn't in the saved text, so none is stored.
No living costs read.
  python3 -I scripts/research/gen/gb_bristol.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify, PAGES

ORG = "University of Bristol"
def t(p): return re.sub(r"\s+", " ", (PAGES / f"{p}.txt").read_text())
def grab(p, pat):
    m = re.search(pat, t(p)); assert m, (p, pat); return m.group(0)

P = [("f94a377fde49", "Computer Science"), ("62358fc85878", "Computer Science with Artificial Intelligence"),
     ("0fff932750c1", "Mathematics and Computer Science")]
spec("gb-bristol", ORG, ["Bristol"], "public", "https://www.bristol.ac.uk", ("gb", "United Kingdom", "GBP"), ("gb-bristol", "Bristol"),
     {"main": src(P[0][0], "BSc Computer Science | University of Bristol", ORG, ["BSc Computer Science | Study at Bristol | University of Bristol"])},
     [("international", "International students", "University of Bristol international Year 1 fee.", "main")])
for page, name in P:
    fee_q = grab(page, r"International students Year Year 1 fee 2027/28 £[\d,]+")
    fee = int(fee_q.rsplit("£", 1)[1].replace(",", ""))
    al_q = grab(page, r"A-level standard offer: \S+ A-level contextual offer: \S+")
    ib_q = grab(page, r"International Baccalaureate Diploma \d+ points overall with 18 at Higher Level, including 7 at Higher Level in Mathematics \(either Analysis and Approaches or Applications and Interpretations\)")
    dur_q = grab(page, r"Programme duration 3 year\(s\) full-time")
    std, ctx = re.search(r"standard offer: (\S+) A-level contextual offer: (\S+)", al_q).groups()
    pts = re.search(r"Diploma (\d+) points", ib_q).group(1)
    prog("gb-bristol", slugify(f"bsc {name}"),
         {"course": src(page, f"BSc {name} | University of Bristol", ORG, [f"BSc {name} | Study at Bristol | University of Bristol", dur_q, fee_q, al_q, ib_q])},
         {"name": name, "degree_type": "BSc", "field": "Computer Science", "faculty": "", "duration_years": 3, "duration_source": "course", "languages": [],
          "entry_year": "2027", "platform": "UCAS", "source": "course", "summary": f"BSc {name}, University of Bristol; 3 years full-time.",
          "application_requirements": []},
         [{"residency": "international", "currency": "GBP", "tuition_annual": fee, "academic_year": "2027/28", "source": "course",
           "note": f"International students, Year 1 fee 2027/28: £{fee:,} (course page)."}],
         adm_all({"a-level": f"{name}: A-level standard offer {std} (contextual offer {ctx}).",
                  "ib": f"{name}: IB Diploma {pts} points overall with 18 at Higher Level, including 7 at Higher Level in Mathematics."}, "course"))
    print("wrote", name, fee, std, pts)

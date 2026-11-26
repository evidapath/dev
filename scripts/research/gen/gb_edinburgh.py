"""University of Edinburgh: base records + three computing BSc (written 2026-11-26). THE queue #19.

Sources, all study.ed.ac.uk (rendered with bfetch.sh):
  - programme page: "Award BSc (Hons) Duration of study 4 years ... Start date September 2027"; living costs
    ("£1,546 each month ... £18,552 for a full year");
  - entry requirements page: A level and IB offer ranges ("grades most applicants needed to receive an offer
    in recent years"), IELTS;
  - fee lookup (2027-2028 entry): "International/EU fee rate" per year.
  python3 -I scripts/research/gen/gb_edinburgh.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify, PAGES

ORG = "The University of Edinburgh"
def t(p): return re.sub(r"\s+", " ", (PAGES / f"{p}.txt").read_text())
def grab(p, pat):
    m = re.search(pat, t(p)); assert m, (p, pat); return m.group(0)

# main page, entry page, fee page, name, field
P = [("a20690111782", "2cf877e7b99e", "4014f7f2f300", "Computer Science", "Computer Science"),
     ("6587f7ef0e16", "c0902af8decb", "e5d681becfc4", "Computer Science and Mathematics", "Computer Science"),
     ("9c3a0968530c", "d52a213eae43", "4b907a21c37a", "Artificial Intelligence and Computer Science", "Computer Science")]
LIV_Q = "we estimate that it will cost an average of £1,546 each month to live in Edinburgh as a single undergraduate student. This equates to £13,914 for a 39-week academic year and £18,552 for a full year"
main0 = src(P[0][0], "Computer Science BSc (Hons) | The University of Edinburgh", ORG, [LIV_Q, "The University of Edinburgh is a charitable body, registered in Sco"])
spec("gb-edinburgh", ORG, ["Edinburgh", "University of Edinburgh"], "public", "https://www.ed.ac.uk", ("gb", "United Kingdom", "GBP"), ("gb-edinburgh", "Edinburgh"),
     {"main": main0}, [("international", "International/EU students", "The University of Edinburgh's International/EU fee rate.", "main")])

for main, req, fee, name, field in P:
    dur = grab(main, r"Award BSc \(Hons\) Duration of study 4 years")
    al = grab(req, r"offer in recent years: from A\*A\*A\* to [A-C*]+ in one set of exams")
    ib = grab(req, r"offer in recent years: from \d+ points with \d+ at HL to \d+ points with \d+ at HL")
    ielts = grab(req, r"IELTS Academic: total 6\.5 with at least 5\.5 in each component")
    row = grab(fee, r"International/EU fee rate Duration 2027/8 £[\d,.]+ £[\d,.]+ £([\d,]+)\.00 4 Years")
    intl = int(re.search(r"£([\d,]+)\.00 4 Years", row).group(1).replace(",", ""))
    al_range = re.search(r"from (A\*A\*A\*) to (\S+)", al).groups()
    ib_m = re.search(r"from (\d+) points with (\d+) at HL to (\d+) points with (\d+) at HL", ib).groups()
    prog("gb-edinburgh", slugify(f"bsc {name}"),
         {"course": src(main, f"{name} BSc (Hons) | The University of Edinburgh", ORG, [dur, f"{name}"]),
          "req": src(req, f"{name} BSc (Hons) entry requirements | The University of Edinburgh", ORG, [al, ib, ielts]),
          "fees": src(fee, f"{name} tuition fees 2027-2028 | The University of Edinburgh", ORG, [row, "The table shows the fee for one year only."]),
          "living": main0},
         {"name": name, "degree_type": "BSc (Hons)", "field": field, "faculty": "", "duration_years": 4, "duration_source": "course", "languages": [],
          "entry_year": "September 2027", "platform": "UCAS", "source": "course",
          "summary": f"BSc (Hons) {name}, The University of Edinburgh; 4 years.", "application_requirements": []},
         [{"residency": "international", "currency": "GBP", "tuition_annual": intl, "academic_year": "2027/8", "source": "fees",
           "note": f"International/EU fee rate 2027/8: £{intl:,} for one year.",
           "living": {"monthly": [1546], "months": 12, "source": "living", "kind": "genuine_cost_of_living_estimate",
                      "note": "The University of Edinburgh estimates £1,546 a month, £18,552 for a full year (× 12 = £18,552)."}}],
         adm_all({"a-level": f"{name}: {al_range[1]} at A level was the lowest offer most applicants needed in recent years; offers ranged up to {al_range[0]} (in one set of exams).",
                  "ib": f"{name}: IB {ib_m[2]} points with {ib_m[3]} at HL was the lowest offer most applicants needed in recent years; offers ranged up to {ib_m[0]} points with {ib_m[1]} at HL."},
                 "req", english={"test_name": "IELTS Academic", "min_score": "IELTS Academic 6.5 overall with at least 5.5 in each component.", "source": "req"}))
    print("wrote", name, intl, al_range, ib_m[0], ib_m[2])

"""London School of Economics and Political Science: base records + three BSc (written 2026-11-26). THE queue #16.

Source: each programme page on lse.ac.uk/study-at-lse/undergraduate: "Overseas full-time students ( Three years )",
"Academic year 2027/28 Start date 27 September 2027", "Overseas £N Overseas student fee per each year of your
programme", A-level and IB Diploma offers. English requirement not in the saved text: none stored.
No living costs read.
  python3 -I scripts/research/gen/gb_lse.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify, PAGES

ORG = "The London School of Economics and Political Science"
def t(p): return re.sub(r"\s+", " ", (PAGES / f"{p}.txt").read_text())
def grab(p, pat):
    m = re.search(pat, t(p)); assert m, (p, pat); return m.group(0)

P = [("6576980a5cde", "Economics", "Economics"), ("63cca37b5284", "Economics and Data Science", "Economics"),
     ("94e5fbd73dfa", "Mathematics and Economics", "Economics")]
spec("gb-lse", ORG, ["LSE", "London School of Economics"], "public", "https://www.lse.ac.uk", ("gb", "United Kingdom", "GBP"), ("uk-london-gb", "London"),
     {"main": src(P[0][0], "BSc Economics | LSE", ORG, ["The London School of Economics and Political Science Houghton Street London"])},
     [("international", "Overseas students", "LSE overseas tuition fee, fixed for each year of the programme.", "main")])
for page, name, field in P:
    fee_q = grab(page, r"Overseas £[\d,]+ Overseas student fee per each year of your programme This is the 2027/28 fee for each year of your programme\.")
    fee = int(re.search(r"£([\d,]+)", fee_q).group(1).replace(",", ""))
    dur_q = grab(page, r"Overseas full-time students \( Three years \) Open Academic year 2027/28 Start date 27 September 2027")
    al_q = grab(page, r"A-levels A\*AA,? with an A\* in Mathematics")
    ib_q = grab(page, r"IB Diploma 39 points overall[.,] (?:including )?766 in higher level subjects, with 7 in [^.]{0,40}?Mathematics(?:: analysis and approaches|: analysis and approaches\"|\")?")
    prog("gb-lse", slugify(f"bsc {name}"),
         {"course": src(page, f"BSc {name} | LSE", ORG, [dur_q, fee_q, al_q, ib_q, f"BSc {name}"])},
         {"name": name, "degree_type": "BSc", "field": field, "faculty": "", "duration_years": 3, "duration_source": "course", "languages": [],
          "entry_year": "2027/28", "platform": "UCAS", "source": "course", "summary": f"BSc {name}, LSE; three years full-time.",
          "application_requirements": []},
         [{"residency": "international", "currency": "GBP", "tuition_annual": fee, "academic_year": "2027/28", "source": "course",
           "note": f"Overseas £{fee:,} per each year of the programme (2027/28 entry, programme page)."}],
         adm_all({"a-level": f"{name}: A-levels A*AA with an A* in Mathematics.",
                  "ib": f"{name}: IB Diploma 39 points overall, 766 at Higher Level, with 7 in Mathematics."}, "course"))
    print("wrote", name, fee)

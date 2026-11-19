"""Purdue (West Lafayette) majors in Science, Liberal Arts and Health and Human Sciences (written
2026-11-19). Admission records are Purdue-wide (test scores, English) and are reused from Computer
Science; the fee is the general 2026-27 international flat rate from the Bursar (these colleges are
not among the programmes with differential fees: CS/Data Science/Engineering, Daniels Business/BA
Economics, Polytechnic, Veterinary Technology, Nursing).
  python3 -I scripts/research/gen/us_purdue.py
"""
import hashlib, re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from us import major

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
pid = lambda u: hashlib.sha1(u.encode()).hexdigest()[:12]
flat = lambda u: re.sub(r"\s+", " ", (PAGES / f"{pid(u)}.txt").read_text())

FU = "https://www.purdue.edu/treasurer/finance/bursar-office/tuition/fee-rates-2026-2027/undergraduate-tuition-and-fees-2026-2027/"
ft = flat(FU)
GEN = "Fall/Spring – Flat Rate (8+ credit hours)"
INTL = "International Student Tuition $ 1,655.00 $ 3,310.00 Sub-Total Tuition: $ 16,052.00 $ 32,104.00"
# the international sub-total quoted must sit in the general flat-rate block, before the first differential block
g, i, d = ft.index(GEN), ft.index(INTL), ft.index("Computer Science/Data Science & Engineering UG")
assert g < i < d, (g, i, d)
DIFF = "Some undergraduate programs at Purdue have additional fees. Please review the chart carefully to select the program that fits your interest."
assert DIFF in ft
FEES = {"fees": {"url": FU, "page": pid(FU), "title": "Undergraduate Tuition and Fees — 2026-2027 - Finance | Purdue University", "organization": "Purdue University Office of the Bursar",
                 "quotes": ["Undergraduate Tuition and Fees — 2026-2027", DIFF, GEN, "Indiana Resident Non-Resident International", INTL]}}
COST = [{"residency": "international", "currency": "USD", "tuition_annual": 32104, "academic_year": "2026-2027 (international, general flat rate; tuition sub-total includes required fees)",
         "source": "fees", "living_from": "costProfile-us-purdue-cost-bscs-international",
         "note": "2026-2027 international, Fall/Spring flat rate (8+ credit hours), general rate: sub-total tuition USD 32,104 for the academic year, including the international student tuition (USD 3,310). This major is not in a programme with differential fees."}]
CQ = "You should pursue the most rigorous high school curriculum available to you."
CQ2 = "stronger candidate for Purdue’s competitive admission process"
COURSE = "Minimum high school coursework (many applicants exceed these minimums): Math – 4 years English – 4 years Lab science – 3 years Social studies – 3 years World language – 2 years"

for slug, name, field in [("mathematics", "Mathematics", "Mathematics"), ("physics", "Physics", "Physics"), ("chemistry", "Chemistry", "Chemistry"),
                          ("biology", "Biology", "Biology"), ("history", "History", "History"), ("english", "English", "English"),
                          ("political-science", "Political Science", "Politics"), ("philosophy", "Philosophy", "Philosophy"),
                          ("psychological-sciences", "Psychological Sciences", "Psychology")]:
    url = f"https://admissions.purdue.edu/majors/{slug}/"
    t = flat(url)
    m = re.search(r"Degree: (Bachelor of (?:Science|Arts)) Location\(s\): West Lafayette College/School: (Science|Liberal Arts|Health and Human Sciences) ", t)
    assert m, slug
    deg_full, college = m.groups()
    title = t.split(" Skip")[0].strip() if " Skip" in t[:120] else t[:t.index("Purdue University") + len("Purdue University")]
    assert title.startswith(f"{name.split()[0]}"), title
    for q in (CQ, CQ2, COURSE, f"College of {college}"):
        assert q in t, (slug, q)
    deg = "BS" if deg_full.endswith("Science") else "BA"
    major("us-purdue", slug, url, pid(url), title, "Purdue University",
          [m.group(0).strip(), CQ, CQ2, COURSE, f"College of {college}"], name, deg, field, f"College of {college}", 4,
          f"{name}, {deg_full}, College of {college} (West Lafayette). Minimum high school coursework: Math 4 years, English 4 years, lab science 3 years, social studies 3 years, world language 2 years.",
          "program-us-purdue-bscs", CQ2, copy=("admissions",), costs=COST, more_sources=FEES)
    print(slug, deg, college, "|", title)

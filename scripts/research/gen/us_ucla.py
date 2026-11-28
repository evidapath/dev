"""University of California, Los Angeles (THE #114): every major on UCLA Undergraduate Admission's "Majors" page
(written 2026-11-28). Left out: majors marked "[5] Not open to entering students" or "*" (Individual Field of
Concentration, Physics B.A.), "[4] Open to junior-level applicants only" (Communication), and "Undeclared".
Costs: UCLA "Tuition and Fees" estimated undergraduate budget (Updated July 2026; the international admission
guide gives the same totals for Academic Year 2026-2027), residence-hall column, non-residents.
Length: Registrar, "declared degree-expected term ... four years for first-year students".
  python3 -I scripts/research/gen/us_ucla.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES
from us_fields import field_for

T = re.sub(r"\s+", " ", (PAGES / "99f934942c4b.txt").read_text(errors="replace"))
SCHOOLS = [("The College brings together", "College of Letters and Science"), ("School of the Arts and Architecture The School", "School of the Arts and Architecture"),
           ("Samueli School of Engineering The Samueli", "Samueli School of Engineering"), ("Herb Alpert School of Music Established", "Herb Alpert School of Music"),
           ("Joe C. Wen School of Nursing The Joe", "Joe C. Wen School of Nursing"), ("Luskin School of Public Affairs The Luskin", "Luskin School of Public Affairs"),
           ("School of Theater, Film and Television One of", "School of Theater, Film and Television"),
           ("School of Education and Information Studies The School", "School of Education and Information Studies"),
           ("Fielding School of Public Health The Fielding", "Fielding School of Public Health"), ("Sidemenu navigation", None)]
cuts = [(T.index(k), fac) for k, fac in SCHOOLS]
items, quotes = [], []
for (a, fac), (b, _) in zip(cuts, cuts[1:]):
    for m in re.finditer(r"([A-Z][A-Za-z ,/&\-—’'()]+?) \((B\.A\.|B\.S\.?|B\.M\.)\)((?: \[[0-9,]+\])?)( new)?( \*)?", T[a:b]):
        name, deg, notes, star = m.group(1).strip(), m.group(2), m.group(3), m.group(5)
        nums = set(re.findall(r"\d", notes))
        if star or nums & {"4", "5"} or name.startswith("Individual Field"):
            continue
        items.append((name, deg if deg.endswith(".") else deg + ".", fac)); quotes.append(m.group(0).strip())

ORG = "UCLA"  # official pages use only "UCLA"; the full name is kept as an alias
ML = src("99f934942c4b", "Majors | UCLA Undergraduate Admission", ORG,
         ["Following is a list of all of the majors offered for undergraduates at UCLA.", "4. Open to junior-level applicants only",
          "5. Not open to entering students.", "1147 Murphy Hall, Box 951436 Los Angeles, CA 90095-1436"] + sorted(set(quotes)))
MY = src("e28e92d3bec5", "Declare Candidacy | UCLA Registrar's Office", ORG,
         ["All undergraduate students begin at UCLA with a declared degree-expected term of two years from matriculation for transfer students, four years for first-year students."])
MF = src("e4a99deba2d5", "Tuition and Fees | UCLA Undergraduate Admission", ORG,
         ["Updated July 2026 Cost Per Academic Year (Nine Months) UCLA Residence Halls Off-Campus Apartments Commuter University Fees $16,430 $16,430 $16,430 Housing $12,299 $14,541 $3,955 Food $7,568 $6,610 $4,834",
          "Nonresident Supplemental Tuition $39,270 $39,270 $39,270 Total – Nonresidents $84,770 $87,056 $75,977",
          "Figures for tuition and fees represent currently approved or proposed amounts and may not be final."])
MG = src("ucla-intl-2026", "UCLA International Applicants: Your Guide to Applying to UCLA (2026)", ORG,
         ["Estimated Costs* for Academic Year 2026–2027"])
spec("us-ucla", ORG, ["University of California, Los Angeles", "University of California Los Angeles"], "public", "https://www.ucla.edu", ("us", "United States", "USD"), ("us-los-angeles-ca", "Los Angeles"),
     {"main": ML, "coa": MF}, [("nonresident", "Non-California residents", "UCLA estimated undergraduate budget for non-residents.", "coa")])
COST = {"residency": "nonresident", "currency": "USD", "tuition_formula": "4*(16430+39270)/4", "academic_year": "2026-27", "source": "coa",
        "note": "University fees $16,430 + nonresident supplemental tuition $39,270 = $55,700 a year (our calculation); approved or proposed amounts, may not be final.",
        "living": {"monthly": [], "months": 9, "yearly": [12299, 7568], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                   "note": "UCLA residence halls, nine-month academic year: housing $12,299 + food $7,568 = $19,867 (our calculation)."}}
seen = set()
for name, deg, fac in items:
    slug = slugify(f"{deg} {name}")[:60].rstrip("-")
    if slug in seen:
        continue
    seen.add(slug)
    prog("us-ucla", slug, {"course": ML, "y": MY, "coa": MF, "g": MG},
         {"name": name, "degree_type": deg, "field": field_for(name), "faculty": fac, "duration_years": 4, "duration_source": "y",
          "languages": ["en"], "entry_year": "Fall 2027", "platform": "", "source": "course",
          "summary": f"{name} ({deg}), {fac}, {ORG}; first-year students begin with a degree-expected term of four years.",
          "application_requirements": []},
         [COST], [])
print("us-ucla", len(seen))

"""THE most-international batch (written 2026-11-27): UC Santa Cruz, Washington University in St. Louis,
University of Notre Dame, Georgetown University (College of Arts & Sciences) with every undergraduate programme on
their official lists, plus the University of Helsinki's two English-taught bachelor's programmes. Each programme
carries its university's own cost-of-attendance figures; admission is holistic (US) and no grade threshold is
published, so no admission rows. Helsinki publishes no grade threshold on its programme pages either.
  python3 -I scripts/research/gen/us_new6.py [uni]
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES
from us_fields import field_for

ONLY = sys.argv[1] if len(sys.argv) > 1 else None
flat = lambda pid: re.sub(r"\s+", " ", (PAGES / f"{pid}.txt").read_text(errors="replace"))


def uni(uid, org, aliases, kind, site, country, city, main, sources, residency, items, years, years_src, cost, tail, langs=("en",)):
    if ONLY and ONLY != uid:
        return
    spec(uid, org, aliases, kind, site, country, city, {"main": main, **sources}, [residency])
    for it in items:
        name, deg, fac = it[:3]
        yrs = it[3] if len(it) > 3 else years
        prog(uid, slugify(f"{deg} {name}")[:60].rstrip("-"), {"course": sources["course"], **{k: v for k, v in sources.items() if k != "course"}},
             {"name": name, "degree_type": deg, "field": field_for(name), "faculty": fac, "duration_years": yrs, "duration_source": years_src,
              "languages": list(langs), "entry_year": "2026-27", "platform": "", "source": "course",
              "summary": f"{name}, {org}{tail}", "application_requirements": []},
             [cost], [])
    print(uid, len(items))


US = ("us", "United States", "USD")

# UC Santa Cruz: Bachelor's Degrees (General Catalog)
T = flat("696f445ae743")
blk = T[T.index("Bachelor's Degrees Bachelor's Degrees") + len("Bachelor's Degrees Bachelor's Degrees "):]
sc = [(n.strip(), d) for n, d in re.findall(r"([A-Z][A-Za-z ,:&/+()'’-]+?) (B\.A\.|B\.S\.|B\.F\.A\.|B\.M\.)(?= |$)", blk)]
ORG = "University of California Santa Cruz"
SL = src("696f445ae743", "Bachelor's Degrees | University of California Santa Cruz", ORG,
         ["University of California Santa Cruz - Bachelor's Degrees"] + [f"{n} {d}" for n, d in sc])
SY = src("d202bb918c57", "Planning Your Academic Program | University of California Santa Cruz", ORG,
         ["Students who enter as frosh are expected to graduate in four years."])
SF = src("4f638e374cb6", "Cost to Attend UC Santa Cruz | Financial Aid", ORG,
         ["2026-27 Undergraduate Budgets for Entering Students (Fall, Winter, & Spring Terms ) Entering Students On-Campus Off-Campus Commuter Tuition and Fees 1 $17,439 $17,439 $17,439 Housing 2 $15,120 $15,614 $3,956 Food $6,837 $5,947 $4,834",
          "Non-Resident Tuition $39,270 $39,270 $39,270 Total Non-California Resident Budget $87,807"])
uni("us-ucsc", ORG, ["UC Santa Cruz", "UCSC", "University of California, Santa Cruz"], "public", "https://www.ucsc.edu", US, ("us-santa-cruz-ca", "Santa Cruz"),
    SL, {"course": SL, "y": SY, "coa": SF},
    ("nonresident", "Non-California residents", "UC Santa Cruz budget for entering students who are not California residents.", "coa"),
    [(n, d, "") for n, d in sc], 4, "y",
    {"residency": "nonresident", "currency": "USD", "tuition_formula": "4*(17439+39270)/4", "academic_year": "2026-27", "source": "coa",
     "note": "Entering students 2026-27: tuition and fees $17,439 + non-resident tuition $39,270 = $56,709 a year (our calculation); estimates, may not be final.",
     "living": {"monthly": [], "months": 12, "yearly": [15120, 6837], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                "note": "On-campus 2026-27: housing $15,120 + food $6,837 = $21,957 (our calculation)."}},
    "; students entering as first-years are expected to graduate in four years.")

# Washington University in St. Louis: Majors (all schools), Undergraduate Bulletin
W = [l.strip() for l in (PAGES / "00ec6572b086.txt").read_text().splitlines() if l.strip()]
wu, seen = [], set()
for l in W:
    m = re.fullmatch(r"(.+?), (BS|BA|BFA|BSBA|BArch|BMus)", l) or re.fullmatch(r"(.+?) Major", l)
    if not m or "Second Major" in l or "Specialization" in l or "Concentration" in l or "Double Majors" in l:
        continue
    name, deg = re.sub(r" \((?:CSE|ESE|EECE|MEMS|BME)\)", "", m.group(1)), (m.group(2) if m.lastindex == 2 else "Bachelor's (major)")
    if (name, deg) in seen:
        continue
    seen.add((name, deg)); wu.append((name, deg, l))
ORG = "Washington University in St. Louis"
WL = src("00ec6572b086", "Majors (all schools) | Washington University Bulletin", ORG,
         ["Majors (all schools) | Washington University Bulletin"] + [x[2] for x in wu])
WY = src("c26bffaf56fe", "Academic Policies | Washington University Bulletin", ORG, ["For undergraduates, this is usually eight semesters"])
WF = src("70471b91aee9", "Costs | WashU Student Financial Services", ORG,
         ["Undergraduate tuition and fees for 2026-27 University charges Tuition $71,310 Student activity fee $712 Student health and wellness fee $700 Average housing and food (university meal plan)* $24,272",
          "©2026 Washington University in St. Louis"])
uni("us-wustl", ORG, ["WashU", "Washington University"], "private", "https://wustl.edu", US, ("us-st-louis-mo", "St. Louis"),
    WF, {"course": WL, "y": WY, "coa": WF},
    ("international", "All undergraduates", "WashU undergraduate university charges, 2026-27.", "coa"),
    [(n, d, "") for n, d, _ in wu], 4, "y",
    {"residency": "international", "currency": "USD", "tuition_annual": 71310, "academic_year": "2026-27", "source": "coa",
     "note": "2026-27: tuition $71,310; plus student activity fee $712 and student health and wellness fee $700.",
     "living": {"monthly": [], "months": 12, "yearly": [24272], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                "note": "Average housing and food (university meal plan) 2026-27: $24,272."}},
    "; undergraduate degrees usually take eight semesters.")

# University of Notre Dame: Academic Programs (2026-2027 Bulletin), every "(Major)" (supplementary majors left out)
N = flat("fc8ad24292ea")
nd, seen = [], set()
for part in N.split("School Degree Program ")[1:]:
    m = re.match(r"([A-Z][^()]*?(?: \((?:BA|BFA|BS)\))?) \(Major\)", part)
    if not m:
        continue
    name = m.group(1).strip()
    if name not in seen:
        seen.add(name); nd.append((name, "Bachelor's (major)", f"{name} (Major)"))
ORG = "University of Notre Dame"
NL = src("fc8ad24292ea", "Academic Programs | University of Notre Dame Academic Catalog", ORG,
         ["2026-2027 Bulletin of Information"] + [x[2] for x in nd])
NY = src("defacaa0b335", "Number of Courses and Credits | Notre Dame Advising", ORG,
         ["remain on pace to graduate in four years/eight semesters (five years/ten semesters for Architecture"])
NF = src("c59ba89fe888", "Costs & Affordability | Notre Dame Financial Aid", ORG,
         ["Average Cost of Attendance for 2026-2027 Item Cost Tuition $69,280 Mandatory Fees $514 Housing and Food $18,992",
          "University of Notre Dame Notre Dame , IN 46556 USA"])
uni("us-notre-dame", ORG, ["Notre Dame"], "private", "https://www.nd.edu", US, ("us-notre-dame-in", "Notre Dame"),
    NF, {"course": NL, "y": NY, "coa": NF},
    ("international", "All undergraduates", "Notre Dame average undergraduate cost of attendance, 2026-2027.", "coa"),
    [(n, d, "", 5 if n == "Architecture" else 4) for n, d, _ in nd], 4, "y",
    {"residency": "international", "currency": "USD", "tuition_annual": 69280, "mandatory_fees_annual": 514, "academic_year": "2026-2027", "source": "coa",
     "note": "2026-2027: tuition $69,280; mandatory fees $514.",
     "living": {"monthly": [], "months": 12, "yearly": [18992], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                "note": "Notre Dame average housing and food 2026-2027: $18,992."}},
    "; on pace to graduate in four years (five years for Architecture).")

# Georgetown University: College of Arts & Sciences undergraduate programs with a degree (A.B./B.S.)
G = flat("3cac469deb69")
gblk = G[G.index("Undergraduate Program Major Minor Certificate Degree") + 52:G.index("Accelerated Bachelor/Master Degree Programs Some graduate")]
gt = []
for m in re.finditer(r"([A-Z][A-Za-z ,&()'’-]+?)(?: \*)? ((?:✓ ?)+)((?:A\.B\.|B\.S \.)(?:, (?:A\.B\.|B\.S \.))*)", gblk):
    name = m.group(1).strip()
    if "Engineering (dual-degree" in name:
        continue
    gt.append((name, m.group(3).replace("B.S .", "B.S."), m.group(0)))
ORG = "Georgetown University"
GL = src("3cac469deb69", "Majors & Minors | Georgetown University's College of Arts & Sciences", ORG,
         ["Majors & Minors | Georgetown University's College of Arts & Sciences"] + [x[2] for x in gt])
GY = src("244f02622c93", "Matriculation | Georgetown Undergraduate Bulletin", ORG,
         ["Students admitted as first-year students are ordinarily expected to complete their degree requirements and graduate by the end of their eighth semester of matriculation."])
GF = src("e5d71d98698e", "How Aid Works for Undergraduates | Georgetown Financial Aid", ORG,
         ["2026-2027 Annual Cost of Attendance First Year Undergraduate", "Full Time Tuition & Fees $74,732 $74,732 $75,091 $75,091 Average Housing Expense $13,944 $900 $13,944 $900 Food Expense $8,236",
          "3700 O St N.W., Box 571252 Washington DC 20057", "Office of Student Financial Aid | Georgetown University"])
uni("us-georgetown", ORG, ["Georgetown"], "private", "https://www.georgetown.edu", US, ("us-washington-dc", "Washington"),
    GF, {"course": GL, "y": GY, "coa": GF},
    ("international", "All undergraduates", "Georgetown first-year undergraduate cost of attendance, 2026-2027.", "coa"),
    [(n, d, "College of Arts & Sciences") for n, d, _ in gt], 4, "y",
    {"residency": "international", "currency": "USD", "tuition_annual": 74732, "academic_year": "2026-2027", "source": "coa",
     "note": "First-year 2026-2027: full-time tuition & fees $74,732.",
     "living": {"monthly": [], "months": 12, "yearly": [13944, 8236], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                "note": "Georgetown 2026-2027 first-year: average housing $13,944 + food $8,236 = $22,180 (our calculation)."}},
    " (College of Arts & Sciences); first-year students ordinarily graduate by the end of their eighth semester.")

# University of Helsinki: the two English-taught bachelor's programmes
ORG = "University of Helsinki"
HB = "Scope of studies and length 180 ECTS credits, 3 years Degree level Bachelor Language English Tuition fee per year (only non-EU/EEA citizens) 13 000 EUR"
HS = src("92a4d3dc7717", "Science | Bachelor's programme | University of Helsinki", ORG, ["Science | Bachelor's programme | University of Helsinki", HB,
                                                                                            "P.O. Box 3 (Fabianinkatu 33) 00014 University of Helsinki"])
HL = src("24e26772c0eb", "Liberal Arts and Sciences | Bachelor's programme | University of Helsinki", ORG, [HB])
HF = src("d0f37d5a667d", "Tuition fees and scholarship programme | University of Helsinki", ORG,
         ["The fee for the English-language bachelor's programmes is 13,000 EUR per academic year."])
if not ONLY or ONLY == "fi-helsinki":
    spec("fi-helsinki", ORG, ["Helsingin yliopisto"], "public", "https://www.helsinki.fi", ("fi", "Finland", "EUR"), ("fi-helsinki", "Helsinki"),
         {"main": HS, "fees": HF}, [("non-eu", "Non-EU/EEA citizens", "Tuition fee for the English-language bachelor's programmes (non-EU/EEA citizens only).", "fees")])
    for slug, name, field, S_ in (("bachelors-programme-in-science", "Bachelor's Programme in Science", "Natural Sciences", HS),
                                  ("bachelors-programme-in-liberal-arts-and-sciences", "Bachelor's Programme in Liberal Arts and Sciences", "Liberal Arts", HL)):
        prog("fi-helsinki", slug, {"course": S_, "fees": HF},
             {"name": name, "degree_type": "Bachelor", "field": field, "faculty": "", "duration_years": 3, "duration_source": "course",
              "languages": ["en"], "entry_year": "2027", "platform": "", "source": "course",
              "summary": f"{name}, University of Helsinki; 180 ECTS credits, 3 years, taught in English.", "application_requirements": []},
             [{"residency": "non-eu", "currency": "EUR", "tuition_annual": 13000, "academic_year": "2027 entry", "source": ["course", "fees"],
               "note": "Non-EU/EEA citizens: €13,000 a year; EU/EEA citizens pay no tuition fee."}], [])
    print("fi-helsinki 2")

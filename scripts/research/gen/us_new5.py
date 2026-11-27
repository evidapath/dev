"""More US universities from THE's most-international list with every undergraduate programme (written
2026-11-27). Each programme carries the university's own cost-of-attendance figures (no base record yet in
Sanity to copy from). Admission is holistic and no grade threshold is published: no admission rows.
  python3 -I scripts/research/gen/us_new5.py [uni]
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES
from us_fields import field_for

ONLY = sys.argv[1] if len(sys.argv) > 1 else None


def flat(pid):
    return re.sub(r"\s+", " ", (PAGES / f"{pid}.txt").read_text(errors="replace"))


def uni(uid, org, aliases, kind, site, city, main, sources, residency, items, years_src, cost, summary_tail):
    if ONLY and ONLY != uid:
        return
    spec(uid, org, aliases, kind, site, ("us", "United States", "USD"), city, {"main": main, **sources}, [residency])
    for name, deg, src_key, faculty in items:
        prog(uid, slugify(f"{deg} {name}")[:60].rstrip("-"), {"course": sources[src_key], **{k: v for k, v in sources.items() if k != src_key}},
             {"name": name, "degree_type": deg, "field": field_for(name), "faculty": faculty, "duration_years": 4, "duration_source": years_src,
              "languages": ["en"], "entry_year": "2026-27", "platform": "", "source": "course",
              "summary": f"{name}, {org}{summary_tail}", "application_requirements": []},
             [cost], [])
    print(uid, len(items))


# Brown University
B = flat("d59d3f1830fc")
blk = B[B.index("Print Options Africana Studies") + len("Print Options "):B.index(" Brown University Providence")]
names = []
for n in ["Africana Studies", "American Studies", "Anthropology", "Applied Mathematics", "Applied Mathematics-Biology", "Applied Mathematics-Computer Science",
          "Applied Mathematics-Economics", "Archaeology and the Ancient World", "Architecture", "Astronomy", "Behavioral Decision Sciences",
          "Biochemistry & Molecular Biology", "Biology", "Biomedical Engineering", "Biophysics", "Chemical Engineering", "Chemical Physics", "Chemistry",
          "Classics", "Cognitive Neuroscience", "Cognitive Science", "Comparative Literature", "Computational Biology",
          "Computational Chemistry and Chemical Physics", "Computational Neuroscience", "Computer Engineering", "Computer Science",
          "Computer Science-Economics", "Contemplative Studies", "Critical Native American and Indigenous Studies", "Design Engineering",
          "Early Modern World", "Earth and Planetary Science", "Earth, Climate, and Biology", "East Asian Studies", "Economics", "Education Studies",
          "Egyptology and Assyriology", "Electrical Engineering", "Engineering", "Engineering and Physics", "English", "Environmental Engineering",
          "Environmental Sciences and Studies", "Ethnic Studies", "French and Francophone Studies", "Gender and Sexuality Studies",
          "Geochemistry and Environmental Chemistry", "Geophysics and Climate Physics", "German Studies", "Health & Human Biology",
          "Hispanic Literatures and Cultures", "History", "History of Art and Architecture", "International and Public Affairs", "Italian Studies",
          "Judaic Studies", "Latin American and Caribbean Studies", "Linguistics", "Literary Arts", "Materials Engineering", "Mathematics",
          "Mathematics-Computer Science", "Mathematics-Economics", "Mechanical Engineering", "Medieval Cultures", "Middle East Studies",
          "Modern Culture and Media", "Music", "Neuroscience", "Philosophy", "Philosophy, Politics, and Economics", "Physics", "Physics and Philosophy",
          "Political Science", "Portuguese and Brazilian Studies", "Psychology", "Public Health", "Religious Studies", "Science, Technology, and Society",
          "Slavic Studies", "Social Analysis and Research", "Sociology", "South Asian Studies", "Statistics", "Theatre Arts and Performance Studies",
          "Urban Studies", "Visual Art"]:
    assert f" {n} " in f" {blk} ", n
    names.append(n)
ORG = "Brown University"
BC = src("d59d3f1830fc", "Undergraduate Concentrations < Brown University", ORG,
         ["Undergraduate Concentrations", "2026-27 University Bulletin", "Brown University Providence, Rhode Island 02912, USA"] + names)
BR = src("bafee22e1c10", "The College < Brown University", ORG,
         ["Students may complete as many as three concentrations during a regular four-year program.",
          "A student’s chosen concentration program determines the degree awarded."])
BF = src("a95e125ef8c0", "Cost of Attendance | Brown Financial Aid", ORG,
         ["2026-27 Academic Year These figures represent the estimated costs for an incoming first-year full time student",
          "Tuition $74,568 Fees (includes $100 Academic record fee for first time students) $3,084 Housing $10,710 Food $8,754"])
uni("us-brown", ORG, ["Brown"], "private", "https://www.brown.edu", ("us-providence-ri", "Providence"), BC,
    {"course": BC, "reg": BR, "coa": BF},
    ("international", "All undergraduates", "Brown's estimated cost of attendance for a full-time first-year undergraduate.", "coa"),
    [(n, "A.B. or Sc.B.", "course", "The College") for n in names], "reg",
    {"residency": "international", "currency": "USD", "tuition_annual": 74568, "mandatory_fees_annual": 3084, "academic_year": "2026-27", "source": "coa",
     "note": "Incoming first-year full-time student 2026-27: tuition $74,568; fees $3,084.",
     "living": {"monthly": [], "months": 12, "yearly": [10710, 8754], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                "note": "Brown 2026-27: housing $10,710 + food $8,754 = $19,464 (our calculation)."}},
    " (concentration in The College); a regular four-year program; the concentration determines whether the degree is an A.B. or Sc.B.")

# Boston University: Degree Programs A–Z (undergraduate degrees BA/BS/BFA/BM; Metropolitan College part-time
# programmes and BLS left out)
U = flat("545466a68f79")
seg = U[U.index("Online Show all Undergraduate Minors Undergraduate Majors Master’s Doctorate Online A ") + len("Online Show all Undergraduate Minors Undergraduate Majors Master’s Doctorate Online "):]
bu, seen = [], set()
for m in re.finditer(r"([A-Z][^()]*?) \( ([^()]+?) \)", seg):
    raw = re.sub(r"^[A-Z] (?=[A-Z])", "", m.group(1).strip())
    toks = [x.strip() for x in m.group(2).split(",")]
    degs = [x for x in toks if x in ("BA", "BS", "BFA", "BM", "BSBA", "BAS")]
    name = re.sub(r"\s+(?:[A-Z]{2,9}(?:/[A-Z]{2,4})?)$", "", raw).strip()
    if not degs or " MET" in raw or "BLS" in toks or not name or name in seen:
        continue
    seen.add(name)
    bu.append((name, "/".join(degs), m.group(0)))
ORG = "Boston University"
UL = src("545466a68f79", "Degree Programs » Academics | Boston University", ORG, ["Degree Programs » Academics | Boston University"] + [b[2] for b in bu])
UF = src("f5d6fa98b3a2", "Full Tuition Figures | Boston University Admissions", ORG,
         ["Cost of Attendance Billed expenses for the 2026/2027 academic year* Tuition $73,024 Housing (depending on type of accommodation) $13,170 Food (most dining plans) $7,570 Fees $1,570",
          "Cost of Attendance based on standard Housing and Dining Plan cost for four years"])
uni("us-bu", ORG, ["BU"], "private", "https://www.bu.edu", ("us-boston-ma", "Boston"), UL,
    {"course": UL, "coa": UF},
    ("international", "All undergraduates", "Boston University billed expenses for undergraduates, 2026/2027.", "coa"),
    [(n, d, "course", "") for n, d, _ in bu], "coa",
    {"residency": "international", "currency": "USD", "tuition_annual": 73024, "mandatory_fees_annual": 1570, "academic_year": "2026/2027", "source": "coa",
     "note": "Billed expenses 2026/2027: tuition $73,024; fees $1,570.",
     "living": {"monthly": [], "months": 12, "yearly": [13170, 7570], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                "note": "Boston University 2026/2027: housing $13,170 (depending on accommodation) + food $7,570 (most dining plans) = $20,740 (our calculation)."}},
    "; Boston University's cost of attendance is based on four years.")

# University of Chicago: The Curriculum page's Programs of Study with B.A./B.S. (minors-only left out)
CH = flat("cc2aa492b687")
ch = [(a, "/".join(x for x in b.split(", ") if x != "minor"), f"{a} ({b})")
      for a, b in re.findall(r"(?<=[)] )([A-Z][A-Za-z ,:&'’-]+?) \(((?:B\.A\.|B\.S\.|minor)(?:, (?:B\.A\.|B\.S\.|minor))*)\)", CH) if "B." in b]
ORG = "The University of Chicago"
CC = src("cc2aa492b687", "The Curriculum | Academic Catalog | The University of Chicago", ORG,
         ["Bachelor's degrees awarded are based on the major(s) selected by the student and may come in two forms: Bachelor of Arts (B.A.) or Bachelor of Science (B.S.).",
          "© 2026-2027 The University of Chicago", "1427 East 60th Street Chicago, IL 60637"] + [c[2] for c in ch])
CQ = src("3ff89c3e05a2", "Enrollment Policies and Statuses | Academic Catalog | The University of Chicago", ORG,
         ["Over the course of a typical four-year program (i.e., 12 quarters)"])
CF = src("924729ad69c5", "Undergraduate Costs | UChicago Financial Aid", ORG,
         ["Cost of Attendance for 2026-2027 On-Campus Commuter Off-Campus Tuition $75,960 $75,960 $75,960 Student Services Fee $1,677 $1,677 $1,677 UPASS Fee $318 $318 $318 Food & Housing (or Maintenance Allowance) $21,414"])
uni("us-uchicago", ORG, ["University of Chicago", "UChicago"], "private", "https://www.uchicago.edu", ("us-chicago-il", "Chicago"), CC,
    {"course": CC, "q": CQ, "coa": CF},
    ("international", "All undergraduates", "UChicago's 2026-2027 cost of attendance for College students.", "coa"),
    [(n, d, "course", "The College") for n, d, _ in ch], "q",
    {"residency": "international", "currency": "USD", "tuition_annual": 75960, "mandatory_fees_annual": 1677, "academic_year": "2026-2027", "source": "coa",
     "note": "2026-2027: tuition $75,960; student services fee $1,677; UPASS fee $318 is separate.",
     "living": {"monthly": [], "months": 12, "yearly": [21414], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                "note": "UChicago 2026-2027 on-campus food & housing allowance: $21,414."}},
    " (major in The College); a typical four-year program.")

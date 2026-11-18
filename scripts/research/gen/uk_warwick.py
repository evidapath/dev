"""University of Warwick courses, 2027 entry (written 2026-11-18).

Course facts are quoted line by line from the saved course page; the overseas fee is the
2027-28 column of Warwick's overseas fees table; the IELTS level is the course's English
band from Warwick's English language requirements page. build.py re-checks every quote.
  python3 -I scripts/research/gen/uk_warwick.py
"""
import hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
W = "https://warwick.ac.uk/study/undergraduate/courses/"
FEES = "https://warwick.ac.uk/services/finance/studentfinance/fees/overseasfees/"
ENGP = "https://warwick.ac.uk/study/undergraduate/applying/english-language-requirements/"
LIVING = "costProfile-uk-warwick-cost-bsc-cs-{}"

# folder, slug, path, name, degree, field, fee-table row name, required subjects
COURSES = [
    ("mathematics", "mathematics", "bsc-mathematics", "Mathematics", "BSc", "Mathematics", "Mathematics (BSc)", ["Mathematics", "Further Mathematics"]),
    ("physics", "physics", "bsc-physics", "Physics", "BSc", "Physics", "Physics (BSc)", ["Mathematics (or Further Mathematics)", "Physics"]),
    ("chemistry", "chemistry", "bsc-chemistry", "Chemistry", "BSc", "Chemistry", "Chemistry (BSc)", ["Chemistry"]),
    ("politics", "politics-international-studies", "ba-politics-international-studies", "Politics and International Studies", "BA", "Politics", "Politics and International Studies (BA)", []),
    ("accounting", "accounting-finance", "bsc-accounting-finance", "Accounting and Finance", "BSc", "Accounting and Finance", "Accounting and Finance (BSc)", ["Mathematics"]),
    ("humanities", "history", "ba-history", "History", "BA", "History", "History (BA)", ["History"]),
]
# Not added: English Literature (BA): the overseas fees table gives "Band 0 £21,950 £27,870 £21,950"
# (2027-28 lower than 2026-27), which looks like an error on the page. Held until it is clear.


def page_id(url):
    return hashlib.sha1(url.encode()).hexdigest()[:12]


def lines(url):
    return [l.strip() for l in (PAGES / f"{page_id(url)}.txt").read_text().splitlines()]


fee_ls, eng_ls = lines(FEES), lines(ENGP)
ielts_at = eng_ls.index("IELTS Academic")
BANDS = {}
for k in range(ielts_at, ielts_at + 12):
    if re.fullmatch(r"Band [ABC]", eng_ls[k]):
        BANDS[eng_ls[k][-1]] = eng_ls[k + 1]


def build(folder, slug, path, name, degree, field, row, req):
    url = W + path + "/"
    ls = lines(url)
    get = lambda label: ls[ls.index(label) + 1]
    ucas = get("UCAS course code").replace(" Link opens in a new window", "")
    start, dept, dur = get("Start date"), get("Department"), get("Duration")
    alevel, ib = get("A level typical offer"), get("International Baccalaureate (IB) typical offer")
    band = get("This course requires:")[-1]
    interview = get("Will I need to interview for this course?")
    assert start == "27 September 2027" and dur == "3 years full-time", (start, dur)
    i = fee_ls.index(row)
    fee_row = " ".join(fee_ls[i:i + 6])
    m = re.fullmatch(re.escape(row) + r" (\w+) (Band \d) £[\d,]+ £[\d,]+ £([\d,]+)", fee_row)
    assert m and m.group(1) == ucas, fee_row
    intl = int(m.group(3).replace(",", ""))
    quotes = [f"UCAS course code {ucas}", f"Start date {start}", f"Department {dept} Duration {dur}",
              f"A level typical offer {alevel}", f"International Baccalaureate (IB) typical offer {ib}",
              f"This course requires: Band {band}", "Warwick does not typically interview applicants.",
              "Tuition fee £10,050 For the 2027-28 academic year, the UK government announced in March 2026 that the tuition fee cap for UK undergraduate students for the 2027-28 academic year would be £10,050."]
    assert interview.startswith("Warwick does not typically interview applicants.")
    tests, apps, extra = [], [], ""
    if slug == "mathematics":
        quotes += ["All applicants will typically be required to take TMUA except for applicants who are eligible for a Contextual Offer",
                   "Grade 2 in STEP will be a requirement of offers to applicants who have not taken TMUA"]
        tests = [{"name": "TMUA", "required": "required"}]
        apps = [{"name": "TMUA", "description": "All applicants will typically be required to take TMUA (except those eligible for a Contextual Offer). Without TMUA, the offer requires grade 2 in STEP.", "type": "standardized_test_score", "source": "course"}]
        extra = " TMUA typically required."
    eng = {"test_name": "IELTS Academic (or accepted equivalent)",
           "min_score": f"IELTS Academic {BANDS[band]} (Warwick English Band {band}).", "source": "english"}
    r = {
        "uni": "uk-warwick", "slug": slug,
        "sources": {
            "course": {"url": url, "page": page_id(url), "title": f"{name} ({degree}) | University of Warwick",
                       "organization": "University of Warwick", "quotes": quotes},
            "fees": {"url": FEES, "page": page_id(FEES), "title": "Overseas fees | University of Warwick",
                     "organization": "University of Warwick",
                     "quotes": ["Course UCAS code 2025-26 2026-27 2027-28", fee_row]},
            "english": {"url": ENGP, "page": page_id(ENGP), "title": "English language requirements | University of Warwick",
                        "organization": "University of Warwick", "quotes": [f"Band {band} {BANDS[band]}"]},
        },
        "program": {"name": name, "degree_type": degree, "field": field, "faculty": dept, "duration_years": 3,
                    "languages": ["en"], "entry_year": "2027 entry", "platform": "UCAS", "source": "course",
                    "summary": f"{name} {degree} (UCAS {ucas}), 3 years.{extra}", "application_requirements": apps},
        "costs": [
            {"residency": "home", "currency": "GBP", "tuition_annual": 10050, "academic_year": "2027-28 (2027 entry)",
             "source": "course", "living_from": LIVING.format("home"), "note": "Home fee, 2027-28: £10,050 (Warwick course page)."},
            {"residency": "international", "currency": "GBP", "tuition_annual": intl, "academic_year": "2027-28 (2027 entry)",
             "source": "fees", "living_from": LIVING.format("international"),
             "note": f"Overseas fee, 2027-28: £{intl:,} ({m.group(2)}, Warwick overseas fees table)."},
        ],
        "admissions": [
            {"curriculum": "a-level", "source": "course", "threshold": f"{name}: {alevel}{extra}", "required_subjects": req, "tests": tests, "english": eng},
            {"curriculum": "ib", "source": "course", "threshold": f"{name}: IB {ib}{extra}", "required_subjects": req, "tests": tests, "english": eng},
        ],
    }
    write(folder, r)
    print(slug, ucas, dept, band, intl)


for c in COURSES:
    build(*c)

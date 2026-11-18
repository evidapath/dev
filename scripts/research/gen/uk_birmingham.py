"""University of Birmingham courses, 2027 entry (written 2026-11-18).

Every quote is taken line by line from the saved course page (.research-cache/pages/<id>.txt),
so it is verbatim; the international fee and the entry year come from the page's embedded
data (<id>-raw.txt, made by scripts/research/raw.py). Thresholds are the quoted lines
themselves. build.py re-checks all of it.
  python3 -I scripts/research/gen/uk_birmingham.py
"""
import hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
B = "https://www.birmingham.ac.uk/study/undergraduate/subjects/"
ENG_IELTS = "IELTS Academic (or accepted equivalent)"

# folder, slug, path, name, degree, field, required subjects (strict), faculty
COURSES = [
    ("mathematics", "mathematics", "mathematics-courses/mathematics-bsc", "Mathematics", "BSc", "Mathematics", ["Mathematics (or Further Mathematics)"], "School of Mathematics"),
    ("physics", "physics", "physics-and-astronomy-courses/physics-bsc", "Physics", "BSc", "Physics", ["Mathematics", "Physics"], ""),
    ("chemistry", "chemistry", "chemistry-courses/chemistry-bsc", "Chemistry", "BSc", "Chemistry", ["Chemistry"], ""),
    # Mechanical Engineering BEng: already in Sanity as program-uk-birmingham-beng-engineering (same page).
    ("engineering", "electrical-electronic-engineering", "electronic-electrical-and-systems-engineering-courses/electronic-electrical-engineering-beng", "Electronic and Electrical Engineering", "BEng", "Electrical and Electronic Engineering", ["Mathematics"], ""),
    ("engineering", "aerospace-engineering", "aerospace-engineering-courses/aerospace-engineering-beng", "Aerospace Engineering", "BEng", "Aerospace Engineering", ["Mathematics"], ""),
    ("engineering", "computer-engineering", "electronic-electrical-and-systems-engineering-courses/computer-engineering-bsc", "Computer Engineering", "BSc", "Computer Engineering", ["Mathematics"], ""),
    ("accounting", "accounting-finance", "accounting-and-finance-courses/accounting-and-finance-bsc", "Accounting and Finance", "BSc", "Accounting and Finance", [], ""),
    ("politics", "international-relations", "politics-international-relations-and-development-courses/international-relations-ba", "International Relations", "BA", "International Relations", [], "Department of Political Science and International Studies"),
    ("politics", "politics-international-relations", "politics-international-relations-and-development-courses/politics-and-international-relations-ba", "Politics and International Relations", "BA", "Politics", [], "Department of Political Science and International Studies"),
    ("politics", "ppe", "politics-international-relations-and-development-courses/politics-philosophy-and-economics-ba", "Politics, Philosophy and Economics", "BA", "Politics, Philosophy and Economics", [], ""),
    ("dentistry", "dentistry", "dentistry-courses/dental-surgery-bds", "Dental Surgery", "BDS", "Dentistry", ["Chemistry", "Biology"], "School of Dentistry"),
]
# Dentistry: international fee differs by year (1 pre-clinical year, 4 clinical years).
FORMULA = {"dentistry": "(1*30180+4*53880)/5"}


def lines(page):
    return [l.strip() for l in (PAGES / f"{page}.txt").read_text().splitlines()]


def after(ls, label, start=0):
    """The line that follows the first line equal to `label` (from `start`)."""
    i = ls.index(label, start)
    return ls[i + 1], i


def build(folder, slug, path, name, degree, field, req, faculty):
    url = B + path
    page = hashlib.sha1(url.encode()).hexdigest()[:12]
    ls = lines(page)
    raw = (PAGES / f"{page}-raw.txt").read_text()
    # header: "UCAS code" ... "Award" + its value, joined as on the page
    i, j = ls.index("UCAS code"), ls.index("Award")
    header = " ".join(ls[i:j + 2])
    duration = int(re.search(r"Duration (\d) years", header).group(1))
    e = ls.index("Entry requirements", ls.index("Entry requirements") + 1)
    alevel, k = after(ls, "A Level", e)
    ib, _ = after(ls, "IB", k)
    ielts = next(l for l in ls if l.startswith("IELTS"))
    home = next(l for l in ls if l.startswith("per year for domestic (UK) students for 2027/28"))
    home_fee = ls[ls.index(home) - 1]
    dl = next(n for n, l in enumerate(ls) if l.startswith("Application deadline for September 2027 entry"))
    intl = re.search(r'"title":"Fees \(international\)","value":"([^"]*)"', raw).group(0)
    year = re.search(r'"courseYearItems":\[\{"year":"2027"', raw).group(0)
    assert '"value":"To be confirmed"' not in intl
    quotes = [header, f"A Level {alevel}", f"IB {ib}", ielts, f"{home_fee} {home}",
              "For all undergraduate courses at Birmingham, you apply online through UCAS.",
              f"{ls[dl - 1]} {ls[dl]}"]
    if faculty:
        quotes.append(faculty)
    apps = []
    if slug == "dentistry":
        quotes += ["Sit the University Clinical Aptitude Test (UCAT) in year of application",
                   "Attend interview if invited",
                   "every applicant for admission to the University must have reached the age of 18 years on 1 October of the year of entry."]
        apps = [
            {"name": "UCAT", "description": "Sit the University Clinical Aptitude Test (UCAT) in the year you apply.", "type": "standardized_test_score", "source": "course"},
            {"name": "Interview", "description": "Attend interview if invited.", "type": "interview_or_evaluation_event", "source": "course"},
            {"name": "Minimum age", "description": "You must be 18 years old on 1 October of the year of entry.", "type": "other", "source": "course"},
        ]
    if slug == "accounting-finance":
        quotes.append("A Level AAA. GCSE Mathematics grade 6.")
    tidy = lambda t: re.sub(r"\s*Further (details|information) below\.", "", t)
    home_n = int(home_fee.strip("£").replace(",", ""))
    intl_val = intl.split('"value":"')[1].rstrip('"')
    eng = {"test_name": ENG_IELTS, "min_score": ielts.replace("IELTS*:", "IELTS").replace("IELTS:", "IELTS"), "source": "course"}
    tests = [{"name": "UCAT", "required": "required"}] if slug == "dentistry" else []
    extra = " UCAT and interview also required." if slug == "dentistry" else ""
    intl_cost = {
        "residency": "international", "currency": "GBP", "academic_year": "2027 entry", "source": "coursedata",
        "living_from": "costProfile-uk-birmingham-cost-beng-engineering-international",
    }
    if slug in FORMULA:
        intl_cost["tuition_formula"] = FORMULA[slug]
        intl_cost["note"] = (f"International fees for 2027 entry: {intl_val.replace('–', '-')}. "
                             "Shown as the average over the 5 years (our calculation).")
    else:
        intl_cost["tuition_annual"] = int(intl_val.strip("£").replace(",", ""))
        intl_cost["note"] = f"International fee for 2027 entry: {intl_val} a year (Birmingham course page)."
    r = {
        "uni": "uk-birmingham", "slug": slug,
        "sources": {
            "course": {"url": url, "page": page, "title": f"{name} {degree} | University of Birmingham",
                       "organization": "University of Birmingham", "quotes": quotes},
            "coursedata": {"url": url, "page": f"{page}-raw",
                           "title": f"{name} {degree} | University of Birmingham (fee data in the page)",
                           "organization": "University of Birmingham", "quotes": [year, intl]},
        },
        "program": {
            "name": name, "degree_type": degree, "field": field, "faculty": faculty,
            "duration_years": duration, "languages": ["en"], "entry_year": "2027 entry",
            "platform": "UCAS", "source": "course",
            "summary": f"{name} {degree} ({header.split()[2]}), {duration} years.{extra}",
            "application_requirements": apps,
        },
        "costs": [
            {"residency": "home", "currency": "GBP", "tuition_annual": home_n,
             "academic_year": "2027/28 (2027 entry)", "source": "course",
             "living_from": "costProfile-uk-birmingham-cost-beng-engineering-home",
             "note": f"UK fee: {home_fee} per year for 2027/28 (Birmingham course page)."},
            intl_cost,
        ],
        "admissions": [
            {"curriculum": "a-level", "source": "course", "threshold": f"{name}: {tidy(alevel)}{extra}",
             "required_subjects": req, "tests": tests, "english": eng},
            {"curriculum": "ib", "source": "course", "threshold": f"{name}: IB {tidy(ib)}{extra}",
             "required_subjects": req, "tests": tests, "english": eng},
        ],
    }
    if slug == "dentistry":
        r["deadline"] = {"date": "2026-10-15", "round": "UCAS deadline", "platform": "UCAS", "source": "course",
                         "note": "Application deadline for September 2027 entry: 15 October 2026."}
    write(folder, r)
    print(folder, slug, duration, alevel, "|", ib, "|", home_fee, intl_val)


for c in COURSES:
    build(*c)

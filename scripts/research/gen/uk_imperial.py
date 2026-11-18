"""Imperial College London courses, 2027 entry (written 2026-11-18).

Quotes are cut from the saved course page text with whitespace collapsed (build.py compares
the same way), so they are verbatim. Each course page states whether the standard or the
higher English requirement applies; the levels come from Imperial's English language page.
  python3 -I scripts/research/gen/uk_imperial.py
"""
import hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
I = "https://www.imperial.ac.uk/study/courses/undergraduate/2027/"
ENGP = "https://www.imperial.ac.uk/study/apply/english-language/"
IELTS_Q = "IELTS - Academic (Test-Centre/UKVI SELT/Online) Standard Higher 6.5 overall (minimum 6.0 in all elements) 7.0 overall (minimum 6.5 in all elements)"
LEVEL = {"standard": "IELTS 6.5 overall (minimum 6.0 in all elements): Imperial's standard level, required for this course.",
         "higher": "IELTS 7.0 overall (minimum 6.5 in all elements): Imperial's higher level, required for this course."}
LIVING = "costProfile-uk-imperial-cost-meng-engineering-{}"

# folder, slug, path, name, field, required subjects, admissions-test quote, test name, test description
COURSES = [
    ("mathematics", "mathematics", "mathematics-bsc", "Mathematics", "Mathematics", ["Mathematics", "Further Mathematics"],
     "All applicants should take the Test for Mathematics for University Admission (TMUA) as part of the application process for this course.",
     "TMUA", "All applicants should take the Test of Mathematics for University Admission (TMUA)."),
    ("physics", "physics", "physics-bsc", "Physics", "Physics", ["Mathematics", "Physics"],
     "You must sit the Engineering and Science Admissions Test (ESAT) as part of the application process for this course.",
     "ESAT", "Sit the Engineering and Science Admissions Test (ESAT): Mathematics 1, Mathematics 2 and Physics modules."),
    ("chemistry", "chemistry", "chemistry-bsc", "Chemistry", "Chemistry", ["Chemistry", "Mathematics"], None, None, None),
    ("biology", "biochemistry", "biochemistry-bsc", "Biochemistry", "Biochemistry", ["Chemistry"],
     "You must sit the Engineering and Science Admissions Test (ESAT) as part of the application process for this course.",
     "ESAT", "Sit the Engineering and Science Admissions Test (ESAT): Mathematics 1, Chemistry and Biology modules."),
    ("engineering", "aeronautical-engineering", "aeronautical-engineering", "Aeronautical Engineering", "Aerospace Engineering", ["Mathematics", "Physics"],
     "You must sit the Engineering and Science Admissions Test (ESAT) as part of the application process for this course.",
     "ESAT", "Sit the Engineering and Science Admissions Test (ESAT): Mathematics 1, Mathematics 2 and Physics modules."),
    ("engineering", "biomedical-engineering", "biomedical-engineering", "Biomedical Engineering", "Biomedical Engineering", ["Mathematics", "Physics"], None, None, None),
]
ESAT_MODULES = {"physics": "you will need to sit three ESAT modules: Mathematics 1 Mathematics 2 Physics",
                "aeronautical-engineering": "you will need to sit three ESAT modules: Mathematics 1 Mathematics 2 Physics",
                "biochemistry": "you will need to sit three ESAT modules: Mathematics 1 Chemistry Biology"}
NO_TEST = "This department does not use a test as part of its selection process"


def pid(url):
    return hashlib.sha1(url.encode()).hexdigest()[:12]


def text(url):
    t = (PAGES / f"{pid(url)}.txt").read_text()
    return re.sub(r"\s+", " ", t.replace(" ", " "))


def first(pat, t):
    m = re.search(pat, t)
    assert m, pat
    return m.group(0).strip()


def build(folder, slug, path, name, field, req, test_q, test_name, test_desc):
    url = I + path + "/"
    t = text(url)
    header = first(r"Qualification (\w+) Duration (\d) [Yy]ears Start date October 2027 UCAS course code \w+", t)
    degree, duration = re.match(r"Qualification (\w+) Duration (\d)", header).groups()
    ucas = header.split()[-1]
    dept = first(r"Delivered by Department of [A-Z][a-z]+(?: [A-Z][a-z]+)?(?= Location)", t)
    alevel = first(r"A-levels Minimum entry standard .+? (?=Not accepted)", t)
    ib = first(r"Minimum entry standard \d\d points To include: .+? (?=Preferred Mathematics syllabus)", t)
    level = first(r"must achieve the (higher|standard) university requirement", t)
    home = first(r"Home fee 2027 entry £[\d,]+ per year", t)
    over = first(r"Overseas fee 2027 entry £[\d,]+ per year", t)
    quotes = [header, dept, alevel, ib, level, home, over]
    tests, apps, extra = [], [], ""
    if test_q:
        assert test_q in t, slug
        quotes.append(test_q)
        if slug in ESAT_MODULES:
            quotes.append(ESAT_MODULES[slug])
        tests = [{"name": test_name, "required": "required"}]
        apps = [{"name": test_name, "description": test_desc, "type": "standardized_test_score", "source": "course"}]
        extra = f" {test_name} also required."
    else:
        assert NO_TEST in t, slug
        quotes.append(NO_TEST)
    lvl = "higher" if "higher" in level else "standard"
    eng = {"test_name": "IELTS Academic (or accepted equivalent)", "min_score": LEVEL[lvl], "source": "english"}
    a_txt = alevel.replace("A-levels Minimum entry standard ", "").replace(" To include:", ", to include:")
    ib_txt = ib.replace("Minimum entry standard ", "").replace(" To include:", ", to include:")
    n = lambda s: int(re.search(r"£([\d,]+)", s).group(1).replace(",", ""))
    r = {
        "uni": "uk-imperial", "slug": slug,
        "sources": {
            "course": {"url": url, "page": pid(url), "title": f"{name} {degree} | Imperial College London",
                       "organization": "Imperial College London", "quotes": quotes},
            "english": {"url": ENGP, "page": pid(ENGP), "title": "English language requirements | Imperial College London",
                        "organization": "Imperial College London", "quotes": [IELTS_Q]},
        },
        "program": {"name": name, "degree_type": degree, "field": field, "faculty": dept.replace("Delivered by ", ""),
                    "duration_years": int(duration), "languages": ["en"], "entry_year": "2027 entry", "platform": "UCAS",
                    "source": "course", "summary": f"{name} {degree} (UCAS {ucas}), {duration} years.{extra}",
                    "application_requirements": apps},
        "costs": [
            {"residency": "home", "currency": "GBP", "tuition_annual": n(home), "academic_year": "2027 entry", "source": "course",
             "living_from": LIVING.format("home"), "note": f"Home fee, 2027 entry: £{n(home):,} per year (Imperial course page)."},
            {"residency": "international", "currency": "GBP", "tuition_annual": n(over), "academic_year": "2027 entry", "source": "course",
             "living_from": LIVING.format("international"), "note": f"Overseas fee, 2027 entry: £{n(over):,} per year (Imperial course page)."},
        ],
        "admissions": [
            {"curriculum": "a-level", "source": "course", "threshold": f"{name}: {a_txt}{extra}", "required_subjects": req, "tests": tests, "english": eng},
            {"curriculum": "ib", "source": "course", "threshold": f"{name}: IB {ib_txt}{extra}", "required_subjects": req, "tests": tests, "english": eng},
        ],
    }
    write(folder, r)
    print(slug, degree, duration, ucas, lvl, n(over), "|", a_txt[:90])


for c in COURSES:
    build(*c)

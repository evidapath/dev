"""University of Manchester courses, 2027 entry (written 2026-11-18).

Quotes are taken line by line from the saved course page text (verbatim). Fees are the
page's own sentences ("Tuition fees for home/international students will be £X for the
2027/28 academic year"). build.py re-checks every quote and number.
  python3 -I scripts/research/gen/uk_manchester.py [--print]
"""
import hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
M = "https://www.manchester.ac.uk/study/undergraduate/courses/2027/"
ENG = "IELTS Academic (or accepted equivalent)"
LIVING = "costProfile-uk-manchester-cost-beng-mechanical-eng-{}"

# folder, slug, path, name, degree, field, required subjects (strict; checked against the quoted A-level line)
COURSES = [
    ("mathematics", "mathematics", "00590/bsc-mathematics", "Mathematics", "BSc", "Mathematics", ["Mathematics (or Further Mathematics)"]),
    ("physics", "physics", "00638/bsc-physics", "Physics", "BSc", "Physics", None),
    ("chemistry", "chemistry", "00544/bsc-chemistry", "Chemistry", "BSc", "Chemistry", None),
    ("pharmacy", "pharmacy", "01695/mpharm-pharmacy", "Pharmacy", "MPharm", "Pharmacy", None),
    ("engineering", "aerospace-engineering", "03333/beng-aerospace-engineering", "Aerospace Engineering", "BEng", "Aerospace Engineering", None),
    ("politics", "politics-international-relations", "00675/bsocsc-politics-and-international-relations", "Politics and International Relations", "BSocSc", "Politics", None),
    ("politics", "ppe", "00154/ba-politics-philosophy-and-economics", "Politics, Philosophy and Economics", "BA", "Politics, Philosophy and Economics", None),
    ("accounting", "accounting-finance", "05151/baecon-accounting-and-finance", "Accounting and Finance", "BAEcon", "Accounting and Finance", None),
    ("dentistry", "dentistry", "00398/bds-dentistry-first-year-entry", "Dentistry", "BDS", "Dentistry", None),
    ("humanities", "english-literature", "00060/ba-english-literature", "English Literature", "BA", "English", None),
    ("humanities", "history", "00255/ba-history", "History", "BA", "History", None),
    ("humanities", "geography", "22122/bsc-geography", "Geography", "BSc", "Geography", None),
    ("biology", "biochemistry", "00521/bsc-biochemistry", "Biochemistry", "BSc", "Biochemistry", None),
    ("biology", "pharmacology", "00634/bsc-pharmacology", "Pharmacology", "BSc", "Pharmacology", None),
]
REQ = {}
SKIP = set()


def facts(page):
    ls = [l.strip() for l in (PAGES / f"{page}.txt").read_text().splitlines()]
    f = {"ls": ls}
    d = next(i for i, l in enumerate(ls) if l.startswith("Duration:"))
    f["header"] = " ".join(ls[d:d + 3])
    assert ls[d + 1] == "Year of entry: 2027" and ls[d + 2].startswith("UCAS course code:"), ls[d:d + 3]
    f["dur_text"] = ls[d]
    e = ls.index("Entry requirements")
    a = ls.index("A-level", e)
    al = [ls[a + 1]]
    if al[0].endswith(":"):
        al.append(ls[a + 2])
    f["alevel"] = al
    b = ls.index("International Baccalaureate", a)
    ib = [ls[b + 1]]
    if re.fullmatch(r"\d+", ib[0]):
        ib.append(ls[b + 2])
    if ib[-1].endswith("either:"):
        ib += ls[b + len(ib) + 1:b + len(ib) + 3]
    f["ib"] = ib
    f["ielts"] = next(l for l in ls[e:] if "IELTS" in l and re.search(r"\d", l))
    f["home"] = next(l for l in ls if l.startswith("Tuition fees for home students will be £"))
    f["intl"] = [l for l in ls if l.startswith("Tuition fees for international students")]
    return f


def sentence(line, upto):
    """The line cut after the first occurrence of `upto` (keeps it a verbatim prefix)."""
    return line[: line.index(upto) + len(upto)]


def build(folder, slug, path, name, degree, field, req):
    url = M + path + "/"
    page = hashlib.sha1(url.encode()).hexdigest()[:12]
    f = facts(page)
    if "--print" in sys.argv:
        print(f"## {slug} {page}\n  {f['header']}\n  A: {' / '.join(f['alevel'])}\n  IB: {' '.join(f['ib'])}\n  {f['ielts']}\n  {f['home'][:110]}")
        for l in f["intl"]:
            print("  " + l[:200])
        return
    if slug in SKIP:
        return
    req = REQ.get(slug, req)
    assert req is not None, slug
    duration = int(re.match(r"Duration: (\d)", f["dur_text"]).group(1))
    home_q = sentence(f["home"], "academic year.")
    home_n = int(re.search(r"£([\d,]+)", home_q).group(1).replace(",", ""))
    alevel = " ".join(f["alevel"])
    ib = " ".join(f["ib"])
    quotes = [f["header"], f"A-level {alevel}", f"International Baccalaureate {ib}", f["ielts"], home_q]
    costs = [{"residency": "home", "currency": "GBP", "tuition_annual": home_n,
              "academic_year": "2027/28 (2027 entry)", "source": "course", "living_from": LIVING.format("home"),
              "note": f"Home fee, 2027/28 (2027 entry): £{home_n:,} a year (The University of Manchester course page)."}]
    intl_cost = {"residency": "international", "currency": "GBP", "academic_year": "2027/28 (2027 entry)",
                 "source": "course", "living_from": LIVING.format("international")}
    if slug in FORMULA:
        quotes += FORMULA[slug]["quotes"]
        intl_cost["tuition_formula"] = FORMULA[slug]["formula"]
        intl_cost["note"] = FORMULA[slug]["note"]
    else:
        iq = f["intl"][0]
        iq = iq[: iq.index("reserves the right to increase the tuition fee by up to 7% each year") + len("reserves the right to increase the tuition fee by up to 7% each year")]
        quotes.append(iq)
        n = int(re.search(r"£([\d,]+)", iq).group(1).replace(",", ""))
        intl_cost["tuition_annual"] = n
        intl_cost["note"] = f"International fee for 2027/28: £{n:,}. The University may raise it by up to 7% a year in later years."
    costs.append(intl_cost)
    quotes += EXTRA.get(slug, [])
    eng_line = re.sub(r",? or;?$", "", f["ielts"].lstrip("•").strip()).rstrip(";,. ")
    eng = {"test_name": ENG, "min_score": eng_line + ".", "source": "course"}
    tests, apps, extra = TESTS.get(slug, ([], [], ""))
    r = {
        "uni": "uk-manchester", "slug": slug,
        "sources": {"course": {"url": url, "page": page, "title": f"{degree} {name} (2027 entry) | The University of Manchester",
                               "organization": "The University of Manchester", "quotes": quotes}},
        "program": {"name": name, "degree_type": degree, "field": field, "faculty": "", "duration_years": duration,
                    "languages": ["en"], "entry_year": "2027 entry", "platform": "UCAS", "source": "course",
                    "summary": f"{degree} {name} (UCAS {f['header'].split('UCAS course code: ')[1].split()[0]}), {duration} years.{extra}",
                    "application_requirements": apps},
        "costs": costs,
        "admissions": [
            {"curriculum": "a-level", "source": "course", "threshold": f"{name}: {alevel}{extra}", "required_subjects": req, "tests": tests, "english": eng},
            {"curriculum": "ib", "source": "course", "threshold": f"{name}: IB {ib}{extra}", "required_subjects": req, "tests": tests, "english": eng},
        ],
    }
    if slug in DEADLINE:
        r["deadline"] = DEADLINE[slug]
    write(folder, r)
    print(folder, slug, duration, home_n, intl_cost.get("tuition_annual", intl_cost.get("tuition_formula")))


FORMULA, TESTS, DEADLINE = {}, {}, {}
REQ.update({"physics": ["Physics", "Mathematics (or Further Mathematics)"], "chemistry": ["Chemistry"],
            "pharmacy": ["Chemistry"], "aerospace-engineering": ["Mathematics", "Physics"],
            "politics-international-relations": [], "ppe": [], "accounting-finance": [],
            "english-literature": ["English Literature (or English Language & Literature)"], "history": ["History"],
            "geography": [], "biochemistry": ["Chemistry"], "pharmacology": []})
# Dentistry: year 1 fee is for 2027/28, but the clinical-year fee is only published for students
# entering Year 2 in 2027 (not 2028), so a full-course cost can't be quoted. Held.
SKIP.add("dentistry")
# "3 or 4 years": the fourth year is an optional year abroad or placement (quoted).
EXTRA = {
    "politics-international-relations": ["Enjoy the option to delve into a different culture on a study abroad year or gain valuable professional experience through a 12-month placement."],
    "ppe": ["If completing a year abroad, you will take the Year 3 course content in Year 4."],
    "accounting-finance": ["You can apply to study overseas for an unforgettable year at one of our international partner universities. You apply in Year 2 to spend a year abroad in Year 3."],
    "pharmacy": ["Selection for interview is normally based on predicted grades matching the entry requirement (i.e. AAB)."],
}
TESTS["pharmacy"] = ([], [{"name": "Interview", "description": "Selection for interview is normally based on predicted grades matching the entry requirement (AAB).", "type": "interview_or_evaluation_event", "source": "course"}], " Interview.")
if __name__ == "__main__":
    for c in COURSES:
        build(*c)

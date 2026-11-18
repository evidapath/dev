"""University of Nottingham (UK) courses, 2027 entry (written 2026-11-18).

Quotes are taken line by line from the saved course page text, so they are verbatim. The
page's info bar labels which fee is for home and which for international students
(`home-student-detail` / `international-student-detail`); those labels are quoted from the
page HTML (<id>-raw.txt, made by scripts/research/raw.py). build.py re-checks everything.
  python3 -I scripts/research/gen/uk_nottingham.py [--print]
"""
import hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
N = "https://www.nottingham.ac.uk/studywithus/ugstudy/courses/UG/"
ENG = "IELTS Academic (or accepted equivalent)"

# folder, slug, page name, name, degree, field, required subjects (strict)
COURSES = [
    ("mathematics", "mathematics", "Mathematics-BSc-Hons", "Mathematics", "BSc (Hons)", "Mathematics", ["Mathematics"]),
    ("physics", "physics", "Physics-BSc-Hons", "Physics", "BSc (Hons)", "Physics", None),
    ("chemistry", "chemistry", "Chemistry-BSc-Hons", "Chemistry", "BSc (Hons)", "Chemistry", None),
    ("pharmacy", "pharmacy", "Pharmacy-MPharm", "Pharmacy", "MPharm (Hons)", "Pharmacy", None),
    ("engineering", "aerospace-engineering", "Aerospace-Engineering-BEng-Hons", "Aerospace Engineering", "BEng (Hons)", "Aerospace Engineering", None),
    ("politics", "politics-international-relations", "Politics-and-International-Relations-BA-Hons", "Politics and International Relations", "BA (Hons)", "Politics", None),
    ("politics", "ppe", "Philosophy-Politics-and-Economics-BA-Hons", "Philosophy, Politics and Economics", "BA (Hons)", "Politics, Philosophy and Economics", None),
    ("accounting", "finance-accounting-management", "Finance-Accounting-and-Management-BSc-Hons", "Finance, Accounting and Management", "BSc (Hons)", "Accounting and Finance", None),
    ("biology", "biochemistry", "Biochemistry-BSc-Hons", "Biochemistry", "BSc (Hons)", "Biochemistry", None),
    ("biology", "pharmacology", "Pharmacology-BSc-Hons", "Pharmacology", "BSc (Hons)", "Pharmacology", None),
    ("humanities", "english", "English-BA-Hons", "English", "BA (Hons)", "English", None),
    ("humanities", "history", "History-BA-Hons", "History", "BA (Hons)", "History", None),
    ("humanities", "geography", "Geography-BSc-Hons", "Geography", "BSc (Hons)", "Geography", None),
]
# required subjects for courses marked None: filled in after reading each page (see REQ)
REQ = {"physics": ["Mathematics", "Physics"], "chemistry": ["Chemistry"], "pharmacy": ["Chemistry"],
       "aerospace-engineering": ["Mathematics"], "pharmacology": ["Chemistry"], "biochemistry": ["Chemistry"],
       "politics-international-relations": [], "ppe": [], "finance-accounting-management": [],
       "english": [], "history": [], "geography": []}


def nxt(ls, label, start=0):
    i = ls.index(label, start)
    return ls[i + 1], i


def facts(page):
    ls = [l.strip() for l in (PAGES / f"{page}.txt").read_text().splitlines()]
    raw = (PAGES / f"{page}-raw.txt").read_text()
    f = {"ls": ls}
    deg, i = ls[ls.index("UCAS Code") - 1], ls.index("UCAS Code")
    f["ucas"] = f"{deg} UCAS Code {ls[i + 1]}"
    d = ls.index("Duration")
    f["duration_q"] = " ".join(ls[d:d + 6])
    f["duration"] = int(re.match(r"(\d) years full-time", ls[d + 1]).group(1))
    assert ls[d + 4] == "Select start date" and ls[d + 5] == "September 2027", ls[d:d + 6]
    q = ls.index("Quick glance")
    f["glance"] = " ".join(ls[q + 2:q + 6])
    assert ls[q + 2] == "A levels" and ls[q + 4] == "IB", ls[q:q + 6]
    f["alevel"], f["ib"] = ls[q + 3], ls[q + 5]
    f["req"] = nxt(ls, "Required subjects")[0] if "Required subjects" in ls else ""
    f["ibscore"] = nxt(ls, "IB score")[0] if "IB score" in ls else ""
    g = ls.index("A level and GCSE requirements")
    f["adetail"] = ls[g + 2] if ls[g + 1] == "A levels" and not f["req"] else ""
    f["gcse"] = nxt(ls, "GCSEs", g)[0] if "GCSEs" in ls[g:g + 6] else ""
    f["ibreq"] = ""
    if f["ibscore"]:
        s_ = ls.index("IB score")
        if ls[s_ + 2] == "IB requirements":
            f["ibreq"] = ls[s_ + 3]
    f["ielts"] = nxt(ls, "IELTS", ls.index("IELTS/English requirements"))[0]
    for who in ("home", "international"):
        m = re.search(r'<span class="info-bar__list-link-label %s-student-detail">\s*(£[\d,]+) per year</span>' % who, raw)
        f[who] = (re.sub(r"\s+", " ", m.group(0)), int(m.group(1)[1:].replace(",", ""))) if m else None
    return f


def build(folder, slug, pname, name, degree, field, req):
    url = N + pname + ".html"
    page = hashlib.sha1(url.encode()).hexdigest()[:12]
    f = facts(page)
    if "--print" in sys.argv:
        print(f"## {slug} {page}\n  {f['ucas']} | {f['duration_q']}\n  glance: {f['glance']}\n  req: {f['req']}\n  ibscore: {f['ibscore']}\n  adetail: {f['adetail']}\n  gcse: {f['gcse']}\n  ibreq: {f['ibreq']}\n  ielts: {f['ielts']}\n  fees: {f['home']} {f['international']}")
        return
    req = REQ.get(slug, req)
    assert req is not None, f"{slug}: required subjects not set"
    quotes = [f["ucas"], f["duration_q"], "The entrance requirements listed apply to 2027 entry.", f["glance"],
              f"IELTS {f['ielts']}"]
    if f["req"]:
        quotes.append(f"Required subjects {f['req']}")
    if f["ibscore"]:
        quotes.append(f"IB score {f['ibscore']}" + (f" IB requirements {f['ibreq']}" if f["ibreq"] else ""))
    if f["adetail"]:
        quotes.append(f"A levels {f['adetail']}")
    if f["gcse"]:
        quotes.append(f"GCSEs {f['gcse']}")
    eng = {"test_name": ENG, "min_score": f"IELTS {f['ielts']}.", "source": "course"}
    def sent(*parts):
        return " ".join(p.strip().rstrip(".") + "." for p in parts if p)
    ibs = re.sub(r"^IB score\s+", "", f["ibscore"]) if f["ibscore"] else f["ib"]
    alevel_t = f"{name}: " + sent(f"A levels {f['adetail'] or f['alevel']}",
                                  f"Required subjects: {f['req']}" if f["req"] else "",
                                  f"GCSEs: {f['gcse']}" if f["gcse"] else "")
    ib_t = f"{name}: " + sent(f"IB {ibs}", f["ibreq"])
    costs = []
    for who, liv in (("home", "home"), ("international", "international")):
        if not f[who]:
            continue
        costs.append({"residency": who, "currency": "GBP", "tuition_annual": f[who][1], "academic_year": "2027 entry",
                      "source": ["coursedata", "course"],
                      "living_from": f"costProfile-uk-nottingham-cost-beng-engineering-{liv}",
                      "note": f"{'Home' if who == 'home' else 'International'} fee for a September 2027 start: £{f[who][1]:,} per year (Nottingham course page)."})
    r = {
        "uni": "uk-nottingham", "slug": slug,
        "sources": {
            "course": {"url": url, "page": page, "title": f"{name} {degree} | University of Nottingham",
                       "organization": "University of Nottingham", "quotes": quotes},
            "coursedata": {"url": url, "page": f"{page}-raw",
                           "title": f"{name} {degree} | University of Nottingham (fee labels in the page)",
                           "organization": "University of Nottingham",
                           "quotes": [f[w][0] for w in ("home", "international") if f[w]]},
        },
        "program": {"name": name, "degree_type": degree, "field": field, "faculty": "",
                    "duration_years": f["duration"], "languages": ["en"], "entry_year": "2027 entry",
                    "platform": "UCAS", "source": "course",
                    "summary": f"{name} {degree} (UCAS {f['ucas'].split()[-1]}), {f['duration']} years.",
                    "application_requirements": []},
        "costs": costs,
        "admissions": [
            {"curriculum": "a-level", "source": "course", "threshold": alevel_t, "required_subjects": req, "tests": [], "english": eng},
            {"curriculum": "ib", "source": "course", "threshold": ib_t, "required_subjects": req, "tests": [], "english": eng},
        ],
    }
    write(folder, r)
    print(folder, slug, "ok")


for c in COURSES:
    build(*c)

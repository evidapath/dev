"""University of Nottingham Malaysia courses, September 2027 start (written 2026-11-18).

Quotes are taken line by line from the saved course page (verbatim). Fees are the page's own
"Malaysian fee" / "International fee" lines (fixed for the programme; 6% SST on top for
non-Malaysians, quoted). build.py re-checks every quote and number.
  python3 -I scripts/research/gen/my_nottingham.py
"""
import hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
U = "https://www.nottingham.edu.my/ugstudy/course/"
CBSE = "Senior School Certificate Examination (CBSE) / Indian School Certificate (CISCE) - Class XII"
SST = "*For International Students, a 6% Sales and Service Tax (SST) will apply to non-Malaysian citizens from 1 July 2025."
FIXED = "Enjoy peace of mind with our Fixed Tuition Fee policy, pay the same amount each year until you graduate."

# folder, slug, page, name, field, required subjects (strict)
COURSES = [
    ("biology", "biomedical-science", "biomedical-science-bsc-hons", "Biomedical Science", "Biomedical Science", ["Biology", "Chemistry"]),
    ("accounting", "finance-accounting-management", "finance-accounting-and-management-bsc-hons", "Finance, Accounting and Management", "Accounting and Finance", []),
    ("business", "international-business-management", "international-business-management-bsc-hons", "International Business Management", "Business", []),
    ("politics", "international-relations", "international-relations-ba-hons", "International Relations", "International Relations", []),
    ("humanities", "english-language-literature", "english-language-and-literature-ba-hons", "English Language and Literature", "English", []),
    ("mathematics", "mathematics-data-science", "mathematics-and-data-science-bsc-hons", "Mathematics and Data Science", "Mathematics", ["Mathematics"]),
    ("engineering", "mechatronic-engineering", "mechatronic-engineering-meng-hons", "Mechatronic Engineering", "Mechatronic Engineering", ["Mathematics", "Physics"]),
]
# Not added: Pharmacy MPharm: 2 years in Malaysia (RM75,000 a year) then 2 years in the UK
# (GBP £33,500 a year); a cost record holds one currency, so it can't be stored faithfully yet.


def build(folder, slug, page_name, name, field, req):
    url = U + page_name
    page = hashlib.sha1(url.encode()).hexdigest()[:12]
    ls = [l.strip() for l in (PAGES / f"{page}.txt").read_text().splitlines()]
    nx = lambda lbl: ls[ls.index(lbl) + 1]
    i = next(k for k, l in enumerate(ls) if l.startswith("Full-time:"))
    title = ls[i - 2]
    block = ls[i:i + 6]
    assert block[2] == "Start date: September 2027", block
    dur = int(re.match(r"Full-time: (\d) years$", block[0]).group(1))
    my = int(re.match(r"Malaysian fee: RM([\d,]+) per year$", block[3]).group(1).replace(",", ""))
    intl = int(re.match(r"International fee: RM([\d,]+) per year\*$", block[4]).group(1).replace(",", ""))
    degree = re.match(r"(BSc \(Hons\)|BA \(Hons\)|MEng \(Hons\))", title).group(1)
    al, ib, cb, ap, ie = nx("A Level"), nx("IB Diploma"), nx(CBSE), nx("Advance Placement (AP)"), nx("IELTS (Academic):")
    joined = " ".join(ls)
    assert SST in joined and FIXED in joined
    quotes = [title, " ".join(block[:5]), FIXED, SST, f"A Level {al}", f"IB Diploma {ib}", f"{CBSE} {cb}",
              f"Advance Placement (AP) {ap}", f"IELTS (Academic): {ie}"]
    eng = {"test_name": "IELTS Academic (or accepted equivalent)", "min_score": f"IELTS (Academic) {ie}.", "source": "course"}
    adm = lambda cur, t: {"curriculum": cur, "source": "course", "threshold": f"{name}: {t}", "required_subjects": req, "tests": [], "english": eng}
    r = {
        "uni": "my-nottingham", "slug": slug,
        "sources": {"course": {"url": url, "page": page, "title": f"{title} | University of Nottingham Malaysia",
                               "organization": "University of Nottingham Malaysia", "quotes": quotes}},
        "program": {"name": name, "degree_type": degree, "field": field, "faculty": "", "duration_years": dur,
                    "languages": ["en"], "entry_year": "2027 entry", "platform": "", "source": "course",
                    "summary": f"{title}, {dur} years full-time, September 2027 start.", "application_requirements": []},
        "costs": [
            {"residency": "international", "currency": "MYR", "tuition_annual": intl,
             "academic_year": "September 2027 start (fixed for the programme)", "source": "course",
             "living_from": "costProfile-my-nottingham-cost-meng-me-international",
             "fees_from": "costProfile-my-nottingham-cost-meng-me-international",
             "note": f"International fee: RM{intl:,} per year, fixed for the programme. A 6% Sales and Service Tax (SST) applies to non-Malaysian citizens on top of this."},
            {"residency": "malaysian", "currency": "MYR", "tuition_annual": my,
             "academic_year": "September 2027 start (fixed for the programme)", "source": "course",
             "living_from": "costProfile-my-nottingham-cost-meng-me-malaysian",
             "note": f"Malaysian fee: RM{my:,} per year, fixed for the programme."},
        ],
        "admissions": [adm("a-level", al), adm("ib", f"IB Diploma {ib}"), adm("cbse", f"CBSE / CISCE Class XII: {cb}"),
                       adm("us-hs", f"Advanced Placement (AP) {ap}")],
    }
    write(folder, r)
    print(slug, degree, dur, intl, my)


for c in COURSES:
    build(*c)

"""University of Birmingham Dubai: thirteen more bachelor's courses (written 2026-11-25).

Each course page gives the length ("Duration 3 years (full-time)"), entry grades and the
September 2027 fee. The visible fee box is labelled "Fees (UK/Ireland)"; the page's embedded data
(scripts/research/raw.py → <id>-raw) gives "Fees (international)" separately, which is the
figure stored. Held: Civil Engineering and Electronic and Electrical Engineering (year 1 in Dubai,
years 2-3 in Birmingham UK, so one Dubai fee doesn't cover the degree).
  python3 -I scripts/research/raw.py <id>   (for each page, first)
  python3 -I scripts/research/gen/ae_bham_dubai.py
"""
import hashlib, re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
B = "https://www.birmingham.ac.uk/dubai/study/undergraduate/subjects/"
def norm(s): return re.sub(r"\s+", " ", s.replace("\xa0", " ").replace("’", "'")).strip().lower()
def raw(p): return re.sub(r"\s+", " ", (PAGES / f"{p}.txt").read_text(errors="replace"))

# url tail, page id, name, degree, field
C = [
 ("biomedical-science-courses/biomedical-science-bsc", "ae7673fdcdb0", "Biomedical Science", "BSc", "Biomedical Science"),
 ("business-and-finance-courses/accounting-and-finance-bsc", "6b3efafe04a9", "Accounting and Finance", "BSc", "Accounting and Finance"),
 ("business-and-finance-courses/business-management-with-economics-bsc", "ebff0721ff79", "Business Management with Economics", "BSc", "Business"),
 ("business-and-finance-courses/business-management-with-finance-bsc", "6e8f714a7c99", "Business Management with Finance", "BSc", "Business"),
 ("business-and-finance-courses/business-management-with-marketing-bsc", "39a824051eb9", "Business Management with Marketing", "BSc", "Business"),
 ("business-and-finance-courses/business-management-with-psychology-bsc", "96faf75ab5c0", "Business Management with Psychology", "BSc", "Business"),
 ("business-and-finance-courses/money-banking-and-finance-bsc", "284f1796093e", "Money, Banking and Finance", "BSc", "Economics"),
 ("computer-science-courses/artificial-intelligence-and-computer-science-bsc", "204539fa77d0", "Artificial Intelligence and Computer Science", "BSc", "Computer Science"),
 ("engineering-courses/mechanical-engineering-beng", "76359992c523", "Mechanical Engineering", "BEng", "Mechanical Engineering"),
 ("engineering-courses/mechanical-engineering-biomedical-beng", "ede5be874547", "Mechanical Engineering (Biomedical)", "BEng", "Biomedical Engineering"),
 ("engineering-courses/robotics-artificial-intelligence-ai-beng-dubai", "9937fb50054c", "Robotics and Artificial Intelligence", "BEng", "Mechatronic Engineering"),
 ("law-courses/bachelor-commercial-law", "511da8c5989c", "Commercial Law", "Bachelor of Commercial Law", "Law"),
 ("media-and-marketing-courses/digital-media-and-communications-ba", "4f8b8ca492ac", "Digital Media and Communications", "BA", "Media and Communication"),
]
ENG_Q = "To study at the University, you must be able to demonstrate a good level of written and spoken English."

for tail, page, name, deg, field in C:
    t = raw(page)
    r = raw(f"{page}-raw")
    dur = re.search(r"Duration 3 years \(full-time\)", t).group(0)
    fee = re.search(r'"Fees \(international\)","value":"September 2027: AED ([\d,]+) per year"', r)
    assert fee, f"{name}: no international fee"
    fee_q = fee.group(0); aed = int(fee.group(1).replace(",", ""))
    al = re.search(r"(?:A Level|Typical offer:) ?(A\*?A\*?[AB]?|AA[AB]|AB[AB]|A[AB]{2})(?: ?- ?[A-C]{3})?", t)
    ib = re.search(r"(?:IB|International Baccalaureate Diploma) \d,\d,\d(?: - \d,\d,\d)?(?: at Higher Level)?[^.]{0,120}?(?:\d+ points(?: overall)?)", t)
    assert al and ib, f"{name}: A-level {bool(al)} IB {bool(ib)}"
    course_q = [dur, al.group(0), ib.group(0)] + ([ENG_Q] if norm(ENG_Q) in norm(t) else [])
    for q in course_q:
        assert norm(q) in norm(t)
    eng = {"test_name": "English language", "min_score": "A good level of written and spoken English (see the course page for accepted tests).", "source": "course"}
    slug = re.sub(r"[^a-z0-9]+", "-", f"{deg} {name}".lower()).strip("-")
    write("bham-dubai", {"uni": "ae-birmingham-dubai", "slug": slug,
        "sources": {"course": {"url": B + tail, "page": page, "title": f"{name} {deg} | University of Birmingham Dubai",
                               "organization": "University of Birmingham Dubai", "quotes": course_q},
                    "intl": {"url": B + tail, "page": f"{page}-raw", "title": f"{name} {deg}: page data (international fee) | University of Birmingham Dubai",
                             "organization": "University of Birmingham Dubai", "quotes": [fee_q]}},
        "program": {"name": name, "degree_type": deg, "field": field, "faculty": "", "duration_years": 3, "languages": [],
                    "entry_year": "September 2027 entry", "platform": "Direct application (Birmingham Dubai admissions portal)", "source": "course",
                    "summary": f"{name} {deg}, 3 years full-time, University of Birmingham Dubai.", "application_requirements": []},
        "costs": [{"residency": "all-students", "currency": "AED", "tuition_annual": aed, "academic_year": "September 2027 entry", "source": "intl",
                   "living_from": "costProfile-ae-birmingham-dubai-cost-bsc-cs-all-students",
                   "note": f"International fee: AED {aed:,} per year for September 2027 entry (the course page's international fee, the same as its UK/Ireland figure)."}],
        "admissions": [
            {"curriculum": "a-level", "source": "course", "threshold": f"{name}: {al.group(0)}.", "required_subjects": [], "tests": [], "english": eng},
            {"curriculum": "ib", "source": "course", "threshold": f"{name}: {ib.group(0)}.", "required_subjects": [], "tests": [], "english": eng}]})
    print("wrote", slug, aed, "|", al.group(0), "|", ib.group(0)[:60])

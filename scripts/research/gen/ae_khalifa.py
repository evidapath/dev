"""Khalifa University: eleven BSc programmes (written 2026-11-25).

Sources, all ku.ac.ae:
  - the programme page: the programme's name;
  - Fee and Payment Guidelines: "Bachelor of Science (BSc) 81,250 AED 4 Years" (estimated cost per
    year and normal duration) at AED 2,500 per credit hour;
  - Undergraduate Admissions: IB / A-level rules, the per-programme subject table (all eleven
    need Mathematics and Physics), English (IELTS 6.0 / TOEFL iBT 79), KU admission tests.
The existing Khalifa records note a conflict with KU's scholarship page ("base tuition AED
100,000/yr"); the same note goes on these. Teaching language not stated on any page read.
  python3 -I scripts/research/gen/ae_khalifa.py
"""
import hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
pid = lambda u: hashlib.sha1(u.encode()).hexdigest()[:12]
FEE_URL = "https://ku.ac.ae/fee-and-payment-guidelines"
ADM_URL = "https://www.ku.ac.ae/undergraduate-admissions"
FEE_Q = ["Bachelor of Science (BSc): AED 2,500 per credit hour", "Bachelor of Science (BSc) 81,250 AED 4 Years"]
ADM_Q = ["*Applicants must be awarded the full IB Diploma with six HL/SL subjects (excluding Islamic Education)",
         "*Minimum score of 4 in each subject – with a total of 24 points.",
         "Minimum five IGCSE/GCSE (O-Level) subjects with grade C or above.",
         "Mathematics (Mandatory) (minimum Grade C) • Two of the following: Physics, Chemistry, and/or Biology (minimum Grade C)",
         "Mandatory English Proficiency Test Score IELTS Academic 6.0 OR TOEFL iBT 79",
         "Shortlisted applicants will be required to take KU Admission Tests",
         "Applicants must have graduated from high school no later than two years before the current year (i.e., not before 2023)."]

# page slug, our slug, name on the page, field, admissions-table row
P = [
 ("b-sc-in-aerospace-engineering", "aerospace-engineering", "Aerospace Engineering", "Aerospace Engineering", "Aerospace Engineering ✔ ✔ X X"),
 ("b-sc-in-biomedical-engineering", "biomedical-engineering", "Biomedical Engineering", "Biomedical Engineering", "Biomedical Engineering ✔ ✔ X X"),
 ("b-sc-in-chemical-engineering", "chemical-engineering", "Chemical Engineering", "Chemical Engineering", "Chemical Engineering ✔ ✔ X X"),
 ("b-sc-in-civil-engineering", "civil-engineering", "Civil Engineering", "Civil Engineering", "Civil Engineering ✔ ✔ X X"),
 ("b-sc-in-electrical-engineering", "electrical-engineering", "Electrical Engineering", "Electrical and Electronic Engineering", "Electrical Engineering ✔ ✔ X X"),
 ("b-sc-in-engineering-systems-and-management", "engineering-systems-management", "Engineering Systems and Management", "Engineering", "Engineering Systems and Management ✔ ✔ X X"),
 ("b-sc-in-mechanical-engineering", "mechanical-engineering", "Mechanical Engineering", "Mechanical Engineering", "Mechanical Engineering ✔ ✔ X X"),
 ("b-sc-in-petroleum-engineering", "petroleum-engineering", "Petroleum Engineering", "Engineering", "Petroleum Engineering ✔ ✔ X X"),
 ("b-sc-in-robotics-artificial-intelligence", "robotics-artificial-intelligence", "Robotics and Artificial Intelligence", "Computer Science", "Robotics and Artificial Intelligence ✔ ✔ X X"),
 ("bsc-in-applied-mathematics-and-statistics", "applied-mathematics-statistics-data-science", "Applied Mathematics, Statistics, and Data Science", "Mathematics", "Applied Mathematics, Statistics, and Data Science ✔ ✔ X X"),
 ("bsc-in-energy-engineering", "energy-engineering", "Energy Engineering", "Engineering", "Energy Engineering ✔ ✔ X X"),
]

def norm(s): return re.sub(r"\s+", " ", s.replace("\xa0", " ").replace("’", "'")).strip().lower()
def text(page): return norm((PAGES / f"{page}.txt").read_text(errors="replace"))
def need(page, quotes):
    t = text(page)
    for q in quotes:
        assert norm(q) in t, f"{page}: not on page: {q}"
    return quotes

ENG = {"test_name": "IELTS Academic / TOEFL iBT", "min_score": "IELTS Academic 6.0 or TOEFL iBT 79 (mandatory).", "source": "admissions"}
NOTE = ("SOURCE CONFLICT: KU's fee page gives AED 2,500 per credit hour and an estimated AED 81,250 a year for a BSc "
        "(normal duration 4 years); KU's partial-scholarship page shows a higher yearly 'Full Tuition'. Housing and transport are extra.")
for page_slug, slug, name, field, row in P:
    url = f"https://www.ku.ac.ae/academics/undergraduate-programs/{page_slug}"
    page = pid(url)
    name_q = f"BSc in {name}" if norm(f"BSc in {name}") in text(page) else f"B.Sc. in {name}"
    write("khalifa", {
        "uni": "ae-khalifa", "slug": slug,
        "sources": {
            "course": {"url": url, "page": page, "title": f"BSc in {name} | Khalifa University",
                       "organization": "Khalifa University", "quotes": need(page, [name_q])},
            "fees": {"url": FEE_URL, "page": pid(FEE_URL), "title": "Fee and Payment Guidelines | Khalifa University",
                     "organization": "Khalifa University", "quotes": need(pid(FEE_URL), FEE_Q)},
            "admissions": {"url": ADM_URL, "page": pid(ADM_URL), "title": "Undergraduate Admissions | Khalifa University",
                           "organization": "Khalifa University", "quotes": need(pid(ADM_URL), ADM_Q + [row])},
        },
        "program": {"name": name, "degree_type": "BSc", "field": field, "duration_years": 4, "duration_source": "fees",
                    "languages": [], "entry_year": "Current (KU pages; year not stated)", "platform": "", "source": "course",
                    "summary": f"BSc in {name} at Khalifa University, Abu Dhabi.", "application_requirements": []},
        "costs": [{"residency": "all-students", "currency": "AED", "tuition_annual": 81250, "academic_year": "Current (KU fee page; year not stated)",
                   "source": "fees", "note": NOTE, "living_from": "costProfile-ae-khalifa-cost-bsc-eng-all-students"}],
        "admissions": [
            {"curriculum": "ib", "source": "admissions",
             "threshold": f"{name}: full IB Diploma (six HL/SL subjects), at least 4 in each subject and 24 points in total, including Mathematics and Physics. Shortlisted applicants take KU's admission tests; high-school graduation no earlier than 2023.",
             "required_subjects": ["Mathematics", "Physics"], "tests": [], "english": ENG},
            {"curriculum": "a-level", "source": "admissions",
             "threshold": f"{name}: five IGCSE/GCSE subjects at grade C or above, plus three AS/A Level subjects at grade C or above including Mathematics and Physics. Shortlisted applicants take KU's admission tests; high-school graduation no earlier than 2023.",
             "required_subjects": ["Mathematics", "Physics"], "tests": [], "english": ENG},
        ],
    })
    print("wrote", slug)

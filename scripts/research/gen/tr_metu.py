"""Middle East Technical University (METU/ODTÜ), Ankara: base records + nine programmes (written 2026-11-25).

Sources, all metu.edu.tr:
  - Undergraduate Programs and Degrees: programme, "Duration 4", degree;
  - International student quotas 2026-2027 (Ankara): the programme is offered to international students;
  - 2026-2027 tuition fees for international students (PDF): per semester, USD 1200 (Engineering),
    USD 800 (Economics and Administrative Sciences), converted to TL at payment;
  - 2026-2027 academic calendar: Fall and Spring semesters (two per year);
  - minimum application requirements (PDF, last update 05/01/2024): IB 33, A-level ABB, SAT 1200
    (Math 700 for Engineering); meeting them doesn't guarantee admission (holistic, quota-based);
  - English proficiency page: English-medium; no English score needed to apply; preparatory year
    if the proficiency exam isn't passed.
Living costs are published in Turkish lira (cost-of-living page) while tuition is in USD; a cost
record can't mix currencies, so living costs aren't stored (the note says so).
  python3 -I scripts/research/gen/tr_metu.py
"""
import json, re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write

ROOT = Path(__file__).resolve().parents[3]
PAGES = ROOT / ".research-cache/pages"
def norm(s): return re.sub(r"\s+", " ", s.replace("\xa0", " ").replace("’", "'")).strip().lower()
def on(page, qs):
    t = norm((PAGES / f"{page}.txt").read_text(errors="replace"))
    for q in qs: assert norm(q) in t, f"{page}: {q}"
    return qs
def url(page): return (PAGES / f"{page}.url").read_text().strip()
ORG = "Middle East Technical University"

DEG = "ae22dad927ab"
QUOTA = "5dd5f79a546f"
FEES = {"url": url("metu-fees-2627"), "page": "metu-fees-2627", "organization": ORG,
        "title": "2026-2027 tuition fees for international students (PDF) | METU",
        "quotes": on("metu-fees-2627", [
            "2026-2027 Academic Year Tuition Fees for International Students per semester (those who registered through international student quotas)",
            "Faculty of Engineering All programs 1200 USD",
            "Faculty of Economics All programs 800 USD"])}
CAL = {"url": url("c14d065eed4b"), "page": "c14d065eed4b", "organization": ORG,
       "title": "METU Ankara and Erdemli Campuses 2026-2027 Academic Year Calendar",
       "quotes": on("c14d065eed4b", ["2026-2027 Academic Year Calendar FALL SEMESTER", "the Spring Semester of the 2026 - 2027 Academic Year"])}
REQ = {"url": url("metu-req"), "page": "metu-req", "organization": ORG,
       "title": "Minimum application requirements for international students (PDF) | METU",
       "quotes": on("metu-req", [
           "INTERNATIONAL STUDENT MINIMUM APPLICATION REQUIREMENTS",
           "(Last update: 05/01/2024)",
           "International Baccalaureate (IB) Diploma An International Baccalaureate Diploma with a min. total score of 33 (at least one High Level-HL course relevant to the program applied for should be taken.)",
           "A minimum grade of ABB in three A-level subjects, two of which are relevant to the program applied for.",
           "A minimum total score of 1200 (with an additional minimum “Math” score of 700 out of 800 for the Faculty of Engineering, Faculty of Architecture, and scientific"])}
POL = {"url": url("48986c480046"), "page": "48986c480046", "organization": ORG, "title": "Application requirements | METU International Students Office",
       "quotes": on("48986c480046", ["The criteria specified in this list represent the minimum application requirements. However, fulfilling these requirements does not guarantee admission."])}
ENGP = {"url": url("5a9afd6a819b"), "page": "5a9afd6a819b", "organization": ORG, "title": "English proficiency | METU International Students Office",
        "quotes": on("5a9afd6a819b", [
            "The medium of instruction at METU is English. However, for undergraduate programs, submitting an English proficiency score is not obligatory for the application .",
            "Those who do not satisfy the minimum score from this exam will attend English Preparatory Class at the Department of Basic English for one year."])}

spec = {"uni": "tr-metu", "name": ORG, "aliases": ["METU", "ODTÜ"], "type": "public",
        "website": "https://www.metu.edu.tr", "country": {"cc": "tr", "name": "Türkiye", "currency": "TRY"},
        "city": {"slug": "tr-ankara", "name": "Ankara"},
        "sources": {"main": {"url": url(DEG), "page": DEG, "organization": ORG, "title": "Undergraduate Programs and Degrees | METU",
                             "quotes": on(DEG, ["Undergraduate Programs and Degrees | METU - Middle East Technical University", "06800 Çankaya/Ankara"])},
                    "fees": FEES}, "main_source": "main",
        "residency": [{"key": "international", "source": "fees", "label": "International students (international student quota)",
                       "description": "METU's per-semester tuition for students registered through the international student quotas, announced in USD and paid in Turkish lira at the Central Bank rate."}]}
Path(ROOT / "fact-checks/research/universities-2026-11/tr-metu.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
print("wrote spec tr-metu")

ENG = {"test_name": "English (not needed to apply)", "source": "engp",
       "min_score": "Not needed to apply. METU teaches in English; without a valid TOEFL or PTE Academic score at registration you take METU's English Proficiency Exam, or a one-year English preparatory class.",
       "notes": "METU no longer accepts IELTS taken on or after 24 December 2022."}
ENGP["quotes"] = ENGP["quotes"] + on("5a9afd6a819b", ["IELTS exams taken on or after the 24th of December 2022 will not be anymore accepted."])

# name, field, faculty fee (USD per semester), engineering?, programmes-page row, quota row
P = [
 ("Computer Engineering", "Computer Science", 1200, True, "Computer Engineering Computer Engineering 4 B.S.", "Computer Engineering 22"),
 ("Electrical and Electronics Engineering", "Electrical and Electronic Engineering", 1200, True, "Electrical and Electronics Engineering Electrical and Electronic Engineering 4 B.S.", "Electrical and Electronics Engineering 30"),
 ("Mechanical Engineering", "Mechanical Engineering", 1200, True, "Mechanical Engineering Mechanical Engineering 4 B.S.", "Mechanical Engineering 24"),
 ("Civil Engineering", "Civil Engineering", 1200, True, "Civil Engineering Civil Engineering 4 B.S.", "Civil Engineering 22"),
 ("Aerospace Engineering", "Aerospace Engineering", 1200, True, "Aerospace Engineering Aerospace Engineering 4 B.S.", "Aerospace Engineering 1 4"),
 ("Industrial Engineering", "Engineering", 1200, True, "Industrial Engineering Industrial Engineering 4 B.S.", "Industrial Engineering 1 1"),
 ("Chemical Engineering", "Chemical Engineering", 1200, True, "Chemical Engineering Chemical Engineering 4 B.S.", "Chemical Engineering 1 0"),
 ("Economics", "Economics", 800, False, "Economics Economics 4 B.S.", "Economics 16"),
 ("Business Administration", "Business", 800, False, "Business Administration Business Administration 4 B.S.", "Business Administration 1 2"),
]
for name, field, fee, eng, row, quota in P:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    sat = "SAT total 1200 with Math 700 (Engineering)" if eng else "SAT total 1200"
    tail = (" These are METU's minimum application requirements (list last updated 05/01/2024); meeting them doesn't guarantee admission, "
            "which is decided within the international student quota.")
    adm = [
        {"curriculum": "ib", "source": "req", "threshold": f"{name}: IB Diploma with at least 33 points, including at least one Higher Level course relevant to the programme.{tail}",
         "required_subjects": [], "tests": [], "english": ENG},
        {"curriculum": "a-level", "source": "req", "threshold": f"{name}: A-levels ABB in three subjects, two of them relevant to the programme (languages other than English can't be used).{tail}",
         "required_subjects": [], "tests": [], "english": ENG},
        {"curriculum": "us-hs", "source": "req", "threshold": f"{name}: {sat} (one of the accepted qualifications).{tail}",
         "required_subjects": [], "tests": [{"name": "SAT", "required": "required"}], "english": ENG},
    ]
    REQ_Q = dict(REQ, quotes=REQ["quotes"] + on("metu-req", ["(Language subjects other than English cannot be used"]))
    write("tr-metu", {"uni": "tr-metu", "slug": f"bs-{slug}",
        "sources": {"course": {"url": url(DEG), "page": DEG, "title": "Undergraduate Programs and Degrees | METU", "organization": ORG, "quotes": on(DEG, [row])},
                    "quota": {"url": url(QUOTA), "page": QUOTA, "title": "International Students Quotas for Undergraduate Programs | METU", "organization": ORG,
                              "quotes": on(QUOTA, ["2026-2027 ACADEMIC YEAR UNDERGRADUATE PROGRAMS OFFERED TO INTERNATIONAL STUDENTS ODTÜ/METU ANKARA", quota])},
                    "fees": FEES, "cal": CAL, "req": REQ_Q, "pol": POL, "engp": ENGP},
        "program": {"name": name, "degree_type": "B.S.", "field": field, "faculty": "", "duration_years": 4, "duration_source": "course",
                    "languages": ["en"], "entry_year": "2026-2027", "platform": "METU international student application (online)", "source": "course",
                    "summary": f"{name} (B.S.), 4 years, METU Ankara campus; taught in English (one-year English preparatory class if needed).", "application_requirements": []},
        "costs": [{"residency": "international", "currency": "USD", "tuition_per_term": fee, "terms_per_year": 2,
                   "terms_evidence": ["2026-2027 Academic Year Calendar FALL SEMESTER", "the Spring Semester of the 2026 - 2027 Academic Year"],
                   "academic_year": "2026-2027", "source": ["fees", "cal"],
                   "note": f"2026-2027: USD {fee} per semester (Fall and Spring), paid in Turkish lira at the Central Bank rate; yearly figure is our calculation. "
                           "Living costs aren't added: METU publishes them in Turkish lira only."}],
        "admissions": adm})
    print("wrote", slug)

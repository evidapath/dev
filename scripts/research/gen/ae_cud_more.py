"""Canadian University Dubai: eleven more bachelor's programmes (written 2026-11-25).

Same sources and rules as ae_cud.py: the programme page ("4 Years (8 Semesters)", credit hours),
CUD's undergraduate admissions page (entry rules, English) and CUD's fee page (per-credit fee
including 5% VAT, "Cr Hrs per Year"). Yearly tuition = VAT-inclusive per-credit fee × credit
hours per year (our calculation), plus AED 2,236.50 incidental fees. For the BBA rows CUD's
"Tuition per Year" column shows AED 0.00, so the note says the figure is our calculation from
the published rate. Teaching language not stated on the pages read, so none is stored.
Held: the three Communication programmes (no row on the fee page).
  python3 -I scripts/research/gen/ae_cud_more.py
"""
import re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
# Shared CUD sources, as in ae_cud.py (copied: importing that script would re-run its writes).
ADM = {"url": "https://www.cud.ac.ae/prospective-students/undergraduate", "page": "d709d1d380f5", "title": "Undergraduate Admissions | Canadian University Dubai",
       "organization": "Canadian University Dubai",
       "quotes": ["Are holders of UAE secondary education certificate with passing grade in all subjects", "British System: Completion of Year 13 / Grade 12 of schooling",
                  "Equivalency Certificate is Issued by Ministry of Education in the UAE.",
                  "Provide a valid English Language Proficiency Certificate with a minimum score of IELTS Academic (Band 5.0), TOEFL iBT (61), TOEFL ITP (500)",
                  "Applicants seeking admission to the Engineering program must meet the following subject-specific requirements:"]}
FEES = {"url": "https://www.cud.ac.ae/fees", "page": "5875657056d8", "title": "Fees | Canadian University Dubai", "organization": "Canadian University Dubai"}
ENG = {"test_name": "IELTS Academic (or TOEFL)", "source": "adm", "min_score": "IELTS Academic 5.0, TOEFL iBT 61 or TOEFL ITP 500.",
       "notes": "Not needed with official proof that your school taught in English, or 80% in English on the UAE Advanced Track."}
TH = {"a-level": "British system: completion of Year 13 / Grade 12, with a UAE Ministry of Education equivalency certificate.",
      "ib": "IB: assessed under UAE Ministry of Education equivalency rules.",
      "us-hs": "American system: high school diploma with a UAE Ministry of Education equivalency certificate.",
      "uae-shs": "UAE secondary education certificate with a passing grade in all subjects."}

def norm(s): return re.sub(r"\s+", " ", s.replace("\xa0", " ").replace("’", "'")).strip().lower()
def on(page, q): assert norm(q) in norm((PAGES / f"{page}.txt").read_text(errors="replace")), f"{page}: {q}"; return q
FEE_T = norm((PAGES / "5875657056d8.txt").read_text(errors="replace"))

B = "https://www.cud.ac.ae/programs/undergraduate/"
# url tail, page id, full name (fee page), name on the programme page, concentration on the page, degree, field, credits
P = [
 ("computer-engineering-and-computational-sciences/bachelor-of-computer-and-networking-engineering-technology", "175afc7b5af2",
  "Bachelor of Computer and Networking Engineering Technology", "Bachelor of Computer and Networking Engineering Technology", None, "Bachelor", "Computer Engineering", 133),
 ("engineering-applied-science-and-technology/bachelor-of-science-in-artificial-intelligence", "403ca8b95f4c",
  "Bachelor of Science in Artificial Intelligence", "Bachelor of Science in Artificial Intelligence", None, "BSc", "Computer Science", 128),
 ("engineering-applied-science-and-technology/bachelor-of-science-in-cyber-security", "ee4df160dece",
  "Bachelor of Science in Cyber Security", "Bachelor of Science in Cyber Security", None, "BSc", "Computer Science", 127),
 ("engineering-applied-science-and-technology/bachelor-of-science-in-software-design", "8ef3492e0732",
  "Bachelor of Science in Software Design", "Bachelor of Science in Software Design", None, "BSc", "Computer Science", 128),
 ("management/bachelor-of-business-administration-in-accounting-and-finance", "285dd70dec3b",
  "Bachelor of Business Administration in Accounting and Finance", "Bachelor of Business Administration", "Accounting and Finance", "BBA", "Accounting and Finance", 123),
 ("management/bachelor-of-business-administration-in-e-business", "a8caffeb8491",
  "Bachelor of Business Administration in E-Business", "Bachelor of Business Administration", "E-Business", "BBA", "Business", 123),
 ("management/bachelor-of-business-administration-in-entrepreneurship", "325730f6a27a",
  "Bachelor of Business Administration in Entrepreneurship", "Bachelor of Business Administration", "Entrepreneurship", "BBA", "Business", 123),
 ("management/bachelor-of-business-administration-in-human-resource-management", "2c7b6d1adadf",
  "Bachelor of Business Administration in Human Resource Management", "Bachelor of Business Administration", "Human Resource Management", "BBA", "Business", 123),
 ("management/bachelor-of-business-administration-in-international-business", "af63a418e2f1",
  "Bachelor of Business Administration in International Business", "Bachelor of Business Administration", "International Business", "BBA", "Business", 123),
 ("management/bachelor-of-business-administration-in-management", "eaa5a87daf31",
  "Bachelor of Business Administration in Management", "Bachelor of Business Administration", "Management", "BBA", "Business", 123),
 ("management/bachelor-of-business-administration-in-marketing", "f8462b3b2398",
  "Bachelor of Business Administration in Marketing", "Bachelor of Business Administration", "Marketing", "BBA", "Business", 123),
]

for tail, page, full, page_name, conc, deg, field, credits in P:
    m = re.search(re.escape(norm(full)) + r" aed ([\d,.]+) aed ([\d,.]+) aed ([\d,.]+) aed ([\d,.]+) (\d+) aed ([\d,.]+) usd aed ([\d,.]+)", FEE_T)
    assert m, f"no fee row: {full}"
    pre, vat, incl, per_course, cr_year, per_year, incidental = m.groups()
    assert incidental == "2,236.50", (full, incidental)
    fee_q = f"{full} AED {pre} AED {vat} AED {incl} AED {per_course} {cr_year} AED {per_year} USD AED {incidental}"
    rate = float(incl.replace(",", "")); cy = int(cr_year)
    zero = per_year == "0.00"
    note = ((f"Tuition per year AED {per_year} (CUD's fee page: " if not zero else "") + f"AED {incl} per credit hour including 5% VAT (AED {pre} before VAT) × {cy} credit hours a year" + (")" if not zero else "")
            + (" (our calculation; CUD's fee page shows AED 0.00 in its 'Tuition per Year' column for this programme)" if zero else "")
            + ", plus AED 2,236.50 incidental fees.")
    course_q = [on(page, f"{page_name} Degree Program"), on(page, "4 Years (8 Semesters)"), on(page, f"{credits} Credit Hours")]
    if conc:
        course_q.append(on(page, conc))
    slug = re.sub(r"[^a-z0-9]+", "-", full.lower().replace("bachelor of business administration in", "bba").replace("bachelor of science in", "bsc").replace("bachelor of", "b")).strip("-")
    name = full.replace("Bachelor of Business Administration in ", "Business Administration: ").replace("Bachelor of Science in ", "").replace("Bachelor of ", "")
    adm = lambda cur: {"curriculum": cur, "source": "adm", "threshold": f"{full}: {TH[cur]} CUD lists subject-specific requirements only for Engineering.",
                       "required_subjects": [], "tests": [], "english": ENG}
    write("cud", {"uni": "ae-canadian-university-dubai", "slug": slug,
        "sources": {"course": {"url": B + tail, "page": page, "title": f"{full} | Canadian University Dubai", "organization": "Canadian University Dubai", "quotes": course_q},
                    "adm": ADM,
                    "fees": {**FEES, "quotes": ["*Estimated first-year costs based on full-time studies, including the application fee.", "Cr Hrs per Year", "VAT 5%", fee_q]}},
        "program": {"name": name, "degree_type": deg, "field": field, "faculty": "", "duration_years": 4, "languages": [],
                    "entry_year": "2026-2027", "platform": "CUD online application", "source": "course",
                    "summary": f"{full}, 4 years (8 semesters), {credits} credit hours.", "application_requirements": []},
        "costs": [{"residency": "all-students", "currency": "AED",
                   **({"tuition_per_credit": rate, "credits_per_year": cy} if zero else {"tuition_annual": float(per_year.replace(",", ""))}),
                   "mandatory_fees_annual": 2236.5,
                   "academic_year": "Rates on CUD's fee page in November 2026 (the page doesn't state the academic year)", "source": "fees",
                   "living_from": "costProfile-ae-canadian-university-dubai-cost-bsc-cs-all-students", "note": note}],
        "admissions": [adm("a-level"), adm("ib"), adm("us-hs"), adm("uae-shs")]})
    print("wrote", slug, rate, cy, "zero-col" if zero else "")

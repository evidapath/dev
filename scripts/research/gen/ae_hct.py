"""Higher Colleges of Technology (HCT): twelve bachelor's programmes (written 2026-11-25).

Sources, all HCT's own:
  - the programme page (hct.ac.ae/en/majors/...): the programme's name;
  - the HCT Catalog page it links to (hctcatalog.hct.ac.ae): total credits and minimum duration;
  - International Admissions (hct.ac.ae/en/admissions/international-admissions/): the 2026-2027
    fee for expatriate (self-sponsored) students per credit hour, entry rules by division, the
    IB / A-level / AP / SAT equivalents and the English requirement.
Yearly tuition = AED 2,473.63 per credit hour × the catalogue's total credits ÷ its minimum
duration (our calculation). The teaching language isn't stated on any page read, so none is
stored. Held: Cybersecurity and Data Science (their pages link to catalogue entries under other
names: Information Technology, Information Systems).
  python3 -I scripts/research/gen/ae_hct.py
"""
import hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
ADM_URL = "https://hct.ac.ae/en/admissions/international-admissions/"
pid = lambda u: hashlib.sha1(u.encode()).hexdigest()[:12]

ADM_FEE = ["Tuition Fees for Expatriate Students (Self-Sponsored Students) Academic Year 2026-2027",
           "Bachelor AED 37,104.45 (Based on 15 CH) AED 2,473.63 per credit hour 4 Years"]
ADM_COMMON = ["Note: All other admission requirements, program-specific criteria, and subject equivalencies are the same for local and international applicants.",
              "Applied Bachelor Degree High School English: 80% and fulfilment of program-specific admission requirements",
              "Bachelor Programs TOEFL iBT 71 (0-120 scale) or 4.0 (1-6 scale)"]
MATH_NE = "Mathematics (Non-Engineering Bachelor Programs): SAT 485, ACT 20, IB SL Mathematics 4, AP Mathematics 3, or IGCSE/AS/A Level Grade C."
MATH_E = "Mathematics (Engineering Bachelor Programs): SAT 555, ACT 24, IB SL Mathematics 4, AP Mathematics 3, or IGCSE/AS/A Level Grade C."
PHYS = "Physics: IGCSE/AS/A Level Grade C, IB SL Physics 4, or AP Physics 3."
CHEM = "Chemistry: IGCSE/AS/A Level Grade C, IB SL Chemistry 4, or AP Chemistry 3."
BIO = "Biology: IGCSE/AS/A Level Grade C, IB SL Biology 4, or AP Biology 3."
ENG_ROW = "Engineering Technology & Science 85% General / 75% Advanced 85% General / 75% Advanced 80% General / 75% Advanced (Chemical Engineering) N/A Mathematics and Physics required"

# division: (table row quote, extra quotes, IB threshold, A-level threshold, required subjects)
DIV = {
 "business": ("Business 80% General / 70% Advanced N/A N/A N/A Mathematics required", [MATH_NE],
              "IB: Mathematics at SL 4 or higher (HCT's equivalent of its 80% school maths requirement).",
              "A-Level: Mathematics at IGCSE/AS/A Level grade C or higher (HCT's equivalent of its 80% school maths requirement).",
              ["Mathematics"]),
 "media": ("Applied Media 70% General / 65% Advanced N/A N/A N/A Mathematics required", [MATH_NE],
           "IB: Mathematics at SL 4 or higher (HCT's equivalent of its 70% school maths requirement).",
           "A-Level: Mathematics at IGCSE/AS/A Level grade C or higher (HCT's equivalent of its 70% school maths requirement).",
           ["Mathematics"]),
 "engineering": (ENG_ROW, [MATH_E, PHYS],
                 "IB: Mathematics and Physics, each at SL 4 or higher (HCT's equivalent of its 85% school maths and physics requirement).",
                 "A-Level: Mathematics and Physics, each at IGCSE/AS/A Level grade C or higher (HCT's equivalent of its 85% school maths and physics requirement).",
                 ["Mathematics", "Physics"]),
 "chemical": (ENG_ROW, [MATH_E, PHYS, CHEM],
              "IB: Mathematics, Physics and Chemistry, each at SL 4 or higher (HCT's equivalent of its 85% maths and physics and 80% chemistry requirement).",
              "A-Level: Mathematics, Physics and Chemistry, each at IGCSE/AS/A Level grade C or higher (HCT's equivalent of its 85% maths and physics and 80% chemistry requirement).",
              ["Mathematics", "Physics", "Chemistry"]),
 "health": ("Health Sciences N/A 80% 80% 80% One Science subject required", [PHYS, CHEM, BIO],
            "IB: one science (Physics, Chemistry or Biology) at SL 4 or higher (HCT's equivalent of its 80% school science requirement).",
            "A-Level: one science (Physics, Chemistry or Biology) at IGCSE/AS/A Level grade C or higher (HCT's equivalent of its 80% school science requirement).",
            ["Physics, Chemistry or Biology"]),
}

# programme page slug, our slug, name as on the page, field, division, catalogue credits quote
P = [
 ("bachelor-of-accounting", "accounting", "Bachelor of Accounting", "Accounting and Finance", "business", "Total Credits 120"),
 ("bachelor-of-actuarial-science", "actuarial-science", "Bachelor of Actuarial Science", "Actuarial Studies", "business", "Total Credits 120"),
 ("bachelor-of-business-analytics", "business-analytics", "Bachelor of Business Analytics", "Business", "business", "Total Credits 120"),
 ("bachelor-of-international-business", "international-business", "Bachelor of International Business", "Business", "business", "Total Credits 120"),
 ("bachelor-of-marketing", "marketing", "Bachelor of Marketing", "Business", "business", "Total Credits 120"),
 ("bachelor-of-digital-media", "digital-media", "Bachelor of Digital Media", "Media and Communication", "media", "120 credit hours"),
 ("chemical-engineering-technology", "chemical-engineering-technology", "Bachelor of Chemical Engineering Technology", "Chemical Engineering", "chemical", "Total Credits 120"),
 ("civil-engineering-technology", "civil-engineering-technology", "Bachelor of Civil Engineering Technology", "Civil Engineering", "engineering", "Total Credits 120"),
 ("electrical-engineering-technology", "electrical-engineering-technology", "Bachelor of Electrical Engineering Technology", "Electrical and Electronic Engineering", "engineering", "Total Credits 120"),
 ("mechanical-engineering-technology", "mechanical-engineering-technology", "Bachelor of Mechanical Engineering Technology", "Mechanical Engineering", "engineering", "Total Credits 120"),
 ("mechatronics-engineering-technology", "mechatronics-engineering-technology", "Bachelor of Mechatronics Engineering Technology", "Mechatronic Engineering", "engineering", "Total Credits 120"),
 ("nursing", "nursing", "Bachelor of Nursing", "Nursing", "health", "Total Credits 120"),
]

def norm(s): return re.sub(r"\s+", " ", s.replace("\xa0", " ").replace("’", "'")).strip().lower()
def text(page): return norm((PAGES / f"{page}.txt").read_text(errors="replace"))
def need(page, quotes):
    t = text(page)
    for q in quotes:
        assert norm(q) in t, f"{page}: not on page: {q}"
    return quotes

adm = pid(ADM_URL)
for page_slug, slug, name, field, div, cred_q in P:
    url = f"https://hct.ac.ae/en/majors/{page_slug}/"
    page = pid(url)
    html = (PAGES / f"{page}.html").read_text(errors="replace")
    cat_url = re.search(r"https://hctcatalog\.hct\.ac\.ae/programmes/[^\"#]+", html).group(0)
    cat = pid(cat_url)
    dur_q = "Minimum Duration of Study 4 years" if norm("Minimum Duration of Study 4 years") in text(cat) else "a four-year, post-foundation, 120-credit program"
    row, extra, ib_t, al_t, req = DIV[div]
    eng = {"test_name": "TOEFL iBT (or 80% in high-school English)",
           "min_score": "TOEFL iBT 71 (0-120 scale) or 4.0 (1-6 scale), or 80% in high-school English.", "source": "admissions"}
    write("hct", {
        "uni": "ae-hct", "slug": slug,
        "sources": {
            "course": {"url": url, "page": page, "title": f"{name} | Higher Colleges of Technology",
                       "organization": "Higher Colleges of Technology", "quotes": need(page, [name])},
            "catalog": {"url": cat_url, "page": cat, "title": f"{name} | HCT Catalog",
                        "organization": "Higher Colleges of Technology", "quotes": need(cat, [cred_q, dur_q])},
            "admissions": {"url": ADM_URL, "page": adm, "title": "International Admissions | Higher Colleges of Technology",
                           "organization": "Higher Colleges of Technology",
                           "quotes": need(adm, ADM_FEE + ADM_COMMON + [row] + extra)},
        },
        "program": {"name": name.replace("Bachelor of ", ""), "degree_type": "Bachelor", "field": field,
                    "duration_years": 4, "duration_source": "catalog", "languages": [],
                    "entry_year": "2026-2027", "platform": "", "source": "course",
                    "summary": f"{name} at the Higher Colleges of Technology (UAE).", "application_requirements": []},
        "costs": [{
            "residency": "international", "currency": "AED", "tuition_per_credit": 2473.63, "degree_credits": 120,
            "credits_source": "catalog", "academic_year": "2026-2027", "source": "admissions",
            "note": "Expatriate (self-sponsored) students, 2026-2027: AED 2,473.63 per credit hour × 120 credits ÷ 4 years (our calculation). HCT says the per-credit fee may vary by programme. Fees are zero-rated for VAT.",
        }],
        "admissions": [
            {"curriculum": "ib", "source": "admissions", "threshold": ib_t, "required_subjects": req, "tests": [], "english": eng},
            {"curriculum": "a-level", "source": "admissions", "threshold": al_t, "required_subjects": req, "tests": [], "english": eng},
        ],
    })
    print("wrote", slug, cat_url.split("/")[-2])

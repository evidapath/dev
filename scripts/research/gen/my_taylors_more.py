"""Taylor's University: eleven more bachelor's programmes (written 2026-11-25).

Each course page (saved earlier, `.research-cache/pages/<id>.txt`) was read by hand: its entry
blocks differ page to page, so every quote below is copied from that page. Fee rule, as for the
Taylor's records built on 2026-11-12: the course page's 2026 programme total in USD for
international students, shown as a yearly average (excludes the 6% Service Tax); Malaysian
students: the MYR total. build.py re-checks every quote and number.
  python3 -I scripts/research/gen/my_taylors_more.py
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
TAX = "Fees shown in the Fee Schedule are exclusive of the 6% Service Tax."
ENG_NOTE = "(or a completed Pre-U/Diploma taught in English)"

# page, slug, name, field, school, years, duration quote, fee quote, intl USD, local MYR,
# A-level quote, IB quote, English quote, English summary, required subjects
C = [
 ("3391181f098c", "software-engineering", "Software Engineering", "Computer Science", "School of Computer Science", 3,
  "Duration 3-year", "Fees MYR 125,414 (Local) USD 41,080 (International)", 41080, 125414,
  "A Level Pass with min. DD", "International Baccalaureate (IB) Min. 24 points in 6 subjects",
  "INTERNATIONAL STUDENTS IELTS 5.0", "IELTS 5.0", []),
 ("d23f64fceaec", "accounting-finance", "Accounting and Finance", "Accounting and Finance", "Taylor's Business School", 3,
  "Duration 3 years", "Fees MYR 125,510 (Local) USD 41,124 (International)", 41124, 125510,
  "A Level Minimum DD", "International Baccalaureate (IB) Minimum 26 points and above in 6 subjects",
  "INTERNATIONAL STUDENTS MUET Band 3.5 IELTS Band 5.0", "MUET Band 3.5 or IELTS 5.0", []),
 ("92fa3acbaac6", "actuarial-studies", "Actuarial Studies", "Actuarial Studies", "Taylor's Business School", 3,
  "Duration 3 years", "MYR 117,962 (Local, 3 years) MYR 128,870 (Local, 4 years) USD 39,001 (International, 3 years)", 39001, 117962,
  "A Level Minimum DD", "International Baccalaureate (IB) Minimum of 24 points for 6 subjects",
  "INTERNATIONAL STUDENTS MUET Band 3 CEFR Low B2", "MUET Band 3 or CEFR Low B2", []),
 ("9d8f32e3271c", "finance-economics", "Finance and Economics", "Economics", "Taylor's Business School", 3,
  "Duration 3 years", "Fees MYR 125,522 (Local) USD 41,110 (International)", 41110, 125522,
  "A Level Minimum DD", "International Baccalaureate (IB) Minimum 26 points and above for 6 subjects",
  "INTERNATIONAL STUDENTS IELTS Band 6.0", "IELTS 6.0", []),
 ("ca7d21c4c0f4", "mechatronics-engineering", "Mechatronics Engineering", "Mechatronic Engineering", "School of Engineering", 4,
  "Duration 4-year", "Fees MYR 173,802 (Local) USD 55,367 (International)", 55367, 173802,
  "A Level Min. DDD including Mathematics and Physics / Chemistry",
  "International Baccalaureate (IB) Min. 24 points in 6 subjects including Mathematics and Physics / Chemistry",
  "INTERNATIONAL STUDENTS IELTS score of 5.0 OR its equivalent", "IELTS 5.0 or equivalent", ["Mathematics", "Physics or Chemistry"]),
 ("a81b3ffc3d5e", "pharmacy", "Pharmacy", "Pharmacy", "School of Pharmacy", 4,
  "Duration 4-year", "Fees MYR 206,662 (Local) USD 64,522 (International)", 64522, 206662,
  "A Level Min. ABC / BBB / AAC in Biology, Chemistry, and Physics / Mathematics with min. B in Chemistry",
  "International Baccalaureate (IB) Pass with min. score of 30 overall and attained a min. score of 5 each in: Chemistry, Biology, Physics / Mathematics with min. 2 at Higher Level and and 1 at Standard Level",
  "INTERNATIONAL STUDENTS IELTS Band 6.0 TOEFL iBT 60 PTE 59 Linguaskill 169", "IELTS 6.0, TOEFL iBT 60, PTE 59 or Linguaskill 169", ["Chemistry", "Biology", "Physics or Mathematics"]),
 ("4dc388830cee", "biomedical-science", "Biomedical Science", "Biomedical Science", "School of Biosciences", 3.5,
  "Duration 3.5-year", "Fees MYR 141,314 (Local) USD 45,956 (International)", 45956, 141314,
  "A Level Min. DD including min. D in (ANY 2) subjects: Biology, Physics / Mathematics, Chemistry",
  "International Baccalaureate (IB) Min. 24 points in 6 subjects including min. 5 points at Higher Level (HL) in (ANY 2) subjects: Biology, Physics / Mathematics, Chemistry",
  "INTERNATIONAL STUDENTS IELTS Band 5.5 TOEFL iBT 46 PTE 51 Linguaskill 160", "IELTS 5.5, TOEFL iBT 46, PTE 51 or Linguaskill 160", []),
 ("3e8c4ecae83a", "mass-communication", "Mass Communication", "Media and Communication", "School of Media and Communication", 3,
  "Duration 3-year", "Fees MYR 124,334 (Local) USD 40,779 (International)", 40779, 124334,
  "A Level Min. DD (2 subjects)", "International Baccalaureate (IB) Min. 24 points in 6 subjects",
  "INTERNATIONAL STUDENTS IELTS 5.0", "IELTS 5.0", []),
 ("701de7eb1f91", "international-relations", "International Relations", "International Relations", "School of Liberal Arts and Sciences", 3,
  "Duration 3-year", "Fees MYR 111,050 (Local) USD 37,073 (International)", 37073, 111050,
  "A Level Min. DDD", "International Baccalaureate (IB) Min. 24 points in 6 subjects",
  "INTERNATIONAL STUDENTS IELTS 5.0", "IELTS 5.0", []),
 ("4cb105a7c23a", "philosophy-politics-economics", "Philosophy, Politics and Economics", "Politics, Philosophy and Economics", "School of Law and Governance", 3,
  "Duration 3 years", "Fees MYR 119,678 (Local) USD 39,477 (International)", 39477, 119678,
  "A Level ABB", "International Baccalaureate (IB) Min. 36 points in 6 subjects",
  "INTERNATIONAL STUDENTS IELTS Band 6.0", "IELTS 6.0", []),
 ("d876eeea3096", "international-hospitality-management", "International Hospitality Management", "Hospitality Management", "School of Hospitality, Tourism and Events", 3,
  "Duration 3-year", "Fees MYR 122,930 (Local) USD 40,387 (International, April and September Intakes) USD 40,736 (International, January Intake)", 40387, 122930,
  "A Level Min. DD", "International Baccalaureate (IB) Min. 24 points in 6 subjects",
  "INTERNATIONAL STUDENTS IELTS 5.0", "IELTS 5.0", []),
]

# Plain wording (same numbers as the quote) where the page's own phrasing can't be compared.
IB_PLAIN = {"pharmacy": "Pharmacy: IB Diploma with at least 30 points overall and at least 5 in each of Chemistry, Biology and Physics / Mathematics (2 of them at Higher Level and 1 at Standard Level)."}

def norm(s): return re.sub(r"\s+", " ", s.replace("\xa0", " ").replace("’", "'")).strip().lower()

for page, slug, name, field, school, years, dq, fq, usd, myr, aq, ibq, eq, eng, req in C:
    raw = (PAGES / f"{page}.txt").read_text(errors="replace")
    text = norm(raw)
    url = (PAGES / f"{page}.url").read_text().strip()
    quotes = ["Programme Information for 2026", dq, fq, aq, ibq, eq]
    if norm(TAX) in text:
        quotes.append(TAX)
    for q in quotes:
        assert norm(q) in text, f"{slug}: not on page: {q}"
    title = re.search(r"^(.*?) \| Taylor", raw, re.M)
    yrs = f"{years:g}"
    english = {"test_name": "English proficiency", "min_score": f"{eng} {ENG_NOTE}.", "source": "course"}
    if slug == "international-hospitality-management":
        intl_note = f"International (April and September intakes): USD {usd:,} for the whole {yrs}-year programme (2026), shown as a yearly average. The January intake is USD 40,736."
    else:
        intl_note = f"International: USD {usd:,} for the whole {yrs}-year programme (2026), shown as a yearly average."
    tax_note = " Excludes the 6% Service Tax for non-Malaysian citizens." if TAX in quotes else ""
    write("taylors", {
        "uni": "my-taylors", "slug": slug,
        "sources": {"course": {"url": url, "page": page,
                               "title": f"{title.group(1).strip() if title else 'Bachelor of ' + name} | Taylor's University",
                               "organization": "Taylor's University", "quotes": quotes}},
        "program": {"name": name, "degree_type": "Bachelor's degree (Honours)", "field": field, "faculty": school,
                    "duration_years": years, "languages": ["en"], "entry_year": "2026 intakes", "platform": "",
                    "source": "course", "summary": f"{name} at Taylor's University, {yrs} years full time.",
                    "application_requirements": []},
        "costs": [
            {"residency": "international", "currency": "USD", "tuition_formula": f"{usd}/{yrs}", "academic_year": "2026 intakes",
             "source": "course", "note": intl_note + tax_note + " Living costs are published by Taylor's in MYR only, so they aren't added to this USD figure."},
            {"residency": "malaysian", "currency": "MYR", "tuition_formula": f"{myr}/{yrs}", "academic_year": "2026 intakes",
             "source": "course", "living_from": "costProfile-my-taylors-cost-bsc-cs-malaysian",
             "note": f"Malaysian students: MYR {myr:,} for the whole {yrs}-year programme (2026), shown as a yearly average."},
        ],
        "admissions": [
            {"curriculum": "a-level", "source": "course", "threshold": f"{name}: " + re.sub(r"^A Level ", "", aq) + ".",
             "required_subjects": req, "tests": [], "english": english},
            {"curriculum": "ib", "source": "course", "threshold": IB_PLAIN.get(slug, f"{name}: " + re.sub(r"^International Baccalaureate \(IB\) ", "", ibq) + "."),
             "required_subjects": req, "tests": [], "english": english},
        ],
    })
    print("wrote", slug)

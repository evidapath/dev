"""RIT Dubai: seven more bachelor's programmes (written 2026-11-25).

Sources, all rit.edu/dubai: the programme page ("Total Credit Hours", the typical course sequence
by year), the tuition page (one AED 68,000 a year figure for every bachelor's listed), the
undergraduate admissions page (English) and the admission-requirements PDF for the programme's
group (Business, Computing, Engineering, New Media Design). Costs are copied from the existing
Global Business Management record (same AED 68,000), as ae_rit.py does for Psychology.
Engineering and Cybersecurity sequences run to a "Fifth Year" (co-op), as RIT's Computer
Engineering (fixed 2026-11-17). Held: Advertising and Public Relations (no admission-requirements
PDF), Management Information Systems (not on the tuition list).
  python3 -I scripts/research/gen/ae_rit_more.py
"""
import re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
def norm(s): return re.sub(r"\s+", " ", s.replace("\xa0", " ").replace("’", "'")).strip().lower()
def on(page, qs):
    t = norm((PAGES / f"{page}.txt").read_text(errors="replace"))
    for q in qs: assert norm(q) in t, f"{page}: {q}"
    return qs

FEEQ = ("Bachelor Tuition (per year) Bachelor of Science in Cybersecurity Bachelor of Science in Computing and Information Technologies "
        "Bachelor of Science in Computer Engineering Bachelor of Science in Electrical Engineering Bachelor of Science in Mechanical Engineering "
        "Bachelor of Science in Industrial Engineering Bachelor of Science in Finance Bachelor of Science in Marketing "
        "Bachelor of Science in Global Business Management Bachelor of Science in Psychology Bachelor of Science in Advertising and Public Relations "
        "Bachelor of Fine Arts in New Media Design 68,000")
ENG = {"test_name": "Academic IELTS (or TOEFL / EmSAT English)", "source": "eng",
       "min_score": "Full admission: Academic IELTS overall 6.5 and above, TOEFL iBT 79 and above, TOEFL ITP 550 and above, or EmSAT English 1550 and above. Conditional admission: IELTS 5.0 - 6.0, TOEFL iBT 61 - 78, TOEFL ITP 500 - 547, EmSAT 1100 - 1525.",
       "notes": "Students in English-medium international curricula may qualify for an exemption."}
ENG_SRC = {"url": "https://www.rit.edu/dubai/undergraduate-admissions", "page": "fc3cdd20e9da", "title": "Undergraduate Admissions | RIT Dubai", "organization": "RIT Dubai",
           "quotes": ["Academic IELTS Overall 6.5 and above Overall 5.0 - 6.0 TOEFL ITP 550 and above 500 - 547 TOEFL IBT 79 and above 61 - 78 EmSAT - English 1550 and above 1100 - 1525",
                      "International Curricula (American, British, IB, Australian, Canadian and SABIS): Students enrolled in international curricula where English is the primary language of instruction may qualify for an exemption from the English Proficiency test"]}

GROUP = {
 "business": ("rit-adm-business", "Business",
   ["British Required Scores Minimum 5 IGCSE (C or above) and 2 As or 1 A level (D grade) Completion of Grade 12/ Year 13 Minimum average 70%",
    "International Baccalaureate Required Scores Minimum 24 points", "Must cover Math at secondary high school."],
   "British system: at least 5 IGCSEs (C or above) and 2 AS-Levels or 1 A-Level (D grade), Year 13 completed, minimum average 70%; must have studied Maths.",
   "IB, minimum 24 points; must have studied Maths.", ["Mathematics"]),
 "computing": ("rit-adm-computing", "Computing",
   ["British Required Scores Minimum 5 IGCSE (C or above) and 2 As or 1 A level (D grade) Completion of Grade 12/ Year 13 Minimum average 70%",
    "International Baccalaureate Required Scores Minimum 24 points",
    "Must cover math and one science at secondary high school and the preferred sciences are Physics or Chemistry."],
   "British system: at least 5 IGCSEs (C or above) and 2 AS-Levels or 1 A-Level (D grade), Year 13 completed, minimum average 70%; Maths and one science (Physics or Chemistry preferred).",
   "IB, minimum 24 points; Maths and one science (Physics or Chemistry preferred).", ["Mathematics"]),
 "engineering": ("rit-adm-engineering", "Engineering",
   ["British Required Scores Minimum 5 IGCSE (C’s or above) and 2 As or 1 A level (D’s or above) Math, Physics and 1 of Chemistry/Biology minimum grade C or above in IGCSE or in AS/A Level Completion of Grade 12/ Year 13 Minimum average 80%",
    "International Baccalaureate Required Scores Minimum 28 points Math, Physics and 1 of Chemistry/Biology minimum grade is 4 or above",
    "Engineering students must appear for Math and physics placement tests prior to course registration."],
   "British system: at least 5 IGCSEs (C or above) and 2 AS-Levels or 1 A-Level (D or above), with Maths, Physics and Chemistry or Biology at grade C or above (IGCSE or AS/A Level), Year 13 completed, minimum average 80%. Maths and physics placement tests.",
   "IB, minimum 28 points, with Maths, Physics and Chemistry or Biology at 4 or above. Maths and physics placement tests.", ["Mathematics", "Physics"]),
 "nmd": ("rit-adm-new-media-design", "New Media Design",
   ["British Required Scores Minimum 5 IGCSE (C or above) and 2 As or 1 A level (D grade) Completion of Grade 12/ Year 13 Minimum average 70%",
    "International Baccalaureate Required Scores Minimum 24 points"],
   "British system: at least 5 IGCSEs (C or above) and 2 AS-Levels or 1 A-Level (D grade), Year 13 completed, minimum average 70%.",
   "IB, minimum 24 points.", []),
}

# page slug, page id, name, degree, field, group, years, credits
P = [
 ("bachelor-science-cybersecurity", "51a6bdfbc6ae", "Cybersecurity", "BS", "Computer Science", "computing", 5, 126),
 ("bachelor-science-electrical-engineering", "c6f0bcb04e8b", "Electrical Engineering", "BS", "Electrical and Electronic Engineering", "engineering", 5, 129),
 ("bachelor-science-mechanical-engineering", "100149f63041", "Mechanical Engineering", "BS", "Mechanical Engineering", "engineering", 5, 129),
 ("bachelor-science-industrial-engineering", "5e6d74e6b9a1", "Industrial Engineering", "BS", "Engineering", "engineering", 5, 129),
 ("bachelor-science-finance", "e7f3df30a0ae", "Finance", "BS", "Accounting and Finance", "business", 4, 123),
 ("bachelor-science-marketing", "413f0a159613", "Marketing", "BS", "Business", "business", 4, 123),
 ("bachelor-fine-arts-new-media-design", "bbcbc28326f6", "New Media Design", "BFA", "Media and Communication", "nmd", 4, 122),
]
for slug, page, name, deg, field, grp, years, credits in P:
    pdf, gname, gq, al, ib, req = GROUP[grp]
    last = "Fifth Year" if years == 5 else "Fourth Year"
    course_q = on(page, [f"Total Credit Hours - {credits}", last])
    if years == 4:
        assert norm("Fifth Year") not in norm((PAGES / f"{page}.txt").read_text(errors="replace")), slug
    seq = "five-year (with co-op)" if years == 5 else "four-year"
    adm = lambda cur, th: {"curriculum": cur, "source": "adm", "threshold": f"{deg} {name}: {th} Meeting the minimum doesn't guarantee direct admission.",
                           "required_subjects": req, "tests": [], "english": ENG}
    write("rit", {"uni": "ae-rit-dubai", "slug": f"{deg.lower()}-{slug.split('-', 2)[-1]}",
        "sources": {
            "course": {"url": f"https://www.rit.edu/dubai/{slug}", "page": page, "title": f"{deg} in {name} | RIT Dubai", "organization": "RIT Dubai", "quotes": course_q},
            "adm": {"url": (PAGES / f"{pdf}.url").read_text().strip(), "page": pdf, "title": f"Admission Requirements, {gname} (PDF) | RIT Dubai", "organization": "RIT Dubai", "quotes": on(pdf, gq)},
            "eng": ENG_SRC,
            "fees": {"url": "https://www.rit.edu/dubai/tuition-and-fees", "page": "3be86f64f014", "title": "Tuition and Fees | RIT Dubai", "organization": "RIT Dubai",
                     "quotes": on("3be86f64f014", ["Bachelor Tuition (per year)", FEEQ])}},
        "program": {"name": name, "degree_type": deg, "field": field, "faculty": "", "duration_years": years, "duration_source": "course",
                    "languages": [], "entry_year": "2026-2027 (Fall 2027 entry)", "platform": "RIT Dubai application", "source": "course",
                    "summary": f"{deg} in {name}, RIT Dubai; {credits} total credit hours over a {seq} typical course sequence.", "application_requirements": []},
        "college": {"from": "program-ae-rit-dubai-bs-global-business", "quote": FEEQ, "copy": ["costs"]},
        "costs": [],
        "admissions": [adm("a-level", al), adm("ib", ib)]})
    print("wrote", slug, years)

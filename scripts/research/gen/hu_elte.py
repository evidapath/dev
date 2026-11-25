"""Eötvös Loránd University (ELTE), Budapest: base records + four bachelor's degrees (written 2026-11-25).

Sources, all elte.hu:
  - course pages on apply.elte.hu (September 2027/28 intake): "Nominal duration 6 semesters (3 years)
    (180 ECTS)", "Study language English", "Tuition fee €N per semester", entry and language requirements;
  - Faculty of Science FAQ for prospective students: typical monthly expenses (ranges); the top of each
    range is used and the yearly total is our calculation.
  python3 -I scripts/research/gen/hu_elte.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "Eötvös Loránd University"
LIVING = src("ad451aabf7de", "FAQ for prospective students | ELTE Faculty of Science", ORG, [
    "Here’s a general breakdown of typical monthly expenses for international students.",
    "Accommodation : €200–€500 per month", "Utilities (electricity, water, heating, internet): €50–€100 per month, if not included in the rent.",
    "Food and Groceries : €150–€250 per month", "Public Transportation : €10–€30 per month", "Health Insurance : €20–€50 per month",
    "Other (entertainment, personal expenses): €50–€150 per month"])
LIVING_NOTE = ("Our calculation from the top of each monthly range in ELTE's Faculty of Science guide: accommodation EUR 500, utilities EUR 100, "
               "food EUR 250, public transport EUR 30, health insurance EUR 50, other EUR 150, × 12 = EUR 12,960 a year.")

# page, name on the portal, display name, degree, field, fee per semester, entry/English quotes, threshold, english
P = [
 ("77a89d9cf43d", "[BSc] Computer Science", "Computer Science", "BSc", "Computer Science", 3200,
  ["Applicants are required to have sufficiently good grades in their secondary school finishing documents, especially in Mathematics.",
   "Minimum level of language proficiency (oral) (A1-C2): B1", "without proof of payment you will not be invited to the entrance exam"],
  "Computer Science: no grade cut-off published; ELTE asks for sufficiently good secondary-school grades, especially in Mathematics, and invites applicants to an entrance exam.",
  {"test_name": "English (B1)", "min_score": "B1 level (oral and written).", "source": "course"}),
 ("c25751caf534", "[BSc] Applied Economics", "Applied Economics", "BSc", "Economics", 2700,
  ["Applicants need to submit their secondary school certificate and records of final two years in secondary school .",
   "Certification of English knowledge (both written and oral): B2 Types of language exams which are accepted: IELTS Score: 5.5",
   "Applicants with a complete application package will be notified about the exact time and date of their online interviews after the application period has ended."],
  "Applied Economics: no grade cut-off published; secondary school certificate and final two years' records, motivation letter, and an online interview.",
  {"test_name": "IELTS (or other B2 certificate)", "min_score": "B2: IELTS 5.5 (or the other certificates ELTE lists).", "source": "course"}),
 ("e81117a4590e", "[BSc] Chemistry", "Chemistry", "BSc", "Chemistry", 3150,
  ["Applicants need to submit their secondary school certificate and records of final two years in secondary school.",
   "Minimum level of language proficiency (oral) (A1-C2): B2"],
  "Chemistry: no grade cut-off published; secondary school certificate and final two years' records, CV and motivation letter.",
  {"test_name": "English (B2)", "min_score": "B2 level (CEFR), oral and written.", "source": "course"}),
 ("f9f9b298fb58", "[BA] English and American Studies", "English and American Studies", "BA", "Humanities", 2300,
  ["a very good command of English is required during the oral entrance exam and throughout the whole program.",
   "Minimum requirement: B2 level proficiency ( CEFR ). TOEFL IBT (Internet-based test): 4.0 – 4.5 (previously 72-94) IELTS (International English Language Testing System): 5.5 minimum"],
  "English and American Studies: no grade cut-off published; secondary school matriculation certificate and an oral entrance exam.",
  {"test_name": "IELTS / TOEFL iBT", "min_score": "B2: IELTS 5.5, or TOEFL iBT 4.0-4.5 (previously 72-94).", "source": "course"}),
]
first = P[0]
spec("hu-elte", ORG, ["ELTE"], "public", "https://www.elte.hu/en/", ("hu", "Hungary", "HUF"), ("hu-budapest", "Budapest"),
     {"main": src(first[0], "Computer Science BSc | ELTE", ORG, [f"{first[1]} - {ORG}", "Study location Hungary, Budapest"])},
     [("international", "Self-financing students (course page fee)", "The tuition fee on each ELTE course page of its application portal (self-financing students).", "main")])

for page, portal, name, deg, field, fee, quotes, th, eng in P:
    q = [f"{portal} - {ORG}", "Nominal duration 6 semesters (3 years)", "Study language English", f"Tuition fee €{fee:,} per semester",
         "September 2027/28", "Studies commence 1 Sept 2027"] + quotes
    prog("hu-elte", f"{deg.lower()}-{slugify(name)}", {"course": src(page, f"{name} {deg} | ELTE", ORG, q), "living": LIVING},
         {"name": name, "degree_type": deg, "field": field, "faculty": "", "duration_years": 3, "duration_source": "course", "languages": ["en"],
          "entry_year": "September 2027/28", "platform": "ELTE application portal (apply.elte.hu)", "source": "course",
          "summary": f"{name} ({deg}), ELTE Budapest, taught in English.", "application_requirements": []},
         [{"residency": "international", "currency": "EUR", "tuition_per_semester": fee, "semesters_quote": "Nominal duration 6 semesters (3 years)",
           "semesters_source": "course", "academic_year": "September 2027/28 intake", "source": "course",
           "note": f"EUR {fee:,} per semester (course page, September 2027/28 intake); 6 semesters over 3 years, so the yearly figure is our calculation.",
           "living": {"monthly": [500, 100, 250, 30, 50, 150], "months": 12, "source": "living", "kind": "genuine_cost_of_living_estimate", "note": LIVING_NOTE}}],
         adm_all({c: th for c in ("ib", "a-level", "us-hs", "cbse", "international-other")}, "course", english=eng))
    print("wrote", name)

"""Boğaziçi University (Istanbul): base records + six engineering programmes (written 2026-11-25).

Sources (globalstudents.bogazici.edu.tr, eng.bogazici.edu.tr, mediastore PDF):
  - Tuition Fees page: "Faculty of Engineering 10.000 USD" per year; no scholarships for international students;
  - 2026-2027 intake fee table (PDF): 5.000,00 USD per semester (first column, Faculty of Engineering);
  - Faculty of Engineering: Computer, Electrical-Electronics, Industrial, Civil, Chemical and Mechanical
    Engineering "through its four-year undergraduate programs";
  - Recognized examinations: SAT 1350 with Math 700 (Engineering), IB 36, A in 3 relevant A levels;
  - English proficiency: language of instruction English; IELTS Academic 6.5 (writing 6.5), TOEFL iBT 4.5.
Held: Humanities (the fee page and the PDF disagree); other faculties' programme lengths not read.
No living-cost figures on the pages read.
  python3 -I scripts/research/gen/tr_boun.py
"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "Boğaziçi University"
FEES = src("08bf6c6b7582", "Tuition Fees | Boğaziçi University Global Students", ORG, [
    "Tuition for Undergraduate Programs for International Students Tuition per Years",
    "Faculty of Engineering 10.000 USD",
    "Bogazici University does not offer scholarships or financial aid to international students."])
PDF = src("boun-fees-2627", "Tuition fees for international students, 2026-2027 intake (PDF) | Boğaziçi University", ORG, [
    "Tuition Fees for Undergraduate (International Quota) and Graduate (International) Students: 2026‐2027 Intake (per semester)",
    "enrolled in 2026‐2027 5.000,00 USD"])
ENGF = src("5c7ef8955248", "Faculty of Engineering | Boğaziçi University", ORG, [
    "our Faculty of Engineering cultivates leading engineers in Computer, Electrical-Electronics, Industrial, Civil, Chemical, and Mechanical Engineering through its four-year undergraduate programs"])
EXAMS = src("b6eaf3ec43d3", "Recognized Examinations / Diplomas | Boğaziçi University", ORG, [
    "Applicants must submit at least one of the following examination or diploma results with the minimum required scores at the time of application.",
    "SAT (Scholastic Aptitude Test) Faculty of Engineering: Minimum Total Score 1350/1600 and Math 700/800",
    "International Baccalaureate (IB) Minimum IB Diploma Diploma Score of 36/45",
    "GCE AL (General Certificate of Education Advanced Level) A grade in minimum 3 subjects relevant to the program applied for",
    "Pakistan Higher Secondary School Certificate (HSSC) Minimum overall success rate of 80% For Engineering and Science programs, a minimum of 75% in both Mathematics and Physics is required"])
ENG = src("be757ac46b20", "English Proficiency and Exemption | Boğaziçi University", ORG, [
    "The language of instruction at Boğaziçi University is English.",
    "IELTS Academic (Paper-based/Computer-delivered) Overall Band Score of 6.5, with a Writing score of 6.5.",
    "TOEFL® IBT and IELTS Academic (Paper-based/Computer-delivered) success criteria effective as of 12 June 2026: TOEFL® IBT Overall Score of at least 4.5, with a minimum score of 4.5 in each of the Reading, Listening, Speaking, and W"])
MAIN = src("6230fb692adf", "Accommodation | Boğaziçi University Global Students", ORG, [
    "Boğaziçi University offers a variety of on-campus housing options",
    "whose families reside outside of Istanbul, are guaranteed on-campus housing only for their first year"])

spec("tr-boun", ORG, ["Bogazici University", "BOUN"], "public", "https://bogazici.edu.tr/en",
     ("tr", "Türkiye", "TRY"), ("tr-istanbul", "Istanbul"), {"main": MAIN, "fees": FEES},
     [("international", "International students (international quota)", "Boğaziçi University's tuition for undergraduate international students; no scholarships or financial aid for them.", "fees")])

ENGLISH = {"test_name": "IELTS Academic / TOEFL iBT", "source": "eng",
           "min_score": "IELTS Academic 6.5 overall with Writing 6.5, or TOEFL iBT 4.5 overall with 4.5 in each section (from 12 June 2026); or Boğaziçi's own BÜYES/BUEPT exam.",
           "notes": "Teaching is in English; proficiency must be documented to register for the programme."}
TAIL = " These are Boğaziçi's minimum scores to apply; places are limited to the international quota."
for name, field in [("Computer Engineering", "Computer Science"), ("Electrical and Electronics Engineering", "Electrical and Electronic Engineering"),
                    ("Industrial Engineering", "Engineering"), ("Civil Engineering", "Civil Engineering"),
                    ("Chemical Engineering", "Chemical Engineering"), ("Mechanical Engineering", "Mechanical Engineering")]:
    prog("tr-boun", f"bs-{slugify(name)}",
         {"course": ENGF, "fees": FEES, "pdf": PDF, "exams": EXAMS, "eng": ENG},
         {"name": name, "degree_type": "B.S.", "field": field, "faculty": "", "duration_years": 4, "duration_source": "course",
          "languages": ["en"], "entry_year": "2026-2027 intake", "platform": "Boğaziçi international student online application", "source": "course",
          "summary": f"{name} (B.S.), Faculty of Engineering, Boğaziçi University, Istanbul; taught in English.", "application_requirements": []},
         [{"residency": "international", "currency": "USD", "tuition_annual": 10000, "academic_year": "2026-2027 intake", "source": ["fees", "pdf"],
           "note": "USD 10,000 a year for the Faculty of Engineering (fee page); the 2026-2027 intake table gives USD 5,000 per semester. "
                   "Boğaziçi gives no scholarships or financial aid to international students. Living costs aren't published on the pages read."}],
         adm_all({"ib": f"{name}: IB Diploma score of at least 36/45.{TAIL}",
                  "a-level": f"{name}: grade A in at least 3 A-level subjects relevant to the programme.{TAIL}",
                  "us-hs": f"{name}: SAT total at least 1350/1600 with Math 700/800 (Faculty of Engineering).{TAIL}"}, "exams", english=ENGLISH))
    print("wrote", name)

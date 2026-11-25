"""Bilkent University (Ankara): base records + ten programmes (written 2026-11-25).

Sources, all bilkent.edu.tr:
  - Tuition fees for international students: 2026-2027, students admitted in 2026: 18,400 USD
    (including 10% VAT), paid in two equal instalments before Fall and Spring registration;
  - How to apply (international): minimum qualifications (SAT 1000 in Math and Critical Reading;
    three A levels at C or better in the programme's area; IB 28 with one related HL subject);
    meeting them doesn't guarantee admission; predicted results not evaluated;
  - English language proficiency: medium of instruction English; IELTS 6.5 (5.5 each), TOEFL iBT 87;
  - International undergraduate programs list (departments);
  - Academic catalog, standing: "The normal period for completion of undergraduate studies at
    Bilkent University is four academic years."
The fee for students admitted in 2027 isn't published yet; the 2026 intake figure is stored and labelled.
No living-cost figures on the pages read.
  python3 -I scripts/research/gen/tr_bilkent.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "Bilkent University"
FEES = src("d2154cea6d18", "Tuition Fees for International Students | Bilkent University", ORG, [
    "Tuition fee for the 2026 – 2027 academic year (including 10% VAT):",
    "For students admitted in 2026 is 18,400 USD",
    "The annual tuition fee is paid in two equal installments, before Fall and Spring semester course registrations"])
APPLY = src("4f4400ee3c47", "How to Apply? | Bilkent University International Students", ORG, [
    "Meeting these minimum qualifications does not guarantee admission to a program.",
    "Reasoning Test: A minimum score of 1000 out of 1600 in “Math” and “Critical Reading” sections.",
    "Minimum three A level subjects in particular area of the applied program with at least “C” grade.",
    "Please note that applications with predicted grades/results/scores will not be evaluated.",
    "International Baccalaureate (IB): A minimum diploma score of 28 out of 45. Mimimum one HL subject related to the applied program.",
    "Ankara, The Capital",
    "Bilkent University accepts international qualifications listed below"])
ENG = src("39ed3dcf001e", "English Language Proficiency | Bilkent University", ORG, [
    "The medium of instruction at Bilkent University is English.",
    "IELTS – 6.5 overall, with a minimum of 5.5 on each section",
    "TOEFL iBT – 87 in total",
    "Students who cannot meet proficiency requirements are required to attend the English Language Preparatory Program."])
LEN = src("76022574ae04", "Duration of study | Bilkent University Online Academic Catalog", ORG, [
    "The normal period for completion of undergraduate studies at Bilkent University is four academic years."])

spec("tr-bilkent", ORG, ["Bilkent"], "private", "https://w3.bilkent.edu.tr/en/",
     ("tr", "Türkiye", "TRY"), ("tr-ankara", "Ankara"), {"main": APPLY, "fees": FEES},
     [("international", "International students and students admitted from abroad", "Bilkent University's tuition for international students and students admitted from abroad, by year of admission.", "fees")])

ENGLISH = {"test_name": "IELTS / TOEFL iBT (or Bilkent's PAE exam)", "source": "eng",
           "min_score": "IELTS 6.5 overall with at least 5.5 in each section, or TOEFL iBT 87; otherwise Bilkent's own PAE exam on arrival, or the English Language Preparatory Program."}
TAIL = " Bilkent's minimum qualifications to apply; meeting them doesn't guarantee admission, and predicted results aren't evaluated."
P = [("Computer Engineering", "Computer Science", "Department of Computer Engineering"),
     ("Electrical and Electronics Engineering", "Electrical and Electronic Engineering", "Department of Electrical and Electronics Engineering"),
     ("Industrial Engineering", "Engineering", "Department of Industrial Engineering"),
     ("Mechanical Engineering", "Mechanical Engineering", "Department of Mechanical Engineering"),
     ("Economics", "Economics", "Department of Economics"),
     ("Management", "Business", "FACULTY OF BUSINESS ADMINISTRATION Department of Management"),
     ("International Relations", "Politics", "Department of International Relations"),
     ("Psychology", "Psychology", "Department of Psychology"),
     ("Mathematics", "Mathematics", "Department of Mathematics"),
     ("Molecular Biology and Genetics", "Biology", "Department of Molecular Biology and Genetics")]
for name, field, dept in P:
    course = src("d958abebf97f", "Undergraduate Programs | Bilkent University International Students", ORG, [dept])
    prog("tr-bilkent", f"bachelor-{slugify(name)}",
         {"course": course, "len": LEN, "fees": FEES, "apply": APPLY, "eng": ENG},
         {"name": name, "degree_type": "Bachelor's", "field": field, "faculty": "", "duration_years": 4, "duration_source": "len",
          "languages": ["en"], "entry_year": "2026-2027 rules (2027 intake fee not yet published)", "platform": "Bilkent international online application",
          "source": "course", "summary": f"{name}, Bilkent University, Ankara; taught in English.", "application_requirements": []},
         [{"residency": "international", "currency": "USD", "tuition_annual": 18400, "academic_year": "2026-2027 (students admitted in 2026)", "source": "fees",
           "note": "2026-2027 tuition for students admitted in 2026: 18,400 USD including 10% VAT, paid in two equal instalments (Fall and Spring). "
                   "The fee for students admitted in 2027 isn't published yet. Living costs aren't published on the pages read."}],
         adm_all({"ib": f"{name}: IB Diploma score of at least 28/45 with at least one HL subject related to the programme.{TAIL}",
                  "a-level": f"{name}: at least three A-level subjects in the programme's area at grade C or better.{TAIL}",
                  "us-hs": f"{name}: SAT at least 1000/1600 in Math and Critical Reading.{TAIL}"}, "apply", english=ENGLISH))
    print("wrote", name)

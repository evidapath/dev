"""National University of Singapore: base records + Bachelor of Computing in Computer Science (written 2026-11-26). THE queue #12.

Sources:
  - NUS Computing FAQ (comp.nus.edu.sg/admissions/faq): "The Computer Science programme spans four years";
    "Not all international students will receive MOE tuition grant subsidy due to limited quota";
  - Registrar, Undergraduate Tuition Fees Per Annum AY2026/2027 (PDF, March 2026), table (A) for new students
    admitted in AY2026/2027: "Computing 8,300 11,600 18,050 21,400 39,700" (Singapore citizens, PRs, ASEAN IS and
    all other IS with the MOE Tuition Grant, and students not receiving the Tuition Grant).
Not stored: entry grades (NUS's grade-profile page returned a bot-check page), English requirement, living costs.
  python3 -I scripts/research/gen/sg_nus.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog

ORG = "National University of Singapore"
FAQ = src("66fb9b98a777", "Frequently Asked Questions | NUS Computing", ORG,
          ["The Computer Science programme spans four years, culminating in an honours classification for most students.",
           "Not all international students will receive MOE tuition grant subsidy due to limited quota for the different programme offers from each college, faculty or school."])
CS = src("33ef28d31f59", "Computer Science | NUS Computing", ORG, ["Bachelor of Computing in Computer Science (with Honours*)", "© National University of Singapore. All Rights Reserved."])
FEE = src("nus-ugtuition", "Undergraduate Tuition Fees Per Annum, AY2026/2027 | NUS Registrar", ORG,
          ["Tuition Fees Per Annum (applicable for Academic Year 2026/2027)", "A) For new students admitted in AY2026/2027",
           "Fees payable by students in receipt of MOE Tuition Grant", "ASEAN6 All other IS",
           "Computing 8,300 11,600 18,050 21,400 39,700",
           "3. Students who are not in receipt of the Tuition Grant will have to pay the non-subsidised fee amounts as quoted here (which are inclusive of the prevailing GST)."])
spec("sg-nus", ORG, ["NUS"], "public", "https://www.nus.edu.sg", ("sg", "Singapore", "SGD"), ("sg-singapore", "Singapore"),
     {"main": CS, "fees": FEE},
     [("intl-no-grant", "International students without the MOE Tuition Grant", "Non-subsidised fee, payable by students not receiving the MOE Tuition Grant.", "fees"),
      ("intl-grant", "International students with the MOE Tuition Grant (other than ASEAN)", "Subsidised fee for international students (other than ASEAN) receiving the MOE Tuition Grant.", "fees"),
      ("asean-grant", "ASEAN international students with the MOE Tuition Grant", "Subsidised fee for ASEAN international students receiving the MOE Tuition Grant.", "fees")])
NOTE = " The Tuition Grant is not given to every international student (limited quota)."
prog("sg-nus", "bachelor-of-computing-computer-science", {"course": FAQ, "cs": CS, "fees": FEE},
     {"name": "Computer Science", "degree_type": "Bachelor of Computing (Honours)", "field": "Computer Science", "faculty": "",
      "duration_years": 4, "duration_source": "course", "languages": ["en"], "entry_year": "AY2026/2027", "platform": "", "source": "course",
      "summary": "Bachelor of Computing in Computer Science (with Honours), National University of Singapore; four years.", "application_requirements": []},
     [{"residency": "intl-no-grant", "currency": "SGD", "tuition_annual": 39700, "academic_year": "AY2026/2027", "source": ["fees", "course"],
       "note": "Students not receiving the MOE Tuition Grant: S$39,700 a year (new students admitted in AY2026/2027, inclusive of GST)." + NOTE},
      {"residency": "intl-grant", "currency": "SGD", "tuition_annual": 21400, "academic_year": "AY2026/2027", "source": ["fees", "course"],
       "note": "International students (other than ASEAN) with the MOE Tuition Grant: S$21,400 a year (AY2026/2027 intake, inclusive of GST)." + NOTE},
      {"residency": "asean-grant", "currency": "SGD", "tuition_annual": 18050, "academic_year": "AY2026/2027", "source": ["fees", "course"],
       "note": "ASEAN international students with the MOE Tuition Grant: S$18,050 a year (AY2026/2027 intake, inclusive of GST)." + NOTE}],
     [])
print("wrote nus")

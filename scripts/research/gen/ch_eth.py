"""ETH Zurich: base records + Bachelor Computer Science (written 2026-11-26). THE queue #8.

Sources (ethz.ch):
  - Bachelor Computer Science page: "Bachelor's degree programme (180 credits)", "ETH Zurich Department of Computer
    Science ... 8092 Zurich";
  - Bachelor's degree programmes page: "the Bachelor’s degree programmes begin in German . In the second and third
    years of the programmes, some of the courses may take place in English.";
  - programme structure page: "The Bachelor’s degree programme comprises 180 credits and usually takes three years.";
  - tuition fees page: threefold tuition fee CHF 2190 / semester for students who don't meet the simple-fee criteria
    (from autumn semester 2025); simple fee CHF 730 / semester;
  - Study and Living Costs, international students (PDF): tuition group 2 "4’380" a year, compulsory total "4’528",
    individual living costs "TOTAL 22’100" (rent average 2024 "Ø 11’300");
  - Admission requirements, academic year 2026/27 (PDF): IB 38 out of 42 without bonus points + HL subjects for
    admission without entrance examination; Great Britain: three A-Levels at minimum grade A in the named subjects.
  python3 -I scripts/research/gen/ch_eth.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "ETH Zurich"
CS = src("5575907880d6", "Bachelor Computer Science | ETH Zurich", ORG,
         ["Bachelor Computer Science | ETH Zurich", "Bachelor's degree programme (180 credits)",
          "ETH Zurich Department of Computer Science Study Administration Office Universitätstrasse 6 CAB F 62.1 8092 Zurich Schweiz"])
LANG = src("c647c6d02ea0", "Bachelor's degree programmes | ETH Zurich", ORG,
           ["Please note: the Bachelor’s degree programmes begin in German . In the second and third years of the programmes, some of the courses may take place in English."])
ST = src("1004057f6be7", "Programme structure | ETH Zurich", ORG,
         ["The Bachelor’s degree programme comprises 180 credits and usually takes three years."])
FEE = src("dc0cf9304150", "Tuition fees | ETH Zurich", ORG,
          ["Simple tuition fee: CHF 730 / semester for students with Swiss citizenship.",
           "Threefold tuition fee: CHF 2190 / semester All students who do not fulfil the criteria for simple tuition fee will be assigned to the second group paying a threefold tuition fe",
           "The threefold tuition fee for foreign students will apply from the Autumn Semester 2025."])
COL = src("eth-col", "Study and Living Costs International students (approximate) | ETH Zurich", ORG,
          ["Study and Living Costs International students (approximate) Annual costs in CHF",
           "Tuition fee (including exam fees) 1’460 4’380", "TOTAL 1’608 4’528",
           "Rent (room including heating, etc; canton of Zurich, average 2024) Ø 11’300",
           "Health insurance (non-EU/EFTA; average) Ø 1’320", "Individual expenses 1’680 TOTAL 22’100"])
ADM = src("eth-adm-2026", "Admission requirements ETH Zurich, Academic Year 2026/27", ORG,
          ["Admission requirements ETH Zurich Academic Year 2026/27",
           "Admission without entrance examination if the following requirements are fulfilled: International Baccalaureate − 38 out of 42 points (without bonus points);",
           "− At Higher Level (HL): a) Mathematics: applications and interpretation or Mathematics: analysis and approaches, b) physics or chemistry or biology, c) 1 language A;",
           "Otherwise: Reduced Entrance Examination ETHZ",
           "England, Wales and Northern Ireland: (I)GCE with three Advanced Levels or",
           "Cambridge Pre-U Certificate (three Principal Subjects) in: 1. mathematics; 2.",
           "physics or chemistry or biology, 3. language of instruction or foreign language with minimum grade A in each A-Level"])
spec("ch-eth", ORG, ["ETH", "Eidgenössische Technische Hochschule Zürich"], "public", "https://ethz.ch",
     ("ch", "Switzerland", "CHF"), ("ch-zurich", "Zurich"),
     {"main": CS, "fees": FEE},
     [("threefold", "Foreign students (threefold tuition fee)", "ETH tuition group 2: students who don't meet the simple-fee criteria (Swiss citizens and certain residents).", "fees")])
prog("ch-eth", "bachelor-computer-science", {"course": CS, "lang": LANG, "structure": ST, "fees": FEE, "costs": COL, "adm": ADM},
     {"name": "Computer Science", "degree_type": "Bachelor", "field": "Computer Science", "faculty": "Department of Computer Science",
      "duration_years": 3, "duration_source": "structure", "languages": ["de"], "entry_year": "2026/27", "platform": "", "source": "course",
      "summary": "Bachelor Computer Science, ETH Zurich; 180 credits, usually three years. Bachelor's programmes begin in German; some later courses may be in English.",
      "application_requirements": []},
     [{"residency": "threefold", "currency": "CHF", "tuition_annual": 4380, "academic_year": "from Autumn Semester 2025", "source": ["costs", "fees"],
       "note": "Threefold tuition fee CHF 2190 per semester, CHF 4,380 a year (foreign students); with compulsory semester fees CHF 4,528 a year.",
       "living": {"monthly": [], "months": 12, "yearly": [22100], "source": "costs", "kind": "genuine_cost_of_living_estimate",
                  "note": "ETH's approximate individual living costs for international students: CHF 22,100 a year (rent, meals, transport, health insurance, personal expenses)."}}],
     adm_all({"ib": "Computer Science: IB 38 out of 42 (without bonus points) with HL Mathematics, HL physics, chemistry or biology, and HL language A, for admission without an entrance examination (2026/27 rules); otherwise the Reduced Entrance Examination.",
              "a-level": "Computer Science: AAA, three A-Levels in mathematics, physics/chemistry/biology and a language at minimum grade A each, plus further subjects, for admission without an entrance examination (2026/27 rules); otherwise the Reduced Entrance Examination."},
             "adm"))
print("wrote eth")

# Every other ETH bachelor's programme (added 2026-11-27). Fees, living costs, length (structure page) and the
# foreign-certificate admission rules are ETH-wide, so each programme cites its own page for its name plus the
# shared sources. Left out: Human Medicine (own admission procedure) and Public Policy (Professional Officer).
import re
from newuni import PAGES, slugify
FIELD = {"Architecture": "Architecture", "Civil Engineering": "Civil Engineering", "Environmental Engineering": "Engineering",
         "Geospatial Engineering": "Engineering", "Electrical Engineering and Information Technology": "Electrical and Electronic Engineering",
         "Materials Science": "Engineering", "Mechanical Engineering": "Mechanical Engineering", "Chemistry / Chemical and Bioengineering": "Chemistry",
         "Biochemistry – Chemical Biology": "Chemistry", "Biology": "Biology", "Computational Science and Engineering": "Computer Science",
         "Interdisciplinary Sciences": "Natural Sciences", "Mathematics": "Mathematics", "Pharmaceutical Sciences": "Pharmacy", "Physics": "Physics",
         "Agricultural Sciences": "Agriculture", "Earth and Climate Sciences": "Earth Sciences", "Environmental Sciences": "Environmental Science",
         "Food Science and Nutrition": "Food Science", "Health Sciences and Technology": "Health Sciences"}
for pid in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "eth_pages.txt")).read().split():
    t = re.sub(r"\s+", " ", open(PAGES / f"{pid}.txt", errors="replace").read())
    title = t.split(" | ")[0].strip()
    name = title.replace("Bachelor ", "", 1)
    P = src(pid, f"{title} | ETH Zurich", ORG, [f"{title} | ETH Zurich"])
    prog("ch-eth", "bachelor-" + slugify(name), {"course": P, "lang": LANG, "structure": ST, "fees": FEE, "costs": COL, "adm": ADM},
         {"name": name, "degree_type": "Bachelor", "field": FIELD[name], "faculty": "", "duration_years": 3, "duration_source": "structure",
          "languages": ["de"], "entry_year": "2026/27", "platform": "", "source": "course",
          "summary": f"Bachelor {name}, ETH Zurich; ETH bachelor's programmes usually take three years and begin in German.",
          "application_requirements": []},
         [{"residency": "threefold", "currency": "CHF", "tuition_annual": 4380, "academic_year": "from Autumn Semester 2025", "source": ["costs", "fees"],
           "note": "Threefold tuition fee CHF 2190 per semester, CHF 4,380 a year (foreign students); with compulsory semester fees CHF 4,528 a year.",
           "living": {"monthly": [], "months": 12, "yearly": [22100], "source": "costs", "kind": "genuine_cost_of_living_estimate",
                      "note": "ETH's approximate individual living costs for international students: CHF 22,100 a year (rent, meals, transport, health insurance, personal expenses)."}}],
         adm_all({"ib": f"{name}: IB 38 out of 42 (without bonus points) with HL Mathematics, HL physics, chemistry or biology, and HL language A, for admission without an entrance examination (2026/27 rules); otherwise the Reduced Entrance Examination.",
                  "a-level": f"{name}: AAA, three A-Levels in mathematics, physics/chemistry/biology and a language at minimum grade A each, plus further subjects, for admission without an entrance examination (2026/27 rules); otherwise the Reduced Entrance Examination."},
                 "adm"))
print("wrote eth (all bachelor's)")

"""EPFL: base records + Bachelor Computer Science (written 2026-11-26). THE queue #9.

Sources (epfl.ch):
  - About EPFL: "renamed École Polytechnique Fédérale de Lausanne in 1969";
  - Bachelor Computer Science page (1st, 2nd and 3rd years; "Study plan (in French)");
  - study programmes structure page: "Bachelor: 180 ECTS"; bachelor FAQs: a university year = 60 credits;
  - Bachelor admission criteria: first-year places limited (3000) from 2025 for at least four years; IB holders
    accepted "within the places available" with HL mathematics, physics and chemistry/biology/computer science,
    at least 38 out of 42 (excluding bonus points) and at least 6 in mathematics and physics; A-levels at least A
    in the same subjects; French level B2 required (C1 highly recommended);
  - tuition fee page: semester tuition CHF 730, tripled to CHF 2190 per semester for foreign students who take up
    residence in Switzerland for study (from fall 2025); invoice CHF 2240 per semester for them;
  - Financing your studies: approximate budget for foreigners, "TOTAL 2’107.- without tuition fees 25’219.- without
    tuition fees" (CHF a month / a year).
  python3 -I scripts/research/gen/ch_epfl.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "EPFL"
AB = src("5b1144d68e0d", "Overview ‒ About ‐ EPFL", ORG,
         ["Founded in 1853, the École Spéciale de Lausanne was renamed École Polytechnique Fédérale de Lausanne in 1969."])
CS = src("f49aa947e084", "Computer Science ‒ Bachelor ‐ EPFL", ORG,
         ["Computer Science ‒ Bachelor ‐ EPFL", "Classes during the 1 st year are given jointly to computer science students and artificial intelligence students.",
          "During the 2 nd and 3 rd years, students pursue their basic training in mathematics and physics as well as in computer science fields",
          "School of Computer & Communication Sciences IC"])
STR = src("fd3a014e0460", "Study programs structure ‒ Bachelor ‐ EPFL", ORG, ["Bachelor: 180 ECTS"])
FAQ = src("f4f12afab434", "FAQs ‒ Bachelor ‐ EPFL", ORG,
          ["ECTS is based on the principal that the full-time work done by a student during a university year corresponds to 60 credits."])
ADM = src("77a6f4005f2c", "Bachelor/CMS admission criteria & application ‒ Admission ‐ EPFL", ORG,
          ["EPFL introduces a limitation on the number of students in the first year of the Bachelor’s programs (3000).",
           "Applicants holding an International Baccalaureate (IB) from IBO.org are accepted in the first year of the Bachelor’s programs , within the places available (see above) , provided that their title fulfils all of the following conditions: the following subjects were studied and examined within the Diploma Programme (DP) at the higher level (HL): 1) mathematics, 2) physics, and 3) chemistry, biology, or computer science",
           "the total number of points scored is at least 38 out of 42 (excluding bonus points) and the grades in mathematics and physics are at least 6 out of 7",
           "The general average (or total number of points scored) of the school-leaving certificate will be used to rank and select the applicants.",
           "the grades in mathematics and physics, as well as in chemistry, biology, or computer science, are at least A and/or 1",
           "EPFL considers that level B2 in French (according to the Common European Framework of Reference for Languages ) is required to follow its Bachelor’s programs. Level C1 is highly recommended."])
FEE = src("598412a4742f", "Tuition fee and other fees ‒ Study management ‐ EPFL", ORG,
          ["only the CHF 730 semester tuition fee is tripled by this measure (it is thus raised to CHF 2190 per semester)",
           "the ETH Board expressed its support for the tripling of tuition fees for foreign students who take up residence in Switzerland for study purposes.",
           "The total amount due per semester invoice is CHF 780 (CHF 2240 for some students from the fall semester, 2025; see above)",
           "EPFL informs at the end of the spring semester", "should they start a new program in the following fall semester"])
FIN = src("cb1aac2f86c2", "Financing your studies ‒ Study management ‐ EPFL", ORG,
          ["Approximate budget for foreigner Types of fees Monthly (CHF) Yearly (CHF) 12 months",
           "TOTAL 2’107.- without tuition fees 25’219.- without tuition fees",
           "Student services desk EPFL VPH-SLE BP 1229 (bâtiment BP) Station 16 CH – 1015 Lausanne"])
spec("ch-epfl", ORG, ["École Polytechnique Fédérale de Lausanne"], "public", "https://www.epfl.ch", ("ch", "Switzerland", "CHF"), ("ch-lausanne", "Lausanne"),
     {"main": FIN, "about": AB, "fees": FEE},
     [("foreign", "Foreign students (tripled tuition fee)", "Foreign students who take up residence in Switzerland to study pay the tripled semester tuition fee.", "fees")])
prog("ch-epfl", "bachelor-computer-science", {"course": CS, "structure": STR, "faq": FAQ, "adm": ADM, "fees": FEE, "fin": FIN},
     {"name": "Computer Science", "degree_type": "Bachelor", "field": "Computer Science", "faculty": "School of Computer & Communication Sciences",
      "duration_years": 3, "duration_source": "course", "languages": ["fr"], "entry_year": "", "platform": "", "source": "course",
      "summary": "Bachelor in Computer Science, EPFL (Lausanne); three years. Taught in French (level B2 required).",
      "application_requirements": []},
     [{"residency": "foreign", "currency": "CHF", "tuition_per_term": 2190, "terms_per_year": 2,
       "terms_evidence": ["EPFL informs at the end of the spring semester", "should they start a new program in the following fall semester"],
       "academic_year": "from fall semester 2025", "source": "fees",
       "note": "Tripled tuition fee for foreign students: CHF 2190 per semester (CHF 2240 per semester invoice with compulsory fees), from fall 2025.",
       "living": {"monthly": [], "months": 12, "yearly": [25219], "source": "fin", "kind": "genuine_cost_of_living_estimate",
                  "note": "EPFL's approximate budget for foreigners: CHF 25,219 a year without tuition fees."}}],
     adm_all({"ib": "Computer Science: IB 38 out of 42 (excluding bonus points) with HL mathematics, physics and chemistry/biology/computer science, and at least 6 in mathematics and physics; accepted within the 3000 first-year places, ranked by total points.",
              "a-level": "Computer Science: A-levels in mathematics, physics and chemistry/biology/computer science at grade A or better (AAA); accepted within the 3000 first-year places, ranked by average."},
             "adm"))
print("wrote epfl")

# Every other EPFL bachelor's programme (added 2026-11-27): tuition, living budget, admission rules and French
# requirement are EPFL-wide; each programme cites its own page for its name and the "Second and third year" plan.
import re
from newuni import PAGES, slugify
FIELD = {"Architecture": "Architecture", "Artificial Intelligence": "Computer Science", "Chemistry and Chemical Engineering": "Chemistry",
         "Civil Engineering": "Civil Engineering", "Communication Systems": "Computer Science",
         "Electrical and Electronic Engineering": "Electrical and Electronic Engineering", "Environmental Sciences and Engineering": "Environmental Science",
         "Life Sciences Engineering": "Biology", "Materials Science and Engineering": "Engineering", "Mathematics": "Mathematics",
         "Mechanical Engineering": "Mechanical Engineering", "Microengineering": "Engineering", "Physics": "Physics"}
for pid in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "epfl_pages.txt")).read().split():
    t = re.sub(r"\s+", " ", open(PAGES / f"{pid}.txt", errors="replace").read())
    name = t.split(" ‒ ")[0].strip()
    P = src(pid, f"{name} ‒ Bachelor ‐ EPFL", ORG, [f"{name} ‒ Bachelor ‐ EPFL", "Second and third year"])
    prog("ch-epfl", "bachelor-" + slugify(name), {"course": P, "structure": STR, "faq": FAQ, "adm": ADM, "fees": FEE, "fin": FIN},
         {"name": name, "degree_type": "Bachelor", "field": FIELD[name], "faculty": "", "duration_years": 3, "duration_source": "course",
          "languages": ["fr"], "entry_year": "", "platform": "", "source": "course",
          "summary": f"Bachelor in {name}, EPFL (Lausanne); three years. Taught in French.", "application_requirements": []},
         [{"residency": "foreign", "currency": "CHF", "tuition_per_term": 2190, "terms_per_year": 2,
           "terms_evidence": ["EPFL informs at the end of the spring semester", "should they start a new program in the following fall semester"],
           "academic_year": "from fall semester 2025", "source": "fees",
           "note": "Tripled tuition fee for foreign students: CHF 2190 per semester (CHF 2240 per semester invoice with compulsory fees), from fall 2025.",
           "living": {"monthly": [], "months": 12, "yearly": [25219], "source": "fin", "kind": "genuine_cost_of_living_estimate",
                      "note": "EPFL's approximate budget for foreigners: CHF 25,219 a year without tuition fees."}}],
         adm_all({"ib": f"{name}: IB 38 out of 42 (excluding bonus points) with HL mathematics, physics and chemistry/biology/computer science, and at least 6 in mathematics and physics; accepted within the 3000 first-year places, ranked by total points.",
                  "a-level": f"{name}: A-levels in mathematics, physics and chemistry/biology/computer science at grade A or better (AAA); accepted within the 3000 first-year places, ranked by average."},
                 "adm"))
print("wrote epfl (all bachelor's)")

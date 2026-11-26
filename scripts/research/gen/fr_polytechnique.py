"""École Polytechnique (a founding school of Institut Polytechnique de Paris): base records + Bachelor of Science
(written 2026-11-26). THE queue #35 lists Institut Polytechnique de Paris; its English-taught undergraduate
programme is École Polytechnique's Bachelor of Science.

Sources:
  - ip-paris.fr/en: "École Polytechnique, one of the founding schools of Institut Polytechnique de Paris";
  - programmes.polytechnique.edu Bachelor of Science page: "three-year program", "taught entirely in English",
    "Three Years - 180 ECTS", double majors (Mathematics and Physics / Computer Science / Economics), address
    "Route de Saclay 91128 PALAISEAU";
  - Bachelor FAQ: "Annual tuition fees for 2027 intake are €15,900 for EU (including EEA) students and €19,600 for
    non-EU (non-EEA) students"; no minimum grades; IB/A-level subject advice; TOEFL iBT 90, IELTS 6,5 (6 per skill);
    accommodation €606 per month (2026 intake), not included in tuition.
Living costs not stored: only the on-campus rent is published, without the number of months.
  python3 -I scripts/research/gen/fr_polytechnique.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "École Polytechnique"
B = src("8274eefe5f2c", "Bachelor of Science - École Polytechnique", ORG,
        ["The Bachelor of Science is a three-year program designed for students with a strong interest in Mathematics and Science. This highly selective and multidisciplinary program is taught entirely in English.",
         "Three Years - 180 ECTS Three Double Majors September International In France In English",
         "students work towards one of three double majors: Mathematics and Physics Mathematics and Computer Science Mathematics and Economics",
         "ECOLE POLYTECHNIQUE Route de Saclay 91128 PALAISEAU Cedex France"])
FAQ = src("8e94c18e4b57", "Bachelor FAQ - École Polytechnique", ORG,
          ["However, as with all of École Polytechnique’s academic programs, the Bachelor programs are designed for top students with very high potential and we require them to have a strong overall academic average.",
           "For the moment, there are no minimum grades required to be able to apply for the programs.",
           "Annual tuition fees for 2027 intake are €15,900 for EU (including EEA) students and €19,600 for non-EU (non-EEA) students.",
           "Accommodation currently costs €606 per month (2026 intake, amount revised annually in January) and is not included in the tuition fees.",
           "International Baccalaureate: Mathematics Higher Level (preferably “Analysis and Approaches”) and at least one other science course should be Higher Level.",
           "A-level program: Mathematics and at least one other scientific subject should be Higher Level.",
           "The minimum grades required are: - TOEFL iBT : 90 - IELTS : 6,5 (minimum grade per each language skill: 6)",
           "Route de Saclay 91128 PALAISEAU Cedex France"])
IP = src("f34332656b0f", "Institut Polytechnique de Paris", "Institut Polytechnique de Paris",
         ["École Polytechnique, one of the founding schools of Institut Polytechnique de Paris"])
spec("fr-polytechnique", ORG, ["Institut Polytechnique de Paris", "IP Paris", "Ecole Polytechnique"], "public", "https://www.polytechnique.edu",
     ("fr", "France", "EUR"), ("fr-palaiseau", "Palaiseau"),
     {"main": FAQ, "course": B, "ip": IP},
     [("non-eu", "Non-EU (non-EEA) students", "Bachelor of Science annual tuition for non-EU (non-EEA) students.", "main"),
      ("eu-eea", "EU/EEA students", "Bachelor of Science annual tuition for EU (including EEA) students.", "main")])
ENG = {"test_name": "TOEFL iBT or IELTS", "source": "faq", "min_score": "TOEFL iBT 90; IELTS 6,5 as published (at least 6 in each skill)."}
NOTE = " There are no minimum grades; the programme is highly selective and expects a strong overall academic average."
prog("fr-polytechnique", "bachelor-of-science", {"course": B, "faq": FAQ},
     {"name": "Bachelor of Science (double major: Mathematics with Physics, Computer Science or Economics)", "degree_type": "Bachelor", "field": "Mathematics",
      "faculty": "", "duration_years": 3, "duration_source": "course", "languages": ["en"], "entry_year": "2027", "platform": "", "source": "course",
      "summary": "Bachelor of Science, École Polytechnique (Palaiseau); three years, 180 ECTS, taught entirely in English, leading to a double major in Mathematics and Physics, Computer Science or Economics.",
      "application_requirements": []},
     [{"residency": "non-eu", "currency": "EUR", "tuition_annual": 19600, "academic_year": "2027 intake", "source": "faq",
       "note": "Non-EU (non-EEA) students: €19,600 a year (2027 intake). On-campus accommodation is extra: €606 per month (2026 intake)."},
      {"residency": "eu-eea", "currency": "EUR", "tuition_annual": 15900, "academic_year": "2027 intake", "source": "faq",
       "note": "EU (including EEA) students: €15,900 a year (2027 intake)."}],
     adm_all({"ib": "Bachelor of Science: IB with Mathematics at Higher Level (preferably Analysis and Approaches) and at least one other science at Higher Level." + NOTE,
              "a-level": "Bachelor of Science: A levels including Mathematics and at least one other scientific subject." + NOTE},
             "faq", english=ENG))
print("wrote polytechnique")

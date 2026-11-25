"""Hungarian University of Agriculture and Life Sciences (MATE), Gödöllő: base records + four BSc (written 2026-11-25).

Sources, all uni-mate.hu:
  - Tuition Fees (Directorate of Education): fees "apply to students beginning their studies in the
    2026-2027 academic year"; per programme, campus and EUR per semester; the first two semesters are paid
    before admission and entering Hungary;
  - programme pages on ed.uni-mate.hu: "Length of program: 7 semesters", language of conduction (Gödöllő: English).
Entry requirements weren't read, so none is stored beyond "not published on the pages read". No living costs.
  python3 -I scripts/research/gen/hu_mate.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "Hungarian University of Agriculture and Life Sciences"
HEAD = ["self-financed courses at the Hungarian University of Agriculture and Life Sciences",
        "The tuition fees listed in the table below apply to students beginning their studies in the 2026-2027 academic year.",
        "Tuition fees for the first two semesters of the programme shall be paid before admission and entering Hungary."]
P = [("822a7cc1a2f3", "Agricultural Engineering", "Agriculture", 2200,
      "Agricultural Engineering Gödöllő 7 Stipendium Hungaricum, Scholarship for Christian Young People, Hungarian Diaspora Scholarship yes 2200 Euro/semester",
      "Language of conduction: Gödöllő: Hungarian and English"),
     ("48fd7b11976c", "Business Administration and Management", "Business", 2300,
      "Business Administration and Management Gödöllő 7 Stipendium Hungaricum, Hungarian Diaspora Scholarship yes 2300 Euro/semester",
      "Language of conduction: Gödöllő (Szent István Campus): Hungarian, English (only full-time training)"),
     ("c583966aed78", "Environmental Engineering", "Environmental Science", 2200,
      "Environmental Engineering Gödöllő 7 Stipendium Hungaricum, Scholarship for Christian Young People, Hungarian Diaspora Scholarship yes 2200 Euro/semester",
      "Language of conduction: Hungarian or English"),
     ("04e83b2d41f3", "Mechanical Engineering", "Mechanical Engineering", 2500,
      "Mechanical Engineering Gödöllő 7 Stipendium Hungaricum, Hungarian Diaspora Scholarship yes 2500 Euro/semester",
      "Language of conduction: Gödöllő (Institute of Technology): Hungarian, English")]

FEES_MAIN = src("c0a01b7c021a", "Tuition Fees | MATE Directorate of Education", ORG, HEAD + [P[0][4]])
spec("hu-mate", ORG, ["MATE"], "public", "https://en.uni-mate.hu", ("hu", "Hungary", "HUF"), ("hu-godollo", "Gödöllő"),
     {"main": FEES_MAIN}, [("self-funded", "Self-funded students", "MATE's per-semester tuition for self-funded students beginning in 2026-2027.", "main")])

TH = "{name}: entry requirements aren't published on the pages read; check MATE's application procedure for BSc."
for page, name, field, fee, row, lang in P:
    course = src(page, f"BSc in {name} | MATE Directorate of Education", ORG, ["Length of program: 7 semesters", lang])
    fees = src("c0a01b7c021a", "Tuition Fees | MATE Directorate of Education", ORG, HEAD + [row])
    prog("hu-mate", f"bsc-{slugify(name)}", {"course": course, "fees": fees},
         {"name": name, "degree_type": "BSc", "field": field, "faculty": "", "duration_years": 3.5, "duration_source": "course", "languages": ["en"],
          "entry_year": "2026-2027 fees", "platform": "MATE application for self-financed students", "source": "course",
          "summary": f"BSc in {name}, MATE, Gödöllő campus; taught in English there.", "application_requirements": []},
         [{"residency": "self-funded", "currency": "EUR", "tuition_per_semester": fee, "semesters_quote": "Length of program: 7 semesters",
           "semesters_source": "course", "academic_year": "2026-2027", "source": "fees",
           "note": f"EUR {fee:,} per semester for students starting in 2026-2027 (Gödöllő); the first two semesters are paid before admission and entering Hungary. Yearly figure our calculation."}],
         adm_all({c: TH.format(name=name) for c in ("ib", "a-level", "us-hs", "cbse", "international-other")}, "fees"))
    print("wrote", name)

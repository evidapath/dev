"""The University of Hong Kong (HKU): base records + eight undergraduate programmes (written 2026-11-26). THE queue #3.

Sources, all hku.hk:
  - HKU General Information 2027 (PDF, admissions): non-subsidised composition fee for students admitted in
    2027-2028, including non-local students: STEM faculties/schools HK$280,000 per annum; non-STEM HK$250,000
    per annum;
  - programme pages on admissions.hku.hk (rendered with bfetch.sh): "Undergraduate Courses <name> CODE <n>
    STUDY PERIOD 4-year ABBREVIATION <abbr> ... FACULTY <faculty>".
Entry requirements by qualification are not on the programme pages read, so none is stored. No living costs.
  python3 -I scripts/research/gen/hk_hku.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify, PAGES

ORG = "The University of Hong Kong"
COPY = "Copyright © 2026 Admissions Office, The Registry, The University of Hong Kong. All rights reserved."
FEE_INTRO = "Students who do not meet the eligibility criteria for subsidised fees, including non-local students, will be required to pay the applicable non-subsidised composition fee, as set out below:"
STEM_Q = ("STEM Faculties and Schools — including the Faculties of Engineering, Medicine (excluding the MBBS programme) and Science, and the Schools of "
          "Biomedical Engineering, Computing and Data Science*, and Innovation: HK$280,000 per annum, inclusive of the STEM fee*.")
NONSTEM_Q = ("Non-STEM Faculties and Schools — including the Faculties of Architecture, Arts, Business and Economics, Education, Law and Social Sciences, "
             "and the Schools of Future Media and Governance and Policy: HK$250,000 per annum.")
YEAR_Q = "The composition fees for students admitted in the 2027–2028 academic year will depend on their eligibility for government-subsidised student places."
FEES = src("hku-geninfo-2027", "General Information 2027 (PDF) | HKU Undergraduate Admissions", ORG, [YEAR_Q, FEE_INTRO, STEM_Q, NONSTEM_Q])

# page, field, stem?
P = [("26af600b4f8b", "Computer Science", True), ("77c44cb202d3", "Civil Engineering", True),
     ("0f9d134ed1f4", "Electrical and Electronic Engineering", True), ("87786b0acb56", "Mechanical Engineering", True),
     ("f6e51bf77386", "Business", False), ("285e86ca256f", "Accounting and Finance", False),
     ("66ec3b3d59e0", "Economics", False), ("6a8844b6b5bc", "Science", True)]
spec("hk-hku", ORG, ["HKU"], "public", "https://www.hku.hk", ("hk", "Hong Kong", "HKD"), ("hk-hong-kong", "Hong Kong"),
     {"main": src(P[0][0], "Computing and Data Science | HKU Undergraduate Admissions", ORG, [COPY])},
     [("non-local", "Non-local students (non-subsidised fee)", "HKU's non-subsidised composition fee, which non-local students pay.", "main")])

TH = "{n}: entry requirements by qualification aren't on the HKU programme page read, so no grade is shown."
for page, field, stem in P:
    t = re.sub(r"\s+", " ", (PAGES / f"{page}.txt").read_text())
    m = re.search(r"Undergraduate Courses (.+?) CODE (\d+) STUDY PERIOD 4-year ABBREVIATION (\S+)", t)
    name, code, abbr = m.groups()
    fee = 280000 if stem else 250000
    course = src(page, f"{name} | HKU Undergraduate Admissions", ORG, [m.group(0), COPY])
    prog("hk-hku", slugify(f"{abbr} {code}"), {"course": course, "fees": FEES},
         {"name": name, "degree_type": abbr, "field": field, "faculty": "", "duration_years": 4, "duration_source": "course", "languages": [],
          "entry_year": "2027-2028", "platform": "HKU international (non-JUPAS) application", "source": "course",
          "summary": f"{abbr}, HKU (programme code {code}); 4 years.", "application_requirements": []},
         [{"residency": "non-local", "currency": "HKD", "tuition_annual": fee, "academic_year": "2027-2028", "source": "fees",
           "note": f"Non-local students admitted in 2027-2028 pay the non-subsidised composition fee: HK${fee:,} per annum ({'STEM' if stem else 'non-STEM'} faculties/schools)."}],
         adm_all({c: TH.format(n=name) for c in ("ib", "a-level", "us-hs", "cbse", "international-other")}, "course"))
    print("wrote", abbr, fee)

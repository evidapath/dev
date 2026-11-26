"""HKUST (Hong Kong): base records + ten undergraduate programmes (written 2026-11-26). THE most-international queue.

Sources, all hkust.edu.hk:
  - Fees and Scholarships (join.hkust.edu.hk): "Tuition Fee (Non-local Students) * HKD 260,000(~USD33,300) per
    academic year in 2027/28 academic year";
  - programme pages: "Modules Award <degree> Duration 4Y";
  - International Qualifications: applicants must meet the General Admissions Requirements, School/Program-specific
    Requirements and English Language Requirements; the per-qualification details are in collapsed sections not
    in the saved page text, so no grade or English requirement is stored.
No living costs read (2027/28 accommodation fee not yet announced).
  python3 -I scripts/research/gen/hk_hkust.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "The Hong Kong University of Science and Technology"
COPY = "Copyright © The Hong Kong University of Science and Technology. All rights reserved."
FEES = src("83655b37d789", "Fees and Scholarships | HKUST Undergraduate Admissions", ORG, [
    "Tuition Fee (Non-local Students) * HKD 260,000(~USD33,300) per academic year in 2027/28 academic year", COPY])
INTL = src("1fa17bf99584", "International Qualifications | HKUST Undergraduate Admissions", ORG, [
    "All applicants with international qualifications are expected to graduate from high school and be able to fulfil the General Admissions Requirements, School/Program-specific Requirements, and English Language Requirements.",
    "Deadline for Priority Round Applications"])
spec("hk-hkust", ORG, ["HKUST"], "public", "https://hkust.edu.hk", ("hk", "Hong Kong", "HKD"), ("hk-hong-kong", "Hong Kong"),
     {"main": FEES}, [("non-local", "Non-local students", "HKUST's tuition for non-local undergraduate students.", "main")])

# page, name, degree, field, award quote
P = [("f5b09b6cb88a", "Computer Science", "BEng/BSc", "Computer Science", "BEng/BSc in Computer Science"),
     ("52e2579c73a4", "Computer Engineering", "BEng", "Computer Engineering", "BEng in Computer Engineering"),
     ("d2cc3baa28c1", "Electronic Engineering", "BEng", "Electrical and Electronic Engineering", "BEng in Electronic Engineering"),
     ("97a36088c38d", "Mechanical Engineering", "BEng", "Mechanical Engineering", "BEng in Mechanical Engineering"),
     ("7b0e16386243", "Artificial Intelligence", "BEng", "Computer Science", "BEng in Artificial Intelligence"),
     ("e943f28371a2", "Civil Engineering", "BEng", "Civil Engineering", "BEng in Civil Engineering"),
     ("9c88dd7562b4", "Chemical Engineering", "BEng", "Chemical Engineering", "BEng in Chemical Engineering"),
     ("7505834f0c00", "Aerospace Engineering", "BEng", "Aerospace Engineering", "BEng in Aerospace Engineering"),
     ("9e668f8998b9", "Economics and Finance", "BSc", "Economics", "BSc in Economics and Finance"),
     ("763fcffcffc0", "Professional Accounting", "BBA", "Accounting and Finance", "BBA in Professional Accounting")]
TH = ("{n}: HKUST lists General Admissions Requirements, School/Program-specific Requirements and English Language Requirements "
      "for each international qualification on its International Qualifications page; the details weren't readable on the saved page, so no grade is shown.")
for page, name, deg, field, award in P:
    course = src(page, f"{award} | HKUST", ORG, [f"Modules Award {award} Duration 4Y", COPY])
    prog("hk-hkust", slugify(f"{deg} {name}"), {"course": course, "fees": FEES, "intl": INTL},
         {"name": name, "degree_type": deg, "field": field, "faculty": "", "duration_years": 4, "duration_source": "course", "languages": [],
          "entry_year": "2027/28", "platform": "HKUST online application (international qualifications)", "source": "course",
          "summary": f"{award}, HKUST, Hong Kong; 4 years.", "application_requirements": []},
         [{"residency": "non-local", "currency": "HKD", "tuition_annual": 260000, "academic_year": "2027/28", "source": "fees",
           "note": "Non-local students: HKD 260,000 per academic year in 2027/28 (HKUST admissions fees page). Accommodation fee for 2027/28 not yet announced."}],
         adm_all({c: TH.format(n=name) for c in ("ib", "a-level", "us-hs", "cbse", "international-other")}, "intl"))
    print("wrote", name)

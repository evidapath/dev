"""The Australian National University: base records + Bachelor of Computing (written 2026-11-26). THE queue #22.

Sources:
  - About ANU (anu.edu.au/about): name and city ("in the inner-city suburb of Acton, Canberra in the ACT");
  - programsandcourses.anu.edu.au/2027/program/bcomp: "Length 3 year full-time", "ATAR: 80 International
    Baccalaureate: 31", "Annual indicative fee for international students $57,640.00".
English requirement: linked, band not on the saved page; none stored. No living costs read.
  python3 -I scripts/research/gen/au_anu.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "The Australian National University"
spec("au-anu", ORG, ["ANU", "Australian National University"], "public", "https://www.anu.edu.au", ("au", "Australia", "AUD"), ("au-canberra", "Canberra"),
     {"main": src("e3a57abca90d", "About ANU | Australian National University", ORG,
                  ["The Australian National University (ANU) is unlike any other university", "You'll find ANU in the inner-city suburb of Acton, Canberra in the ACT."])},
     [("international", "International students", "ANU annual indicative fee for international students.", "main")])
Q = ["Bachelor of Computing - ANU", "Academic Year 2027", "Length 3 year full-time Minimum 144 Units",
     "English Language Requirements for Admission ATAR: 80 International Baccalaureate: 31",
     "Annual indicative fee for international students $57,640.00"]
prog("au-anu", "bachelor-of-computing", {"course": src("654c442ffec9", "Bachelor of Computing (BCOMP) 2027 | ANU Programs and Courses", ORG, Q)},
     {"name": "Bachelor of Computing", "degree_type": "Bachelor", "field": "Computer Science", "faculty": "ANU College of Systems and Society",
      "duration_years": 3, "duration_source": "course", "languages": [], "entry_year": "2027", "platform": "", "source": "course",
      "summary": "Bachelor of Computing, The Australian National University; 3 years full-time.", "application_requirements": []},
     [{"residency": "international", "currency": "AUD", "tuition_annual": 57640, "academic_year": "2027", "source": "course",
       "note": "Annual indicative fee for international students: $57,640 (2027, standard full-time load)."}],
     adm_all({"ib": "Bachelor of Computing: International Baccalaureate 31 (ANU admission requirement, 2027)."}, "course"))
print("wrote anu")

"""Xiamen University (THE #210): the English-medium MBBS from the "2027 Admission Guide of Xiamen University for
Undergraduate Programs" (written 2026-11-28). It is the only programme whose length the guide states on its own
("English-medium MBBS program: 6 years"); other programmes are given as "4-5 years" without a per-programme list,
and the three English-medium design programmes (joint with UCA) have no stated length, so they are not stored.
  python3 -I scripts/research/gen/cn_xmu.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog

ORG = "Xiamen University"
P = src("364983a73973", "2027 Admission Guide of Xiamen University for Undergraduate Programs | Admissions Office of Xiamen University", ORG,
        ["2027 Admission Guide of Xiamen University for Undergraduate Programs", "Length of Program: English-medium MBBS program: 6 years.",
         "(2) English-medium programs: Ø MBBS: RMB 38,000/year.",
         "Tuition fees are payable in RMB by academic year and do not include textbook fees. Tuition fees are subject to change without prior notice upon approval by price regulators.",
         "Address: 422 South Siming Road, Xiamen, Fujian Province, China, 361005"])
spec("cn-xmu", ORG, ["XMU", "Xiamen Univ."], "public", "https://www.xmu.edu.cn", ("cn", "China", "CNY"), ("cn-xiamen", "Xiamen"), {"main": P},
     [("international", "International students", "Xiamen University 2027 tuition for international undergraduates.", "main")])
prog("cn-xmu", "mbbs-english-medium", {"course": P},
     {"name": "MBBS (English-medium)", "degree_type": "MBBS", "field": "Medicine", "faculty": "", "duration_years": 6, "duration_source": "course",
      "languages": ["en"], "entry_year": "2027", "platform": "", "source": "course",
      "summary": "English-medium MBBS, Xiamen University; length of program 6 years (2027 admission guide).", "application_requirements": []},
     [{"residency": "international", "currency": "CNY", "tuition_annual": 38000, "academic_year": "2027 entry", "source": "course",
       "note": "Tuition RMB 38,000 a year (2027 guide); textbooks not included; fees may change with price-regulator approval."}], [])
print("wrote cn-xmu")

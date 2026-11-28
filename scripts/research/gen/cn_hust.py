"""Huazhong University of Science and Technology (THE #217): the English-taught undergraduate programmes in its
"2027 Application Guide for International Undergraduate Programs" (dated October 26, 2026), each with the duration
and yearly tuition in the guide's fee table (written 2026-11-28). The Chinese-taught fees are given only by
discipline group with a 4-5 year range and no list of majors, so they are not stored.
  python3 -I scripts/research/gen/cn_hust.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify

ORG = "Huazhong University of Science and Technology"
ROWS = [("Telecommunications Engineering", 4, 30000, "Electrical and Electronic Engineering", "Bachelor of Engineering"),
        ("Software Engineering", 4, 30000, "Computer Science", "Bachelor of Engineering"),
        ("Biomedical Engineering", 4, 30000, "Biomedical Engineering", "Bachelor of Engineering"),
        ("Clinical Medicine(MBBS)", 6, 40000, "Medicine", "MBBS"),
        ("Pharmacy", 4, 35000, "Pharmacy", "Bachelor")]
P = src("fa7dcdd6dbd6", "2027 Application Guide for International Undergraduate Programs | International Student Office, HUST", ORG,
        ["2027 Application Guide for International Undergraduate Programs Editor： Date：October 26, 2026",
         "English Telecommunications Engineering 4 30000 Software Engineering 4 30000 Biomedical Engineering 4 30000 Clinical Medicine(MBBS) 6 40000 Pharmacy 4 35000",
         "Tuition (CNY/Year) Language of Instruction Discipline/Major Duration Tuition",
         "Double Room: 700-900CNY/month", "Insurance Premium: 1,000 CNY/year",
         "International Student Office Huazhong University of Science and Technology",
         "Address:1037 Luoyu Road, Hongshan District, Wuhan 430074, P.R.China"])
spec("cn-hust", ORG, ["HUST", "Huazhong University of Science & Technology"], "public", "https://www.hust.edu.cn", ("cn", "China", "CNY"), ("cn-wuhan", "Wuhan"),
     {"main": P}, [("international", "International students", "HUST 2027 tuition for international undergraduates (CNY/Year).", "main")])
for n, y, fee, field, deg in ROWS:
    prog("cn-hust", slugify(f"en {n}"), {"course": P},
         {"name": f"{n} (English-taught)", "degree_type": deg, "field": field, "faculty": "", "duration_years": y, "duration_source": "course",
          "languages": ["en"], "entry_year": "2027", "platform": "", "source": "course",
          "summary": f"{n}, Huazhong University of Science and Technology (Wuhan); English-taught, {y} years (2027 guide).", "application_requirements": []},
         [{"residency": "international", "currency": "CNY", "tuition_annual": fee, "academic_year": "2027 entry", "source": "course",
           "note": f"Tuition CNY {fee:,} a year (2027 guide); insurance 1,000 CNY/year; double room 700-900 CNY/month extra."}], [])
print("wrote cn-hust")

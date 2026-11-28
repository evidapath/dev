"""Xi'an Jiaotong University (THE #209): programmes in "Xi'an Jiaotong University International Undergraduate
Programs 2027" (released 2026-10-28) whose row states a study duration (written 2026-11-28). About 40 Chinese-taught
rows show "Chinese" in the Study Duration column instead of a number; they are left out until the page is fixed.
Fees: the same page's "Fee Standard" table (RMB/Year); the 180,000 cell spans the four English-taught engineering
programmes (checked in the page's HTML table).
  python3 -I scripts/research/gen/cn_xjtu.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify

ORG = "Xi'an Jiaotong University"
FEE = ("1. Tuition fee (RMB/Year) Chinese-taught Program Science & Engineering Business\\Economics\\Humanities Arts 22,000 20,000 40,000 English-taught Program "
       "Electrical Engineering & Automation Intelligent Manufacturing Engineering Energy and Power Engineering Materials Science and Engineering MBBS BDS 180,000 60,000 80,000")
ROWS = [  # (name, years, degree, school, language, fee, field, quote)
    ("Intelligent Manufacturing Engineering", 4, "Bachelor of Engineering", "School of Mechanical Engineering", "en", 180000, "Mechanical Engineering"),
    ("Energy and Power Engineering", 4, "Bachelor of Engineering", "School of Energy and Power Engineering", "en", 180000, "Engineering"),
    ("Electrical Engineering and Automation", 4, "Bachelor of Engineering", "School of Electrical Engineering", "en", 180000, "Electrical and Electronic Engineering"),
    ("Materials Science and Engineering", 4, "Bachelor of Engineering", "School of Materials Science and Engineering", "en", 180000, "Materials Science"),
    ("MBBS", 6, "Bachelor of Medicine and Bachelor of Surgery", "Health Science Center", "en", 60000, "Medicine"),
    ("BDS", 6, "Bachelor of Dental Surgery", "Health Science Center", "en", 80000, "Dentistry"),
    ("Materials Science and Engineering", 4, "Bachelor of Engineering", "School of Materials Science and Engineering", "zh", 22000, "Materials Science"),
    ("Mechanical Engineering", 4, "Bachelor of Engineering", "School of Mechanical Engineering", "zh", 22000, "Mechanical Engineering"),
    ("Electrical Engineering and Automation", 4, "Bachelor of Engineering", "School of Electrical Engineering", "zh", 22000, "Electrical and Electronic Engineering"),
    ("Energy and Power Engineering", 4, "Bachelor of Engineering", "School of Energy and Power Engineering", "zh", 22000, "Engineering"),
    ("Environmental Engineering", 4, "Bachelor of Engineering", "School of Energy and Power Engineering", "zh", 22000, "Environmental Engineering"),
    ("Nuclear Engineering and Technology", 4, "Bachelor of Engineering", "School of Energy and Power Engineering", "zh", 22000, "Engineering"),
    ("Energy Storage Science and Engineering", 4, "Bachelor of Engineering", "School of Energy and Power Engineering", "zh", 22000, "Engineering"),
    ("New Energy Science and Engineering", 4, "Bachelor of Engineering", "School of New Energy Science and Engineering", "zh", 22000, "Engineering"),
    ("Computer Science and Technology", 4, "Bachelor of Engineering", "Faculty of Electronic and Information Engineering-School of Computer Science and Technology", "zh", 22000, "Computer Science"),
]
Q = ["Xi’an Jiaotong University International Undergraduate Programs 2027 Release time :2026-10-28", FEE,
     "English-Taught Programs Schools Programs Study Duration(Y) Degree Conferred", "No.28, Xianning West Road, Xi'an, Shaanxi, 710049, P.R. China",
     "English-taught program: Submit English proficiency certificate. IELTS 6.0 or TOEFL 80 (or above)", "The accommodation fee varies from RMB 8000 to 19000 every year.",
     "Chinese-taught program: Submit Chinese proficiency certificate. Proficiency must be above HSK 4 or equivalent."]
Q += sorted({f"{n} {y} {d}" for n, y, d, *_ in ROWS})
P = src("d4730794fd93", "Xi'an Jiaotong University International Undergraduate Programs 2027 | School of International Education", ORG, Q)
spec("cn-xjtu", ORG, ["XJTU", "Xian Jiaotong University"], "public", "https://www.xjtu.edu.cn", ("cn", "China", "CNY"), ("cn-xian", "Xi'an"), {"main": P},
     [("international", "International students", "XJTU 2027 tuition for international undergraduates (RMB/Year).", "main")])
for n, y, d, sch, lang, fee, field in ROWS:
    tl = "English-taught" if lang == "en" else "Chinese-taught"
    prog("cn-xjtu", slugify(f"{lang} {n}"), {"course": P},
         {"name": f"{n} ({tl})", "degree_type": d, "field": field, "faculty": sch, "duration_years": y, "duration_source": "course",
          "languages": [lang], "entry_year": "2027", "platform": "", "source": "course",
          "summary": f"{n}, {sch}, Xi'an Jiaotong University; {tl}, {y} years, {d}.", "application_requirements": []},
         [{"residency": "international", "currency": "CNY", "tuition_annual": fee, "academic_year": "2027 entry", "source": "course",
           "note": f"{tl} tuition RMB {fee:,} a year (2027 programmes page); accommodation RMB 8000 to 19000 a year extra."}], [])
print("wrote cn-xjtu")

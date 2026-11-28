"""Fudan University (THE #184): Undergraduate International Program in Economics (UIPE), its English-taught
bachelor's with a stated length (written 2026-11-28). The Chinese-taught programmes are left out: the 2027
brochure gives only a fee range (23,000-42,000 RMB/Year) with per-programme fees in a separate document.
  python3 -I scripts/research/gen/cn_fudan.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog

ORG = "Fudan University"
CU = src("2af0cafbe5dc", "Curriculum - Undergraduate International Program in Economics | Fudan University", ORG,
         ["Undergraduate International Program in Economics (UIPE) is an English-taught program with a duration of 4 years",
          "Bachelor in Economics will be granted by Fudan University to those who meet the requirement",
          "579 Guoquan Road, Shanghai, 200433, China © School of Economics , Fudan University"])
TU = src("221bd1f9d545", "Tuition and Expenses - Undergraduate International Program in Economics | Fudan University", ORG,
         ["For Degree Students of UIPE and UIPI (Undergraduate International Program in International Economy and Trade) Application Fee: RMB 800 Tuition: RMB 100,000/year (starting with the intake of 2027)"])
spec("cn-fudan", ORG, ["Fudan"], "public", "https://www.fudan.edu.cn", ("cn", "China", "CNY"), ("cn-shanghai", "Shanghai"), {"main": CU, "fees": TU},
     [("international", "International students", "UIPE tuition for degree students.", "fees")])
prog("cn-fudan", "bachelor-economics-uipe", {"course": CU, "fees": TU},
     {"name": "Economics (Undergraduate International Program in Economics, UIPE)", "degree_type": "Bachelor in Economics", "field": "Economics",
      "faculty": "School of Economics", "duration_years": 4, "duration_source": "course", "languages": ["en"], "entry_year": "2027", "platform": "", "source": "course",
      "summary": "Undergraduate International Program in Economics (UIPE), School of Economics, Fudan University (Shanghai); English-taught, 4 years.",
      "application_requirements": []},
     [{"residency": "international", "currency": "CNY", "tuition_annual": 100000, "academic_year": "2027 intake", "source": "fees",
       "note": "Tuition RMB 100,000 a year (starting with the intake of 2027); application fee RMB 800."}], [])
print("wrote cn-fudan")

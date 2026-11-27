"""National Taiwan University (THE #135): its English-taught undergraduate programme for international students,
the International College's Global Undergraduate Program in Semiconductors (written 2026-11-27). NTU's other
bachelor's programmes are taught in Mandarin and are not added here. No grade threshold published.
  python3 -I scripts/research/gen/tw_ntu.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog

ORG = "National Taiwan University"
IC = src("0bc9271fb228", "Admissions - International College, NTU", ORG,
         ["The Global Undergraduate Program in Semiconductors only recruits international students only.", "applying to National Taiwan University's International College (NTUIC)",
          "7F, Zonghe Lecture Building, No.1, Sec.4 Roosevelt Rd., Taipei 10617, Taiwan"])
TF = src("aac78d3d7b06", "Tuition Fees | NTU Office of International Affairs", ORG,
         ["Tuition is billed each semester (one academic year consists of two semesters).",
          "International College Global Undergraduate Program in Semiconductors 60,000 2,000"])
GL = src("ntu-tw-2027", "National Taiwan University (NTU) 2027/2028 September Entry Admission Guidelines for International Degree Students", ORG,
         ["National Taiwan University (NTU) 2027/2028 September Entry Admission Guidelines for International Degree Students",
          "A. Undergraduate programs shall be completed within 4 to 6 years."])
spec("tw-ntu", ORG, ["NTU", "National Taiwan Univ."], "public", "https://www.ntu.edu.tw", ("tw", "Taiwan", "TWD"), ("tw-taipei", "Taipei"),
     {"main": IC, "guide": GL, "fees": TF}, [("international", "International students", "NTU tuition and fees per semester for international students.", "fees")])
prog("tw-ntu", "global-undergraduate-program-in-semiconductors", {"course": IC, "fees": TF, "guide": GL},
     {"name": "Global Undergraduate Program in Semiconductors", "degree_type": "Bachelor", "field": "Electrical and Electronic Engineering",
      "faculty": "International College", "duration_years": 4, "duration_source": "guide", "languages": ["en"], "entry_year": "2027/2028",
      "platform": "", "source": "course",
      "summary": "Global Undergraduate Program in Semiconductors, International College, National Taiwan University (Taipei); for international students only.",
      "application_requirements": []},
     [{"residency": "international", "currency": "TWD", "tuition_per_term": 60000, "terms_per_year": 2,
       "terms_evidence": ["Tuition is billed each semester", "(one academic year consists of two semesters)"],
       "academic_year": "", "source": "fees", "note": "International students: TWD 60,000 per semester (tuition and fees); the page is for reference only."}], [])
print("wrote tw-ntu")

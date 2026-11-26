"""KTH Royal Institute of Technology: base records + BSc Information and Communication Technology (written 2026-11-26). THE queue #25.

KTH's only English-taught bachelor's programme. Sources (kth.se):
  - programme page: "This is a three year programme (180 ECTS credits) given in English", School of Electrical
    Engineering and Computer Science, address "SE-100 44 Stockholm";
  - fee page (last changed Feb 17, 2025): "The full programme tuition fee for non-EU/EEA/Swiss citizens ... is
    SEK 453,000"; per year = 453,000 / 3 (our calculation); EU/EEA/Swiss citizens pay no fees;
  - entry requirements page: IB Diploma with 24 points + passing grades in English, Mathematics, Physics (minimum
    to be eligible); "In 2024, 10% of eligible applicants were admitted"; predicted grades not accepted;
    IELTS 6.5 (no section below 5.5).
  python3 -I scripts/research/gen/se_kth.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "KTH Royal Institute of Technology"
P = src("3624de9c135e", "BSc Information and Communication Technology | KTH", ORG,
        ["This is a three year programme (180 ECTS credits) given in English. Graduates are awarded the degree of Bachelor of Science.",
         "The programme is given by the School of Electrical Engineering and Computer Science (at KTH).",
         "KTH Royal Institute of Technology SE-100 44 Stockholm Sweden"])
F = src("8b8d4d29e54f", "Application and tuition fees for bachelor's programmes | KTH", ORG,
        ["The full programme tuition fee for non-EU/EEA/Swiss citizens studying the bachelor's programme in Information and Communication Technology is SEK 453,000.",
         "Citizens of an EU/EEA country or Switzerland are not required to pay application and tuition fees.",
         "The tuition fee is charged in advance for each semester and you pay by bank transfer.",
         "Last changed : Feb 17, 2025"])
R = src("1a49190f46b2", "Entry requirements for Information and Communication Technology | KTH", ORG,
        ["Admission is highly competitive, with far fewer places than qualified applicants. In 2024, 10% of eligible applicants were admitted.",
         "Conditional admission for applicants in their final year of upper secondary school is not possible and predicted grades are not accepted.",
         "International Baccalaureate The requirements are an International Baccalaureate Diploma with 24 points and passing grades in: English A HL, English A SL, English B HL or English B SL corresponds to English 6 in Sweden Mathematics: analysis and approaches SL or Mathematics: applications and interpretation HL (from 2021 and onwards) corresponds to Mathematics 4 in Sweden Physics, SL or HL corresponds to Physics 2 in Sweden",
         "United Kingdom and international education according to the British system The requirements are an upper-secondary education giving access to university studies in the United Kingdom including a minimum grade C in IGCSE/GCSE/GCE English as well as the following: Mathematics GCE AS level or GCE A level (grade E or above) level corresponds to Mathematics 4 in Sweden GCE A/AS level Physics corresponds to Physics 2 in Sweden",
         "You can meet the requirement with an English test, for example an IELTS total score of 6.5 with no section below 5.5"])
spec("se-kth", ORG, ["KTH"], "public", "https://www.kth.se", ("se", "Sweden", "SEK"), ("se-stockholm", "Stockholm"),
     {"main": P, "fees": F},
     [("non-eu", "Non-EU/EEA/Swiss citizens", "Programme tuition fee for citizens of countries outside the EU/EEA and Switzerland.", "fees")])
LEAD = " Admission is highly competitive (10% of eligible applicants admitted in 2024) and predicted grades are not accepted, so you apply with final results."
ENG = {"test_name": "IELTS (or equivalent)", "source": "req", "min_score": "IELTS 6.5 overall, no section below 5.5 (English 6 level).",
       "notes": "Can also be met through some upper secondary or university studies, depending on the country."}
prog("se-kth", "bsc-information-and-communication-technology", {"course": P, "fees": F, "req": R},
     {"name": "Information and Communication Technology", "degree_type": "BSc", "field": "Computer Science", "faculty": "School of Electrical Engineering and Computer Science",
      "duration_years": 3, "duration_source": "course", "languages": ["en"], "entry_year": "", "platform": "University Admissions", "source": "course",
      "summary": "Bachelor's programme in Information and Communication Technology, KTH; three years (180 ECTS credits), taught in English.", "application_requirements": []},
     [{"residency": "non-eu", "currency": "SEK", "tuition_formula": "453000/3", "academic_year": "", "source": "fees",
       "note": "Full programme fee SEK 453,000 for non-EU/EEA/Swiss citizens, about SEK 151,000 a year over three years (our calculation); charged each semester. Fee page last changed Feb 17, 2025."}],
     adm_all({"ib": "ICT: the minimum to be eligible is an International Baccalaureate Diploma with a total of 24 Diploma points and passing grades in English, Mathematics (analysis and approaches SL or applications and interpretation HL) and Physics (SL or HL); this is not an admission cut-off." + LEAD,
              "a-level": "ICT: upper-secondary education giving access to UK universities, with at least grade C in IGCSE/GCSE English, Mathematics at GCE AS or A level (grade E or above) and GCE A/AS level Physics; this is the minimum to be eligible, not an admission cut-off." + LEAD},
             "req", english=ENG))
print("wrote kth")

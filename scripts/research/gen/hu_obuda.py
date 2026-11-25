"""Obuda University (Óbuda University), Budapest: base records + six English-taught BSc (written 2026-11-25).

Sources, all uni-obuda.hu:
  - Bachelor's Programs: each programme block "... Credits 210 Study Option Full-time Study Type In-person
    at OU campus Language English Duration 7 semesters Location Budapest, <faculty>";
  - Tuition fees: per programme, "EU/EEA" and "Non-EEA" EUR per semester (the year isn't stated on the page).
Held: Business Administration and Management, Commerce and Marketing (their blocks share a specialisation
name, so the page block can't be tied to one programme). Entry requirements not read. No living costs.
  python3 -I scripts/research/gen/hu_obuda.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "Obuda University"
PROGS = "0b20bbcdad94"
FEES = "5504bfbb9d75"
# name, field, programme-block quote, fee row quote, non-EEA fee
P = [("Computer Science Engineering", "Computer Engineering",
      "IT Security Credits 210 Study Option Full-time Study Type In-person at OU campus Language English Duration 7 semesters Location Budapest, John von Neumann Faculty of Informatics",
      "Computer Science Engineering Cloud Service Technologies 2,000 EUR 3,200 EUR", 3200),
     ("Electrical Engineering", "Electrical and Electronic Engineering",
      "Applied Electrical Engineering Credits 210 Study Option Full-time Study Type In-person at OU campus Language English Duration 7 semesters Location Budapest, Kandó Kálmán Faculty of Electrical Engineering",
      "Electrical Engineering Communication engineering 2,000 EUR 3,000 EUR", 3000),
     ("Mechatronics Engineering", "Mechatronic Engineering",
      "Robotics Credits 210 Study Option Full-time Study Type In-person at OU campus Language English Duration 7 semesters Location Budapest, Bánki Donát Faculty of Mechanical and Safety Engineering",
      "Mechatronical Engineering Intelligent Control Systems 2,000 EUR 2,900 EUR", 2900),
     ("Engineering Management", "Business",
      "Corporate Management Credits 210 Study Option Full-time Study Type In-person at OU campus Language English Duration 7 semesters Location Budapest, Keleti Károly Faculty of Business and Management",
      "Engineering Management Projectmanagement 2,000 EUR 2,700 EUR", 2700),
     ("Environmental Engineering", "Environmental Science",
      "Water Management Credits 210 Study Option Full-time Study Type In-person at OU campus Language English Duration 7 semesters Location Budapest, Rejtő Sándor Faculty of Light Industry and Environmental Engineering",
      "Environmental Engineering Sustainable Energy Management 2,000 EUR 2,900 EUR", 2900),
     ("Industrial Engineering", "Engineering",
      "Packaging Credits 210 Study Option Full-time Study Type In-person at OU campus Language English Duration 7 semesters Location Budapest, Rejtő Sándor Faculty of Light Industry",
      "Industrial Engineering Product design (Interior-textile, fashion-accessories) 2,000 EUR 2,900 EUR", 2900)]

FEE_HEAD = ["Level Program Specialisation(s) Tuition Fee/semester EU/EEA Non-EEA BSc"]
spec("hu-obuda", ORG, ["Óbuda University", "OU"], "public", "https://uni-obuda.hu", ("hu", "Hungary", "HUF"), ("hu-budapest", "Budapest"),
     {"main": src(PROGS, "Bachelor's Programs | Obuda University", ORG, ["Obuda University Venture Capital", P[0][2]]),
      "fees": src(FEES, "Tuition fees | Obuda University", ORG, FEE_HEAD)},
     [("non-eea", "Non-EEA students", "Obuda University's per-semester tuition for non-EEA students, by programme.", "fees")])

TH = "{name}: entry requirements aren't on the pages read; see Obuda University's admission pages."
for name, field, block, row, fee in P:
    prog("hu-obuda", f"bsc-{slugify(name)}",
         {"course": src(PROGS, "Bachelor's Programs | Obuda University", ORG, [block]),
          "fees": src(FEES, "Tuition fees | Obuda University", ORG, FEE_HEAD + [row])},
         {"name": name, "degree_type": "BSc", "field": field, "faculty": "", "duration_years": 3.5, "duration_source": "course", "languages": ["en"],
          "entry_year": "Fee page (year not stated)", "platform": "Obuda University online application", "source": "course",
          "summary": f"{name} (BSc), Obuda University, Budapest; taught in English.", "application_requirements": []},
         [{"residency": "non-eea", "currency": "EUR", "tuition_per_semester": fee, "semesters_quote": "Duration 7 semesters", "semesters_source": "course",
           "academic_year": "Fee page (year not stated)", "source": "fees",
           "note": f"EUR {fee:,} per semester for non-EEA students (Obuda University's fee table; the year isn't stated). Yearly figure our calculation."}],
         adm_all({c: TH.format(name=name) for c in ("ib", "a-level", "us-hs", "cbse", "international-other")}, "course"))
    print("wrote", name)

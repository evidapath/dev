"""Wageningen University & Research: base records + BSc Data Science for Global Challenges (written 2026-11-26). THE queue #20.

Sources (wur.nl):
  - programme page: "Full-time 3 Years English & Dutch" (dual-language track; English track chosen for the whole
    programme), subjects "Mathematics and (Biology or Chemistry or Physics)";
  - bachelor tuition page: non-EU €18,300 (2026-2027) and €18.840 (2027-2028); European €2,694 / €2,771;
  - study-costs page: 2027/2028 non-EU €18,800.00 "(estimate)", "The definite amount of tuition fees of 2027-2028
    will be determined in the end of 2026." The two pages differ for 2027-2028, so the stored fee is the agreed
    2026-2027 figure and the note gives both 2027-2028 figures;
  - Diploma Eligibility List, 2026 intake (PDF): IB DP row and the England A-level rule.
Living costs (€41,400 for 3 years, IND amount) not stored: only a three-year total is published.
  python3 -I scripts/research/gen/nl_wur.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "Wageningen University & Research"
P = src("848bc2d60b8b", "Bachelor's in Data Science for Global Challenges | WUR", ORG,
        ["Bachelor’s in Data Science for Global Challenges What to expect Facts & figures Technology, Climate, Nature Full-time 3 Years English & Dutch Wageningen",
         "This programme has a dual language track. You can either choose the English or the Dutch track for the whole programme depending on your preference.",
         "You are eligible for various master's programmes at Wageningen University & Research",
         "completed a relevant high school diploma in which you studied Mathematics and (Biology or Chemistry or Physics). You should be proficient in English."])
F = src("e56f658cd494", "Tuition fees and study finances bachelor | WUR", ORG,
        ["Are you a non-EU student**? Then your tuition fee for the academic year 2026-2027 is € 18,300 and € 18.840 for 2027-2028.",
         "Are you a European student*? Your tuition fee for the 2026-2027 academic year is € 2,694 in total.",
         "For the 2027-2028 academic year, the tuition fee will be € 2,771.",
         "*Students with a nationality from NL/EEA/SME¹ countries and Ukraine are considered European students."])
SC = src("0fde3b1b4572", "Study expenses bachelor's: tuiton fees and other costs | WUR", ORG,
         ["Tuition Fee 2027/2028 €2,775.00 (estimate) €18,800.00 (estimate)",
          "The definite amount of tuition fees of 2027-2028 will be determined in the end of 2026."])
E = src("wur-elig-2026", "Diploma Eligibility List Wageningen University 2026 intake", ORG,
        ["Diploma Eligibility List Wageningen University 2026 intake",
         "Appendix 2 - International Baccalaureate DP Diploma",
         "Data Science for Global Challenges* Mathematics A&I (HL)/Mathematics A&A (SL/HL) + Chemistry (SL/HL)/Biology (SL/HL)/Physics (SL/HL)",
         "*These BSc programmes are English taught BSc programmes",
         "General Certificate of Secondary Education (GCSE) in at least 3 subjects with grades A*-C or 9-4 + General Certificate of Education Advanced Level (GCE A-level) in at least 3 academic subjects with grades A*-C or 9-4 (6 different subjects in total)"])
spec("nl-wur", ORG, ["Wageningen University", "WUR"], "public", "https://www.wur.nl", ("nl", "Netherlands", "EUR"), ("nl-wageningen", "Wageningen"),
     {"main": P, "fees": F},
     [("non-eu", "Non-EU students", "Institutional tuition fee for students without an NL/EEA/SME nationality (Ukraine excepted).", "fees"),
      ("eu-eea", "EU/EEA students", "Statutory tuition fee for European students (NL/EEA/SME nationals and Ukraine).", "fees")])
prog("nl-wur", "bsc-data-science-for-global-challenges", {"course": P, "fees": F, "costs": SC, "elig": E},
     {"name": "Data Science for Global Challenges", "degree_type": "BSc", "field": "Data Science", "faculty": "",
      "duration_years": 3, "duration_source": "course", "languages": ["en", "nl"], "entry_year": "2026-2027", "platform": "Studielink", "source": "course",
      "summary": "BSc Data Science for Global Challenges, Wageningen University & Research; full-time, 3 years, English or Dutch track.", "application_requirements": []},
     [{"residency": "non-eu", "currency": "EUR", "tuition_annual": 18300, "academic_year": "2026-2027", "source": ["fees", "costs"],
       "note": "Non-EU students: €18,300 (2026-2027). For 2027-2028 the tuition page says €18,840 and the study-costs page estimates €18,800; the definite amount is set at the end of 2026."},
      {"residency": "eu-eea", "currency": "EUR", "tuition_annual": 2694, "academic_year": "2026-2027", "source": "fees",
       "note": "European students: €2,694 (2026-2027); €2,771 for 2027-2028."}],
     adm_all({"ib": "Data Science for Global Challenges: IB DP Diploma with Mathematics A&I (HL) or Mathematics A&A (SL/HL), plus Chemistry, Biology or Physics (SL/HL) (2026 intake list). No minimum points total is published.",
              "a-level": "Data Science for Global Challenges: at least 3 GCSEs (A*-C or 9-4) and at least 3 academic A-levels (A*-C), 6 different subjects in total (2026 intake list), having studied Mathematics and Biology, Chemistry or Physics."},
             "elig"))
print("wrote wur")

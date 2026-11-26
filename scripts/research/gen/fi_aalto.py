"""Aalto University: base records + Data Science (Bachelor of Science (Technology)) (written 2026-11-26). THE queue #53.

Sources (aalto.fi):
  - Data Science study option page: "Language of instruction: English Duration: 3+2 years, full-time", "Credits:
    180+120 ECTS", "Organising school: School of Science", "For non-EU/EEA citizens, €12000/y (Bachelor’s studies)",
    "The tuition fee for this programme is 12 000 euros per academic year." EU/EEA/Swiss citizens pay none;
  - IB applicants page: admission round B, application period 7 to 22 January 2027, predicted grades accepted with
    a conditional offer (revocable if final scores are lower);
  - Certificate of required funds, March 2026 (PDF): address "Visiting address Otakaari 1 Espoo, Finland".
The admission-criteria page for the Science and Technology programme returned "Access denied" (403): no IB points
threshold or English test scores stored. Living costs in that PDF extract out of order; not stored.
  python3 -I scripts/research/gen/fi_aalto.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "Aalto University"
DS = src("ca75bf814c98", "Data Science, Bachelor of Science and Master of Science (Technology) | Aalto University", ORG,
         ["Data Science, Bachelor of Science and Master of Science (Technology) | Aalto University",
          "Application period: 7 Jan 2027 – 22 Jan 2027 Language of instruction: English Duration: 3+2 years, full-time",
          "Credits: 180+120 ECTS Organising school: School of Science Tuition fees: For non-EU/EEA citizens, €12000/y (Bachelor’s studies) + €17000/y (M",
          "The tuition fee for this programme is 12 000 euros per academic year. Citizens of European Union (EU), the European Economic Area (EEA) or Switzerland do not pay tuition"])
IB = src("480803617d04", "English-taught bachelor's programmes - I am applying with an IB Diploma | Aalto University", ORG,
         ["If you apply on the basis of your International Baccalaureate (IB) diploma, you apply to the English-taught bachelor’s programmes at Aalto University in the admission round B .",
          "If you are accepted based on IB predicted grades, the admission is conditional until Aalto University Admission Services receives your official final grades from the IBO.",
          "If the scores calculated based on the final grades are lower than the scores calculated based on the predicted grades, the admission offer may be revoked."])
FUNDS = src("aalto-funds-2026", "Certificate of required funds for Aalto University students (March 2026)", ORG,
            ["Certificate of required funds for Aalto University students", "Visiting address Otakaari 1 Espoo, Finland"])
spec("fi-aalto", ORG, ["Aalto"], "public", "https://www.aalto.fi", ("fi", "Finland", "EUR"), ("fi-espoo", "Espoo"),
     {"main": FUNDS, "ds": DS},
     [("non-eu", "Non-EU/EEA citizens", "Tuition fee for citizens of countries outside the EU, EEA and Switzerland.", "ds")])
prog("fi-aalto", "bsc-tech-data-science", {"course": DS, "ib": IB},
     {"name": "Data Science", "degree_type": "Bachelor of Science (Technology)", "field": "Data Science", "faculty": "School of Science",
      "duration_years": 3, "duration_source": "course", "languages": ["en"], "entry_year": "2027", "platform": "", "source": "course",
      "summary": "Data Science, a major of the Aalto Bachelor's Programme in Science and Technology; Bachelor of Science (Technology) in 3 years (180 ECTS), with a 2-year master's to follow; taught in English.",
      "application_requirements": []},
     [{"residency": "non-eu", "currency": "EUR", "tuition_annual": 12000, "academic_year": "2027 entry", "source": "course",
       "note": "Non-EU/EEA citizens: €12,000 a year for the bachelor's studies (€17,000 a year for the master's studies)."}],
     adm_all({"ib": "Data Science: apply in admission round B with the IB Diploma; selection is on IB grades, and no minimum points total is published. Offers made on predicted grades are conditional and may be revoked if final scores are lower."}, "ib"))
print("wrote aalto")

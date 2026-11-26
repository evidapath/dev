"""Leiden University: base records + BSc Data Science and Artificial Intelligence (written 2026-11-26). THE queue #47.

Leiden's BSc Computer Science is taught in Dutch (its English page says so), so the English-taught
Data Science & Artificial Intelligence bachelor is added instead. Sources (universiteitleiden.nl):
  - programme page: "Language English Location Leiden Programme code 50300 ... Duration 3 years";
  - its tuition-fee page: "Tuition fee: €19,200,- (academic year 2027-2028)" (non-EEA), statutory €2771,-;
  - its admission page: vwo-equivalent diploma with comparable Mathematics (or OMPT-D 60%); IELTS 6.0 overall
    and 6.0 per component; TOEFL iBT 4.5 (or 80 / 20 before 21 January 2026).
The 'Specific diploma requirements for science programmes' PDF returned an "Access Blocked" page; not used.
  python3 -I scripts/research/gen/nl_leiden.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "Leiden University"
P = src("4653334fb7df", "Data Science and Artificial Intelligence (BSc) - Leiden University", ORG,
        ["Data Science and Artificial Intelligence (BSc) - Leiden University",
         "Facts & Figures Degree Bachelor of Science Language English Location Leiden Programme code 50300 Start September Mode of study Fulltime Duration 3 years",
         "The programme is organized by LIACS, the Leiden Institute of Advanced Computer Science."])
F = src("e3e9ed8a3121", "Tuition fees - Data Science and Artificial Intelligence (BSc) - Leiden University", ORG,
        ["The statutory tuition fee of the academic year 2027-2028 for first-year bachelor's students is: €2771,-.",
         "If you do not qualify for Dutch student finance and you are not a national of an EEA country, Suriname or Switzerland you can find the amount of tuition fee you are required to pay for your study programme here below.",
         "Tuition fee: €19,200,- (academic year 2027-2028)"])
A = src("7c93a4db2d12", "Admission requirements - Data Science and Artificial Intelligence (BSc) - Leiden University", ORG,
        ["International students An equivalent of a Dutch pre-university education (VWO) diploma with a comparable level of Mathematics.",
         "If you do not have this level, the equivalent of Dutch VWO Mathematics B can be acquired through: Having obtained at least 60% for the Online Mathematics Placement Test (OMPT-D), or,",
         "have obtained an International Baccalaureate™ Diploma (IB DP) taught in English or with English A HL.",
         "IELTS - Academic modules only, on paper or on computer. Minimum score of 6.0 overall and 6.0 for each separate component.",
         "TOEFL Internet Based. Minimum score of 4.5 overall, with at least 4.5 for each separate component score (or 80 overall and 20 for each separate component if taken before 21 January 2026)."])
spec("nl-leiden", ORG, ["Universiteit Leiden"], "public", "https://www.universiteitleiden.nl", ("nl", "Netherlands", "EUR"), ("nl-leiden", "Leiden"),
     {"main": P, "fees": F},
     [("non-eea", "Non-EU/EEA students", "Institutional tuition fee for students who are not nationals of an EEA country, Suriname or Switzerland.", "fees"),
      ("eu-eea", "EU/EEA students", "Statutory tuition fee (EEA, Suriname and Swiss nationals).", "fees")])
ENG = {"test_name": "IELTS Academic (or TOEFL iBT)", "source": "adm",
       "min_score": "IELTS Academic 6.0 overall and 6.0 for each component; TOEFL iBT 4.5 overall and 4.5 per component (80 overall, 20 per component if taken before 21 January 2026).",
       "notes": "Not needed with an IB Diploma taught in English or with English A HL."}
prog("nl-leiden", "bsc-data-science-and-artificial-intelligence", {"course": P, "fees": F, "adm": A},
     {"name": "Data Science and Artificial Intelligence", "degree_type": "BSc", "field": "Computer Science", "faculty": "",
      "duration_years": 3, "duration_source": "course", "languages": ["en"], "entry_year": "2027-2028", "platform": "Studielink", "source": "course",
      "summary": "BSc Data Science and Artificial Intelligence, Leiden University (organised by LIACS); 3 years, taught in English.", "application_requirements": []},
     [{"residency": "non-eea", "currency": "EUR", "tuition_annual": 19200, "academic_year": "2027-2028", "source": "fees",
       "note": "Institutional fee for non-EEA students: €19,200 (2027-2028)."},
      {"residency": "eu-eea", "currency": "EUR", "tuition_annual": 2771, "academic_year": "2027-2028", "source": "fees",
       "note": "Statutory fee for first-year bachelor's students: €2,771 (2027-2028)."}],
     adm_all({"international-other": "Data Science and AI: a diploma equivalent to Dutch pre-university education (VWO) with a comparable level of Mathematics; without it, at least 60% on the Online Mathematics Placement Test (OMPT-D). No minimum grade or points total is published."},
             "adm", english=ENG))
print("wrote leiden")

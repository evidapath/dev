"""University of Groningen: base records + BSc Computing Science (written 2026-11-26). THE queue #42.

Source: rug.nl/bachelors/computing-science: "Duration 36 months (180 EC)", "Language of instruction English",
"Faculty Science and Engineering", tuition table (non-EU/EEA €19,800 in 2026-2027 and 2027-2028; EU/EEA €2,771
in 2027-2028), entry rule (vwo-equivalent secondary education + sufficient Mathematics, judged by the
Admissions Board). No points threshold is published, so the admission row is the general international one.
English test scores are on a faculty page that returned 404; none stored. No living costs read.
  python3 -I scripts/research/gen/nl_rug.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "University of Groningen"
FEES = "Tuition fees Nationality Year Fee Programme form EU/EEA 2026-2027 € 2694 full-time non-EU/EEA 2026-2027 € 19800 full-time EU/EEA 2027-2028 € 2771 full-time non-EU/EEA 2027-2028 € 19800 full-time"
C = src("b770185796e7", "Computing Science | Bachelor's degree programmes | University of Groningen", ORG,
        ["Computing Science | Bachelor's degree programmes | University of Groningen",
         "Degree BSc in Computing Science Course type Bachelor Duration 36 months (180 EC) Programme code 56978 Language of instruction English Start September Faculty Science and Engineering",
         FEES,
         "Secondary education equivalent to Dutch pre-university (vwo) is required.",
         "Sufficient background knowledge in Mathematics is required. The Admissions Board will determine whether your background knowledge in this subject is sufficient to start the Bachelor's degree programme of your choice.",
         "non-EU/EEA students 01 May 2027 01 September 2027"])
spec("nl-rug", ORG, ["Rijksuniversiteit Groningen", "RUG"], "public", "https://www.rug.nl", ("nl", "Netherlands", "EUR"), ("nl-groningen", "Groningen"),
     {"main": C},
     [("non-eu", "Non-EU/EEA students", "Institutional tuition fee for students without EU/EEA nationality.", "main"),
      ("eu-eea", "EU/EEA students", "Statutory tuition fee for EU/EEA students.", "main")])
prog("nl-rug", "bsc-computing-science", {"course": C},
     {"name": "Computing Science", "degree_type": "BSc", "field": "Computer Science", "faculty": "Faculty of Science and Engineering",
      "duration_years": 3, "duration_source": "course", "languages": ["en"], "entry_year": "2027-2028", "platform": "Studielink", "source": "course",
      "summary": "BSc Computing Science, University of Groningen; 36 months (180 EC), taught in English.", "application_requirements": []},
     [{"residency": "non-eu", "currency": "EUR", "tuition_annual": 19800, "academic_year": "2027-2028", "source": "course",
       "note": "Non-EU/EEA students: €19,800 a year (2027-2028; also €19,800 in 2026-2027)."},
      {"residency": "eu-eea", "currency": "EUR", "tuition_annual": 2771, "academic_year": "2027-2028", "source": "course",
       "note": "EU/EEA students: €2,771 (2027-2028)."}],
     adm_all({"international-other": "Computing Science: secondary education equivalent to Dutch pre-university (vwo), with sufficient background knowledge in Mathematics (the Admissions Board decides). No minimum grade or points total is published."}, "course"))
print("wrote rug")

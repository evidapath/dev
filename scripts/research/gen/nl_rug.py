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
from newuni import src, spec, prog, adm_all, slugify, PAGES

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

# All other English-taught bachelor's from rug.nl/bachelors/in-english (added 2026-11-27). Each page has the
# same "Facts & Figures" block and tuition table. The three Economics and Business Economics track pages share
# programme code 50950 with the main page, so only the main page is added; Philosophy of a Specific Discipline
# is not a standalone degree. The admission row is stored only where the page states a subject requirement.
import re
FIELD = {"American Studies": "Humanities", "Applied Mathematics": "Mathematics", "Applied Physics": "Physics", "Art History": "Humanities",
         "Artificial Intelligence": "Artificial Intelligence", "Arts, Culture and Media": "Media and Communication", "Astronomy": "Physics",
         "Biology": "Biology", "Biomedical Engineering": "Engineering", "Chemical Engineering": "Chemical Engineering", "Chemistry": "Chemistry",
         "Communication and Information Studies": "Media and Communication", "Data Science & Society": "Data Science",
         "Econometrics and Operations Research": "Econometrics", "Economics and Business Economics": "Economics",
         "English Language and Culture": "Humanities", "European Languages, Cultures and Politics": "Humanities",
         "Global Politics & Sustainability": "Politics", "History": "History", "Human Geography and Planning": "Geography",
         "Industrial Engineering and Management": "Engineering", "Information Science": "Information Science",
         "International and European Law": "Law", "International Business": "Business",
         "International Relations and International Organization": "Politics", "Liberal Arts and Sciences": "Liberal Arts",
         "Life Science and Technology": "Biology", "Mathematics": "Mathematics", "Media Studies": "Media and Communication",
         "Physics": "Physics", "Psychology (EN)": "Psychology", "Religious Studies": "Humanities", "Spatial Planning and Design": "Geography"}
LANG = {"English": ["en"], "English, Dutch": ["en", "nl"], "Dutch, English": ["nl", "en"]}
IDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rug_pages.txt")
for line in open(IDS):
    pid = line.split()[0]
    t = re.sub(r"\s+", " ", open(PAGES / f"{pid}.txt", errors="replace").read())
    title = t.split(" | ")[0].strip()
    if title not in FIELD:
        continue
    facts = re.search(r"Degree (\S+) in (.+?) Course type Bachelor Duration 36 months \(180 EC\) Programme code (\d+) Language of instruction (English, Dutch|Dutch, English|English) Start ([A-Za-z, ]+?) Faculty (.+?) Apply now", t)
    fees = re.search(r"Tuition fees Nationality Year Fee Programme form EU/EEA 2026-2027 € \d+ full-time non-EU/EEA 2026-2027 € \d+ full-time EU/EEA 2027-2028 € (\d+) full-time non-EU/EEA 2027-2028 € (\d+) full-time", t)
    deg, pname, code, lang, start, fac = facts.groups()
    eu, non = int(fees.group(1)), int(fees.group(2))
    subj = re.search(r"additional subject ((?:Sufficient background knowledge in [A-Za-z, ]+ is required\. The Admissions Board will determine whether your background knowledge in (?:this subject|these subjects) is sufficient)|(?:Mathematics should have been passed as a [a-z/ ]+ level(?: \(advanced\))? subject in your secondary school education\.))", t)
    lw = "Why study this programme in Leeuwarden?" in t
    qs = [f"{title} | Bachelor's degree programmes | University of Groningen" if f"{title} | Bachelor's degree programmes | University of Groningen" in t else title,
          facts.group(0).replace(" Apply now", ""), fees.group(0)] + ([subj.group(1)] if subj else []) + (["Why study this programme in Leeuwarden?"] if lw else [])
    S = src(pid, f"{title} | Bachelor's degree programmes | University of Groningen", ORG, qs)
    name = pname.replace(" (EN)", "")
    where = " at Campus Fryslân in Leeuwarden" if lw else ""
    prog("nl-rug", "b-" + slugify(name), {"course": S},
         {"name": name, "degree_type": deg, "field": FIELD[title], "faculty": f"Faculty {fac}" if not fac.startswith(("Campus", "University College")) else fac,
          "duration_years": 3, "duration_source": "course", "languages": LANG[lang], "entry_year": "2027-2028", "platform": "Studielink", "source": "course",
          "summary": f"{deg} {name}, University of Groningen{where}; 36 months (180 EC), language of instruction {lang}.", "application_requirements": []},
         [{"residency": "non-eu", "currency": "EUR", "tuition_annual": non, "academic_year": "2027-2028", "source": "course",
           "note": f"Non-EU/EEA students: €{non:,} a year (2027-2028)."},
          {"residency": "eu-eea", "currency": "EUR", "tuition_annual": eu, "academic_year": "2027-2028", "source": "course",
           "note": f"EU/EEA students: €{eu:,} (2027-2028)."}],
         adm_all({"international-other": f"{name}: {subj.group(1).rstrip('.')}. No minimum grade or points total is published."}, "course") if subj else [])
print("wrote rug (all English-taught bachelor's)")

"""Nordic universities from THE's most-international list (written 2026-11-27): every English-taught bachelor's
programme found on each university's own pages. Fees are whole-programme totals for non-EU/EEA/Swiss citizens
(per year = total / 3, our calculation) except Oslo (per year). No grade threshold published (Swedish selection
is by grades in a quota); no admission rows. EU/EEA/Swiss citizens pay no tuition.
  python3 -I scripts/research/gen/nordic.py [uni]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog

ONLY = sys.argv[1] if len(sys.argv) > 1 else None
SE = ("se", "Sweden", "SEK")


def P(name, deg, field, fac, summary, dur="course"):
    return {"name": name, "degree_type": deg, "field": field, "faculty": fac, "duration_years": 3, "duration_source": dur,
            "languages": ["en"], "entry_year": "Autumn 2027", "platform": "University Admissions in Sweden", "source": "course",
            "summary": summary, "application_requirements": []}


def T(total, note):
    return {"residency": "non-eu", "currency": "SEK", "tuition_formula": f"{total}/3", "academic_year": "Autumn 2027 entry", "source": "course", "note": note}


# Lund University
if not ONLY or ONLY == "se-lund":
    ORG = "Lund University"
    IB = src("5c8d71d97730", "International Business - Bachelor's Programme | Lund University", ORG,
             ["International Business - Bachelor's Programme | Lund University", "Start Autumn 2027 Duration 3 years Level Bachelor's Language English Place of study Lund",
              "Full programme/course tuition fee: SEK 390,000 First payment: SEK 65,000"])
    SM = src("eed4921f1836", "Sciences, Mathematics | Lund University", ORG,
             ["Sciences, Mathematics | Lund University", "Start Autumn 2027 Duration 3 years Level Bachelor's Language English Place of study Lund",
              "Full programme/course tuition fee: SEK 555,000 First payment: SEK 92,500"])
    spec("se-lund", ORG, ["Lunds universitet"], "public", "https://www.lunduniversity.lu.se", SE, ("se-lund", "Lund"), {"main": IB},
         [("non-eu", "Non-EU/EEA/Swiss citizens", "Programme tuition fee for citizens outside the EU/EEA and Switzerland.", "main")])
    prog("se-lund", "bachelor-international-business", {"course": IB},
         P("International Business", "Bachelor", "Business", "", "International Business, Bachelor's Programme, Lund University; 3 years, taught in English."),
         [T(390000, "Full programme fee SEK 390,000 (about SEK 130,000 a year, our calculation); first payment SEK 65,000.")], [])
    prog("se-lund", "bachelor-sciences-mathematics", {"course": SM},
         P("Sciences, Mathematics", "Bachelor", "Mathematics", "", "Sciences, Mathematics, Bachelor's programme, Lund University; 3 years, taught in English."),
         [T(555000, "Full programme fee SEK 555,000 (about SEK 185,000 a year, our calculation); first payment SEK 92,500.")], [])
    print("se-lund 2")

# Uppsala University (Campus Gotland, Visby)
if not ONLY or ONLY == "se-uppsala":
    ORG = "Uppsala University"
    GD = src("c33b14ae9811", "Bachelor's Programme in Game Design and Programming – Uppsala University", ORG,
             ["Bachelor's Programme in Game Design and Programming – Uppsala University",
              "The Bachelor's Programme in Game Design and Programming spans three years", "Location Visby",
              "First tuition fee instalment: SEK 75,000 Total tuition fee: SEK 450,000 Read more about fees. Application deadline 15 January 2027",
              "Language of instruction English"])
    LQ = src("52f65ff9aad2", "Bachelor's Programme in Leadership – Quality Management – Improvement – Uppsala University", ORG,
             ["The programme is divided into six semesters", "Location Visby",
              "First tuition fee instalment: SEK 75,000 Total tuition fee: SEK 450,000 Read more about fees. Application deadline 15 January 2027",
              "Language of instruction English"])
    spec("se-uppsala", ORG, ["Uppsala universitet"], "public", "https://www.uu.se", SE, ("se-visby", "Visby"), {"main": GD},
         [("non-eu", "Non-EU/EEA/Swiss citizens", "Programme tuition fee for students required to pay fees.", "main")])
    prog("se-uppsala", "bachelor-game-design-and-programming", {"course": GD},
         P("Game Design and Programming", "Bachelor", "Computer Science", "", "Bachelor's Programme in Game Design and Programming, Uppsala University (Campus Gotland, Visby); spans three years, taught in English."),
         [T(450000, "Autumn 2027 entry: total fee SEK 450,000 (about SEK 150,000 a year, our calculation); first instalment SEK 75,000.")], [])
    prog("se-uppsala", "bachelor-leadership-quality-management-improvement", {"course": LQ},
         P("Leadership – Quality Management – Improvement", "Bachelor", "Business", "", "Bachelor's Programme in Leadership – Quality Management – Improvement, Uppsala University (Visby); six semesters, taught in English."),
         [T(450000, "Autumn 2027 entry: total fee SEK 450,000 (about SEK 150,000 a year, our calculation); first instalment SEK 75,000.")], [])
    print("se-uppsala 2")

# Karolinska Institutet
if not ONLY or ONLY == "se-ki":
    ORG = "Karolinska Institutet"
    KB = src("68812d5b792f", "Bachelor's Programme in Biomedicine | Karolinska Institutet", ORG,
             ["Bachelor's Programme in Biomedicine | Karolinska Institutet", "Study location: Solna Study mode: On Campus Language of instruction: English",
              "lay a solid foundation for the courses in molecular medicine during the third year",
              "Tuition fee Total amount: 540 000 SEK First instalment: 90 000 SEK", "Degree: Bachelor of Medical Science with a Major in Biomedicine"])
    spec("se-ki", ORG, ["KI", "Karolinska Institute"], "public", "https://ki.se", SE, ("se-solna", "Solna"), {"main": KB},
         [("non-eu", "Non-EU/EEA/Swiss citizens", "Tuition fees apply to citizens of a country outside the EU, EEA or Switzerland.", "main")])
    prog("se-ki", "bachelor-biomedicine", {"course": KB},
         {**P("Biomedicine", "Bachelor of Medical Science", "Biomedical Science", "", "Bachelor's Programme in Biomedicine, Karolinska Institutet (Solna); taught in English; molecular medicine in the third year."),
          "entry_year": "Autumn 2027"},
         [T(540000, "Total amount SEK 540,000 (about SEK 180,000 a year, our calculation); first instalment SEK 90,000.")], [])
    print("se-ki 1")

# University of Oslo
if not ONLY or ONLY == "no-uio":
    ORG = "University of Oslo"
    OP = src("63dc3d411f03", "Technology Systems: Science and Engineering (bachelor) – University of Oslo", ORG,
             ["Technology Systems: Science and Engineering (bachelor) – University of Oslo", "Technology Systems: Science and Engineering Level: Bachelor Duration: 3 years ECTS Credits: 180"])
    OA = src("ca9aa0fe492a", "Admission without Norwegian proficiency – Technology Systems | University of Oslo", ORG,
             ["The tuition fee for the 2027/2028 academic year is NOK 218 000. The tuition fee applies for each year of study and is adjusted annually. The programme is taught in English.",
              "must pay tuition fees to the University of Oslo, unless they qualify for an exemption"])
    spec("no-uio", ORG, ["UiO", "Universitetet i Oslo"], "public", "https://www.uio.no", ("no", "Norway", "NOK"), ("no-oslo", "Oslo"), {"main": OP, "adm": OA},
         [("non-eu", "Non-EU/EEA/Swiss citizens", "Tuition fee for citizens of countries outside the EU/EEA and Switzerland.", "adm")])
    prog("no-uio", "bachelor-technology-systems", {"course": OP, "adm": OA},
         {**P("Technology Systems: Science and Engineering", "Bachelor", "Engineering", "", "Technology Systems: Science and Engineering (bachelor), University of Oslo; 3 years, 180 ECTS, taught in English."),
          "entry_year": "2027/2028", "platform": ""},
         [{"residency": "non-eu", "currency": "NOK", "tuition_annual": 218000, "academic_year": "2027/2028", "source": "adm",
           "note": "NOK 218,000 for 2027/2028, for each year of study, adjusted annually."}], [])
    print("no-uio 1")

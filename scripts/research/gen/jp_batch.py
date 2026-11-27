"""Japanese universities from THE's most-international list (written 2026-11-27): every English-taught (or
English-entry) bachelor's programme each publishes for international students, at the national-university
tuition each states (JPY 535,800 a year; one-time admission/registration fee JPY 282,000 noted, not annual).
No grade thresholds are published (document screening), so no admission rows. No living costs stored.
  python3 -I scripts/research/gen/jp_batch.py [uni]
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify

ONLY = sys.argv[1] if len(sys.argv) > 1 else None
JP = ("jp", "Japan", "JPY")


def one(uid, org, aliases, site, city, main, sources, residency, items, cost, years_src, tail, langs=("en",)):
    if ONLY and ONLY != uid:
        return
    spec(uid, org, aliases, "public", site, JP, city, {"main": main, **sources}, [residency])
    for name, deg, field, fac in items:
        prog(uid, slugify(f"{name} {fac}")[:60].rstrip("-"), sources,
             {"name": name, "degree_type": deg, "field": field, "faculty": fac, "duration_years": 4, "duration_source": years_src,
              "languages": list(langs), "entry_year": "2027", "platform": "", "source": "course",
              "summary": f"{name}, {fac}, {org}{tail}", "application_requirements": []},
             [cost], [])
    print(uid, len(items))


def C(src_key, note, per_term=None, terms=None, annual=None):
    c = {"residency": "all-students", "currency": "JPY", "academic_year": "2027 entry", "source": src_key, "note": note}
    if per_term:
        c.update({"tuition_per_term": per_term, "terms_per_year": 2, "terms_evidence": terms})
    else:
        c["tuition_annual"] = annual
    return c


# Nagoya University, G30 International Programs
ORG = "Nagoya University"
NL = src("193e0e84c609", "Undergraduate – Nagoya University Global 30 International Programs", ORG,
         ["Undergraduate – Nagoya University Global 30 International Programs", "About Nagoya City",
          "Automotive Engineering Program Mechanical Engineering - School of Engineering Electrical, Electronic and Information Engineering - School of Engineering Physics Program - School of Science Chemistry Program - School of Science - School of Engineering Biological Science Program - School of Science (Biology) - School of Agricultural Sciences (Applied Bioscience) Social Science Program - School of Law - School of Economics Japan-in-Asia Cultural Studies (JACS) Program - School of Humanities"])
NF = src("1a38c227504f", "Tuition and Financial Aid | Nagoya University G30", ORG,
         ["Tuition fee, regardless the nationality of students, is JPY535,800 per academic year",
          "Annual Tuition Fee JPY 535,800 Non-Refundable Registration Fee One time payment at admission JPY 282,000"])
NY = src("51b72b8fb3a2", "FAQs | Nagoya University G30", ORG, ["All admitted students start as freshmen and complete 4 years of our bachelor’s degree program."])
one("jp-nagoya", ORG, ["Nagoya Univ."], "https://en.nagoya-u.ac.jp", ("jp-nagoya", "Nagoya"), NL, {"course": NL, "fees": NF, "y": NY},
    ("all-students", "All students", "Nagoya University tuition is the same regardless of nationality.", "fees"),
    [("Automotive Engineering (Mechanical Engineering)", "Bachelor of Engineering", "Mechanical Engineering", "School of Engineering"),
     ("Automotive Engineering (Electrical, Electronic and Information Engineering)", "Bachelor of Engineering", "Electrical and Electronic Engineering", "School of Engineering"),
     ("Physics", "Bachelor of Science", "Physics", "School of Science"),
     ("Chemistry", "Bachelor of Science", "Chemistry", "School of Science"),
     ("Chemistry", "Bachelor of Engineering", "Chemistry", "School of Engineering"),
     ("Biological Science (Biology)", "Bachelor of Science", "Biology", "School of Science"),
     ("Biological Science (Applied Bioscience)", "Bachelor", "Biology", "School of Agricultural Sciences"),
     ("Social Science (Law)", "Bachelor", "Law", "School of Law"),
     ("Social Science (Economics)", "Bachelor", "Economics", "School of Economics"),
     ("Japan-in-Asia Cultural Studies", "Bachelor", "Humanities", "School of Humanities")],
    C("fees", "JPY 535,800 a year for all students; one-time registration fee JPY 282,000 at admission.", annual=535800), "y",
    " (G30 International Programs, taught in English); a four-year bachelor's programme.")

# Tohoku University, Future Global Leadership (FGL)
ORG = "Tohoku University"
TP = src("6913c91e9a33", "Undergraduate (English): Future Global Leadership Program | Tohoku University", ORG,
         ["GLOBAL LEARNING CENTER, TOHOKU UNIVERSITY", "Language: English Duration: 4 years",
          "offers three outstanding undergraduate degree courses that are taught in English: - Advanced Molecular Chemistry (AMC) - International Mechanical and Aerospace Engineering (IMAC-U) - Applied Marine Biology (AMB)",
          "Entrance Fee (Admission Fee) JPY 282,000 (Paid once for entrance to Tohoku University) Tuition Fees JPY 267,900 (Paid every semester for tuition.",
          "Annual Tuition JPY 535,800 (JPY 267,900 x 2)", "Sendai is a relatively inexpensive city"])
one("jp-tohoku", ORG, ["Tohoku Univ."], "https://www.tohoku.ac.jp", ("jp-sendai", "Sendai"), TP, {"course": TP},
    ("all-students", "All students", "Tohoku University undergraduate tuition and entrance fee.", "course"),
    [("Advanced Molecular Chemistry", "Bachelor", "Chemistry", ""),
     ("International Mechanical and Aerospace Engineering", "Bachelor", "Mechanical Engineering", ""),
     ("Applied Marine Biology", "Bachelor", "Biology", "")],
    C("course", "JPY 535,800 a year (JPY 267,900 per semester); one-time entrance fee JPY 282,000.", annual=535800), "course",
    " (Future Global Leadership programme, taught in English); 4 years.")

# Kyushu University, International Undergraduate Programs in Engineering (IUPE)
ORG = "Kyushu University"
KP = src("kyushu-iupe-2026", "Application Instructions, International Undergraduate Programs in Engineering, October 2026 | Kyushu University", ORG,
         ["International Undergraduate Programs in Electrical Engineering and Computer Science Applied Chemistry Civil Engineering Mechanical and Aerospace Engineering October 2026 School of Engineering Kyushu University",
          "The International Undergraduate Program is a four-year bachelor program, in which all classes, with the exception of Japa",
          "Tuition Fee for Fall 2026 Tuition Fee for Spring 2027", "282,000 267,900 267,900 817,800",
          "Kyushu University 744 Motooka, Nishi-ku, Fukuoka, 819-0395"])
one("jp-kyushu", ORG, ["Kyushu Univ."], "https://www.kyushu-u.ac.jp", ("jp-fukuoka", "Fukuoka"), KP, {"course": KP},
    ("all-students", "All students", "Kyushu University IUPE enrolment fee and tuition (original amounts).", "course"),
    [("Electrical Engineering and Computer Science", "Bachelor of Engineering", "Computer Science", "School of Engineering"),
     ("Applied Chemistry", "Bachelor of Engineering", "Chemistry", "School of Engineering"),
     ("Civil Engineering", "Bachelor of Engineering", "Civil Engineering", "School of Engineering"),
     ("Mechanical and Aerospace Engineering", "Bachelor of Engineering", "Mechanical Engineering", "School of Engineering")],
    C("course", "JPY 267,900 per semester (original amount); one-time enrollment fee JPY 282,000. Half the first-year tuition can be exempted if conditions are met.",
      per_term=267900, terms=["Tuition Fee for Fall 2026", "Tuition Fee for Spring 2027"]), "course",
    " (International Undergraduate Program, taught in English); four-year bachelor programme.")

# Kyoto University, Kyoto iUP
ORG = "Kyoto University"
KY = src("kyoto-iup-2027", "Application Guidelines for October 2027 Enrollment, Kyoto iUP | Kyoto University", ORG,
         ["Kyoto iUP comprises a six-month preparatory course followed by a four-year undergraduate course.",
          "In the first two-and-a-half years, students develop an essential understanding of core subjects in both English and Japanese, and acquire sufficient Japanese language proficiency to attend specialized lectures and pursue advanced studies in Japanese in their final two years.",
          "Faculty of Integrated Human Studies Faculty of Letters*2*3 Faculty of Education Faculty of Law Faculty of Economics Faculty of Science*2 Faculty of Pharmaceutical Sciences*4 Faculty of Engineering*2 Faculty of Agriculture*2*5",
          "Undergraduate Course JPY 282,000 Full waiver available JPY 535,800 (Annual) Full or partial waivers available",
          "Kyoto University reserves the right"])
one("jp-kyoto", ORG, ["Kyoto Univ.", "Kyodai"], "https://www.kyoto-u.ac.jp", ("jp-kyoto", "Kyoto"), KY, {"course": KY},
    ("all-students", "All students", "Kyoto iUP undergraduate course admission fee and annual tuition (waivers available).", "course"),
    [(f"Kyoto iUP: {f}", "Bachelor", fld, f) for f, fld in
     [("Faculty of Integrated Human Studies", "Humanities"), ("Faculty of Letters", "Humanities"), ("Faculty of Education", "Education"),
      ("Faculty of Law", "Law"), ("Faculty of Economics", "Economics"), ("Faculty of Science", "Natural Sciences"),
      ("Faculty of Pharmaceutical Sciences", "Pharmacy"), ("Faculty of Engineering", "Engineering"), ("Faculty of Agriculture", "Agriculture")]],
    C("course", "Undergraduate course: JPY 535,800 a year (full or partial waivers available); admission fee JPY 282,000 (full waiver available). A six-month preparatory course comes first.", annual=535800), "course",
    " (Kyoto iUP); a six-month preparatory course, then a four-year undergraduate course taught in English and Japanese, with Japanese for the final two years.", langs=("en", "ja"))

# Hokkaido University, Modern Japanese Studies Program (MJSP)
ORG = "Hokkaido University"
HM = src("hokudai-mjsp-2028", "2028 Enrollment Application Guidelines, Modern Japanese Studies Program | Hokkaido University", ORG,
         ["Modern Japanese Studies Program Hokkaido University",
          "*The Modern Japanese Studies Program is a four-year Bachelor’s degree program preceded by a sixmonth Intensive Japanese Course.",
          "Bachelor’s degree in ¥5,000 ¥282,000 ¥535,800 (per year) Modern Japanese Studies",
          "*The full amount of the Enrollment Fee and first-year Tuition Fees will be waived (2028 academic year) for students enrolling in the Modern Japanese Studies Program in April (2028).",
          "Office of Admissions, Hokkaido University Kita 17, Nishi 8, Kita-ku, Sapporo, Hokkaido, Japan 060-0817"])
if not ONLY or ONLY == "jp-hokkaido":
    spec("jp-hokkaido", ORG, ["Hokudai"], "public", "https://www.global.hokudai.ac.jp", JP, ("jp-sapporo", "Sapporo"), {"main": HM},
         [("all-students", "All students", "MJSP enrollment fee and annual tuition.", "main")])
    prog("jp-hokkaido", "bachelor-modern-japanese-studies", {"course": HM},
         {"name": "Modern Japanese Studies", "degree_type": "Bachelor", "field": "Japanese Studies", "faculty": "", "duration_years": 4, "duration_source": "course",
          "languages": ["en"], "entry_year": "April 2028", "platform": "", "source": "course",
          "summary": "Modern Japanese Studies Program, Hokkaido University; a four-year bachelor's degree preceded by a six-month Intensive Japanese Course.",
          "application_requirements": []},
         [C("course", "JPY 535,800 a year; enrollment fee JPY 282,000. For April 2028 entrants the enrollment fee and first-year tuition are waived in full.", annual=535800)], [])
    print("jp-hokkaido 1")

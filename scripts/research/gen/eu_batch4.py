"""Five low-fee European universities from THE's most-international list (written 2026-11-26), all taught in
German: University of Vienna (#14), TU Wien (#48), Freie Universität Berlin (#64), University of Freiburg (#81),
University of Tübingen (#89). One computer science bachelor each; fees per semester from each university's own
fee page (per year = 2 semesters, our calculation). No grade cut-offs are published: the admission row says how
places are given (entrance exam, selection procedure, local restriction, or open admission). No living costs read.
  python3 -I scripts/research/gen/eu_batch4.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all


def P(name, faculty, summary, dur="course"):
    return {"name": name, "degree_type": "BSc", "field": "Computer Science", "faculty": faculty, "duration_years": 3,
            "duration_source": dur, "languages": ["de"], "entry_year": "2027", "platform": "", "source": "course",
            "summary": summary, "application_requirements": []}


def C(res, per, mand, terms, src_key, note, year):
    c = {"residency": res, "currency": "EUR", "tuition_per_term": per, "terms_per_year": 2, "terms_evidence": terms,
         "academic_year": year, "source": src_key, "note": note}
    if mand:
        c["mandatory_per_term"] = mand
    return c


# University of Vienna
ORG = "University of Vienna"
VP = src("b555e889c0c8", "Computer Science (bachelor's programme) | Entrance exam | University of Vienna", ORG,
         ["University of Vienna / Entrance exam / Before the entrance exam / Degree programmes / Computer Science (bachelor's programme)",
          "033 521", "6 semesters", "180 ECTS (15 ECTS possible as extension curricula )", "German (admission requirement)",
          "1 March to 4 May 2027", "19 July 2027 on site in Vienna (no alternative dates)",
          "415 (total for Computer Science and Business Informatics)"])
VF = src("1c48f4ab395f", "Amount of the tuition fee/Students' Union fee | University of Vienna", ORG,
         ["Amount non-EU/EEA Students' Union fee: 26.20 Euro Tuition fee: 726.72 Euro Total: 752.92 Euro per semester",
          "Students with non-EU/EEA Citizenship You must pay your tuition fee/Students' Union fee every semester",
          "from winter semester 2025 onwards", "before summer semester 2021"])
VG = src("7fc2cfa55a74", "German language proficiency | University of Vienna", ORG,
         ["The following applies to all bachelor’s and diploma programmes instructed in German : In your application, you need a proof of German language proficiency at level A2 (or higher). To be admitted, you must provide proof of German language proficiency at level C1."])
spec("at-univie", ORG, ["Universität Wien", "Uni Wien"], "public", "https://www.univie.ac.at", ("at", "Austria", "EUR"), ("at-vienna", "Vienna"),
     {"main": VP, "fees": VF}, [("non-eu", "Non-EU/EEA citizens", "Tuition fee and Students' Union fee for non-EU/EEA citizens.", "fees")])
prog("at-univie", "bsc-computer-science", {"course": VP, "fees": VF, "german": VG},
     {**P("Computer Science", "", "Bachelor's programme in Computer Science (033 521), University of Vienna; 6 semesters, 180 ECTS, taught in German."),
      "application_requirements": [{"name": "German language proficiency", "source": "german", "type": "language",
                                    "description": "Programmes taught in German: proof of German at level A2 (or higher) to apply, and at level C1 to be admitted."}]},
     [C("non-eu", 726.72, 26.20, ["winter semester", "summer semester"], "fees",
        "Non-EU/EEA citizens: tuition €726.72 + Students' Union fee €26.20 = €752.92 per semester.", "per semester")],
     adm_all({"international-other": "Computer Science: entrance exam (written test on 19 July 2027 in Vienna; applications 1 March to 4 May 2027) for 415 places shared with Business Informatics; taught in German (German proficiency required). No grade cut-off is published."},
             "course"))

# TU Wien
ORG = "TU Wien"
TP = src("596b8a742699", "Informatics | TU Wien", ORG,
         ["Informatics | TU Wien", "Degree programme code UE 033 521 - Bachelor's Programme Informatics",
          "Duration of the degree programme 6 semesters Credits 180 ECTS Language of instruction German Degree Bachelor of Science (BSc)",
          "the selection procedure does not assess programming skills and does not require any prior experience with computers. Instead, it evaluates your ability to solve problems, think logically, and comprehend texts.",
          "The selection procedure takes place only once a year",
          "Dean's Office of Faculty of Informatics Erzherzog-Johann-Platz 1 4 th floor 1040 Vienna"])
TF = src("0bd8758b7bea", "Tuition Fee | TU Wien", ORG,
         ["Non-degree students and non-EU nationals are subject to tuition fees from the first semester.",
          "The tuition fee is regular € 363.36 per semester (or € 726.72 per semester for non-EU nationals ). In addition to the respective tuition fee, the ÖH fee including insurance has to be paid each semester.",
          "until October 31 st for winter semester and March 31 st for summer semester"])
spec("at-tuwien", ORG, ["Technische Universität Wien", "Vienna University of Technology"], "public", "https://www.tuwien.at", ("at", "Austria", "EUR"), ("at-vienna", "Vienna"),
     {"main": TP, "fees": TF}, [("non-eu", "Non-EU nationals", "Tuition fee for non-EU nationals, payable from the first semester.", "fees")])
prog("at-tuwien", "bsc-informatics", {"course": TP, "fees": TF},
     P("Informatics", "", "Bachelor's Programme Informatics (UE 033 521), TU Wien; 6 semesters, 180 ECTS, taught in German."),
     [C("non-eu", 726.72, None, ["winter semester", "summer semester"], "fees",
        "Non-EU nationals: €726.72 tuition per semester, plus the ÖH (student union) fee each semester.", "per semester")],
     adm_all({"international-other": "Informatics: a selection procedure held once a year that tests problem solving, logical thinking and reading comprehension (no programming); taught in German. No grade cut-off is published."},
             "course"))

# Freie Universität Berlin
ORG = "Freie Universität Berlin"
FP = src("cf19ccd2f163", "Informatik (Mono-Bachelor) | Fachbereich Mathematik und Informatik | Freie Universität Berlin", ORG,
         ["Informatik (Mono-Bachelor) • Studium • Fachbereich Mathematik und Informatik", "Freie Universität Berlin Fachbereich Mathematik und Informatik",
          "Zulassungs­modus Lokale Zulassungsbeschränkung", "Studienbeginn Wintersemester (WS) Studiensprache Deutsch Abschluss Bachelor of Science (B.Sc.) Regelstudienzeit 6 Semester"])
FF = src("79d5a81ed4b4", "Fees and dues | Freie Universität Berlin", ORG,
         ["Freie Universität Berlin does not charge any tuition fees (except for continuing education programs), rather so-called \"Semestergebühren und -beiträge\" (fees and dues).",
          "Fees for new enrollments for winter semester 2026/27 A total of €376,80 is payable for registration for the winter semester 2026/27",
          "Fees for new enrollments for summer semester 2027"])
spec("de-fu-berlin", ORG, ["FU Berlin", "Free University of Berlin"], "public", "https://www.fu-berlin.de", ("de", "Germany", "EUR"), ("de-berlin", "Berlin"),
     {"main": FP, "fees": FF}, [("all-students", "All students", "Freie Universität Berlin charges no tuition fees; every student pays the semester fees and dues.", "fees")])
prog("de-fu-berlin", "bsc-informatik", {"course": FP, "fees": FF},
     P("Informatik (Computer Science)", "Fachbereich Mathematik und Informatik", "B.Sc. Informatik (Mono-Bachelor), Freie Universität Berlin; 6 semesters, taught in German, starts in the winter semester."),
     [C("all-students", 0, 376.80, ["winter semester", "summer semester"], "fees",
        "No tuition fee. Semester fees and dues €376.80 for new enrolment in winter semester 2026/27.", "winter semester 2026/27")],
     adm_all({"international-other": "Informatik: places are limited locally (Lokale Zulassungsbeschränkung); taught in German. No grade cut-off is published."}, "course"))

# University of Freiburg
ORG = "University of Freiburg"
GP = src("a238d9d3c1d5", "Computer Science (Bachelor of Science) | Faculty of Engineering | University of Freiburg", ORG,
         ["the Faculty of Engineering at the University of Freiburg organizes a robotic competition every year",
          "Very good German language skills (level C1 of the European reference framework required for application already)",
          "Total Credits: 180 ECTS points Standard Length of Studies: 6 semester resp. 3 years Language of Instruction: German based, with only some advanced courses in English Start of Courses: Winter semester (October)",
          "German and European nationals 103€ fee for the Studierendenwerk (student organization) 80€ administrative fees 7€ student union fee Total: A 190€ fee per semester to be paid to the University.",
          "Non-EU nationals 1500€ tuition 103€ fee for the Studierendenwerk (student organization) 80€ administrative fees 7€ student union fee Total: A 1690€ fee per semester to be paid to the University.",
          "Admissions: First semester: without special admission requirements (admission-free)",
          "June 1st – September 30 th (winter semester), December 1 st – March 31 st (summer semester)"])
GF = src("c36be828b052", "Tuition fees for international students | University of Freiburg", ORG,
         ["The tuition fee for international students is 1,500 euros per semester in accordance with Section 4 (1) of the State Higher Education Fees Act."])
spec("de-freiburg", ORG, ["Albert-Ludwigs-Universität Freiburg", "Universität Freiburg"], "public", "https://uni-freiburg.de", ("de", "Germany", "EUR"), ("de-freiburg", "Freiburg"),
     {"main": GP, "fees": GF}, [("non-eu", "Non-EU nationals", "Tuition fee for international (non-EU/EEA) students, in addition to the semester fee.", "fees")])
prog("de-freiburg", "bsc-computer-science", {"course": GP, "fees": GF},
     P("Computer Science", "Faculty of Engineering", "B.Sc. Computer Science, University of Freiburg; 6 semesters (3 years), 180 ECTS, taught mainly in German."),
     [C("non-eu", 1500, 190, ["(winter semester)", "(summer semester)"], ["course", "fees"],
        "Non-EU nationals: €1500 tuition + €190 semester fees = €1690 per semester.", "per semester")],
     adm_all({"international-other": "Computer Science: a university entrance qualification, German at level C1 already when applying, and an online orientation test; first-semester admission is admission-free (no selection). No grade cut-off is published."}, "course"))

# University of Tübingen
ORG = "University of Tübingen"
UP = src("d414ea826c33", "Computer Science - Bachelor (mono) | University of Tübingen", ORG,
         ["Computer Science - Bachelor (mono) | University of Tübingen",
          "Key data on study program Faculty Science Academic Degree Bachelor (mono) Restricted admission None Regular duration of studies 6 semester",
          "Program start Winter semester, Summer semester Language of instruction German",
          "Dieser Studiengang ist zulassungsfrei, insofern Sie die Zugangsvoraussetzungen erfüllen, d.h. es ist keine Bewerbung notwendig."])
UF = src("bdf14d3c94a1", "Tuition fees | University of Tübingen", ORG,
         ["International students (=students who are not citizens of an EU/EEA member state) will be charged a tuition fee of 1,500.00 euros per semester .",
          "This is in addition to the general semester fee of currently 194.80 euros per semester .",
          "since winter semester 2017-18", "since the summer semester 2017"])
spec("de-tuebingen", ORG, ["Universität Tübingen", "Eberhard Karls Universität Tübingen"], "public", "https://uni-tuebingen.de", ("de", "Germany", "EUR"), ("de-tuebingen", "Tübingen"),
     {"main": UP, "fees": UF}, [("non-eu", "Non-EU/EEA students", "Tuition fee for students who are not citizens of an EU/EEA member state.", "fees")])
prog("de-tuebingen", "bsc-computer-science", {"course": UP, "fees": UF},
     P("Computer Science", "", "Computer Science Bachelor (mono), University of Tübingen; regular duration 6 semesters, taught in German, start in winter or summer semester."),
     [C("non-eu", 1500, 194.80, ["winter semester", "summer semester"], "fees",
        "Non-EU/EEA students: €1,500.00 tuition + €194.80 semester fee per semester.", "per semester")],
     adm_all({"international-other": "Computer Science: no restricted admission and no selection procedure, if you meet the entry requirements; taught in German. No grade cut-off is published."}, "course"))
print("wrote eu batch4")

# Tübingen: every other Bachelor (mono) and Bachelor (major subject) in the course finder (added 2026-11-27).
# Fees are Tübingen's (same page as above, valid for all Bachelor's degree programs). Lateinamerikastudien left
# out: its language of instruction is given only as "Other".
import re
from newuni import PAGES, slugify
TFIELD = {"Ägyptologie": "History", "Allgemeine Rhetorik": "Humanities", "Altorientalische Philologie": "Humanities", "Biochemistry": "Biochemistry",
          "Biologie": "Biology", "Chemistry": "Chemistry", "Cognitive Science": "Cognitive Science", "Computational Linguistics": "Linguistics",
          "Economics and Business Administration": "Economics", "English and American Studies": "English", "Geographie": "Geography",
          "Geoökologie": "Environmental Science", "Geowissenschaften": "Earth Sciences", "Germanistik": "German Studies",
          "Geschichtswissenschaft": "History", "Griechisch": "Classics", "Hebammenwissenschaft": "Midwifery", "International Business Administration": "Business",
          "International Economics": "Economics", "Internationale Literaturen": "Literature", "Italienisch": "Italian Studies", "Judaistik": "Religious Studies",
          "Katholische Theologie": "Theology", "Klassische Archäologie": "Archaeology", "Kunstgeschichte": "Art History", "Latein": "Classics",
          "Mathematics": "Mathematics", "Medizintechnik": "Biomedical Engineering", "Molekulare Medizin": "Biomedical Science", "Musikwissenschaft": "Music",
          "Nano-Science": "Physics", "Pflege": "Nursing", "Philosophie": "Philosophy", "Physics": "Physics", "Politikwissenschaft": "Politics",
          "Psychologie": "Psychology", "Religionswissenschaft": "Religious Studies", "Slavistik": "Slavic Studies", "Soziologie": "Sociology",
          "Spanisch": "Spanish", "Umweltnaturwissenschaften": "Environmental Science", "Französisch": "French"}
for pid in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tue_pages.txt")).read().split():
    t = re.sub(r"\s+", " ", open(PAGES / f"{pid}.txt", errors="replace").read())
    title = t.split(" | ")[0].strip()
    name, kind = re.match(r"(.+?) - Bachelor \((mono|major subject)\)", title).groups()
    k = re.search(r"Restricted admission (None|Yes, in first and higher semesters|Yes, in first semester) Regular duration of studies (\d) semester Is a combination subject required\? (Yes|No)", t)
    lang = re.search(r"Language of instruction (German|English)\b", t)
    if not (k and lang):
        continue
    restricted, sem, combo = k.groups()
    field = TFIELD.get(name) or TFIELD.get(name.split(" mit ")[0]) or TFIELD.get(name.split("/")[0].strip()) or ("Sport Science" if name.startswith("Sportwissenschaft") else name)
    years = int(sem) / 2
    P2 = src(pid, f"{title} | University of Tübingen", ORG, [f"{title} | University of Tübingen", k.group(0), f"Language of instruction {lang.group(1)}"])
    combo_txt = " As a major subject it is studied together with a second (combination) subject." if combo == "Yes" else ""
    adm = {"None": "no restricted admission (no selection procedure if you meet the entry requirements)",
           "Yes, in first and higher semesters": "restricted admission in first and higher semesters",
           "Yes, in first semester": "restricted admission in the first semester"}[restricted]
    asc = name.translate(str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}))
    prog("de-tuebingen", "bachelor-" + slugify(asc)[:45].rstrip("-") + ("-major" if kind != "mono" else ""), {"course": P2, "fees": UF},
         {"name": name, "degree_type": "Bachelor" + (" (major subject)" if kind != "mono" else ""), "field": field, "faculty": "",
          "duration_years": years if years % 1 else int(years), "duration_source": "course", "languages": ["de" if lang.group(1) == "German" else "en"],
          "entry_year": "2027", "platform": "", "source": "course",
          "summary": f"{title}, University of Tübingen; regular duration {sem} semesters, taught in {lang.group(1)}.{combo_txt}", "application_requirements": []},
         [C("non-eu", 1500, 194.80, ["winter semester", "summer semester"], "fees",
            "Non-EU/EEA students: €1,500.00 tuition + €194.80 semester fee per semester.", "per semester")],
         adm_all({"international-other": f"{name}: {adm}; taught in {lang.group(1)}. No grade cut-off is published."}, "course"))
print("wrote tuebingen (all bachelor's)")

VKEY = {"Geography": "Geography", "Mathematics": "Mathematics", "Physics": "Physics", "Philosophy": "Philosophy", "History": "History",
        "Linguistics": "Linguistics", "Musicology": "Music", "Statistics and Data Analytics": "Statistics", "Meteorology and Climate Science": "Earth Sciences",
        "Sport and Human Movement Science": "Sport Science", "Theatre, Film and Media Studies": "Media and Communication", "Comparative Literature": "Literature",
        "History of Art and Architecture": "Art History", "Classical Archaeology": "Archaeology", "Prehistory and Historical Archaeology": "Archaeology",
        "Protestant Theology": "Theology", "Islamic Theological Studies": "Theology", "Religious Education": "Theology", "German Philology": "German Studies"}
field_for_vie = lambda n: VKEY.get(n, n)
# Vienna: the bachelor's programmes on "Bachelor's and diploma programmes" (added 2026-11-27); each page's
# "in a nutshell" block. Fees are the University of Vienna's non-EU/EEA semester fees (same page as above).
VF_ = 'p]:mb-0"> '
for pid in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "vie_pages.txt")).read().split():
    t = re.sub(r"\s+", " ", open(PAGES / f"{pid}.txt", errors="replace").read())
    title = t.split(" Skip to main")[0].strip()
    name = title.replace(" (bachelor's programme)", "")
    code = re.search(r"Programme Code " + re.escape(VF_) + r"(\d{3} \d{3})", t).group(1)
    deg = re.search(r"Degree " + re.escape(VF_) + r"(Bachelor of [A-Za-z ]+?(?: \((?:BA|BSc)\))?) Contents", t).group(1)
    ex = re.search(r"Additional exam " + re.escape(VF_) + r"(.+?) Degree " + re.escape(VF_), t)
    if "German (admission requirement)" not in t or "6 semesters" not in t:
        continue
    qs = [title, f"Programme Code {VF_}{code}", f"Duration {VF_}6 semesters", f"Degree {VF_}{deg}", "no fixed upper limit", "German (admission requirement)"]
    if ex:
        qs.append(f"Additional exam {VF_}{ex.group(1)}")
    P3 = src(pid, f"{title} | University of Vienna", "University of Vienna", qs)
    extra = "" if not ex or ex.group(1) == "None" else f" Additional exam: {ex.group(1)}."
    asc = name.translate(str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue"}))
    prog("at-univie", "ba-" + slugify(asc)[:50].rstrip("-"), {"course": P3, "fees": VF, "german": VG},
         {"name": name, "degree_type": deg, "field": field_for_vie(name) if "field_for_vie" in globals() else name, "faculty": "",
          "duration_years": 3, "duration_source": "course", "languages": ["de"], "entry_year": "2027", "platform": "", "source": "course",
          "summary": f"{title}, University of Vienna (programme code {code}); 6 semesters, German required for admission.",
          "application_requirements": [{"name": "German language proficiency", "source": "german", "type": "language",
                                        "description": "Programmes taught in German: proof of German at level A2 (or higher) to apply, and at level C1 to be admitted."}]},
         [C("non-eu", 726.72, 26.20, ["winter semester", "summer semester"], "fees",
            "Non-EU/EEA citizens: tuition €726.72 + Students' Union fee €26.20 = €752.92 per semester.", "per semester")],
         adm_all({"international-other": f"{name}: no fixed upper limit on places; German required for admission.{extra} No grade cut-off is published."}, "course"))
print("wrote vienna (bachelor's list)")

# TU Wien: other bachelor's programmes on its Bachelor Programmes page (added 2026-11-27). Pages without the key
# facts line (Civil Engineering, Technical Mathematics: overview pages) are skipped.
WFIELD = {"Architecture": "Architecture", "Chemical and Process Engineering": "Chemical Engineering", "Electrical Engineering": "Electrical and Electronic Engineering",
          "Environmental Engineering": "Engineering", "Geodesy and Geoinformation": "Engineering", "Mechanical Engineering": "Mechanical Engineering",
          "Mechanical Engineering - Management": "Mechanical Engineering", "Technical Chemistry": "Chemistry", "Technical Physics": "Physics",
          "Urban and Regional Planning": "Urban Studies", "Business Informatics": "Business", "Computer Engineering": "Computer Engineering"}
for pid in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tuw_pages.txt")).read().split():
    t = re.sub(r"\s+", " ", open(PAGES / f"{pid}.txt", errors="replace").read())
    title = t.split(" | ")[0].strip()
    k = "Duration of the degree programme 6 semesters Credits 180 ECTS Language of instruction German Degree Bachelor of Science (BSc)"
    if k not in t or title not in WFIELD:
        continue
    P4 = src(pid, f"{title} | TU Wien", "TU Wien", [f"{title} | TU Wien", k])
    prog("at-tuwien", "bsc-" + slugify(title), {"course": P4, "fees": TF},
         {"name": title, "degree_type": "BSc", "field": WFIELD[title], "faculty": "", "duration_years": 3, "duration_source": "course",
          "languages": ["de"], "entry_year": "2027", "platform": "", "source": "course",
          "summary": f"Bachelor's programme {title}, TU Wien; 6 semesters, 180 ECTS, taught in German.", "application_requirements": []},
         [C("non-eu", 726.72, None, ["winter semester", "summer semester"], "fees",
            "Non-EU nationals: €726.72 tuition per semester, plus the ÖH (student union) fee each semester.", "per semester")],
         adm_all({"international-other": f"{title}: taught in German. No grade cut-off is published."}, "course"))
print("wrote tuwien (bachelor's list)")

# FU Berlin: every mono bachelor and combi-bachelor major subject in "Our Degree Programs" (added 2026-11-27),
# from each page's "Basic Information" block. Left out: minor subjects, teacher-training tracks, programmes whose
# page has no Basic Information block, and Equine Sciences ("No admissions").
LANGC = {"German": "de", "English": "en", "French": "fr", "Italian": "it", "Spanish": "es", "Modern Greek": "el"}
FFIELD = {"Biochemistry": "Biochemistry", "Biology": "Biology", "Chemistry": "Chemistry", "Mathematics": "Mathematics", "Physics": "Physics",
          "Economics": "Economics", "Psychology": "Psychology", "Political Science": "Politics", "Philosophy": "Philosophy", "History": "History",
          "Geographical Sciences": "Geography", "Geological Sciences": "Earth Sciences", "Meteorology": "Earth Sciences",
          "Digital Media and Technology": "Computer Science", "Media and Communication Studies": "Media and Communication", "Film Studies": "Media and Communication",
          "English Language and Literature": "English", "German Language and Literature": "German Studies", "Social and Cultural Anthropology": "Anthropology",
          "Theater Studies": "Theatre"}
seen_fu = set()
for pid in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fu_pages.txt")).read().split():
    t = re.sub(r"\s+", " ", open(PAGES / f"{pid}.txt", errors="replace").read())
    m = re.search(r"Bachelor's Degree and State Exam (.+?) \1 - (Mono bachelor|Major subject in a combi bachelor)", t)
    d = re.search(r"Basic Information 1st Semester Admissions (Restricted admission|Unrestricted admission).*? Language ([A-Za-z, ]+?) Degree (Bachelor of (?:Science \(B\.Sc\.\)|Arts \(B\.A\.\))).*? Duration (\d) Semester", t)
    if not (m and d) or re.search(r"Teacher Training|for Teaching", m.group(1)) or m.group(1) in seen_fu:
        continue
    name, kind = m.group(1), m.group(2)
    langs = [LANGC[x.strip()] for x in d.group(2).split(",") if x.strip() in LANGC]
    if not langs:
        continue
    seen_fu.add(name)
    adm, deg, sem = d.group(1), d.group(3), int(d.group(4))
    P5 = src(pid, f"{name} - {kind} | Freie Universität Berlin", "Freie Universität Berlin",
             [f"{name} - {kind}", f"1st Semester Admissions {adm}", f"Language {d.group(2)} Degree {deg}", f"Duration {sem} Semester"])
    prog("de-fu-berlin", ("b-" if kind == "Mono bachelor" else "major-") + slugify(name)[:50].rstrip("-"), {"course": P5, "fees": FF},
         {"name": name, "degree_type": deg.split(" (")[0] + (" (major subject, combi bachelor)" if kind != "Mono bachelor" else ""),
          "field": FFIELD.get(name, name), "faculty": "", "duration_years": sem / 2 if sem % 2 else sem // 2, "duration_source": "course",
          "languages": langs, "entry_year": "2027", "platform": "", "source": "course",
          "summary": f"{name} ({kind}), Freie Universität Berlin; {sem} semesters, language {d.group(2)}.", "application_requirements": []},
         [C("all-students", 0, 376.80, ["winter semester", "summer semester"], "fees",
            "No tuition fee. Semester fees and dues €376.80 for new enrolment in winter semester 2026/27.", "winter semester 2026/27")],
         adm_all({"international-other": f"{name}: {adm.lower()} in the 1st semester; language of instruction {d.group(2)}. No grade cut-off is published."}, "course"))
print("wrote fu-berlin (bachelor's list)")

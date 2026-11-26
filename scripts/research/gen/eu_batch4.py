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

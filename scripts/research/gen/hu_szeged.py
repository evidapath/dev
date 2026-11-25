"""University of Szeged: base records + three English-taught BSc programmes (written 2026-11-25).

Source: course pages on apply.u-szeged.hu: "Nominal duration N semesters", "Study language English",
"Tuition fee €N per semester", entry and English requirements, location Szeged.
Agricultural Engineering not added (taught in Hódmezővásárhely). No living-cost figures read.
  python3 -I scripts/research/gen/hu_szeged.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "University of Szeged"
P = [
 ("448262d7f496", "[BSc] Computer Science", "Computer Science", "Computer Science", 3200, 6,
  "a demonstrated proficiency in English ( TELC B2, ECL B2, TOEFL iBT test score of 72, or RPDT score 72; Cambridge First Certificate “B”; IELTS score of 5.5 at least, LanguageCert B2 level) and an entrance exam (skype interview online).",
  "Computer Science: no grade cut-off published; completed secondary education, English proficiency and an entrance exam (online interview).",
  {"test_name": "IELTS / TOEFL iBT (or B2 certificate)", "min_score": "IELTS 5.5, TOEFL iBT 72, or a B2 certificate (TELC, ECL, LanguageCert, Cambridge First 'B').", "source": "course"}),
 ("c0d8cc0fde10", "[BSc] Business Administration and Management", "Business Administration and Management", "Business", 2700, 7,
  "a demonstrated proficiency in English (Intermediate, B2, IELTS or TOEFL ) ; - and a written and oral entrance examination taken in the university’s electronic study system. A solid knowledge of Mathematics is essential",
  "Business Administration and Management: no grade cut-off published; high school diploma, transcripts of all secondary years, English (B2) and a written and oral entrance examination; solid Mathematics is essential.",
  {"test_name": "English (B2)", "min_score": "B2 (intermediate) from an accredited four-skill exam, IELTS or TOEFL.", "source": "course"}),
 ("e368ecf78880", "[BSc] Biochemical Engineer", "Biochemical Engineering", "Biochemistry", 3200, 7,
  "Accepted Language Certificates: demonstrated proficiency in English ( TELC /ECL B2, TOEFL IBT – 72, RPDT – 72, Cambridge FC B, IELTS – 5.5, LanguageCert B2 level)",
  "Biochemical Engineering: no grade cut-off published; high school diploma, medical certificate and further requirements set by the faculty.",
  {"test_name": "IELTS / TOEFL iBT (or B2 certificate)", "min_score": "IELTS 5.5, TOEFL iBT 72, or a B2 certificate.", "source": "course"}),
]
spec("hu-szeged", ORG, ["SZTE", "Szegedi Tudományegyetem"], "public", "https://u-szeged.hu/english", ("hu", "Hungary", "HUF"), ("hu-szeged", "Szeged"),
     {"main": src(P[0][0], "Computer Science BSc | University of Szeged", ORG, [f"{P[0][1]} - {ORG}", "Study location Hungary, Szeged"])},
     [("international", "Self-financing students (course page fee)", "The tuition fee on each University of Szeged course page of its application portal.", "main")])

for page, portal, name, field, fee, sem, entry_q, th, eng in P:
    q = [f"{portal} - {ORG}", "Study location Hungary, Szeged", f"Nominal duration {sem} semesters", "Study language English",
         f"Tuition fee €{fee:,} per semester", entry_q]
    prog("hu-szeged", f"bsc-{slugify(name)}", {"course": src(page, f"{name} BSc | University of Szeged", ORG, q)},
         {"name": name, "degree_type": "BSc", "field": field, "faculty": "", "duration_years": sem / 2, "duration_source": "course", "languages": ["en"],
          "entry_year": "Course page (year not stated)", "platform": "University of Szeged application portal (apply.u-szeged.hu)", "source": "course",
          "summary": f"{name} (BSc), University of Szeged; taught in English.", "application_requirements": []},
         [{"residency": "international", "currency": "EUR", "tuition_per_semester": fee, "semesters_quote": f"Nominal duration {sem} semesters",
           "semesters_source": "course", "academic_year": "Course page (year not stated)", "source": "course",
           "note": f"EUR {fee:,} per semester (course page; the academic year isn't stated); two semesters a year, so the yearly figure is our calculation. "
                   "Living costs not added."}],
         adm_all({c: th for c in ("ib", "a-level", "us-hs", "cbse", "international-other")}, "course", english=eng))
    print("wrote", name, sem / 2)

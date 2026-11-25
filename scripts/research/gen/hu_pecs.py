"""University of Pécs: base records + six English-taught bachelor's degrees (written 2026-11-25).

Source: course pages on apply.pte.hu: "<name> University of Pécs Hungary, Pécs", "Nominal duration
N semesters (Y years)", "Study language English", "Tuition fee ..." (per year or per semester, EUR or USD).
The course pages point to a general entry-requirements page for admission and English rules, which wasn't
read, so no grade or English requirement is stored; the academic year isn't stated on the course pages.
  python3 -I scripts/research/gen/hu_pecs.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "University of Pécs"
# page, name, degree, field, fee quote, currency, per ("year"|"semester"), amount, semesters, years, duration quote
P = [("9e030f857bbe", "Chemistry", "BSc", "Chemistry", "Tuition fee €6,000 per year", "EUR", "year", 6000, 6, 3, "Nominal duration 6 semesters (3 years)"),
     ("03a7ba2432af", "Computer Science", "BSc", "Computer Science", "Tuition fee €6,000 per year", "EUR", "year", 6000, 6, 3, "Nominal duration 6 semesters (3 years)"),
     ("da54aebc2dc9", "Biology", "BSc", "Biology", "Tuition fee €6,000 per year", "EUR", "year", 6000, 6, 3, "Nominal duration 6 semesters (3 years)"),
     ("e29922803c2a", "Computer Science Engineering", "BSc", "Computer Engineering", "Tuition fee US$3,400 per semester", "USD", "semester", 3400, 7, 3.5, "Nominal duration 7 semesters (3.5 years)"),
     ("28b39223181f", "Civil Engineering", "BSc", "Civil Engineering", "Tuition fee US$3,400 per semester", "USD", "semester", 3400, 8, 4, "Nominal duration 8 semesters (4 years)"),
     ("0bf0ab24c4fa", "Biotechnology", "BSc", "Biology", "Tuition fee €3,500 per semester", "EUR", "semester", 3500, 6, 3, "Nominal duration 6 semesters (3 years)")]

spec("hu-pecs", ORG, ["PTE", "Pécsi Tudományegyetem"], "public", "https://international.pte.hu", ("hu", "Hungary", "HUF"), ("hu-pecs", "Pécs"),
     {"main": src(P[1][0], "Computer Science BSc | University of Pécs", ORG, ["Computer Science BSc University of Pécs Hungary, Pécs"])},
     [("international", "International students (course page fee)", "The tuition fee on each University of Pécs course page of its application portal.", "main")])

TH = ("{name}: the course page lists no grade cut-off and refers to the University of Pécs's general entry requirements "
      "(international.pte.hu/admission/entry-requirements); a motivation letter is required.")
for page, name, deg, field, fee_q, cur, per, amount, sem, years, dur_q in P:
    q = [f"{name} {deg} University of Pécs Hungary, Pécs", dur_q, "Study language English", fee_q, "A motivation letter must be adde"]
    cost = {"residency": "international", "currency": cur, "academic_year": "Course page (year not stated)", "source": "course"}
    if per == "year":
        cost.update(tuition_annual=amount, note=f"{cur} {amount:,} a year (course page; the academic year isn't stated). Living costs not added.")
    else:
        cost.update(tuition_per_semester=amount, semesters_quote=dur_q, semesters_source="course",
                    note=f"{cur} {amount:,} per semester (course page; the academic year isn't stated); yearly figure our calculation. Living costs not added.")
    prog("hu-pecs", f"{deg.lower()}-{slugify(name)}", {"course": src(page, f"{name} {deg} | University of Pécs", ORG, q)},
         {"name": name, "degree_type": deg, "field": field, "faculty": "", "duration_years": years, "duration_source": "course", "languages": ["en"],
          "entry_year": "Course page (year not stated)", "platform": "University of Pécs application portal (apply.pte.hu)", "source": "course",
          "summary": f"{name} ({deg}), University of Pécs; taught in English.", "application_requirements": []},
         [cost], adm_all({c: TH.format(name=name) for c in ("ib", "a-level", "us-hs", "cbse", "international-other")}, "course"))
    print("wrote", name)

"""University of Auckland: base records + Bachelor of Commerce and Bachelor of Engineering (Honours) (written 2026-11-26). THE queue #40.

The BSc is left out: its 2027 international fee is published only as a range (NZ$48,426 – $60,910 on the
programme page; NZ$49,581.60 - NZ$60,909.60 on the fee schedule), so no single figure can be stored.
Sources (auckland.ac.nz) per programme page: "Duration Full-time: 3 years" / "4 years", the "Outside New Zealand"
secondary-school rows (IB, GCE A Level, IELTS; "likely grades required and do not guarantee entry"), and
"2027 fees ... International students NZ$51,020 / NZ$60,910" (inclusive of 15% GST). No living costs read.
  python3 -I scripts/research/gen/nz_auckland.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all

ORG = "University of Auckland"
MIN = "Minimum requirements listed here are the likely grades required and do not guarantee entry. We assess each application individually and applicants may require a higher grade to be offered a place."
GST = "Fees are set in advance of each calendar year and will be updated on this website. Fees are inclusive of 15% G"
BC = src("4f26e69bd8b1", "Bachelor of Commerce – University of Auckland", ORG,
         ["Bachelor of Commerce – University of Auckland", "Get an idea of how much accommodation and general living in Auckland will cost.",
          "Apply now for Bachelor of Commerce Duration Full-time: 3 years", MIN,
          "Qualification IB International Baccalaureate Diploma Score required 28 + Qualification IELTS Academic International English Language Testing System Score required 6.0 No bands less than 5.5.",
          "Qualification GCE A Level/CIE General Certificate of Education Advanced Level Score required BBC",
          "2027 fees Domestic students NZ$8,698.80 * International students NZ$51,020 *", GST])
BE = src("e544df41c7d1", "Bachelor of Engineering (Honours) – University of Auckland", ORG,
         ["Apply now for Bachelor of Engineering (Honours) Duration Full-time: 4 years", MIN,
          "Qualification IB International Baccalaureate Diploma Score required 33 Mathematics and Physics at HL level",
          "Qualification GCE A Level/CIE General Certificate of Education Advanced Level Score required BBB Mathematics and Physics + Qualification IELTS Academic International English Language Testing System Score required 6.5 No bands less than 6.0.",
          "2027 fees Domestic students NZ$10,766.40 * International students NZ$60,910 *", GST,
          "Mechatronics Engineering Software Engineering Structural Engineering"])
spec("nz-auckland", ORG, [], "public", "https://www.auckland.ac.nz", ("nz", "New Zealand", "NZD"), ("nz-auckland", "Auckland"),
     {"main": BC}, [("international", "International students", "University of Auckland 2027 fees for international students.", "main")])
ENG_C = {"test_name": "IELTS Academic", "source": "course", "min_score": "IELTS Academic 6.0, no bands less than 5.5."}
ENG_E = {"test_name": "IELTS Academic", "source": "course", "min_score": "IELTS Academic 6.5, no bands less than 6.0."}
T = " (likely grade for applicants from outside New Zealand; does not guarantee entry)."
prog("nz-auckland", "bachelor-of-commerce", {"course": BC},
     {"name": "Bachelor of Commerce", "degree_type": "Bachelor", "field": "Business", "faculty": "", "duration_years": 3, "duration_source": "course",
      "languages": ["en"], "entry_year": "2027", "platform": "", "source": "course",
      "summary": "Bachelor of Commerce, University of Auckland; full-time, 3 years.", "application_requirements": []},
     [{"residency": "international", "currency": "NZD", "tuition_annual": 51020, "academic_year": "2027", "source": "course",
       "note": "International students: NZ$51,020 a year (2027 fees, inclusive of 15% GST)."}],
     adm_all({"ib": "Bachelor of Commerce: IB Diploma 28" + T, "a-level": "Bachelor of Commerce: BBC at A level (best three academic subjects)" + T}, "course", english=ENG_C))
prog("nz-auckland", "bachelor-of-engineering-honours", {"course": BE},
     {"name": "Bachelor of Engineering (Honours)", "degree_type": "Bachelor", "field": "Engineering", "faculty": "", "duration_years": 4, "duration_source": "course",
      "languages": ["en"], "entry_year": "2027", "platform": "", "source": "course",
      "summary": "Bachelor of Engineering (Honours), University of Auckland; full-time, 4 years; specialisations include Software Engineering.", "application_requirements": []},
     [{"residency": "international", "currency": "NZD", "tuition_annual": 60910, "academic_year": "2027", "source": "course",
       "note": "International students: NZ$60,910 a year (2027 fees, inclusive of 15% GST)."}],
     adm_all({"ib": "Bachelor of Engineering (Honours): IB Diploma 33 with Mathematics and Physics at HL" + T,
              "a-level": "Bachelor of Engineering (Honours): BBB at A level including Mathematics and Physics" + T},
             "course", english=ENG_E, subjects=["Mathematics", "Physics"]))
print("wrote auckland")

# Every other single bachelor's degree on "Find a study option" with one published 2027 international fee
# (added 2026-11-27). Left out: fee published as a range (BSc, BA, Communication) or not shown (Health Sciences,
# Optometry); conjoint degrees; MBChB. Admission rows only where the page gives the "Outside New Zealand" IB row.
import re
from newuni import PAGES, slugify
AFIELD = {"Bachelor of Architectural Studies": "Architecture", "Bachelor of Dance Studies": "Dance", "Bachelor of Design": "Design",
          "Bachelor of Early Childhood Studies": "Education", "Bachelor of Education (Teaching)": "Education", "Bachelor of Education (TESOL)": "Education",
          "Bachelor of Fine Arts": "Art", "Bachelor of Global Studies": "International Relations", "Bachelor of Laws": "Law", "Bachelor of Music": "Music",
          "Bachelor of Nursing": "Nursing", "Bachelor of Pharmacy": "Pharmacy", "Bachelor of Property": "Business", "Bachelor of Psychology": "Psychology",
          "Bachelor of Sport, Health and Physical Education": "Sport Science"}
for pid in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "auk_pages.txt")).read().split():
    t = re.sub(r"\s+", " ", open(PAGES / f"{pid}.txt", errors="replace").read())
    title = t.split(" – ")[0].strip()
    d = re.search(r"Apply now for " + re.escape(title) + r" Duration Full-time: (\d) years", t)
    f = re.search(r"2027 fees Domestic students NZ\$[\d,.]+ \* International students NZ\$([\d,]+) \*", t)
    if title not in AFIELD or not (d and f):
        continue
    ib = re.search(r"Qualification IB International Baccalaureate Diploma Score required (\d+)[^+]{0,80}? \+ Qualification IELTS Academic International English Language Testing System Score required ([\d.]+) No bands less than ([\d.]+)\.", t)
    al = re.search(r"Qualification GCE A Level/CIE General Certificate of Education Advanced Level Score required ([A-E*]{3})", t)
    has_min = MIN in t
    qs = [f"{title} – University of Auckland", d.group(0), f.group(0), GST] + ([MIN] if has_min else []) + ([ib.group(0)] if ib else []) + ([al.group(0)] if al else [])
    S6 = src(pid, f"{title} – University of Auckland", ORG, qs)
    fee = int(f.group(1).replace(",", ""))
    rows = {}
    if ib:
        rows["ib"] = f"{title}: IB Diploma {ib.group(1)}" + (T if has_min else " (applicants from outside New Zealand).")
    if al:
        rows["a-level"] = f"{title}: {al.group(1)} at A level" + (T if has_min else " (applicants from outside New Zealand).")
    eng = {"test_name": "IELTS Academic", "source": "course", "min_score": f"IELTS Academic {ib.group(2)}, no bands less than {ib.group(3)}."} if ib else None
    prog("nz-auckland", slugify(title), {"course": S6},
         {"name": title, "degree_type": "Bachelor", "field": AFIELD[title], "faculty": "", "duration_years": int(d.group(1)), "duration_source": "course",
          "languages": ["en"], "entry_year": "2027", "platform": "", "source": "course",
          "summary": f"{title}, University of Auckland; full-time, {d.group(1)} years.", "application_requirements": []},
         [{"residency": "international", "currency": "NZD", "tuition_annual": fee, "academic_year": "2027", "source": "course",
           "note": f"International students: NZ${fee:,} a year (2027 fees, inclusive of 15% GST)."}],
         adm_all(rows, "course", english=eng) if rows else [])
print("wrote auckland (all single bachelor's with one fee)")

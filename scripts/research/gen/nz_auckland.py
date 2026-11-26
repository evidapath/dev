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

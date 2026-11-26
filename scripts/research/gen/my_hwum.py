"""Heriot-Watt University Malaysia, Putrajaya: base records + three undergraduate degrees (written 2026-11-26).

Sources (hw.ac.uk/malaysia):
  - Fee Structure International Students 2026/27 (PDF): per programme block, "Annual Tuition Fee (RM)"
    and 6% SST per year (Years 1-3);
  - course pages: "Duration 3 years", entry by qualification (A-Level, IB Diploma), Putrajaya campus.
The 2027/28 fees aren't published yet. No English test requirement is on the pages read. No living costs.
  python3 -I scripts/research/gen/my_hwum.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify, text, norm, url

ORG = "Heriot-Watt University Malaysia"
PDF = "hwm-fee-intl-2627"
T = text(PDF)


def block(prog_name, first_row):
    """The PDF text from the programme's name to its Year 1 row, as one quote (must be short)."""
    i = T.find(norm(prog_name)); j = T.find(norm(first_row), i)
    assert i >= 0 and j > i and j - i < 900, prog_name
    return T[i:j + len(norm(first_row))]


# page, name, degree, field, PDF programme line, Year-1 row, annual tuition, SST, A-level quote, IB quote
P = [("c0f6f078214f", "Computing Science", "BSc (Hons)", "Computer Science", "Computing Science KPT/JPS (R/0613/6/0123)",
      "1 1&2 24,200.00 1,452.00 25,652.00 48,400.00 2,904.00 51,304.00", 48400, 2904,
      "A-Level: BBC including B in Mathematics", "IB Diploma : 26 points for 6 subjects including 5 in HL Mathematics AA or AI"),
     ("801bbf6e1208", "Business Administration", "BBA (Hons)", "Business", "Business Administration KPT/JPS (R2/0414/7/0079)",
      "1 1&2 24,060.00 1,443.60 25,503.60 48,120.00 2,887.20 51,007.20", 48120, 2887.2,
      "A-Level: CCC", "IB Diploma : 27 points for 6 subjects (3 HL including business and 3 SL subjects)"),
     ("195853d7bad5", "Actuarial Science", "BSc (Hons)", "Actuarial Studies", "Actuarial Science KPT/JPS (R2/0542/6/0012)",
      "1 1&2 25,960.00 1,557.60 27,517.60 51,920.00 3,115.20 55,035.20", 51920, 3115.2,
      "A-Level : BBB (including B in Mathematics)", "IB Diploma : 28 points for 6 subjects including 6 in HL, AA Mathematics (HL Analysis and Approaches Mathematics)")]

PUTRA = "Heriot-Watt University Malaysia's purpose-built, state-of-the-art, lakeside campus in Putrajaya"
spec("my-hwum", ORG, ["HWUM", "Heriot-Watt Malaysia"], "private", "https://www.hw.ac.uk/malaysia", ("my", "Malaysia", "MYR"), ("my-putrajaya", "Putrajaya"),
     {"main": src(P[0][0], "BSc (Hons) Computing Science | Heriot-Watt University Malaysia", ORG, [PUTRA])},
     [("international", "International students", "Heriot-Watt University Malaysia's 2026/27 fee structure for international students (6% SST added).", "main")])

for page, name, deg, field, pline, row, tuition, sst, al_q, ib_q in P:
    fees = {"url": url(PDF), "page": PDF, "title": "Fee Structure International Students 2026/27 (PDF) | Heriot-Watt University Malaysia",
            "organization": ORG, "quotes": ["Fee Structure International Students 2026/27", block(pline, row)]}
    course = src(page, f"{deg} {name} | Heriot-Watt University Malaysia", ORG, [f"Degree qualification {deg}", "Duration 3 years Location Malaysia", al_q, ib_q, PUTRA])
    prog("my-hwum", slugify(f"{deg} {name}"), {"course": course, "fees": fees},
         {"name": name, "degree_type": deg, "field": field, "faculty": "", "duration_years": 3, "duration_source": "course", "languages": [],
          "entry_year": "2026/27 fees (2027/28 not yet published)", "platform": "Heriot-Watt University Malaysia application", "source": "course",
          "summary": f"{deg} {name}, Heriot-Watt University Malaysia, Putrajaya; 3 years.", "application_requirements": []},
         [{"residency": "international", "currency": "MYR", "tuition_annual": tuition, "mandatory_fees_annual": sst, "academic_year": "2026/27", "source": "fees",
           "note": f"2026/27 international: annual tuition RM{tuition:,} plus 6% SST RM{sst:,.2f} a year (shown as compulsory fees)."}],
         adm_all({"a-level": f"{name}: {al_q.split(':', 1)[1].strip()} at A-Level.", "ib": f"{name}: {ib_q.split(':', 1)[1].strip()}."}, "course"))
    print("wrote", name)

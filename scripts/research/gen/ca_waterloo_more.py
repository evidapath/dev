"""More University of Waterloo majors (written 2026-11-19), same pattern as ca_waterloo.py. Each
programme page names the admission group it is applied to (Life Sciences, Physical Sciences,
Honours Arts, Mathematics); the requirements come from that group's international-system pages
(British, IB, American) and the fee from that faculty's block of the Fall 2026 international fee
schedule (maximum tuition per term, Regular Year 1).
  python3 -I scripts/research/gen/ca_waterloo_more.py
"""
import hashlib, re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write
import ca_waterloo as W   # shared sources (regular system, deadlines, fee schedule, Life Sciences pages); re-writes its two files unchanged

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
pid = lambda u: hashlib.sha1(u.encode()).hexdigest()[:12]
flat = lambda u: re.sub(r"\s+", " ", (PAGES / f"{pid(u)}.txt").read_text())
P = "https://uwaterloo.ca/future-students/programs/"
R = "https://uwaterloo.ca/future-students/admissions/admission-requirements/"
FEES_URL = W.SRC["fees"]["url"]
FEE_HEAD = "Fees below are for Fall 2026 term only."
ORG = "University of Waterloo"


def req_sources(group, title_head, ib, uk, us):
    out = {}
    for key, sysname, label, quotes in (("uk", "british-system", "British System (A Levels)", uk), ("ib", "ib", "International Baccalaureate (IB)", ib),
                                        ("us", "american-system", "American (US) system", us)):
        url = f"{R}{group}/high-school/international-system/{sysname}/"
        title = f"{title_head} admission requirements for {label} high school students | Undergraduate Programs | University of Waterloo"
        assert flat(url).startswith(title), (url, flat(url)[:200])
        for q in quotes:
            assert q in flat(url), (url, q)
        out[key] = {"url": url, "page": pid(url), "title": title, "organization": ORG, "quotes": quotes}
    return out


def fee_source(row):
    for q in (FEE_HEAD, row):
        assert q in flat(FEES_URL), q
    return {"url": FEES_URL, "page": pid(FEES_URL), "title": W.SRC["fees"]["title"], "organization": ORG,
            "quotes": [FEE_HEAD, *W.SRC["fees"]["quotes"][1:4], row]}


def wl(slug, path, name, deg, full, field, faculty, course_quotes, group_name, reqs, fees, per_term, incidental, fee_label, adm, app_reqs=()):
    url = P + path
    title = f"{name} degree | Undergraduate Programs | University of Waterloo"
    t = flat(url)
    assert t.startswith(title), (url, t[:100])
    for q in course_quotes:
        assert q in t, (url, q)
    srcs = {"course": {"url": url, "page": pid(url), "title": title, "organization": ORG, "quotes": course_quotes},
            "reg": W.SRC["reg"], **reqs, "dl": W.SRC["dl"], "fees": fees}
    where = faculty if group_name == name else f"{group_name}, {faculty}"
    a = lambda cur, src, th, subj: {"curriculum": cur, "source": src, "threshold": f"{name} ({where}): {th}",
                                    "required_subjects": subj, "tests": [], "english": W.ENG}
    write(W.SUB, {"uni": W.U, "slug": slug, "sources": srcs,
        "program": {"name": name, "degree_type": deg, "field": field, "faculty": faculty, "duration_years": 4, "languages": ["en"],
                    "entry_year": "2026-2027 (Fall 2027 entry)", "platform": "OUAC", "source": "course", "duration_source": "reg",
                    "summary": f"{name}, {full}, applied to through {group_name} ({faculty}; regular system of study, co-op also offered).",
                    "application_requirements": list(app_reqs)},
        "costs": [{"residency": "international", "currency": "CAD", "tuition_per_term": per_term, "terms_per_year": 2,
                   "terms_evidence": ["fall term – September to December", "winter term – January to April"],
                   "academic_year": f"Fall 2026 rate ({fee_label}, regular, maximum tuition per term × fall and winter terms)", "source": ["fees", "reg"],
                   "mandatory_per_term": incidental, "living_from": "costProfile-ca-waterloo-cost-bsc-cs-international",
                   "note": f"International, {fee_label}, Regular Year 1: maximum tuition CAD {per_term:,.2f} per term (Fall 2026), billed one term at a time; regular students are in school September to April (fall and winter terms). Incidental fees CAD {incidental:,.2f} per full-time term."}],
        "deadline": {"date": "2027-02-01", "source": "dl", "round": "Application (OUAC)", "platform": "OUAC", "note": "Programs other than Engineering. Documents due February 15, 2027."},
        "admissions": [a(*x) for x in adm]})
    print(slug, deg, per_term)


# Life Sciences (Biochemistry joins Biology and Psychology; same sources as ca_waterloo.py)
LS = {k: W.SRC[k] for k in ("uk", "ib", "us")}
SCI = W.SRC["fees"]
SCI_ADM = [("a-level", "uk", "A-Level Maths (B), two of Biology, Chemistry or Physics (B, one at A-Level), one other A-Level (B) and GCSE English (B/5); passes in five subjects, three at A-Level.", ["Mathematics", "two of Biology, Chemistry, Physics"]),
           ("ib", "ib", "IB Diploma (six courses, at least three HL) with Maths Analysis and Approaches (HL or SL, minimum 4), English A (minimum 4, or HL English B 5) and two of Biology, Chemistry or Physics; total 27, excluding diploma points.", ["Mathematics", "two of Biology, Chemistry, Physics"]),
           ("us-hs", "us", "AP or Grade 12 Calculus, Grade 12 English and Pre-Calculus (each at least 75%), two of Biology, Chemistry, Physics or Statistics, one other Grade 12 academic or AP course; overall Grade 12 average at least 85%.", ["Mathematics", "English"])]
wl("bsc-biochemistry", "biochemistry", "Biochemistry", "BSc", "Bachelor of Science", "Biochemistry", "Faculty of Science",
   ["Bachelor of Science in Biochemistry", "Apply to Life Sciences and select Biochemistry as your major.", "Faculty of Science"],
   "Life Sciences", LS, SCI, 25296, 1190.59, "Science programs", SCI_ADM)

# Physical Sciences: the same three requirement lines as Life Sciences, on the group's own pages
PS = req_sources("physical-sciences", "Physical Sciences (includes eight majors in Chemistry, Physics, Earth Sciences, Materials and Nanosciences)",
                 ib=W.SRC["ib"]["quotes"], uk=W.SRC["uk"]["quotes"], us=W.SRC["us"]["quotes"])
for slug, path, name, cq in [("bsc-physics", "physics", "Physics", ["Bachelor of Science in Physics", "Apply to Physical Sciences and select Physics as your major in first year.", "Faculty of Science"]),
                             ("bsc-chemistry", "chemistry", "Chemistry", ["Bachelor of Science in Chemistry", "Apply to Physical Sciences and choose Chemistry as your major.", "Faculty of Science"])]:
    wl(slug, path, name, "BSc", "Bachelor of Science", name, "Faculty of Science", cq, "Physical Sciences", PS, SCI, 25296, 1190.59, "Science programs", SCI_ADM)

# Honours Arts (Faculty of Arts)
HA = req_sources("honours-arts", "Honours Arts (includes 28 majors)",
                 ib=["HL or SL English A - minimum 4 or HL English B - minimum 5; total 27", "IB diploma required with six total IB courses; at least three must be HL.", "Total scores exclude diploma points."],
                 uk=["Three A Level courses, minimum final grade of two B's and one C. English at either the GCSE, AS, or A Level, minimum final grade of B/5.", "Passes in at least five unique subjects, three of which must be at the Advanced Level"],
                 us=["Grade 12 English, minimum final grade of 75%. Minimum Grade 12 average of low 80s."])
ARTS_ROW = "Arts programs Faculty/Program Price per 0.5 unit course Maximum tuition per term Co-op fee Incidental fees (including HST) FT = 1.5 or more units PT = fewer than 1.5 units Regular Year 1 $5,402.00 $27,010.00 - $1,143.94 FT"
ARTS_ADM = [("a-level", "uk", "three A-Levels with minimum final grades of two Bs and one C, and English at GCSE, AS or A-Level (minimum B/5); passes in five subjects, three at A-Level.", ["English"]),
            ("ib", "ib", "IB Diploma (six courses, at least three HL) with English A (HL or SL, minimum 4, or HL English B 5); total 27, excluding diploma points.", ["English"]),
            ("us-hs", "us", "Grade 12 English (minimum 75%) and a Grade 12 average in the low 80s (no exact figure published).", ["English"])]
for slug, path, name, field, degline in [("ba-political-science", "political-science", "Political Science", "Politics", "Bachelor of Arts in Political Science"),
                                         ("ba-history", "history", "History", "History", "Bachelor of Arts in History"),
                                         ("ba-english", "english", "English", "English", "Bachelor of Arts in one of the four English majors"),
                                         ("ba-philosophy", "philosophy", "Philosophy", "Philosophy", "Bachelor of Arts in Philosophy")]:
    wl(slug, path, name, "BA", "Bachelor of Arts", field, "Faculty of Arts",
       [degline, f"You can choose to study {name} through Honours Arts or Honours Arts and Business .", "Faculty of Arts"],
       "Honours Arts", HA, fee_source(ARTS_ROW), 27010, 1143.94, "Arts programs", ARTS_ADM)

# Mathematics (Faculty of Mathematics; Admission Information Form required)
MA = req_sources("mathematics", "Mathematics (includes 16 majors)",
                 ib=["HL Mathematics: Analysis and Approaches, minimum 6; HL or SL English A. Total 30. The Admission Information Form is required for admission to this program.",
                     "IB diploma required with six total IB courses; at least three must be HL.", "Total scores exclude diploma points."],
                 uk=["A Level Mathematics, minimum final grade of A", "Two other academic A Level courses, minimum final grade of A in each", "English at either the GCSE, AS, or A Level",
                     "Passes in at least five unique subjects, three of which must be at the Advanced Level"],
                 us=["AP Calculus, minimum final grade of 4.", "Algebra (Pre-Calculus).", "Grade 12 English.", "Minimum overall Grade 12 average: 88%.",
                     "SAT and ACT test scores are not required for admission."])
MATH_ROW = "Mathematics programs Faculty/ Program Price per 0.5 unit course Maximum tuition per term Co-op fee Incidental fees (including HST) FT = 1.5 or more units PT = fewer than 1.5 units Math - Regular Year 1 $5,851.80 $29,259.00 - $1,171.91 FT"
wl("bmath-mathematics", "mathematics", "Mathematics", "BMath", "Bachelor of Mathematics", "Mathematics", "Faculty of Mathematics",
   ["Bachelor of Mathematics in one of 16 majors", "Apply to Mathematics and choose one of the majors listed above at the end of first year.",
    "The Admission Information Form is required for admission.", "Faculty of Mathematics"],
   "Mathematics", MA, fee_source(MATH_ROW), 29259, 1171.91, "Mathematics programs",
   [("a-level", "uk", "A-Level Mathematics (minimum A) and two other academic A-Levels (minimum A in each); English at GCSE, AS or A-Level; passes in five subjects, three at A-Level. Admission Information Form required.", ["Mathematics"]),
    ("ib", "ib", "IB Diploma (six courses, at least three HL) with HL Maths Analysis and Approaches (minimum 6) and English A (HL or SL); total 30, excluding diploma points. Admission Information Form required.", ["Mathematics", "English"]),
    ("us-hs", "us", "AP Calculus (minimum 4), Pre-Calculus and Grade 12 English; overall Grade 12 average at least 88%. SAT/ACT not required. Admission Information Form required.", ["Mathematics", "English"])],
   app_reqs=[{"name": "Admission Information Form", "description": "The Admission Information Form is required for admission.", "type": "form", "source": "course"}])

"""More University of Toronto (St. George, Faculty of Arts & Science) programmes (written
2026-11-18), same pattern as ca_ut.py. The requirement rows are taken programmatically from the
St. George section of each saved requirement view (ut-<key>-ib/uk/us, saved with utreq.sh),
never from another campus. Fees: Arts & Science international program fee 2026/27, Year 1
(all admission streams) and Year 2 or higher (Honours BSc or Honours BA), from Tuition Explorer.
  python3 -I scripts/research/gen/ca_ut_more.py
"""
import re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
SUB, U = "ca-majors", "ca-university-of-toronto"
FU = "https://tuitionexplorer.registrar.utoronto.ca/index.php?academicYear=2026-27&sessionType=1&studyLevel=UG&residency=INT&campus=UTSG&faculty=ARTSC-UG"
ENG = {"from_existing": "admissionsRequirement-ca-university-of-toronto-admreq-ba-economics-ib"}
HEAD = {"ib": "INTERNATIONAL BACCALAUREATE REQUIREMENTS", "uk": "BRITISH-PATTERNED EDUCATION REQUIREMENTS", "us": "U.S.-PATTERNED EDUCATION REQUIREMENTS"}
GEN = {"ib": "Complete Diploma, including English.",
       "uk": "Five different IGCSE/GCSE/Ordinary Level academic subjects and three different A Level/International A Level academic subjects.",
       "us": "High School Diploma from an accredited high school. We expect competitive applicants to be enrolled in a rigorous academic course load, and to have taken the highest level of course available to them in prerequisite subjects."}
YEAR1 = {"url": FU, "page": "ut-fee-207", "title": "Tuition Explorer 2026/27, Arts & Science, international | University of Toronto", "organization": "University of Toronto",
         "quotes": ["Admission Streams Year 1: Commerce, Computer Science, Humanities, Life Sciences, Mathematical and Physical Sciences, and Social Sciences",
                    "Students with fewer than 4.0 credits completed $66,110.00 $2,100.29 $948.00 $69,158.29"]}
YEAR2 = {"HBSc": {"url": FU, "page": "ut-fee-199", "title": "Tuition Explorer 2026/27, Arts & Science, international | University of Toronto", "organization": "University of Toronto",
                  "quotes": ["2026/27 Fall and Winter", "(Honours) Bachelor of Science - Year 2 or Higher", "Students with 4.0 or more credits completed $66,110.00 $2,100.29 $948.00 $69,158.29"]},
         "HBA": {"url": FU + "&program=7", "page": "e879706074f4", "title": "Tuition Explorer 2026/27, Arts & Science, international, Honours BA Year 2 or higher | University of Toronto", "organization": "University of Toronto",
                 "quotes": ["(Honours) Bachelor of Arts - Year 2 or Higher International Full-time Program Fee", "Students with 4.0 or more credits completed $66,110.00 $2,135.97 $948.00 $69,193.97", "2026/27 Fall and Winter"]}}
SUBJ = {"Math (Calculus)": "Mathematics", "Math": "Mathematics"}


def st_george(key, sysname):
    ls = [l.strip() for l in (PAGES / f"ut-{key}-{sysname}.txt").read_text().splitlines()]
    i = ls.index("St. George campus")
    assert ls[i + 1] == "Faculty of Arts & Science", ls[i:i + 2]
    h = ls.index(HEAD[sysname], i)
    title_line = next(l for l in ls[i:h] if re.match(r"(HBSc|HBA)\t", l) or re.search(r"\t(HBSc|HBA)\t", l))
    j = ls.index("Change School System", h)
    rows = []
    for l in ls[j + 1:]:
        if "\t" not in l:
            break
        rows.append(l)
    assert ls[h + 1].startswith(GEN[sysname][:40]), (key, sysname, ls[h + 1][:60])
    return title_line, rows


def describe(rows):
    req, rec = [], []
    for r in rows:
        label, what = r.split("\t", 1)
        (rec if label.endswith("RECOMMENDED") else req).append(label.replace(" RECOMMENDED", ""))
    return req, rec


def build(slug, path, key, name, field):
    url = f"https://future.utoronto.ca/program/{path}"
    t = f"{name} | Future Students, University of Toronto"
    out = {}
    for s in ("ib", "uk", "us"):
        out[s] = st_george(key, s)
    deg = re.search(r"\b(HBSc|HBA)\b", out["ib"][0]).group(1)
    code = out["ib"][0].split("\t")[-1].strip()
    assert all(out[s][0] == out["ib"][0] for s in out), "program line differs between views"
    q = lambda rows: [r.replace("\t", " ") for r in rows]
    srcs = {
        "course": {"url": url, "page": f"ut-{key}-ib", "title": t, "organization": "University of Toronto",
                   "quotes": ["St. George campus Faculty of Arts & Science", out["ib"][0].replace("\t", " "), GEN["ib"], *q(out["ib"][1])]},
        "uk": {"url": url, "page": f"ut-{key}-uk", "title": t + " (British-patterned requirements)", "organization": "University of Toronto", "quotes": [GEN["uk"], *q(out["uk"][1])]},
        "us": {"url": url, "page": f"ut-{key}-us", "title": t + " (U.S.-patterned requirements)", "organization": "University of Toronto", "quotes": [GEN["us"], *q(out["us"][1])]},
        "fees": YEAR1, "fees2": YEAR2[deg]}

    def th(sysname, lead):
        rq, rc = describe(out[sysname][1])
        return f"{lead} Required: {', '.join(rq)}." + (f" Recommended: {', '.join(rc)}." if rc else "")

    def subj(sysname):
        rq, _ = describe(out[sysname][1])
        return sorted({SUBJ.get(x, x) for x in rq})

    a = lambda cur, src, text, sj: {"curriculum": cur, "source": src, "required_subjects": sj, "tests": [], "english": ENG,
                                    "threshold": f"{name} (St. George, Arts & Science, OUAC {code}): {text} Admission is competitive."}
    full = "Honours Bachelor of Science" if deg == "HBSc" else "Honours Bachelor of Arts"
    write(SUB, {"uni": U, "slug": slug, "sources": srcs,
        "program": {"name": name, "degree_type": deg, "field": field, "faculty": "Faculty of Arts & Science", "duration_years": 4, "languages": ["en"],
                    "entry_year": "2026-2027 (Fall 2027 entry)", "platform": "OUAC", "source": "course",
                    "summary": f"{name}, {full} ({deg}), Faculty of Arts & Science, St. George campus. Apply through OUAC (code {code}).", "application_requirements": []},
        "college": {"from": "program-ca-university-of-toronto-ba-economics", "quote": "St. George campus Faculty of Arts & Science", "copy": []},
        "costs": [{"residency": "international", "currency": "CAD", "tuition_annual": 66110,
                   "academic_year": f"2026/27 (Arts & Science international program fee; Year 1 and {full} Year 2 or higher)", "source": ["fees", "fees2"],
                   "fees_from": "costProfile-ca-university-of-toronto-cost-ba-economics-international",
                   "living_from": "costProfile-ca-university-of-toronto-cost-ba-economics-international",
                   "note": f"International program fee 2026/27: CAD 66,110 for Year 1 (all Arts & Science admission streams) and CAD 66,110 for the {full} from Year 2. Incidental and system access fee and UHIP (CAD 948) are extra."}],
        "admissions": [a("ib", "course", th("ib", "complete IB Diploma including English."), subj("ib")),
                       a("a-level", "uk", th("uk", "five different IGCSE/GCSE/O-Level subjects and three different A-Levels."), subj("uk")),
                       a("us-hs", "us", th("us", "a high school diploma from an accredited school."), subj("us"))]})
    print(slug, deg, code, [describe(out[s][1]) for s in ("ib", "uk", "us")])


for c in [("hbsc-mathematics", "mathematics", "math", "Mathematics", "Mathematics"),
          ("hbsc-physics", "physics", "phys", "Physics", "Physics"),
          ("hbsc-chemistry", "chemistry", "chem", "Chemistry", "Chemistry"),
          ("hba-political-science", "political-science", "pol", "Political Science", "Politics"),
          ("hba-history", "history", "hist", "History", "History"),
          ("hba-english", "english", "eng", "English", "English")]:
    build(*c)

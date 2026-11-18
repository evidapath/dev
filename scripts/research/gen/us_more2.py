"""USC and ASU majors (written 2026-11-19): same-college reuse, as in us_rest.py and us_more.py.
USC: degree names from the 2026-2027 catalogue's Programs by School page (Dornsife section, the
same school as Economics). ASU: Tempe degree pages of The College of Liberal Arts and Sciences
(the same college as Psychology and Biological Sciences), each saying applicants meet the
general university admission requirements; plan codes from ASU's degree search.
  python3 -I scripts/research/gen/us_more2.py
"""
import hashlib, re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from us import major

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
pid = lambda u: hashlib.sha1(u.encode()).hexdigest()[:12]
flat = lambda u: re.sub(r"\s+", " ", (PAGES / f"{pid(u)}.txt").read_text())

# USC: the Dornsife block of Programs by School runs from its heading to the next school's
U = "https://catalogue.usc.edu/content.php?catoid=22&navoid=9453"
t = flat(U)
HEAD = "USC Dornsife College of Letters, Arts and Sciences Go to information for USC Dornsife College of Letters, Arts and Sciences."
i = t.index(HEAD)
block = t[i:t.index("Go to information for", i + len(HEAD))]
block = block[:block.index("Minor")]   # bachelor's list only
for slug, name, deg, field in [("mathematics", "Mathematics", "BS", "Mathematics"), ("physics", "Physics", "BS", "Physics"),
                               ("chemistry", "Chemistry", "BS", "Chemistry"), ("biochemistry", "Biochemistry", "BS", "Biochemistry"),
                               ("political-science", "Political Science", "BA", "Politics"),
                               ("international-relations", "International Relations", "BA", "International Relations"),
                               ("history", "History", "BA", "History"), ("english", "English", "BA", "English"),
                               ("philosophy", "Philosophy", "BA", "Philosophy"), ("psychology", "Psychology", "BA", "Psychology")]:
    q = f"{name} ({deg})"
    assert f"• {q} •" in block, q
    other = "BA" if deg == "BS" else "BS"
    also = f"; a {other} is also offered" if f"• {name} ({other}) •" in block else ""
    major("us-usc", slug, U, pid(U), "Programs by School - USC Catalogue 2026-2027", "University of Southern California",
          ["USC Catalogue 2026-2027", "USC Dornsife College of Letters, Arts and Sciences", "Bachelor’s Degree", q],
          name, deg, field, "USC Dornsife College of Letters, Arts and Sciences", 4,
          f"{name} ({deg}{also}), USC Dornsife College of Letters, Arts and Sciences (the same school as Economics).",
          "program-us-usc-economics", "USC Dornsife College of Letters, Arts and Sciences")
print("usc ok")

# ASU: Tempe, The College of Liberal Arts and Sciences
BQ = "All students are required to meet general university admission requirements."
for code, slug, name, deg, field in [("LAMATBS", "mathematics", "Mathematics", "BS", "Mathematics"), ("LAPHYBS", "physics", "Physics", "BS", "Physics"),
                                     ("LACHMBS", "chemistry", "Chemistry", "BS", "Chemistry"), ("LABCHBS", "biochemistry", "Biochemistry", "BS", "Biochemistry"),
                                     ("LAPOSBA", "political-science", "Political Science", "BA", "Politics"), ("LAHISBA", "history", "History", "BA", "History"),
                                     ("LAPHIBA", "philosophy", "Philosophy", "BA", "Philosophy")]:
    url = f"https://degrees.apps.asu.edu/bachelors/major/ASU00/{code}/{slug}"
    t = flat(url)
    title = t.split(" Skip to main content")[0].strip()
    assert title.startswith(f"{name} Degree, {deg} |"), title
    for q in (BQ, f"Plan code: {code}", "The College of Liberal Arts and Sciences", "Tempe"):
        assert q in t, (code, q)
    major("us-asu", slug, url, pid(url), title, "Arizona State University",
          [title, f"Plan code: {code}", BQ], name, deg, field, "The College of Liberal Arts and Sciences", 4,
          f"{name}, {deg} (The College of Liberal Arts and Sciences, Tempe). Applicants meet the university's general admission requirements.",
          "program-us-asu-bs-economics", BQ)
print("asu ok")

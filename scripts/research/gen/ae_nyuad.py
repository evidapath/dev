"""NYU Abu Dhabi majors (written 2026-11-19): same-university reuse of Economics' admission and fee
records (NYUAD admits to the university; "Students declare a major by the end of their second
year."). Degree per major from the NYU Bulletin page (NYU Abu Dhabi › Programs › <Major> (BA/BS)),
checked against NYUAD's own rule (BA for Arts and Humanities, Social Science and Psychology; BS for
Engineering and Science). Psychology is held: the Bulletin says BS, NYUAD's page says BA.
Writes to us-majors (us.major's folder).
  python3 -I scripts/research/gen/ae_nyuad.py
"""
import hashlib, re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from us import major

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
pid = lambda u: hashlib.sha1(u.encode()).hexdigest()[:12]
flat = lambda u: re.sub(r"\s+", " ", (PAGES / f"{pid(u)}.txt").read_text())

GR = "https://nyuad.nyu.edu/en/about/administration-and-governance/graduation-requirements-undergraduate.html"
DECL = "Students declare a major by the end of their second year."
BA = "Students who major in the Arts and Humanities, Social Science, and Psychology, and who complete all the degree and other graduation requirements earn the BA degree."
BS = "The BS degree is awarded to students who major in Engineering or Science (except Psychology) and who complete all the degree and other graduation requirements."
for q in (DECL, BA, BS):
    assert q in flat(GR), q
MORE = {"grad": {"url": GR, "page": pid(GR), "title": "Graduation Requirements for Undergraduates | NYU Abu Dhabi", "organization": "NYU Abu Dhabi",
                 "quotes": [DECL, BA, BS]}}

for slug, name, deg, field, division in [
        ("mathematics-bs", "Mathematics", "BS", "Mathematics", "Science"), ("physics-bs", "Physics", "BS", "Physics", "Science"),
        ("chemistry-bs", "Chemistry", "BS", "Chemistry", "Science"), ("biology-bs", "Biology", "BS", "Biology", "Science"),
        ("political-science-ba", "Political Science", "BA", "Politics", "Social Science"), ("history-ba", "History", "BA", "History", "Arts and Humanities"),
        ("philosophy-ba", "Philosophy", "BA", "Philosophy", "Arts and Humanities"),
        ("mechanical-engineering-bs", "Mechanical Engineering", "BS", "Mechanical Engineering", "Engineering"),
        ("civil-engineering-bs", "Civil Engineering", "BS", "Civil Engineering", "Engineering"),
        ("electrical-engineering-bs", "Electrical Engineering", "BS", "Electrical and Electronic Engineering", "Engineering")]:
    url = f"https://bulletins.nyu.edu/undergraduate/abu-dhabi/programs/{slug}/"
    t = flat(url)
    crumb = f"NYU Abu Dhabi › Programs › {name} ({deg})"
    title = f"{name} ({deg}) | NYU Bulletins"
    assert t.startswith(title) and crumb in t, (slug, t[:80])
    major("ae-nyu-abu-dhabi", slug, url, pid(url), title, "New York University", [title, crumb], name, deg, field, "", 4,
          f"{name} ({deg}), NYU Abu Dhabi. Students are admitted to NYUAD and declare a major by the end of their second year.",
          "program-ae-nyu-abu-dhabi-ba-economics", DECL, more_sources=MORE)
    print(slug)

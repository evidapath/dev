"""More US majors (written 2026-11-18): same-college reuse, as in us_rest.py. Each major reuses
the admission and fee records of an existing programme in the same college, with a quote from
the university saying so. Degree lines are lifted from the saved catalog pages.
  python3 -I scripts/research/gen/us_more.py
"""
import hashlib, re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from us import major

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
pid = lambda u: hashlib.sha1(u.encode()).hexdigest()[:12]
lines = lambda u: [l.strip() for l in (PAGES / f"{pid(u)}.txt").read_text().splitlines()]
flat = lambda u: re.sub(r"\s+", " ", (PAGES / f"{pid(u)}.txt").read_text())
first_sentence = lambda s: re.match(r"(.+?\.)(\s|$)", s).group(1)

# Harvard: concentrations page tags each concentration with its degree (B.A.) and division
U = "https://college.harvard.edu/academics/liberal-arts-sciences/concentrations"
CQ = 'At Harvard College, students choose a "concentration," which is what we call a major.'
ls = lines(U)
for slug, name, field in [("mathematics", "Mathematics", "Mathematics"), ("physics", "Physics", "Physics"),
                          ("chemistry", "Chemistry", "Chemistry"), ("government", "Government", "Politics"),
                          ("history", "History", "History"), ("english", "English", "English"),
                          ("philosophy", "Philosophy", "Philosophy")]:
    i = next(k for k in range(len(ls) - 1) if ls[k] == name and ls[k + 1] == "B.A.")
    tag = " ".join(ls[i:i + 3])
    desc = first_sentence(ls[i + 3])
    major("us-harvard", slug, U, pid(U), "Concentrations | Harvard College", "Harvard College", [CQ, tag, desc],
          name, "BA", field, "", 4,
          f"{name} concentration (B.A.), Harvard College. The concentration (major) is chosen at Harvard College after admission.",
          "program-us-harvard-economics", CQ)

# Penn: majors of the School of Arts & Sciences (the same school as Economics)
U = "https://catalog.upenn.edu/undergraduate/arts-sciences/majors/"
for slug, name, field in [("mathematics", "Mathematics", "Mathematics"), ("physics", "Physics", "Physics"),
                          ("chemistry", "Chemistry", "Chemistry"), ("biochemistry", "Biochemistry", "Biochemistry"),
                          ("political-science", "Political Science", "Politics"), ("international-relations", "International Relations", "International Relations"),
                          ("history", "History", "History"), ("english", "English", "English"), ("philosophy", "Philosophy", "Philosophy")]:
    major("us-upenn", slug, U, pid(U), "Majors | School of Arts & Sciences | University of Pennsylvania Catalog", "University of Pennsylvania",
          ["School of Arts & Sciences", f"{name}, BA"], name, "BA", field, "School of Arts & Sciences", 4,
          f"{name}, BA, a major in Penn's School of Arts & Sciences (the same school as Economics).",
          "program-us-upenn-economics", "School of Arts & Sciences")

# MIT: one admission to MIT; majors declared in the first or second year
REG = {"reg": {"url": "https://registrar.mit.edu/registration-academics/academic-requirements/majors-minors/declaring-major", "page": "b39aefafe459",
               "title": "Declaring a major | MIT Registrar's Office", "organization": "MIT Registrar's Office",
               "quotes": ["Most students declare a major in the spring term of their first year at MIT. Those who do not must decide on a major by the end of their sophomore year."]}}
MQ = REG["reg"]["quotes"][0]
for slug, path, name, field, course in [
        ("mathematics-18", "mathematics-course-18", "Mathematics", "Mathematics", "Course 18"),
        ("physics-8", "physics-course-8", "Physics", "Physics", "Course 8"),
        ("chemistry-5", "chemistry-course-5", "Chemistry", "Chemistry", "Course 5"),
        ("mechanical-engineering-2", "mechanical-engineering-course-2", "Mechanical Engineering", "Mechanical Engineering", "Course 2"),
        ("aerospace-engineering-16", "aerospace-engineering-course-16", "Aerospace Engineering", "Aerospace Engineering", "Course 16"),
        ("chemical-engineering-10", "chemical-engineering-course-10", "Chemical Engineering", "Chemical Engineering", "Course 10"),
        ("political-science-17", "political-science-course-17", "Political Science", "Politics", "Course 17")]:
    url = f"https://catalog.mit.edu/degree-charts/{path}/"
    q = f"{name} (SB, {course})"
    assert q in flat(url), q
    major("us-mit", slug, url, pid(url), f"{name} ({course}) | MIT Course Catalog", "Massachusetts Institute of Technology", [q],
          name, "SB", field, "", 4,
          f"{name} ({course}), Bachelor of Science (SB). MIT students declare a major in the first or second year.",
          "program-us-mit-econ-14-1", MQ, more_sources=REG)

# Stanford: majors are selected by the end of sophomore year
SB = {"pol": {"url": "https://bulletin.stanford.edu/academic-polices/degree-requirements/undergraduate-major", "page": "bb90f314bec2",
              "title": "Undergraduate Majors | Stanford Bulletin", "organization": "Stanford University",
              "quotes": ["Undergraduates must select a major by the end of their sophomore year."]}}
SQ = SB["pol"]["quotes"][0]
for slug, code, name, field, school in [("mathematics", "MATH-BS", "Mathematics", "Mathematics", "School of Humanities & Sciences"),
                                        ("chemistry", "CHEM-BS", "Chemistry", "Chemistry", "School of Humanities & Sciences"),
                                        ("mechanical-engineering", "ME-BS", "Mechanical Engineering", "Mechanical Engineering", "School of Engineering")]:
    url = f"https://bulletin.stanford.edu/programs/{code}"
    q = f"{name} {school} Major Minor Program Info About the Program Major: Bachelor of Science"
    assert q in flat(url), q
    major("us-stanford", slug, url, pid(url), f"{code} - {name} (BS) | Stanford Bulletin", "Stanford University", [q],
          name, "BS", field, school, 4,
          f"{name}, Bachelor of Science (BS), {school}. Stanford undergraduates select a major by the end of sophomore year.",
          "program-us-stanford-economics", SQ, more_sources=SB)

# Cornell: majors of the College of Arts and Sciences (the same college as Economics)
for slug, path, name, field in [("mathematics", "mathematics-ba", "Mathematics", "Mathematics"), ("physics", "physics-ba", "Physics", "Physics"),
                                ("chemistry", "chemistry-ba", "Chemistry", "Chemistry"), ("government", "government-ba", "Government", "Politics"),
                                ("history", "history-ba", "History", "History"), ("english", "english-ba", "English", "English")]:
    url = f"https://courses.cornell.edu/programs/{path}/"
    q = f"{name} (BA) College of Arts and Sciences Program Website"
    assert q in flat(url), q
    major("us-cornell", slug, url, pid(url), f"{name} (BA) | Cornell University Courses of Study", "Cornell University", [q],
          name, "BA", field, "College of Arts and Sciences", 4,
          f"{name} (BA) in the College of Arts and Sciences (the same college as Economics).",
          "program-us-cornell-economics", q)

# NYU: College of Arts and Science (the same college as Economics)
for slug, path, name, field in [("mathematics", "mathematics-ba", "Mathematics", "Mathematics"), ("physics", "physics-ba", "Physics", "Physics"),
                                ("chemistry", "chemistry-ba", "Chemistry", "Chemistry"), ("politics", "politics-ba", "Politics", "Politics"),
                                ("history", "history-ba", "History", "History")]:
    url = f"https://bulletins.nyu.edu/undergraduate/arts-science/programs/{path}/"
    major("us-nyu", slug, url, pid(url), f"{name} (BA) | NYU Bulletins", "New York University", [f"{name} (BA)", "College of Arts and Science"],
          name, "BA", field, "College of Arts and Science", 4,
          f"{name} (BA), College of Arts and Science (the same college as Economics).",
          "program-us-nyu-economics", "College of Arts and Science")
print("ok")

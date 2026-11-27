"""US majors from each college's own official list of majors (written 2026-11-27). Every major reuses the fees
and living costs of the college's verified Computer Science record (builder 'college' option, costs only: these
universities publish no grade threshold, so there are no entry rows to copy). Length 4 years from that record.
  python3 -I scripts/research/gen/us_majors.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write
from newuni import src, slugify, text, PAGES

from us_fields import KEYS, field_for  # noqa: E402


def majors(uni, source, base, college_quote, faculty, items, skip=(), fmt="{name} ({deg})"):
    """items: (name, degree) pairs that each appear on the source page as "<name> (<degree>)"."""
    t = text(source["page"])
    n = 0
    for it in items:
        name, deg = it[0], it[1]
        if name in skip:
            continue
        q = it[2] if len(it) > 2 else fmt.format(name=name, deg=deg)
        fac = faculty(name) if callable(faculty) else faculty
        src_ = dict(source, quotes=list(source["quotes"]) + [q])
        assert all(re.sub(r"\s+", " ", x.replace("’", "'")).strip().lower() in t for x in src_["quotes"]), q
        write(uni, {"uni": uni, "slug": slugify(f"{deg} {name}"), "sources": {"course": src_},
                    "program": {"name": name, "degree_type": deg, "field": field_for(name), "faculty": fac, "duration_years": 4,
                                "languages": ["en"], "entry_year": "2026-27", "platform": "", "source": "course",
                                "summary": f"{name} ({deg}), {fac}; same college fees as the university's other majors.",
                                "application_requirements": []},
                    "college": {"from": base, "quote": college_quote, "copy": ["costs"]}, "costs": [], "admissions": []})
        n += 1
    return n


# Yale College: "Majors in Yale College" (Yale College Programs of Study 2026–2027)
Y = src("4499ee1af2d3", "Majors in Yale College < Yale University", "Yale University",
        ["Yale College Programs of Study 2026–2027", "Majors in Yale College"])
t = re.sub(r"\s+", " ", (PAGES / "4499ee1af2d3.txt").read_text())
block = t.replace("South Asian Studies (second major only) ", "")
block = block[block.index("General Information Majors in Yale College") + len("General Information Majors in Yale College"):block.index("Yale Accessibility at Yale")]
items = re.findall(r"\s*(.+?) \((B\.A\.|B\.S\.|B\.A\. or B\.S\.)\)", block)
print("yale", majors("us-yale", Y, "program-us-yale-bs-computer-science", "Majors in Yale College", "Yale College", items,
                     skip={"Computer Science", "Special Divisional Major"}))

# Carnegie Mellon: Degrees Offered (2026-2027 Catalog), Pittsburgh degrees only (Qatar campus and additional majors left out)
C = src("4cdf6315f024", "Degrees Offered < Carnegie Mellon University", "Carnegie Mellon University",
        ["Carnegie Mellon offers a wide range of programs in seven schools and colleges", "To browse the primary undergraduate degrees offered, select a school or college above."])
CMU = {"College of Engineering": [("Chemical Engineering", "B.S."), ("Civil Engineering", "B.S."), ("Environmental Engineering", "B.S."),
                                  ("Electrical and Computer Engineering", "B.S."), ("Materials Science and Engineering", "B.S."), ("Mechanical Engineering", "B.S.")],
       "College of Fine Arts": [("Architecture", "B.Arch."), ("Architecture", "B.A."), ("Art", "B.F.A."), ("Design", "B.Des."), ("Drama", "B.F.A."),
                                ("Music Composition", "B.F.A."), ("Music Performance", "B.F.A."), ("Music and Technology", "B.S.")],
       "Dietrich College of Humanities and Social Sciences": [
           ("International Relations and Political Science", "B.S."), ("Political Science, Security, and Technology", "B.S."), ("Economics and Politics", "B.S."),
           ("Creative Writing", "B.A."), ("Film and Visual Media", "B.A."), ("Literature and Culture", "B.A."), ("Professional Writing", "B.A."),
           ("Technical Writing", "B.S."), ("History", "B.A."), ("Anthropology", "B.A."), ("Science, Technology and Society", "B.S."),
           ("Ethics, History, and Public Policy", "B.A./B.S."), ("Information Systems", "B.S."), ("Languages and Cultures", "B.A."),
           ("Global Cultures and Emerging Technologies", "B.A."), ("Philosophy", "B.A."), ("Logic and Computation", "B.S."), ("Linguistics", "B.A."),
           ("Cognitive Science", "B.S."), ("Psychology and Biological Sciences", "B.S."), ("Behavioral Economics", "B.S."), ("Decision Science", "B.S."),
           ("Policy and Management", "B.S."), ("Statistics and Data Science", "B.S."), ("Economics and Statistics", "B.S."), ("Statistics and Machine Learning", "B.S.")],
       "Mellon College of Science": [("Biological Sciences", "B.S."), ("Biological Sciences", "B.A."), ("Mathematical Sciences", "B.S."), ("Neuroscience", "B.S."), ("Chemistry", "B.S."), ("Chemistry", "B.A."),
                                     ("Mathematical Sciences", "B.A."), ("Mathematical Sciences and Economics", "B.S."), ("Computational Finance", "B.S."), ("Physics", "B.S.")],
       "School of Computer Science": [("Artificial Intelligence", "B.S."), ("Computational Biology", "B.S."), ("Human-Computer Interaction", "B.S."), ("Robotics", "B.S.")],
       "David A. Tepper School of Business": [("Business Administration", "B.S."), ("Economics", "B.A."), ("Economics", "B.S."), ("Economics and Mathematical Sciences", "B.S.")]}
n = 0
for school, items in CMU.items():
    n += majors("us-cmu", dict(C, quotes=C["quotes"] + [school]), "program-us-cmu-bs-computer-science",
                "Carnegie Mellon offers a wide range of programs in seven schools and colleges", school, items, fmt="{name}, {deg}")
print("cmu", n)

# Georgia Tech: Programs (2026-2027 Catalog), every program listed with a BS
G = src("ad4c90c03899", "Programs | Georgia Tech Catalog", "Georgia Institute of Technology", ["Programs | Georgia Tech Catalog", "2026-2027 Edition"])
t = re.sub(r"\s+", " ", (PAGES / "ad4c90c03899.txt").read_text())
seg = t[t.index("Online Aerospace Engineering.") + len("Online "):]
D = r"(?:Minor|BS|MS|PhD|MBA|M\.Arch|M\.ID|PMASE|MBID|MCRP|PMML|PMOSH|MS \(undesignated\)|[A-Z]{2,6})"
seen, items = set(), []
for m in re.finditer(r"([A-Z][A-Za-z ,&'’-]+?)\. (" + D + r"(?:\s*,\s*" + D + r")*\s*\.?)(?= [A-Z])", seg):
    name = m.group(1).strip()
    if re.search(r"\bBS\b", m.group(2)) and name not in seen:
        seen.add(name); items.append((name, "BS", m.group(0)))
print("gatech", majors("us-gatech", G, "program-us-gatech-bs-computer-science", "Programs | Georgia Tech Catalog", "Georgia Institute of Technology", items, skip={"Computer Science"}))

# Johns Hopkins: e-catalogue Programs list, full-time on-campus bachelor's of the Krieger School of Arts and
# Sciences and the Whiting School of Engineering (the divisions the cost-of-attendance tuition covers)
J = src("16a9c9316274", "Programs | Johns Hopkins University Academic Catalogue", "Johns Hopkins University",
        ["(Full Time, On Campus Programs) Bachelor's Full-time"])
t = re.sub(r"\s+", " ", (PAGES / "16a9c9316274.txt").read_text())
nav, body = t[:52000], t[52000:]
items, seen = [], set()
for m in re.finditer(r"(?:In-person|Online|Full-time|Part-time) ((?:(?!In-person|Online)[^.])+?), (Bachelor of (?:Arts|Science)) (Krieger School of Arts and Sciences|Whiting School of Engineering) \(Full Time, On Campus Programs\) Bachelor's Full-time", body):
    words = m.group(1).split(" ")
    name = next((" ".join(words[i:]) for i in range(len(words)) if f" {' '.join(words[i:])}, {m.group(2)}" in nav), None)
    if name and (name, m.group(2)) not in seen:
        seen.add((name, m.group(2))); items.append((name, m.group(2), f"{name}, {m.group(2)} {m.group(3)} (Full Time, On Campus Programs)", m.group(3)))
n = 0
for school in ("Krieger School of Arts and Sciences", "Whiting School of Engineering"):
    n += majors("us-jhu", J, "program-us-jhu-bs-computer-science", "(Full Time, On Campus Programs) Bachelor's Full-time", school,
                [i[:3] for i in items if i[3] == school], skip={"Computer Science"} if school.startswith("Whiting") else ())
print("jhu", n, sorted(i[0] for i in items))

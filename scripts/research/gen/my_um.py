"""Universiti Malaya bachelor's programmes (written 2026-11-19), same pattern as
biology/my-um-biotechnology.json. Each course page has Local and International entry-requirement
tabs; the A-Level and IB lines are taken from the International tab only (the generator checks each
quoted block comes after the last "Malaysian citizen" block). Fee: the course page's International
fee and the matching row of UM's international fee structure (academic session 2025/2026), which
covers the minimum period of study; shown per year as the total over the stated duration.
  python3 -I scripts/research/gen/my_um.py
"""
import hashlib, re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
pid = lambda u: hashlib.sha1(u.encode()).hexdigest()[:12]
FEE_URL = (PAGES / "um-fee.url").read_text().strip()
FT = re.sub(r"\s+", " ", (PAGES / "um-fee.txt").read_text())
FEEQ = ["3) Fees structure is based on minimum or common period of study.", "Academic session 2025/2026"]
for q in FEEQ:
    assert q in FT, q
STOP = (r"(?= (International Baccalaureate|GCE A-Level|Matriculation|STPM|Diploma|UEC|Unified|Foundation|American|AUSMAT|Australian|"
        r"Canadian|SAT|Indian|IGCSE|O-Level|Other|English Requirement|MUET|Programme Requirement|Specific)|$)")

PROGS = [  # folder, slug, page slug, fee-row name, programme name, degree, field
    ("chemistry", "bsc-chemistry", "bachelor-of-science-in-chemistry", "Bachelor of Science in Chemistry", "Chemistry", "BSc", "Chemistry"),
    ("physics", "bsc-physics", "bachelor-of-science-in-physics", "Bachelor of Science in Physics", "Physics", "BSc", "Physics"),
    ("biology", "bsc-biochemistry", "bachelor-of-science-in-biochemistry", "Bachelor of Science in Biochemistry", "Biochemistry", "BSc", "Biochemistry"),
    ("mathematics", "actuarial-science", "bachelor-of-actuarial-science", "Bachelor of Actuarial Science", "Actuarial Science", "Bachelor", "Actuarial Studies"),
    ("business", "bba", "bachelor-of-business-administration", "Bachelor of Business Administration", "Business Administration", "BBA", "Business"),
    ("accounting", "finance", "bachelor-of-finance", "Bachelor of Finance", "Finance", "Bachelor", "Accounting and Finance"),
    ("architecture", "bsc-architecture", "bachelor-of-science-in-architecture", "Bachelor of Science in Architecture", "Architecture", "BSc", "Architecture"),
    ("biology", "biomedical-science", "bachelor-of-biomedical-science", "Bachelor of Biomedical Science", "Biomedical Science", "Bachelor", "Biomedical Science"),
    ("humanities", "ba-english", "bachelor-of-arts-english", "Bachelor of Arts English", "English", "BA", "English"),
    ("humanities", "ba-history", "bachelor-of-arts-history", "Bachelor of Arts History", "History", "BA", "History"),
]
for folder, slug, page, feerow, name, deg, field in PROGS:
    url = f"https://study.um.edu.my/{page}"
    raw = (PAGES / f"{pid(url)}.txt").read_text()
    t = re.sub(r"\s+", " ", raw)
    title = raw.splitlines()[0].strip()
    dur = re.search(r"Duration: ([\d.]+) [Yy]ears \([^)]*\)", t)
    fee = re.search(r"International RM ([\d,]+) \( Note: Not inclusive of 6% Sales and Service Tax \(SST\)\)", t)
    last_local = max(m.end() for m in re.finditer("Malaysian citizen", t))
    al = [m for m in re.finditer(r"GCE A-Level (?!Malaysian).*?" + STOP, t)][-1]
    ib = [m for m in re.finditer(r"International Baccalaureate \(IB\) (?!Malaysian).*?" + STOP, t)][-1]
    en = re.findall(r"MUET [\d.]+ IELTS \(Academic\) [\d.]+ TOEFL iBT \(Centre-based\) \d+", t)
    assert dur and fee and al.start() > last_local and ib.start() > last_local and len(set(en)) == 1, slug
    total = fee.group(1)
    row = f"{feerow} {total}.00"
    assert row in FT, row
    years = float(dur.group(1))
    yrs = int(years) if years == int(years) else years
    ielts = re.search(r"IELTS \(Academic\) ([\d.]+)", en[0]).group(1)
    muet = re.search(r"MUET ([\d.]+)", en[0]).group(1)
    toefl = re.search(r"TOEFL iBT \(Centre-based\) (\d+)", en[0]).group(1)
    eng = {"test_name": "IELTS Academic (or MUET / TOEFL iBT)", "min_score": f"IELTS (Academic) {ielts}, MUET {muet} or TOEFL iBT (centre-based) {toefl}.", "source": "course"}
    ibs = re.search(r"minimum score of (\d+) points", ib.group(0)).group(1)
    al_txt = al.group(0).strip().removeprefix("GCE A-Level ").replace("Qualification ", "").replace("qualification ", "")
    ib_txt = ib.group(0).strip().removeprefix("International Baccalaureate (IB) ")
    write(folder, {"uni": "my-um", "slug": slug,
        "sources": {
            "course": {"url": url, "page": pid(url), "title": title, "organization": "Universiti Malaya",
                       "quotes": [dur.group(0), fee.group(0), "Entry Requirement Local International", al.group(0).strip(), ib.group(0).strip(), en[0]]},
            "fees": {"url": FEE_URL, "page": "um-fee", "title": "Fee structure, Bachelor programme (international), Universiti Malaya (PDF)", "organization": "Universiti Malaya",
                     "quotes": [row, *FEEQ]}},
        "program": {"name": name, "degree_type": deg, "field": field, "faculty": "", "duration_years": yrs, "languages": ["en"],
                    "entry_year": "2027 entry", "platform": "", "source": "course",
                    "summary": f"{title.split(' | ')[0]}, {dur.group(0).removeprefix('Duration: ')}.", "application_requirements": []},
        "costs": [{"residency": "international", "currency": "MYR", "tuition_formula": f"{total.replace(',', '')}/{yrs}", "academic_year": "2025/2026 fee structure",
                   "source": ["fees", "course"], "living_from": "costProfile-my-um-cost-bsc-cs-international",
                   "note": f"International: RM {total} for the programme (UM's fee structure is based on the minimum period of study, {yrs} years), shown spread over {yrs} years. Not inclusive of 6% Sales and Service Tax (SST)."}],
        "admissions": [
            {"curriculum": "a-level", "source": "course", "required_subjects": [], "tests": [], "english": eng,
             "threshold": f"{name} (international applicants): GCE A-Level: {al_txt}"},
            {"curriculum": "ib", "source": "course", "required_subjects": [], "tests": [], "english": eng,
             "threshold": f"{name} (international applicants): IB: {ib_txt}"}]})
    print(slug, yrs, total, "IB", ibs, "|", al_txt[:90])

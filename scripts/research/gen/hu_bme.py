"""Budapest University of Technology and Economics (BME): base records + five BSc programmes (written 2026-11-25).

Sources, all xplore.bme.hu:
  - Tuition fees 2026/27: Non-EU citizens EUR 3200 / semester (the five programmes below);
  - Degree programmes: "Duration of studies N semesters" per BSc;
  - Calendar: FIRST (FALL) SEMESTER and SECOND (SPRING) SEMESTER (two a year);
  - Admission: BSc documents (CV and motivational letter, high school certificate, English proof);
    English B2 (IELTS 5.5, TOEFL iBT 72, Duolingo 100...); units may add criteria such as oral exams;
  - Useful info: monthly costs of living in HUF with BME's own EUR equivalents (shared flat ~174 EUR,
    basic food ~125 EUR, student monthly transport pass ~11 EUR); yearly total our calculation.
  python3 -I scripts/research/gen/hu_bme.py
"""
import json, re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write

ROOT = Path(__file__).resolve().parents[3]
PAGES = ROOT / ".research-cache/pages"
def norm(s): return re.sub(r"\s+", " ", s.replace("\xa0", " ").replace("’", "'")).strip().lower()
def on(page, qs):
    t = norm((PAGES / f"{page}.txt").read_text(errors="replace"))
    for q in qs: assert norm(q) in t, f"{page}: {q}"
    return qs
def url(page): return (PAGES / f"{page}.url").read_text().strip()
ORG = "Budapest University of Technology and Economics"

FEES_Q = ["Please see below the tuition fees for academic year 2026/27.",
          "Budapest University of Technology and Economics determines all tuition fees for the academic year and reserves the right to change them without prior notice."]
CAL = {"url": url("78b2c2b59ab0"), "page": "78b2c2b59ab0", "organization": ORG, "title": "Calendar | BME Xplore",
       "quotes": on("78b2c2b59ab0", ["FIRST (FALL) SEMESTER", "SECOND (SPRING) SEMESTER"])}
ADM = {"url": url("5a072c27416a"), "page": "5a072c27416a", "organization": ORG, "title": "Admission | BME Xplore",
       "quotes": on("5a072c27416a", [
           "BSc, OTM a) CV and motivational letter b) copy of passport c) high School certificate d) proof of English language proficiency e) Receipt of the transfer of EUR 150 application fee",
           "individual units may establish additional criteria for admission, such as specific academic backgrounds, oral examinations , or minimum language test scores higher than the general BME minimum requirements.",
           "Students applying for BSc or MSc Programmes are required to submit one of the following documents of English language proficiency (minimum level B2): IELTS & IELTS Online min. 5.5",
           "TOEFL iBT & TOEFL iBT Home Edition min. 72", "Duolingo English Test min. 100"])}
LIVING = {"url": url("c0101be4c9df"), "page": "c0101be4c9df", "organization": ORG, "title": "Useful info: costs of living | BME Xplore",
          "quotes": on("c0101be4c9df", ["Costs of Living / month", "Shared flat 55 500 HUF ~ 174 €", "Basic food/ month 40 000 HUF ~ 125 €",
                                        "Urban public transport (Monthly pass with Hungarian Student ID) 3 450 HUF ~11 €",
                                        "Please note that the prices listed are guidelines, not actual prices."])}
DEG = "ca95119fd146"

spec = {"uni": "hu-bme", "name": ORG, "aliases": ["BME", "Budapest University of Technology"], "type": "public",
        "website": "https://www.bme.hu/en", "country": {"cc": "hu", "name": "Hungary", "currency": "HUF"},
        "city": {"slug": "hu-budapest", "name": "Budapest"},
        "sources": {"main": {"url": url("fdcdd07115d4"), "page": "fdcdd07115d4", "organization": ORG, "title": "Tuition fees | BME Xplore", "quotes": on("fdcdd07115d4", FEES_Q)}},
        "main_source": "main",
        "residency": [{"key": "non-eu", "source": "main", "label": "Non-EU citizens",
                       "description": "BME's per-semester tuition for non-EU citizens on its 2026/27 tuition fee table."}]}
Path(ROOT / "fact-checks/research/universities-2026-11/hu-bme.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
print("wrote spec hu-bme")

ENG = {"test_name": "English B2 certificate (IELTS / TOEFL iBT / Duolingo...)", "source": "adm",
       "min_score": "B2: IELTS 5.5, TOEFL iBT 72, Duolingo 100 (or the other certificates BME lists), or a Medium of Instruction Certificate."}
LIVING_NOTE = ("Our calculation from BME's monthly guide prices (its own EUR equivalents): shared flat EUR 174, basic food EUR 125, "
               "student monthly transport pass EUR 11, × 12 = EUR 3,720 a year. BME says these are guidelines, not actual prices.")

# name on the programmes page, display name, field, fee row quote, semesters
P = [
 ("Computer Science Engineer Bsc", "Computer Science Engineering", "Computer Science", "Faculty of Electrical Engineering and Informatics - Computer Science Engineering / Non-EU citizens 3200 EUR/ semester", 7),
 ("Electrical Engineer Bsc", "Electrical Engineering", "Electrical and Electronic Engineering", "Faculty of Electrical Engineering and Informatics - Electrical Engineering / Non-EU citizens 3200 EUR/ semester", 7),
 ("Civil Engineer BSc", "Civil Engineering", "Civil Engineering", "BSc Faculty of Civil Engineering / Non-EU citizens 3200 EUR/ semester", 8),
 ("Engineering Management BSc", "Engineering Management", "Business", "Faculty of Economic and Social Sciences - Engineering Management / Non-EU citizens 3200 EUR/ semester", 7),
 ("Mathematics Bsc", "Mathematics", "Mathematics", "Faculty of Natural Sciences - Mathematics /Non-EU citizens 3200 EUR/ semester", 6),
]
txt = norm((PAGES / f"{DEG}.txt").read_text())
for page_name, name, field, fee_row, sem in P:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    i = txt.find(norm(page_name)); j = txt.find("duration of studies", i)
    seg = txt[i:j + len(f"duration of studies {sem} semesters")]
    assert seg.endswith(f"duration of studies {sem} semesters") and len(seg) < 400, (name, seg[-60:])
    dur_q = [page_name, f"Duration of studies {sem} semesters"]
    th = (f"{name}: no grade cut-off is published on the pages read. BSc applications need a CV and motivational letter, the high school certificate "
          "and proof of English; individual units may add criteria such as oral examinations.")
    adm = lambda cur: {"curriculum": cur, "source": "adm", "threshold": th, "required_subjects": [], "tests": [], "english": ENG}
    write("hu-bme", {"uni": "hu-bme", "slug": f"bsc-{slug}",
        "sources": {"course": {"url": url(DEG), "page": DEG, "title": "Degree programmes | BME Xplore", "organization": ORG, "quotes": on(DEG, [seg])},
                    "fees": {"url": url("fdcdd07115d4"), "page": "fdcdd07115d4", "organization": ORG, "title": "Tuition fees | BME Xplore",
                             "quotes": on("fdcdd07115d4", FEES_Q + [fee_row])},
                    "cal": CAL, "adm": ADM, "living": LIVING},
        "program": {"name": name, "degree_type": "BSc", "field": field, "faculty": "", "duration_years": sem / 2, "duration_source": "course",
                    "languages": ["en"], "entry_year": "2026/27 fees", "platform": "BME E-admission", "source": "course",
                    "summary": f"{name} (BSc), BME Budapest, taught in English.", "application_requirements": []},
        "costs": [{"residency": "non-eu", "currency": "EUR", "tuition_per_term": 3200, "terms_per_year": 2,
                   "terms_evidence": ["FIRST (FALL) SEMESTER", "SECOND (SPRING) SEMESTER"], "academic_year": "2026/27", "source": ["fees", "cal"],
                   "note": "2026/27: EUR 3200 per semester for non-EU citizens (fall and spring); yearly figure is our calculation.",
                   "living": {"monthly": [174, 125, 11], "months": 12, "source": "living", "kind": "genuine_cost_of_living_estimate", "note": LIVING_NOTE}}],
        "admissions": [adm("ib"), adm("a-level"), adm("us-hs"), adm("cbse"), adm("international-other")]})
    print("wrote", slug, sem / 2)

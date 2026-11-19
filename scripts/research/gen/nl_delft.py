"""TU Delft English-taught bachelor's programmes not yet on the site (written 2026-11-19): Earth,
Climate and Technology, and Nanobiology (a joint degree with Erasmus University Rotterdam). The
bachelors overview lists only four English programmes; Aerospace Engineering and Computer
Science and Engineering are already in. Required subjects from the shared "specific diploma
requirements" page; study load from each "about the programme" page; fees from the shared
tuition page (2027/2028 institutional rate BSc, statutory rate).
  python3 -I scripts/research/gen/nl_delft.py
HELD 2026-11-19: Delft writes the fee as "€ 20.563" (dot thousands); build.py reads that as 20.563, so
the records are not built until the builder can read that format for this source.
"""
import hashlib, re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
pid = lambda u: hashlib.sha1(u.encode()).hexdigest()[:12]
flat = lambda u: re.sub(r"\s+", " ", (PAGES / f"{pid(u)}.txt").read_text())
title = lambda u: (PAGES / f"{pid(u)}.txt").read_text().splitlines()[0].strip()
D = "https://www.tudelft.nl"
REQ = D + "/en/education/admission-and-application/bsc-international-diploma/admission-requirements/specific-diploma-requirements"
FEE = D + "/en/education/study-programme-orientation/practical-matters/tuition-fee-finances"
GCSE = ("We require six GCSE in different subjects with grades *A - C (or, for England grades 9 – 4). On top of that at least three and in some cases four "
        "A levels with grades *A - C are required, depending on the BSc programme.")
IBG = "TU Delft only accepts the Mathematics course ‘Analysis & Approaches HL’. NB. we do not accept students with an IBCP."
INST = "Institutional rate 2026/2027 2027/2028 Institutional rate BSc € 19.906 MSc € 25.633 BSc € 20.563 MSc € 26.479"
STAT = "Statutory rate 2026/2027 2027/2028 Statutory rate € 2.694 € 2.771"
for u, qs in ((REQ, [GCSE, IBG, "Mandatory GCE A Levels (grade *A - C)", "Required IB examination subjects"]), (FEE, [INST, STAT])):
    for q in qs:
        assert q in flat(u), (u, q)
ENG = {"from_existing": "admissionsRequirement-nl-tu-delft-admreq-bsc-aerospace-engineering-ib"}

PROGS = [
    ("bsc-earth-climate-technology", "Earth, Climate and Technology", "Engineering",
     D + "/en/onderwijs/opleidingen/bachelors/ect/bsc-earth-climate-and-technology", "about-the-programme",
     "Earth, Climate and Technology (Previously Applied Earth Sciences )(English Stream)", "Mathematics + Physics + Chemistry",
     "Mathematics: AA HL + Physics HL + Chemistry: SL", ["Mathematics", "Physics", "Chemistry"],
     ["Language : English Numerus fixus : No Start : September Required courses : Physics, Mathematics B and Chemistry"], "Study load 180 EC, 3 years", ""),
    ("bsc-nanobiology", "Nanobiology", "Biology",
     D + "/en/education/programmes/bachelors/nb/bsc-nanobiology", "about-the-programme",
     "Nanobiology (English Stream)", "Mathematics + Physics + Biology + Chemistry",
     "Mathematics: AA HL + Physics HL + Biology HL + Chemistry SL", ["Mathematics", "Physics", "Biology", "Chemistry"],
     ["Working language : English Joint degree : yes Numerus clausus : no Mandatory matching: yes",
      "a joint programme offered by TU Delft and Erasmus University Rotterdam"], "Study load 180 EC, 36 months",
     " A joint degree with Erasmus University Rotterdam; mandatory matching applies."),
]
rq = flat(REQ)
for slug, name, field, cu, sub, label, al, ib, subj, cq, load, extra in PROGS:
    au = f"{cu}/{sub}"
    for q in cq:
        assert q in flat(cu), (slug, q)
    assert load in flat(au), (slug, load)
    alq, ibq = f"{label} {al}", f"{label} {ib}"
    assert alq in rq and ibq in rq, slug
    ct = flat(cu)
    write("nl-majors", {"uni": "nl-tu-delft", "slug": slug,
        "sources": {
            "course": {"url": cu, "page": pid(cu), "title": title(cu), "organization": "Delft University of Technology", "quotes": cq},
            "about": {"url": au, "page": pid(au), "title": title(au), "organization": "Delft University of Technology", "quotes": [load]},
            "req": {"url": REQ, "page": pid(REQ), "title": title(REQ), "organization": "Delft University of Technology",
                    "quotes": [GCSE, "Mandatory GCE A Levels (grade *A - C)", alq, IBG, "Required IB examination subjects", ibq]},
            "fees": {"url": FEE, "page": pid(FEE), "title": title(FEE), "organization": "Delft University of Technology", "quotes": [INST, STAT]}},
        "program": {"name": name, "degree_type": "BSc", "field": field, "faculty": "", "duration_years": 3, "languages": ["en"],
                    "entry_year": "2027-2028", "platform": "Studielink", "source": "course", "duration_source": "about",
                    "summary": f"BSc {name}, taught in English.{extra}", "application_requirements": []},
        "costs": [{"residency": "non-eu", "currency": "EUR", "tuition_annual": 20563, "academic_year": "2027/2028 (institutional rate, BSc)", "source": "fees",
                   "living_from": "costProfile-nl-tu-delft-cost-bsc-aerospace-engineering-non-eu",
                   "note": "Institutional rate 2027/2028 for a BSc: €20.563 a year (TU Delft writes thousands with a dot). Students without entitlement to the statutory rate pay this."},
                  {"residency": "eu-efta", "currency": "EUR", "tuition_annual": 2771, "academic_year": "2027/2028 (statutory rate)", "source": "fees",
                   "living_from": "costProfile-nl-tu-delft-cost-bsc-aerospace-engineering-eu-efta", "note": "Statutory rate 2027/2028: €2.771 a year."}],
        "admissions": [
            {"curriculum": "a-level", "source": "req", "required_subjects": subj, "tests": [], "english": ENG,
             "threshold": f"{name}: six GCSEs in different subjects (A*-C or 9-4) and at least three A-Levels (A*-C), including {al.replace(' + ', ', ')}."},
            {"curriculum": "ib", "source": "req", "required_subjects": subj, "tests": [], "english": ENG,
             "threshold": f"{name}: IB Diploma with {ib.replace('Mathematics: AA HL', 'Mathematics Analysis and Approaches HL').replace(' + ', ', ')} (the IBCP is not accepted)."}]})
    print(slug)

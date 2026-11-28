"""Charles University (THE #110): every full-time, English-taught bachelor's listed in the university's admission
portal (is.cuni.cz, search: full-time, Bachelor's, English; 2 result pages, 21 entries) (written 2026-11-28).
Each entry's detail page gives faculty, language, standard length and the tuition fee for studies in a foreign
language, all quoted from that page. Double-subject teacher-education combinations are one record each.
  python3 -I scripts/research/gen/cz_cuni.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES

ORG = "Charles University"
MAIN = src("b883031f1117", "Tuition fees for studying in a foreign language | Faculty of Science, Charles University", ORG,
           ["Faculty of Science Charles University Albertov 6 128 00 Prague 2"])
spec("cz-cuni", ORG, ["Univerzita Karlova", "CUNI"], "public", "https://cuni.cz", ("cz", "Czechia", "CZK"), ("cz-prague", "Prague"), {"main": MAIN},
     [("international", "Foreign-language study", "Tuition fee for studies in a foreign language (English-taught programmes).", "main")])

# id_obor -> (saved page id, field)
ROWS = [("36283", "f4e8e5530f18", "Theology"), ("37295", "f8549d14176a", "Psychology"), ("37453", "830e957f8ec2", "Natural Sciences"),
        ("36423", "6b3bcde7850f", "Computer Science"), ("37237", "d3b544ea7412", "Education"), ("37236", "08ad7ce53cc4", "Education"),
        ("37240", "3fb430ddb18e", "Education"), ("37243", "3875d34530f2", "Education"), ("37242", "a715654526cc", "Education"),
        ("37241", "14527391a528", "Education"), ("37239", "6eee2d8d80b1", "Education"), ("37238", "0b98a74174ad", "Education"),
        ("36346", "5a79af90894c", "Economics"), ("36347", "bc15a68f6392", "History"), ("36345", "1d449b8025eb", "Politics, Philosophy and Economics"),
        ("36344", "be9a3278f189", "Sociology"), ("36343", "4df56f2a3704", "Marketing"), ("37211", "b561e29873d5", "Sport Science"),
        ("37212", "4f101affb069", "Sport Science"), ("37213", "8c40ab04ce85", "Physiotherapy"), ("36324", "bb8e29b9d45f", "Liberal Arts")]

for oid, pid, field in ROWS:
    t = re.sub(r"\s+", " ", (PAGES / f"{pid}.txt").read_text())
    head = re.search(r"Branch programme/details Search programme/branch Branch programme/details (.*?) Faculty: ", t).group(1)
    name = re.sub(r" \([0-9A-Z /]+\)( - double subject study)?$", "", head).strip()
    fac = re.search(r"Faculty: (.*?) Study programme: ", t).group(1)
    core = re.search(r"Faculty: .*? Language of instruction: English", t).group(0)
    years = re.search(r"Standard length of study: (\d) years", t)
    fee = re.search(r"Tuition \[(EUR|CZK)\] / per period: (\d+) (EUR|CZK) / year", t)
    if not (years and fee):
        print("skip", oid, name); continue
    cur, amt = fee.group(1), int(fee.group(2))
    S = src(pid, f"{name} | Charles University admission (SIS)", ORG, [head, core, years.group(0), fee.group(0)])
    double = " (double subject study)" if "double subject study" in head else ""
    prog("cz-cuni", slugify(name)[:80].rstrip("-"), {"course": S},
         {"name": name + double, "degree_type": "Bachelor's", "field": field, "faculty": fac, "duration_years": int(years.group(1)),
          "duration_source": "course", "languages": ["en"], "entry_year": "2027/2028 admission", "platform": "", "source": "course",
          "summary": f"{name}{double}, {fac}, Charles University (Prague); full-time bachelor's taught in English, standard length {years.group(1)} years.",
          "application_requirements": []},
         [{"residency": "international", "currency": cur, "tuition_annual": amt, "academic_year": "2027/2028 admission", "source": "course",
           "note": f"Tuition fee for studies in a foreign language: {amt} {cur} a year (admission portal)."}], [])
print("wrote cz-cuni")

"""University of Bologna: base records + two English-taught first-cycle degrees (written 2026-11-25).

Sources, all unibo.it:
  - programme overviews: "Language English", "Duration 3 years";
  - programme "how to enrol" pages: selection solely by SAT score ranking, no minimum score;
    places reserved for non-EU citizens resident abroad;
  - fees page: fixed instalment EUR 157.04 + the programme's maximum all-inclusive contribution
    when no exemption is requested; maximum table 2026/2027 (PDF, Italian): first cycle EUR 2,040;
  - reduced fixed fee page (2026/27): non-OECD nationals EUR 1,000 + 157.04, particularly poor or
    developing countries EUR 500 + 157.04 (freshmen), family income/assets only outside Italy;
  - living costs in Bologna: single room EUR 400/month, food EUR 60/week, student bus EUR 27/month,
    health service EUR 700/year (yearly total our calculation; utilities not included).
No English-test requirement is stated on the pages read, so none is stored.
  python3 -I scripts/research/gen/it_unibo.py
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
ORG = "University of Bologna"

FEES = {"url": url("69cefa25782d"), "page": "69cefa25782d", "organization": ORG,
        "title": "Fees and exemptions: amounts and deadlines | University of Bologna",
        "quotes": on("69cefa25782d", [
            "The tuition fee is composed of two instalments: a fixed instalment of €157.04 a variable part that depends on the programme you choose and is calculated based on the economic situation of your family unit.",
            "for an amount equal to the maximum all-inclusive contribution set for the programme you are enrolling on, plus the fixed fee of €157.04"])}
MAX = {"url": url("unibo-max-2627"), "page": "unibo-max-2627", "organization": ORG,
       "title": "Maximum all-inclusive contribution 2026/2027 (PDF, Italian) | University of Bologna",
       "quotes": on("unibo-max-2627", [
           "Importo massimo di contributo onnicomprensivo A.A. 2026/2027",
           "Il contributo onnicomprensivo è al netto della Tassa regionale per il diritto allo studio, dell'imposta di bollo e del premio assicurativo",
           "Corsi di primo ciclo: 2.040,00 €"])}
RED = {"url": url("f516ccc643bf"), "page": "f516ccc643bf", "organization": ORG,
       "title": "Reduced fixed fee for citizens of particularly poor and developing countries or non-EU, non-OECD countries | University of Bologna",
       "quotes": on("f516ccc643bf", [
           "It is a fee that allows you to enrol in a first, second or single cycle degree programme paying the following fixed amounts for the a.y. 2026/27:",
           "Reduced fixed fee for citizens of particularly poor and developing countries Requirements Enrolled on a first- or single-cycle degree programme Enrolled in second-cycle programmes If you are a freshman or have the minimum number of credits €500 + €157.04",
           "Reduced fixed fee for nationals of non-OECD countries Requirements Enrolled on a first- or single-cycle degree programme Enrolled in second-cycle programmes If you are a freshman or have the minimum number of credits € 1,000 + €157.04",
           "your family has income and/or assets only outside Italy.",
           "You do not have to attach any documentation on your family's economic situation."])}
LIVING = {"url": url("fd516cbd7dd8"), "page": "fd516cbd7dd8", "organization": ORG,
          "title": "Living costs in Bologna | University of Bologna",
          "quotes": on("fd516cbd7dd8", [
              "Living costs in Bologna",
              "Single room in a shared apartment : average cost € 400,00 a month + utilities",
              "Food at a supermarket for one week : € 60,00 approximately",
              "Monthly bus ticket (for students up to 27 years of age) : € 27,00",
              "Annual registration with the Italian National Health Service (SSN) for non-EU students € 700 approximately per year",
              "The University of Bologna offers to international and Italian students information and services to help them find an accommodation"])}

spec = {"uni": "it-unibo", "name": ORG, "aliases": ["Unibo", "Alma Mater Studiorum"], "type": "public",
        "website": "https://www.unibo.it/en", "country": {"cc": "it", "name": "Italy", "currency": "EUR"},
        "city": {"slug": "it-bologna", "name": "Bologna"},
        "sources": {"main": LIVING, "fees": FEES, "red": RED}, "main_source": "main",
        "residency": [
            {"key": "international", "source": "fees", "label": "International students (maximum fee)",
             "description": "Students who don't qualify for a reduced fee pay the programme's maximum all-inclusive contribution plus the fixed EUR 157.04."},
            {"key": "non-oecd", "source": "red", "label": "Nationals of non-OECD countries (family income only outside Italy)",
             "description": "University of Bologna reduced fixed fee for nationals of the non-OECD countries on its 2026 list whose family has income and assets only outside Italy."},
            {"key": "poor-developing", "source": "red", "label": "Nationals of particularly poor or developing countries (family income only outside Italy)",
             "description": "University of Bologna reduced fixed fee for nationals of the particularly poor or developing countries on its 2026 list whose family has income and assets only outside Italy."}]}
Path(ROOT / "fact-checks/research/universities-2026-11/it-unibo.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
print("wrote spec it-unibo")

LIVING_NOTE = ("Our calculation from the University of Bologna's living-costs page: single room in a shared flat EUR 400 a month and student bus pass "
               "EUR 27 a month × 12, food EUR 60 a week × 52, and the health service registration for non-EU students EUR 700 a year = EUR 8,944 a year. "
               "Utilities are extra (not priced on the page).")
LIVING_C = {"monthly": [400, 27], "months": 12, "weekly": [60], "yearly": [700], "source": "living",
            "kind": "genuine_cost_of_living_estimate", "note": LIVING_NOTE}
COSTS = [
    {"residency": "international", "currency": "EUR", "tuition_annual": 2040, "mandatory_fees_annual": 157.04,
     "academic_year": "2026/2027", "source": ["max", "fees"], "living": LIVING_C,
     "note": "2026/2027 maximum all-inclusive contribution for first-cycle degrees (EUR 2,040), plus the fixed EUR 157.04. The table says the regional tax, stamp duty and insurance are not included. Lower with an ISEE or documents for foreign income."},
    {"residency": "non-oecd", "currency": "EUR", "tuition_annual": 1000, "mandatory_fees_annual": 157.04,
     "academic_year": "2026/27", "source": "red", "living": LIVING_C,
     "note": "Reduced fixed fee 2026/27 for nationals of non-OECD countries on the University of Bologna's list, freshmen: EUR 1,000 + EUR 157.04. Your family must have income and assets only outside Italy; no documents needed."},
    {"residency": "poor-developing", "currency": "EUR", "tuition_annual": 500, "mandatory_fees_annual": 157.04,
     "academic_year": "2026/27", "source": "red", "living": LIVING_C,
     "note": "Reduced fixed fee 2026/27 for nationals of particularly poor or developing countries on the University of Bologna's list, freshmen: EUR 500 + EUR 157.04. Your family must have income and assets only outside Italy; no documents needed."},
]

# overview page, enrol page, name, field, at-a-glance quote, places quote
P = [
 ("a260aa76a1a1", "ca132bc1813e", "Economics and Finance", "Economics", "Place of teaching Bologna Language English Degree Programme Class L-33 - Economics Duration 3 years",
  "Admission to the degree programme is limited to 130 places, 40 of which are reserved for NON-EU citizens resident abroad."),
 ("0763de728fda", "a4c0bb59e5b4", "Business and Economics", "Business", "Place of teaching Bologna Language English Degree Programme Class L-18 - Business administration Duration 3 years",
  "Admission to the degree programme is limited to 190 places, 32 of which are reserved for non-EU citizens resident abroad and 13 to Special Programmes."),
]
for ov, enrol, name, field, glance, places in P:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    sel_q = on(enrol, ["Ranking is in descending order, based solely on the score obtained in the SAT. No minimum score is required.", places])
    th = (f"{name}: no school-grade cut-off. Selection is by ranking on the SAT score alone, with no minimum score. "
          f"{places.replace('Admission to the degree programme is limited to', 'Limited to')}")
    adm = lambda cur: {"curriculum": cur, "source": "enrol", "threshold": th, "required_subjects": [],
                       "tests": [{"name": "SAT (ranking)", "required": "required"}]}
    write("it-unibo", {"uni": "it-unibo", "slug": f"laurea-{slug}",
        "sources": {"course": {"url": url(ov), "page": ov, "title": f"{name}, First Cycle Degree | University of Bologna", "organization": ORG,
                               "quotes": on(ov, [glance])},
                    "enrol": {"url": url(enrol), "page": enrol, "title": f"{name}: programme enrolment | University of Bologna", "organization": ORG, "quotes": sel_q},
                    "fees": FEES, "max": MAX, "red": RED, "living": LIVING},
        "program": {"name": name, "degree_type": "Laurea (Bachelor)", "field": field, "faculty": "", "duration_years": 3,
                    "duration_source": "course", "languages": ["en"], "entry_year": "2026/2027",
                    "platform": "Studenti Online (University of Bologna)", "source": "course",
                    "summary": f"{name}, first-cycle degree (3 years), taught in English, University of Bologna.", "application_requirements": []},
        "costs": COSTS,
        "admissions": [adm("ib"), adm("a-level"), adm("us-hs"), adm("cbse"), adm("international-other")]})
    print("wrote", slug)

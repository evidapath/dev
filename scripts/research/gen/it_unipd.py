"""University of Padua: base records + four English-taught bachelor's degrees (written 2026-11-25).

Sources, all unipd.it:
  - course pages on apply.unipd.it: "Nominal duration 3 years (180 ECTS)", "Study language English",
    "Tuition fee €2,950 per year", the CISIA CEnT-S test, English B2, limited access by ranking;
  - Student fees: first-year first instalment EUR 208 (regional tax 192 + stamp duty 16); the course
    pages don't say whether the EUR 2,950 includes it, so it is added (overstating is the safe error);
  - Cost of living in Padua: single room up to EUR 600/month, groceries EUR 60/week, annual bus
    travelcard EUR 247.50, residence permit EUR 116.46, health insurance up to EUR 150 (non-EU).
  python3 -I scripts/research/gen/it_unipd.py
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
ORG = "University of Padua"

FEES = {"url": url("50fd577665bf"), "page": "50fd577665bf", "organization": ORG, "title": "Student fees | University of Padua",
        "quotes": on("50fd577665bf", [
            "208 euros (of which 192 euros for the regional tax for the right to university education and 16 euros for stamp duty) for those enrolling in the first year, to be paid at the time of enrolment",
            "Tuition Fees and Exemptions Notice for the 2026-2027 academic year"])}
LIVING = {"url": url("b1906f861991"), "page": "b1906f861991", "organization": ORG, "title": "Cost of living in Padua | University of Padua",
          "quotes": on("b1906f861991", [
              "Cost of living in Padua These are some examples of general expenses that you need to cover to live in Padua as a Unipd student.",
              "Accommodation in a single room: from € 300 to € 600 + expenses",
              "Supermarket grocery shopping for one week: approximately € 60",
              "Bus/tram travelcard: from €8,80 (weekly) to €247,50 (annual)",
              "Application for issue / renewal of the residence permit for study purposes: approximately € 116,46",
              "Health insurance valid for the issue / renewal of the residence permit for study purposes: approximately from € 120 to € 150"])}

MAIN = {"url": url("d299bd382330"), "page": "d299bd382330", "organization": ORG, "title": "Information Engineering | University of Padua",
        "quotes": on("d299bd382330", ["Information Engineering University of Padua Italy, Padua"])}
spec = {"uni": "it-unipd", "name": ORG, "aliases": ["Università di Padova", "UniPD", "University of Padova"], "type": "public",
        "website": "https://www.unipd.it/en", "country": {"cc": "it", "name": "Italy", "currency": "EUR"},
        "city": {"slug": "it-padua", "name": "Padua"},
        "sources": {"main": MAIN, "fees": FEES}, "main_source": "main",
        "residency": [{"key": "international", "source": "fees", "label": "International students (course page fee)",
                       "description": "The fee listed on each English-taught course page of the University of Padua's application portal."}]}
Path(ROOT / "fact-checks/research/universities-2026-11/it-unipd.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
print("wrote spec it-unipd")

LIVING_NOTE = ("Our calculation from the University of Padua's cost-of-living page: single room up to EUR 600 a month × 12, groceries EUR 60 a week × 52, "
               "annual bus travelcard EUR 247.50, residence permit EUR 116.46 and health insurance up to EUR 150 = EUR 10,834 a year. "
               "Utilities and other expenses on top of rent aren't priced.")
ENG = {"test_name": "English B2 (CEFR) certificate", "min_score": "English B2 level (CEFR) or equivalent; accepted certificates and exemptions on the University of Padua's list.", "source": "course"}

# page id, name, field, award quote (or None)
P = [
 ("d299bd382330", "Information Engineering", "Computer Engineering"),
 ("4c7064cd5731", "Biology of Human and Environmental Health", "Biology"),
 ("6d1093af4153", "Economics, Governance and Decision-Making", "Economics"),
 ("38e4c8d54a84", "Earth and Climate Dynamics", "Earth Sciences"),
]
for page, name, field in P:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    q = on(page, [f"{name} University of Padua Italy, Padua",
                  "Nominal duration 3 years (180 ECTS ) Study language English",
                  "Tuition fee €2,950 per year",
                  "This degree programme requires the new CISIA CEnT-S test.",
                  "B2 level"])
    lim = next((x for x in ["This is a Limited access programme.", "This is a limited access programme."] if norm(x) in norm((PAGES / f"{page}.txt").read_text())), None)
    if lim: q.append(lim)
    th = (f"{name}: no school-grade cut-off is published. Entry needs the CISIA CEnT-S test"
          + (" and places go by a ranking list (limited access)." if lim else "."))
    adm = lambda cur: {"curriculum": cur, "source": "course", "threshold": th, "required_subjects": [],
                       "tests": [{"name": "CISIA CEnT-S", "required": "required"}], "english": ENG}
    write("it-unipd", {"uni": "it-unipd", "slug": f"bachelor-{slug}",
        "sources": {"course": {"url": url(page), "page": page, "title": f"{name} | University of Padua", "organization": ORG, "quotes": q},
                    "fees": FEES, "living": LIVING},
        "program": {"name": name, "degree_type": "Bachelor's degree", "field": field, "faculty": "", "duration_years": 3,
                    "duration_source": "course", "languages": ["en"], "entry_year": "2027/2028 intake (course page)",
                    "platform": "University of Padua application portal (apply.unipd.it)", "source": "course",
                    "summary": f"{name}, bachelor's degree, 3 years (180 ECTS), taught in English, University of Padua.", "application_requirements": []},
        "costs": [{"residency": "international", "currency": "EUR", "tuition_annual": 2950, "mandatory_fees_annual": 208,
                   "academic_year": "2027/2028 intake (course page)", "source": ["course", "fees"],
                   "note": "EUR 2,950 a year (course page). Compulsory fees: the EUR 208 first-year instalment (regional tax EUR 192 + stamp duty EUR 16) from the fees page; the course page doesn't say whether the EUR 2,950 already includes it.",
                   "living": {"monthly": [600], "months": 12, "weekly": [60], "yearly": [247.5, 116.46, 150], "source": "living",
                              "kind": "genuine_cost_of_living_estimate", "note": LIVING_NOTE}}],
        "admissions": [adm("ib"), adm("a-level"), adm("us-hs"), adm("cbse"), adm("international-other")]})
    print("wrote", slug)

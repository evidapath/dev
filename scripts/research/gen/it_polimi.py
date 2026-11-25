"""Politecnico di Milano: base records + four English-taught BSc engineering programmes (written 2026-11-25).

Sources, all polimi.it:
  - each programme page: name, "Duration 3 Years", "Language English" (Civil: "Italian or English"), campus;
  - "Laurea, Laurea Magistrale and Single-cycle programmes" (costs): the yearly amount, from
    EUR 157.04 (ISEE up to EUR 22,000) to a maximum of EUR 3,943.04, charged when no ISEE is submitted;
  - "Students with income and property abroad": an ISEEU parificato from an affiliated CAF;
  - Engineering BSc call for admission 2026-27 (English translation, PDF): admission by
    entrance-test ranking (TOL, or CEnT-S / SAT in English) for English-taught programmes;
  - Language requirements: English certificates and scores;
  - Cost of living: monthly ranges (top of each range used, yearly total our calculation).
The 2027-28 call and fees are not published yet; the 2026-27 ones are stored and labelled.
  python3 -I scripts/research/gen/it_polimi.py
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
ORG = "Politecnico di Milano"

FEES = {"url": url("7fe6091013b3"), "page": "7fe6091013b3", "organization": ORG,
        "title": "Laurea, Laurea Magistrale and Single-cycle programmes: costs | Politecnico di Milano",
        "quotes": on("7fe6091013b3", [
            "For a standard study plan of between 46 and 74 ECTS and an ISEE of up to € 22,000, the amount is € 157.04 ; for a higher-value ISEE, the amount gradually increases up to a maximum of € 3,943.04 .",
            "The maximum amount is automatically charged to students: without an ISEE certificate who decide not to submit one;",
            "You are a future student of the 2026/2027 academic year"])}
ABROAD = {"url": url("ade533cf5813"), "page": "ade533cf5813", "organization": ORG,
          "title": "Students with income and property abroad | Politecnico di Milano",
          "quotes": on("ade533cf5813", [
              "If you have income or assets abroad (*), for the calculation of your university fees you must request the document known as the ISEEU parificato from the affiliated CAF, which will send it directly to the Politecnico di Milano.",
              "exempt only from payment of the all-inclusive contribution"])}
CALL = {"url": url("polimi-call-eng-2026"), "page": "polimi-call-eng-2026", "organization": ORG,
        "title": "Engineering BSc call for admission 2026-27, English translation (PDF) | Politecnico di Milano",
        "quotes": on("polimi-call-eng-2026", [
            "CEnT-S (provided by the Interuniversity Consortium for Integrated Access Systems - CISIA www.cisiaonline.it), test administered in English;",
            "SAT (provided by The College Board www.collegeboard.org), test administered in English.",
            "To access Bachelor degree programmes taught in English, the following are required:",
            "Proficiency in English is an entry requirement, which must be demonstrated before enrollment;",
            "For courses taught in English, access will be granted through specific rankings.",
            "Those eligible for enrollment must complete the application for a study visa through the Universitaly portal",
            "ART. 7 - NON-EU ENTRIES A.Y. 2026/2027"])}
LANG = {"url": url("90a0674f7060"), "page": "90a0674f7060", "organization": ORG,
        "title": "Language requirements, Bachelor of Science | Politecnico di Milano",
        "quotes": on("90a0674f7060", [
            "Internet Based Score ≥ 59 (total score)",
            "IELTS Academic and IELTS General Training+ ≥ 5",
            "≥ B2 First - GRADE C",
            "students holding a high school qualification (or equivalent) awarded in English",
            "Italian-language proficiency is not an admission requirement"])}
LIVING = {"url": url("528203fd44d5"), "page": "528203fd44d5", "organization": ORG,
          "title": "Cost of living | Politecnico di Milano",
          "quotes": on("528203fd44d5", [
              "Accomodation €400 - €700 per month", "Food €150 - €200 per month",
              "Social life €100-200 for month", "Travel costs €20-30 per month", "Mobile phones €10 - €30 per month",
              "It is impossible to calculate these costs because it depends on what you are studying"])}
NEW = {"url": url("7f7abe63a070"), "page": "7f7abe63a070", "organization": ORG,
       "title": "New undergraduate programmes | Politecnico di Milano",
       "quotes": on("7f7abe63a070", [
           "Politecnico di Milano is launching other three new international bachelor's programmes, fully taught in English and starting in September 2026",
           "Engineering Science Milano – Leonardo and Bovisa Campuses"])}

# ── base records (scripts/research/new_university.py) ──
spec = {"uni": "it-polimi", "name": ORG, "aliases": ["PoliMi", "Polimi"], "type": "public",
        "website": "https://www.polimi.it/en", "country": {"cc": "it", "name": "Italy", "currency": "EUR"},
        "city": {"slug": "it-milan", "name": "Milan"},
        "sources": {"main": NEW, "fees": FEES}, "main_source": "main",
        "residency": [{"key": "all-students", "source": "fees",
                       "label": "All students (amount depends on family income)",
                       "description": "Politecnico di Milano charges every bachelor's student on one scale set by family income (ISEE, or ISEEU parificato for income abroad); the maximum applies when none is submitted."}]}
Path(ROOT / "fact-checks/research/universities-2026-11/it-polimi.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
print("wrote spec it-polimi")

ENG = {"test_name": "English certificate (TOEFL iBT / IELTS / Cambridge)", "source": "lang",
       "min_score": "TOEFL iBT 59 (total), IELTS Academic 5, or Cambridge B2 First grade C. Not needed with a high school qualification awarded in English.",
       "notes": "Italian isn't an admission requirement; without it you get Additional Educational Obligations to clear during the degree."}
THRESHOLD = ("{name}: no school-grade cut-off. Places on English-taught programmes go by ranking on an entrance test: "
             "Politecnico's own test (TOL), or the CEnT-S or SAT, both taken in English. English proficiency must be shown before enrolment. "
             "Non-EU applicants living abroad also apply for a study visa through the Universitaly portal. (2026/2027 call; the next call isn't published yet.)")
NOTE = ("2026/2027: the yearly amount depends on family income. EUR 3,943.04 is the maximum (all-inclusive contribution), charged when no ISEE is submitted; "
        "with an ISEE of up to EUR 22,000 it is EUR 157.04. With income or assets abroad you need an ISEEU parificato from an affiliated CAF to pay less.")
LIVING_NOTE = ("Our calculation: the top of each monthly range in Politecnico di Milano's cost-of-living guide "
               "(accommodation EUR 700, food EUR 200, social life EUR 200, travel EUR 30, mobile phone EUR 30) × 12 = EUR 13,920 a year. "
               "Study costs aren't included; PoliMi says it is impossible to calculate them.")

# page id, name, field, length/language/campus quote, campus for the summary
P = [
 ("ae76b1245903", "Engineering Science", "Engineering", "Duration 3 Years Language English Campus Milano Leonardo Milano Bovisa", "Milan (Leonardo and Bovisa campuses)"),
 ("d8e68b6f51e8", "Process Engineering", "Chemical Engineering", "Duration 3 Years Language English Campus Cremona", "Cremona campus"),
 ("d60b7577ccc3", "Industrial Engineering", "Mechanical Engineering", "Duration 3 Years Language English Campus Piacenza", "Piacenza campus"),
 ("b8cac8251a79", "Civil Engineering", "Civil Engineering", "Duration 3 Years Language Italian or English Campus Milano Leonardo", "Milan (Leonardo campus), taught in Italian or English"),
]
for page, name, field, dur_q, campus in P:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    adm = lambda cur: {"curriculum": cur, "source": "call", "threshold": THRESHOLD.format(name=name),
                       "required_subjects": [], "tests": [{"name": "TOL, CEnT-S or SAT (entrance test ranking)", "required": "required"}],
                       "english": ENG}
    write("it-polimi", {"uni": "it-polimi", "slug": f"bsc-{slug}",
        "sources": {"course": {"url": url(page), "page": page, "title": f"{name} (BSc) | Politecnico di Milano", "organization": ORG,
                               "quotes": on(page, [name, dur_q])},
                    "fees": FEES, "abroad": ABROAD, "call": CALL, "lang": LANG, "living": LIVING},
        "program": {"name": name, "degree_type": "BSc", "field": field, "faculty": "", "duration_years": 3,
                    "duration_source": "course", "languages": ["en"], "entry_year": "2026/2027 rules (next year's not yet published)",
                    "platform": "Politecnico di Milano Online Services", "source": "course",
                    "summary": f"BSc in {name}, Politecnico di Milano, 3 years, taught in English; {campus}.", "application_requirements": []},
        "costs": [{"residency": "all-students", "currency": "EUR", "tuition_annual": 3943.04,
                   "academic_year": "2026/2027", "source": ["fees", "abroad"], "note": NOTE,
                   "living": {"monthly": [700, 200, 200, 30, 30], "months": 12, "source": "living",
                              "kind": "genuine_cost_of_living_estimate", "note": LIVING_NOTE}}],
        "admissions": [adm("ib"), adm("a-level"), adm("us-hs"), adm("cbse"), adm("international-other")]})
    print("wrote", slug)

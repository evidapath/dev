"""KAIST (Korea): base records, eleven majors, and the KAIST Scholarship (written 2026-11-25).

Sources, all kaist.ac.kr:
  - 2027 admissions guide (PDF): undergraduate departments; undeclared major (choose in year two);
    English-medium; required documents (test reports e.g. SAT, ACT, AP, IB, A-level); English test
    (TOEFL iBT 83 / IELTS 6.5 recommended, exemptions); "All international students receive full
    financial support, including tuition and living expenses."
  - Cost of attendance page: tuition KRW 6,866,000 a year; NHI premiums KRW 916,680; housing
    KRW 1,328,000; food KRW 5,475,000; books KRW 300,000; KAIST Scholarship covers the entire tuition
    for 4 years, a KRW 350,000 monthly stipend and NHI.
  - KAIST Scholarship page: tuition exemption for 8 semesters; automatic on admission; GPA over 2.7/4.3.
The scholarship is written as a scholarship record (guaranteed, full tuition) so the site subtracts it.
  python3 -I scripts/research/gen/kr_kaist.py
"""
import hashlib, json, re, sys, os
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
ORG = "KAIST"

GUIDE = {"url": url("kaist-guide-2027"), "page": "kaist-guide-2027", "organization": ORG, "title": "Admissions Guide for 2027 admission, international undergraduates (PDF) | KAIST",
         "quotes": on("kaist-guide-2027", [
             "Thank you for your interest in KAIST (Korea Advanced Institute of Science and Technology).",
             "291 Daehak-ro, Yuseong-gu, Daejeon 34141,",
             "All international students receive full financial support, including tuition and living expenses.",
             "Students enter KAIST without declaring a major and have the opportunity to explore various STEM fields",
             "The official language of communication and instruction for international students at KAIST is English.",
             "TOEFL iBT 83 (Taken before Jan 21, 2026) / 4.5 (Taken on or after Jan 21, 2026)",
             "IELTS 6.5",
             "(e.g., SAT, ACT, AP, IB, GCE A-Level, or other national high school leaving or university entrance",
             "Interviews may be conducted if deemed necessary."])}
COA = {"url": url("ada244a8f2f4"), "page": "ada244a8f2f4", "organization": ORG, "title": "Cost of Attendance | KAIST Office of Admissions",
       "quotes": on("ada244a8f2f4", [
           "Tuition Fees 3,433,000 3,433,000 6,866,000",
           "NHI Premiums 458,340 458,340 916,680",
           "Books 150,000 150,000 300,000",
           "Housing 664,000 664,000 1,328,000",
           "Food 2,737,500 2,737,500 5,475,000",
           "KAIST Scholarship covering entire tution fee for 4 years once admitted",
           "Monthly Stipend 2,100,000 2,100,000 4,200,000 KRW 350,000 * 12 Months",
           "Total((A+B)-C)) 1,679,500 1,679,500 3,359,000"])}
SCH = {"url": url("ecf4842c5cae"), "page": "ecf4842c5cae", "organization": ORG, "title": "KAIST Scholarship | KAIST Office of Admissions",
       "quotes": on("ecf4842c5cae", [
           "Full tuition fee: tuition exemption for 8 semesters",
           "Living expenses: 350,000 KRW per month",
           "Students must maintain GPA over 2.7 out of 4.3 at KAIST after their freshman year",
           "Upon being selected for admission, you will automatically be entitled to the KAIST Scholarship."])}

spec = {"uni": "kr-kaist", "name": "Korea Advanced Institute of Science and Technology", "aliases": ["KAIST"], "type": "public",
        "website": "https://www.kaist.ac.kr/en/", "country": {"cc": "kr", "name": "South Korea", "currency": "KRW"},
        "city": {"slug": "kr-daejeon", "name": "Daejeon"},
        "sources": {"main": GUIDE, "coa": COA}, "main_source": "main",
        "residency": [{"key": "international", "source": "coa", "label": "International students",
                       "description": "KAIST's published cost of attendance for international undergraduates; the KAIST Scholarship covers tuition."}]}
Path(ROOT / "fact-checks/research/universities-2026-11/kr-kaist.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")

# The KAIST Scholarship as a scholarship record (guaranteed, full tuition, every admitted international student).
sch_src = f"sourceRecord-ev-{hashlib.sha1(SCH['url'].encode()).hexdigest()[:12]}"
sch = {"createOrReplace": {
    "_id": "scholarship-kr-kaist-scholarship", "_type": "scholarship", "id": "kr-kaist-scholarship",
    "name": "KAIST Scholarship (international undergraduates)", "provider": "KAIST", "provider_type": "university",
    "award_amount": "Full tuition fee: tuition exemption for 8 semesters, plus living expenses of KRW 350,000 a month and national health insurance.",
    "award_amount_currency": "KRW", "award_type": "full_tuition", "selection_basis": "guaranteed",
    "academic_criteria": "Automatic on admission; keep a GPA over 2.7 out of 4.3 after the freshman year.",
    "eligible_citizenships": ["all"], "residency_restrictions": "Applicants admitted through KAIST's international student admission.",
    "other_eligibility_criteria": "No separate application: tick 'KAIST scholarship' on the admission application.",
    "institutions_covered": ["kr-kaist"], "degree_levels": ["undergraduate"], "duration": "8 semesters",
    "renewable": True, "renewal_conditions": "GPA over 2.7 out of 4.3 after the freshman year.",
    "deadline_academic_year": "2027", "official_source_url": SCH["url"], "last_checked": "2026-11-25",
    "record_status": "VERIFIED", "verification_status": "VERIFIED", "notes": "",
    "source_refs": [{"_key": "s1", "_ref": sch_src, "_type": "reference", "_weak": True}],
    "extension_metadata": {"_type": "extensionMetadata", "fields": []}}}
for v in ("8 semesters", "350,000", "2.7 out of 4.3"):
    assert norm(v) in norm(" ".join(SCH["quotes"])), v
Path(ROOT / "fact-checks/research/universities-2026-11/kr-kaist-scholarship.ndjson").write_text(json.dumps(sch, ensure_ascii=False) + "\n")
print("wrote spec + scholarship kr-kaist")

ENG = {"test_name": "TOEFL iBT / IELTS (recommended scores)", "source": "guide",
       "min_score": "Recommended: TOEFL iBT 83 (taken before 21 Jan 2026) or 4.5 (from 21 Jan 2026), IELTS 6.5.",
       "notes": "Exempt: nationals of English-speaking countries listed by KAIST, or a high school taught in English (school letter needed)."}
TH = ("{name} at KAIST: no published grade cut-off. You enter KAIST without a declared major and choose {name} in your second year. "
      "Applications are reviewed as a whole: transcripts, standardized test reports (e.g. SAT, ACT, AP, IB, GCE A-Level), English test, "
      "recommendation letters (highly recommended) and awards; interviews only if deemed necessary.")
LIVING_NOTE = ("KAIST's cost of attendance: housing KRW 1,328,000 (shared Hee Mang Hall), food KRW 5,475,000 (school cafeteria) and books "
               "KRW 300,000 = KRW 7,103,000 a year. The KAIST Scholarship's KRW 350,000 monthly stipend (KRW 4,200,000 a year) isn't subtracted here.")

# major, field, quote from the guide's department list
P = [("Computer Science", "Computer Science"), ("Electrical Engineering", "Electrical and Electronic Engineering"),
     ("Mechanical Engineering", "Mechanical Engineering"), ("Aerospace Engineering", "Aerospace Engineering"),
     ("Chemical & Biomolecular Engineering", "Chemical Engineering"), ("Industrial & Systems Engineering", "Engineering"),
     ("Materials Science & Engineering", "Materials Science"), ("Physics", "Physics"), ("Mathematical Sciences", "Mathematics"),
     ("Biological Sciences", "Biology"), ("Business and Technology Management", "Business")]
for name, field in P:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower().replace("&", "and")).strip("-")
    adm = lambda cur: {"curriculum": cur, "source": "guide", "threshold": TH.format(name=name), "required_subjects": [], "tests": [], "english": ENG}
    write("kr-kaist", {"uni": "kr-kaist", "slug": f"bs-{slug}",
        "sources": {"guide": dict(GUIDE, quotes=GUIDE["quotes"] + on("kaist-guide-2027", [name])), "coa": COA, "sch": SCH},
        "program": {"name": name, "degree_type": "B.S.", "field": field, "faculty": "", "duration_years": 4, "duration_source": "coa",
                    "languages": ["en"], "entry_year": "Spring or Fall 2027", "platform": "KAIST international undergraduate application (online)", "source": "guide",
                    "summary": f"{name} at KAIST, Daejeon: enter with an undeclared major, choose it in year two; taught in English; the KAIST Scholarship covers tuition for admitted international students.",
                    "application_requirements": []},
        "costs": [{"residency": "international", "currency": "KRW", "tuition_annual": 6866000, "mandatory_fees_annual": 916680,
                   "academic_year": "Cost of attendance as published (KAIST Office of Admissions)", "source": "coa",
                   "note": "Tuition KRW 6,866,000 a year before the KAIST Scholarship, which covers the entire tuition for 4 years for admitted international students "
                           "(plus a KRW 350,000 monthly stipend and NHI). Compulsory: NHI premiums KRW 916,680 a year. KAIST's own net figure is KRW 3,359,000 a year.",
                   "living": {"monthly": [], "months": 12, "yearly": [1328000, 5475000, 300000], "source": "coa",
                              "kind": "genuine_cost_of_living_estimate", "note": LIVING_NOTE}}],
        "admissions": [adm("ib"), adm("a-level"), adm("us-hs"), adm("cbse"), adm("international-other")]})
    print("wrote", slug)

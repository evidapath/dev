# Data fixes found by the 2026-11-24 SEO/content review, each re-read from the official page.
# Same helpers as fixes.py (every quote must be on the saved page; patches carry ifRevisionID).
import json, re, hashlib, sys, datetime
import os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from q import q
P = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".research-cache", "pages") + "/"
TODAY = datetime.date.today().isoformat()
def norm(s): return re.sub(r"\s+", " ", s.replace("\xa0"," ").replace("’","'").replace("–","-")).strip().lower()
out = []; srcs = {}
def source(page, title, org, quotes, method=None):
    url = open(P + page + ".url").read().strip(); text = norm(open(P + page + ".txt").read())
    for qq in quotes:
        assert norm(qq) in text, f"quote not on {page}: {qq}"
    h = hashlib.sha1(url.encode()).hexdigest()[:12]; sid = f"sourceRecord-ev-{h}"
    if sid not in srcs:
        old = q(f'*[_id=="{sid}"][0].excerpt')
        if old is None:
            out.append({"createOrReplace": {"_id": sid, "_type": "sourceRecord", "id": f"ev-{h}", "url": url, "title": title, "source_organization": org,
                "source_type": "official_university", "excerpt": " ".join(quotes), "retrieved_at": f"{TODAY}T00:00:00Z",
                "retrieval_method": method or f"Read by EvidaPath data-fix pass {TODAY}; quotes checked against the saved page", "fields_supported": [], "notes": ""}})
        else:
            missing = [qq for qq in quotes if norm(qq) not in norm(old)]
            if missing: out.append({"patch": {"id": sid, "set": {"excerpt": " ".join([old, *missing])}}})
        srcs[sid] = True
    return {"_key": h, "_ref": sid, "_type": "reference", "_weak": True}
def doc(i):
    d = q(f'*[_id=="{i}"][0]'); assert d, i; return d
def patch(i, set_=None, refs=(), unset=()):
    d = doc(i); m = {"patch": {"id": i, "ifRevisionID": d["_rev"]}}
    if set_: m["patch"]["set"] = set_
    if unset: m["patch"]["unset"] = list(unset)
    have = {r["_ref"] for r in d.get("source_refs", [])}
    new = [r for r in refs if r["_ref"] not in have]
    if new: m["patch"]["insert"] = {"after": "source_refs[-1]", "items": new}
    out.append(m)
NOTE = 'extension_metadata.fields[_key=="fee_note"].value'
def has_note(i): return any(f.get("_key") == "fee_note" for f in (doc(i).get("extension_metadata") or {}).get("fields", []))

# 1. Imperial EFDS: the £44,800 figure is right; the note quoted the 2026-27 fee (£42,700).
imp = source("500645630fa5", "BSc Economics, Finance and Data Science | Imperial College London", "Imperial College London",
             ["Start date October 2027", "Tuition fees Home: £10,050 International: £44,800"])
cid = "costProfile-uk-imperial-cost-bsc-econ-finance-ds-international"
assert has_note(cid)
patch(cid, {NOTE: "International: £44,800 a year for October 2027 entry (Imperial course page)."}, [imp])

# 2. TU/e: €22,400 (2027-2028) is right; the notes quoted the 2026-2027 fee (€18,600).
tue = source("02c5000c99d0", "Tuition fee | Eindhoven University of Technology", "Eindhoven University of Technology",
             ["2026-2027 2027-2028 Institutional fee for bachelor's students € 18,600 € 22,400"])
for cid in ["costProfile-nl-tue-cost-bsc-cse-international", "costProfile-nl-tue-cost-bsc-ee-international"]:
    assert has_note(cid), cid
    patch(cid, {NOTE: "Institutional fee for bachelor's students: € 22,400 for 2027-2028 (€ 18,600 in 2026-2027), for students who don't qualify for the statutory fee."}, [tue])

# 3. UBC: the per-credit rates are on UBC's own fee table; the notes said "secondary sources".
ubc = source("ff6d5ef77a2c", "Undergraduate tuition fees | UBC Vancouver Academic Calendar", "University of British Columbia",
             ["International per-credit rate (commenced in 2026S or later)", "Applied Science $1,789.18", "Arts $1,717.68",
              "Commerce $2,222.61", "Science $1,769.40"])
for cid, fac, rate in [("costProfile-ca-ubc-cost-ba-economics-international", "Arts", "1,717.68"),
                       ("costProfile-ca-ubc-cost-basc-engineering-international", "Applied Science", "1,789.18"),
                       ("costProfile-ca-ubc-cost-bcom-international", "Commerce", "2,222.61"),
                       ("costProfile-ca-ubc-cost-bsc-cs-international", "Science", "1,769.40")]:
    assert has_note(cid), cid
    assert rate in doc(cid)["academic_year"], cid
    patch(cid, {NOTE: f"International per-credit rate for {fac} students starting in 2026/27: CAD {rate} (UBC Vancouver Academic Calendar). The yearly figure assumes 30 credits a year (our calculation); student fees are extra."}, [ubc])

# 4. NYU Abu Dhabi: the stored USD 68,576 is the tuition line, not the cost of attendance.
nyu = source("3c7fabbf761e", "Cost of Attendance | NYU Abu Dhabi | NYU Bulletins", "New York University Abu Dhabi",
             ["NYU Abu Dhabi Estimated Cost of Attendance 2026-2027", "Student Tuition $68,576"])
for d in q('*[_type=="costProfile" && program_ref->university_ref->id=="ae-nyu-abu-dhabi" && tuition_annual==68576]{_id}'):
    if has_note(d["_id"]):
        patch(d["_id"], {NOTE: "Student Tuition $68,576 for 2026-2027 (NYU Abu Dhabi Estimated Cost of Attendance), the same for every major. Housing, food, insurance and books are listed separately."}, [nyu])

# 5. UNSW Media: AUD 52,167 is the 3-year full fee spread evenly; say so.
unsw = source("78928d194e0c", "Bachelor of Media (Communication and Journalism) | UNSW Sydney", "UNSW Sydney",
              ["2026 Indicative first year full fee $49,000*", "2026 Indicative full fee to complete degree $156,500*", "3 Year(s)"])
cid = "costProfile-au-unsw-cost-media-communication-journalism-international"
assert has_note(cid)
patch(cid, {NOTE: "International: 2026 indicative full fee to complete the degree AUD 156,500 over 3 years = about AUD 52,167 a year (our calculation). UNSW's indicative first-year fee is AUD 49,000."}, [unsw])

# 6. AUS English: first-year applicants may use only TOEFL or IELTS (EmSAT 1550 is listed for transfer
#    applicants), and the Bridge Program score range isn't on the cited page.
aus = source("22de3cd61421", "Application requirements, bachelor's degrees | American University of Sharjah", "American University of Sharjah",
             ["IELTS Academic TOEFL iBT TOEFL iTP 6.5 4.5 (previously 80) 550",
              "Only TOEFL and IELTS are accepted by the American University of Sharjah",
              "Other required documents for Transfer applicants: a minimum EmSAT Achieve English result of 1550"])
rows = q('*[_type=="admissionsRequirement" && program_ref->university_ref->id=="ae-aus"]{_id,"lr":language_requirements}')
assert len(rows) == 32, len(rows)
for r in rows:
    assert [x["_key"] for x in r["lr"]] == ["lr1"], r["_id"]
    patch(r["_id"], {'language_requirements[_key=="lr1"].min_score': "IELTS Academic 6.5, or TOEFL iBT 4.5 (previously 80), or TOEFL iTP 550. Only TOEFL and IELTS are accepted for first-year applicants (EmSAT Achieve English 1550 is listed for transfer applicants).",
                     'language_requirements[_key=="lr1"].test_name': "IELTS Academic / TOEFL iBT / TOEFL iTP"}, [aus])

# 7. UAEU: records used the UAE-nationals requirements; international applicants have their own page.
#    Read in Subhan's Chrome on 2026-11-24 (the site blocks automated fetches); saved as page text.
uaeu = source("bde70b7f9083", "Undergraduate admissions: international students and children of UAEU employees | UAE University", "United Arab Emirates University",
              ["Obtaining a minimum score of (90%) in the English subject on the MOE Grade 12 certificate",
               "(Academic) IELTS (Local) TOEFL ITP TOEFL iBT 5.5 525 70", "TOEFL ITP tests taken from outside the UAE",
               "College of Engineering High School Average English Language Proficiency Requirement Mathematics Requirement Science Requirement Other College-Specific Requirements 90% or its equivalent",
               "SAT Math: 590 points AP Math: 4 points IB- HL Math: 5 points GCE A-Level: B grade Physics plus one Science Subject (Chemistry or Biology)",
               "College of Computing and Artificial Intelligence High School Average English Language Proficiency Requirement Mathematics Requirement Science Requirement Other College-Specific Requirements 90% or its equivalent",
               "One of the Science Subjects (Physics or Computer Science): HS 90% or its equivalent: AP: 4 points IB- HL: 5 points GCE A-Level: B grade",
               "College of Business and Economics High School Average English Language Proficiency Requirement Mathematics Requirement Science Requirement Other College-Specific Requirements 85% or its equivalent",
               "Math: HS 80% or its equivalent: SAT Math: 555 points AP Math: 3 points IB- HL Math: 4 points GCE A-Level: C grade"],
              method=f"Read in a normal browser by EvidaPath on {TODAY} (the site blocks automated fetches); page text saved and quotes checked against it")
ccai = source("91755835c0b6", "About the College of Computing and Artificial Intelligence | UAE University", "United Arab Emirates University",
              ["the BSc in Computer Science, and the BSc in Information Security programs in the CCAI"])
nat_src = "sourceRecord-ev-" + hashlib.sha1(b"https://www.uaeu.ac.ae/en/admission/undergraduate-admissions-current-student.shtml").hexdigest()[:12]
ENG = "English: 90% in high-school English, or IELTS Academic 5.5, TOEFL ITP 525 (taken in the UAE) or TOEFL iBT 70."
BE = "International applicants (College of Business and Economics): high-school average 85% or its equivalent. " + ENG + " Maths: 80% in high school or its equivalent (SAT Math 555, AP Maths 3, IB HL Maths 4, or A-Level grade C)."
TH = {
  "b-econ": BE, "bba": BE,
  "bsc-eng": "International applicants (College of Engineering): high-school average 90% or its equivalent. " + ENG + " Maths: 90% in high school or its equivalent (SAT Math 590, AP Maths 4, IB HL Maths 5, or A-Level grade B). Science: Physics plus Chemistry or Biology at 90% or its equivalent (AP 4, IB HL 5, or A-Level grade B).",
  "bsc-cs": "International applicants (College of Computing and Artificial Intelligence): high-school average 90% or its equivalent. " + ENG + " Maths: 90% in high school or its equivalent (SAT Math 590, AP Maths 4, IB HL Maths 5, or A-Level grade B). Science: Physics or Computer Science at 90% or its equivalent (AP 4, IB HL 5, or A-Level grade B).",
}
rows = q('*[_type=="admissionsRequirement" && program_ref->university_ref->id=="ae-uaeu"]{_id,"lr":language_requirements,"st":standardized_tests,"refs":source_refs[]._ref}')
assert len(rows) == 16, len(rows)
for r in rows:
    prog = next(k for k in TH if f"-admreq-{k}-" in r["_id"])
    assert [x["_key"] for x in r["lr"]] == ["lr1"], r["_id"]
    unset = []
    if any(t.get("_key") == "st1" and "EmSAT" in (t.get("test_name") or "") for t in (r["st"] or [])):
        unset.append('standardized_tests[_key=="st1"]')
    if nat_src in (r["refs"] or []):
        unset.append(f'source_refs[_ref=="{nat_src}"]')
    patch(r["_id"], {"academic_threshold": TH[prog],
                     'language_requirements[_key=="lr1"].min_score': "IELTS Academic 5.5, TOEFL ITP 525 (taken in the UAE) or TOEFL iBT 70, or 90% in English on the UAE MOE Grade 12 certificate. IELTS Indicator, TOEFL Home Edition and Duolingo are not accepted."},
          [uaeu] + ([ccai] if prog == "bsc-cs" else []), unset)

dest = sys.argv[1] if len(sys.argv) > 1 else "/Users/subhanrao/Desktop/evidapath/fact-checks/pending/2026-11-24-data-fixes.ndjson"
open(dest, "w").write("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in out))
print(len(out), "mutations ->", dest)

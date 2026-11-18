import json, re, hashlib, sys, datetime
import os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from q import q
P = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".research-cache", "pages") + "/"
TODAY = datetime.date.today().isoformat()
def norm(s): return re.sub(r"\s+", " ", s.replace("\xa0"," ").replace("’","'").replace("–","-")).strip().lower()
out = []; srcs = {}
def source(page, title, org, quotes):
    url = open(P + page + ".url").read().strip(); text = norm(open(P + page + ".txt").read())
    for qq in quotes:
        assert norm(qq) in text, f"quote not on {page}: {qq}"
    h = hashlib.sha1(url.encode()).hexdigest()[:12]; sid = f"sourceRecord-ev-{h}"
    if sid not in srcs:
        old = q(f'*[_id=="{sid}"][0].excerpt')
        if old is None:
            out.append({"createOrReplace": {"_id": sid, "_type": "sourceRecord", "id": f"ev-{h}", "url": url, "title": title, "source_organization": org,
                "source_type": "official_university", "excerpt": " ".join(quotes), "retrieved_at": f"{TODAY}T00:00:00Z",
                "retrieval_method": f"Read by EvidaPath data-fix pass {TODAY}; quotes checked against the saved page", "fields_supported": [], "notes": ""}})
        else:
            missing = [qq for qq in quotes if norm(qq) not in norm(old)]
            if missing: out.append({"patch": {"id": sid, "set": {"excerpt": " ".join([old, *missing])}}})
        srcs[sid] = True
    return {"_key": h, "_ref": sid, "_type": "reference", "_weak": True}
def doc(i):
    d = q(f'*[_id=="{i}"][0]'); assert d, i; return d
def patch(i, set_=None, refs=()):
    d = doc(i); m = {"patch": {"id": i, "ifRevisionID": d["_rev"]}}
    if set_: m["patch"]["set"] = set_
    have = {r["_ref"] for r in d.get("source_refs", [])}
    new = [r for r in refs if r["_ref"] not in have]
    if new: m["patch"]["insert"] = {"after": "source_refs[-1]", "items": new}
    out.append(m)
NOTE = 'extension_metadata.fields[_key=="fee_note"].value'

# 1. Taylor's international fees: the stored figure used the Malaysian total + 6%; Taylor's international schedule gives the tuition.
T = [("costProfile-my-taylors-cost-bsc-cs-international","tay-usd-cs","Computer Science","GRAND TOTAL 2,800 127,776 644 3,000 7,500 2,920 3,000 147,640 156,105 41,080",127776,3,"BACHELOR OF COMPUTER SCIENCE (HONOURS)"),
     ("costProfile-my-taylors-cost-bba-international","tay-usd-bus","Business","GRAND TOTAL 2,800 136,200 644 3,000 7,500 2,920 3,000 156,064 165,034 43,430",136200,3,"BACHELOR OF BUSINESS (HONOURS) WITH FREE ELECTIVES / MINOR / EXTENSION"),
     ("costProfile-my-taylors-cost-beng-me-international","tay-usd-e","Engineering","GRAND TOTAL 2,800 176,192 644 3,000 10,000 3,240 3,000 198,876 210,396 55,367",176192,4,"BACHELOR OF MECHANICAL ENGINEERING WITH HONOURS")]
for cid, page, school, row, tuition, years, prog in T:
    r = source(page, f"Academic terms and fee schedule 2027, international students ({school}, PDF) | Taylor's University", "Taylor's University",
               ["ACADEMIC TERMS AND FEE SCHEDULE FOR 2027", prog, "International Student", row])
    annual = round(tuition / years)
    patch(cid, {"tuition_annual": annual,
                "academic_year": f"2027 (international tuition RM {tuition:,} / {years} years, our calculation; excludes 6% service tax)",
                NOTE: f"International student tuition fee RM {tuition:,} for the programme (Taylor's 2027 international fee schedule) / {years} years = RM {annual:,} a year. Excludes the 6% service tax for non-Malaysian citizens and the other international charges in the schedule. Corrected from a figure that used the Malaysian-student total plus 6%."},
          [r])

# 2. Universiti Malaya: 3.5-year programmes, and fees not inclusive of 6% SST.
umfee = source("um-fee", "Fee structure, Bachelor programme (international), Universiti Malaya (PDF)", "Universiti Malaya",
               ["Bachelor of Computer Science 89,200.00", "Bachelor of Economic 77,100.00", "3) Fees structure is based on minimum or common period of study."])
umcs = source("2c2a83940091", "Bachelor of Computer Science (Artificial Intelligence) | Study@UM, Universiti Malaya", "Universiti Malaya",
              ["Duration: 3.5 Years (7 Semester and 1 special semester), Full time (Coursework)", "International RM 89,200", "( Note: Not inclusive of 6% Sales and Service Tax (SST))"])
umec = source("4ee04c6da1f2", "Bachelor of Economics | Study@UM, Universiti Malaya", "Universiti Malaya",
              ["Duration: 3.5 Years (7 Semester), Full time (Coursework)", "International RM 77,100", "( Note: Not inclusive of 6% Sales and Service Tax (SST))"])
umee = source("d6d76574c800", "Bachelor of Electrical Engineering | Study@UM, Universiti Malaya", "Universiti Malaya",
              ["Duration: 4 Years (8 semester and 1 special semester ), Full time (Coursework)", "( Note: Not inclusive of 6% Sales and Service Tax (SST))"])
for pid, total, ref, name in [("bsc-cs", 89200, umcs, "Computer Science"), ("ba-economics", 77100, umec, "Economics")]:
    patch(f"program-my-um-{pid}", {"duration_value": 3.5}, [ref])
    patch(f"costProfile-my-um-cost-{pid}-international",
          {"duration_years": 3.5, "tuition_annual": round(total / 3.5),
           "academic_year": f"2025/2026 intake onwards (RM {total:,} for the whole programme / 3.5 years, our calculation)",
           NOTE: f"International: RM {total:,} for the programme (UM's fee structure is based on the minimum period of study, 3.5 years), shown as RM {round(total/3.5):,} a year. Not inclusive of 6% Sales and Service Tax (SST)."},
          [ref, umfee])
for pid, total in [("bsc-cs", 10200), ("ba-economics", 8800)]:
    d = doc(f"costProfile-my-um-cost-{pid}-malaysian-upu")
    patch(d["_id"], {"duration_years": 3.5, "tuition_annual": round(total / 3.5),
                     NOTE: f"RM {total:,} for the whole programme for Malaysians admitted through UPU, 2025/2026 intake onwards (UM fee structure) = about RM {round(total/3.5):,}/yr over 3.5 years (our calculation). Living cost: same estimate as for international students (a student living away from home)."},
          [ref for ref in [umcs if pid == "bsc-cs" else umec]])
patch("costProfile-my-um-cost-beng-ee-international",
      {NOTE: "International: RM 132,100 for the programme (UM's fee structure is based on the minimum period of study, 4 years), shown as RM 33,025 a year. Not inclusive of 6% Sales and Service Tax (SST)."}, [umee])

# 3. Twente English: TOEFL iBT 90 (21 per section) or 4.5 on the new scale.
tw = source("979afa0dca25", "Language requirements | University of Twente", "University of Twente",
            ["not older than two years, with an overall band score of at least 6.0, and a minimum score on each section of at least 5.5.",
             "not older than two years, with an overall score of 90, and a minimum score on each section of at least 21.",
             "not older than two years, with an overall score of 4.5, and a minimum score of 4.5 on reading, listening and writing."])
for prog in ["bsc-iba", "bsc-me", "bsc-tcs"]:
    for cur in ["a-level", "ib", "international-other"]:
        patch(f"admissionsRequirement-nl-ut-admreq-{prog}-{cur}",
              {'language_requirements[_key=="lr1"].min_score': "IELTS Academic: overall 6.0, minimum 5.5 per section. Also accepted: TOEFL iBT 90 (minimum 21 per section, scale used before January 2026) or 4.5 on the new scale (4.5 in reading, listening and writing, 4 in speaking)."}, [tw])

# 4. McGill BSc Computer Science: normally a four-year, 120-credit degree.
mg = source("225dee1426b1", "Minimum Credit Requirement | Faculty of Science | Course Catalogue - McGill University", "McGill University",
            ["Students are normally admitted to a four-year degree requiring the completion of 120 credits. At the time of admission to the Science program, Advanced Standing of up to 30 credits may be granted based on pre-McGill academic studies"])
patch("program-ca-mcgill-bsc-cs", {"duration_value": 4}, [mg])
for d in q('*[_type=="costProfile" && program_ref._ref=="program-ca-mcgill-bsc-cs"]{_id}'):
    patch(d["_id"], {"duration_years": 4}, [mg])

# 5. RIT Dubai Computer Engineering: the typical course sequence runs to a fifth year (with co-op).
rit = source("26ef7884d1f5", "Bachelor of Science in Computer Engineering | RIT Dubai", "RIT Dubai", ["Total Credit Hours - 129", "Fourth Year", "Fifth Year", "Co-op"])
patch("program-ae-rit-dubai-bs-computer-engineering", {"duration_value": 5}, [rit])
for d in q('*[_type=="costProfile" && program_ref._ref=="program-ae-rit-dubai-bs-computer-engineering"]{_id}'):
    patch(d["_id"], {"duration_years": 5}, [rit])

# 6. AUS compulsory fees: activities fee, health plan (Plan II minimum) and clinic fee are paid by every student.
aus = source("d6ebdade3863", "Undergraduate Tuition and Fees | American University of Sharjah", "American University of Sharjah",
             ["Student Activities Fee AED 422 + 5% VAT per semester", "Plan II: For all students who are not on Plan I 300",
              "For All Students: Medical services at University Hospital Sharjah's Primary Care Clinic and Emergency Room 112.50 + 5% VAT"])
for d in q('*[_type=="costProfile" && _id match "costProfile-ae-aus*"]{_id}'):
    patch(d["_id"], {"mandatory_fees_annual": 1722,
                     'extension_metadata.fields[_key=="fee_note"].value': doc(d["_id"])["extension_metadata"]["fields"][0]["value"].split(" mandatory_fees_annual")[0].split(" Compulsory fees:")[0]
                       + " Compulsory fees: Student Activities Fee AED 422 + 5% VAT per semester, health insurance at least AED 300 per semester (Plan II, for students not on Plan I) and the clinic fee AED 112.50 + 5% VAT per semester = about AED 1,722 a year (our calculation); Plan I costs more."}, [aus])

# 7. CUD: the stored Computer Science and Engineering figures already include VAT; the notes said pre-VAT.
cud = source("5875657056d8", "Fees | Canadian University Dubai", "Canadian University Dubai",
             ["Bachelor of Science in Computer Science AED 2,300.50 AED 115.03 AED 2,415.53 AED 7,246.58 30"])
patch("costProfile-ae-canadian-university-dubai-cost-bsc-cs-all-students",
      {NOTE: "Computer Science: AED 2,415.53 per credit hour including 5% VAT (AED 2,300.50 before VAT) × 30 credit hours a year = AED 72,465.90 a year, plus AED 2,236.50 incidental fees."}, [cud])
patch("costProfile-ae-canadian-university-dubai-cost-bsc-eng-all-students",
      {NOTE: "Engineering: AED 2,415.53 per credit hour including 5% VAT (AED 2,300.50 before VAT) × 34 credit hours a year = AED 82,127.85 a year, plus AED 2,236.50 incidental fees."}, [cud])

# 8. Sharjah: the stored AED 63,740 is right; the notes quoted older rates.
uos = source("uos-fee", "Tuition fees for undergraduates admitted from 2022/2023 (PDF) | University of Sharjah", "University of Sharjah",
             ["Tuition Fees for Students who have been admitted from Academic Year 2022/2023", "Bachelor of Science in Computer Science", "Bachelor of Science in Electrical and Electronics Engineering 31,870 63,740 2,656"])
for pid in ["b-econ", "bba", "bsc-cs", "bsc-eng"]:
    patch(f"costProfile-ae-university-of-sharjah-cost-{pid}-all-students",
          {NOTE: "Annual fee AED 63,740 (semester fee AED 31,870; AED 2,656 per credit hour) for Business, Economics, Computer Science and Computer, Civil and Electrical and Electronics Engineering, per Sharjah's fee table for students admitted from 2022/2023. Some engineering programmes (Mechanical, Nuclear and others) cost more."}, [uos])

# 9. Waterloo: stored figures are right (terms 1A + 1B); the notes described other terms.
wl = source("92cd8f540ce4", "Fee schedule for international undergraduate students, Fall 2026 | University of Waterloo", "University of Waterloo",
            ["Co-op - Term 1A $6,988.40 $34,942.00", "Co-op - Term 1B $6,919.40 $34,597.00",
             "Accounting & Financial Management - Co-op Term 1A $5,402.00 $27,010.00", "Accounting & Financial Management - Co-op Term 1B $5,402.00 $27,010.00"])
patch("costProfile-ca-waterloo-cost-basc-engineering-international",
      {NOTE: "First year, Engineering (co-op): term 1A maximum tuition CAD 34,942 + term 1B CAD 34,597 = CAD 69,539 (Fall 2026 international fee schedule, our sum). Co-op fee CAD 836 per term is extra."}, [wl])
patch("costProfile-ca-waterloo-cost-bafm-international",
      {NOTE: "First year, Accounting & Financial Management (co-op): terms 1A and 1B at CAD 27,010 each = CAD 54,020 (Fall 2026 international fee schedule, our sum). From term 2A the rate is CAD 27,673 a term."}, [wl])

# 10. Heriot-Watt Dubai "Engineering" is the Electrical and Electronic Engineering programme (its own page).
hw = source("09db54a3bef2", "BEng (Hons) Electrical and Electronic Engineering | Heriot-Watt University Dubai", "Heriot-Watt University Dubai", ["BEng (Hons) Electrical and Electronic Engineering"])
patch("program-ae-heriot-watt-dubai-beng-engineering",
      {"program_name": "Electrical and Electronic Engineering", "degree_type_local": "BEng (Hons) Electrical and Electronic Engineering, Heriot-Watt University Dubai. Civil and Mechanical Engineering are separate programmes."}, [hw])

open("/Users/subhanrao/Desktop/evidapath/fact-checks/pending/2026-11-17-data-fixes.ndjson", "w").write("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in out))
print(len(out), "mutations")

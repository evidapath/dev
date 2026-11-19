"""University of Twente English-taught bachelor's programmes (written 2026-11-19), same pattern as
the Twente Psychology record in nl_psych.py. Subject requirements come from the two shared pages
(GCE A2-Level and IB "Admission requirements per bachelor's programme", valid for the September
2027 intake); duration, language, faculty and numerus fixus from each programme page; fees from
each programme's tuition-fee page (2027-2028 institutional and statutory).
  python3 -I scripts/research/gen/nl_ut.py
"""
import hashlib, re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
pid = lambda u: hashlib.sha1(u.encode()).hexdigest()[:12]
flat = lambda u: re.sub(r"\s+", " ", (PAGES / f"{pid(u)}.txt").read_text())
lines = lambda u: [l.strip() for l in (PAGES / f"{pid(u)}.txt").read_text().splitlines() if l.strip()]
B = "https://www.utwente.nl/en/education/bachelor/"
AL = B + "application-admission/admission/diplomas/uk/"
IB = B + "admission/diplomas/international-baccalaureate/"
LANG = B + "application-admission/admission/language-requirements/"
ENG = {"test_name": "IELTS Academic (or accepted equivalent)", "source": "lang",
       "min_score": "IELTS Academic 6.0 overall, at least 5.5 in each section; TOEFL iBT 90 (at least 21 per section, scale before January 2026) or 4.5 (new scale); Cambridge C1 Advanced or C2 Proficiency 169 (162 per section).",
       "notes": "An IB Diploma taught in English with an English exam subject exempts you from a test."}
LANGQ = ["not older than two years, with an overall band score of at least 6.0, and a minimum score on each section of at least 5.5.",
         "not older than two years, with an overall score of 90, and a minimum score on each section of at least 21.",
         "not older than two years, with an overall score of 4.5, and a minimum score of 4.5 on reading, listening and writing.",
         "obtained with an overall score of at least 169 and a minimum score on each section of at least 162.",
         "TOEFL iBT (internet-based) certificate (before January 2026)",
         "Cambridge C1 Advanced , formerly known as; Cambridge English Advanced (CAE).", "Cambridge C2 Proficiency , formerly known as; Cambridge English Proficiency (CPE)."]
ALQ = ["3 (I)GCSE / GCE O-Level with an A, B or C grade or 4 – 9 score, and 3 full GCE A2-Level with an A, B or C grade.",
       "Students need to have six different subjects in (I)GCSE / GCE O-Level and A2-Level.", "These admission requirements are valid for the September 2027 intake."]
IBQ = ["Besides the requirements from the IBO organization for you to graduate with your full IB Diploma.", "These admission requirements are valid for the September 2027 intake."]
for u, qs in ((LANG, LANGQ), (AL, ALQ), (IB, IBQ)):
    for q in qs:
        assert q in flat(u), (u, q)
TABLE_END = ("Close", "Suggestions")


def rows(u, label, start_marker):
    """The lines of one programme in a 'per bachelor's programme' list: its first line starts with the
    programme name, and the block runs until the next programme's first line."""
    ls = lines(u)
    i0 = max(i for i, l in enumerate(ls) if l.startswith(start_marker))
    firsts = [i for i in range(i0, len(ls)) if re.match(r"^[A-Z][A-Za-z &-]+ (GCE A2-Level|Mathematics) ", ls[i])]
    i = next(k for k in firsts if ls[k].startswith(label + " "))
    j = min([k for k in firsts if k > i] + [next(k for k in range(i, len(ls)) if ls[k] in TABLE_END)])
    return ls[i:j]


def subjects(block, label):
    req = [block[0][len(label) + 1:]] + block[1:]
    assert "Dutch" not in req, (label, req)
    return req


PROGS = [  # slug, page path, name on the A-level list, name on the IB list, programme name, field
    ("bsc-advanced-technology", "advanced-technology", "Advanced Technology", "Advanced Technology", "Advanced Technology", "Engineering"),
    ("bsc-applied-mathematics", "applied-mathematics", "Applied Mathematics", "Applied Mathematics", "Applied Mathematics", "Mathematics"),
    ("bsc-applied-physics", "applied-physics", "Applied Physics", "Applied Physics", "Applied Physics", "Physics"),
    ("bsc-business-it", "business-information-technology", "Business Information Technology", "Business Information Technology", "Business Information Technology", "Computing"),
    ("bsc-civil-engineering", "civil-engineering", "Civil Engineering", "Civil Engineering", "Civil Engineering", "Civil Engineering"),
    ("bsc-communication-science", "communication-science", "Communication Science", "Communication Science", "Communication Science", "Media and Communication"),
    ("bsc-creative-technology", "creative-technology", "Creative Technology", "Creative Technology", "Creative Technology", "Computing"),
    ("bsc-electrical-engineering", "electrical-engineering", "Electrical Engineering", "Electrical Engineering", "Electrical Engineering", "Electrical and Electronic Engineering"),
    ("bsc-industrial-design-engineering", "industrial-design-engineering", "Industrial Design Engineering", "Industrial Design Engineering", "Industrial Design Engineering", "Engineering"),
    ("bsc-industrial-engineering-management", "industrial-engineering-and-management", "Industrial Engineering & Management Science", "Industrial Engineering & Management", "Industrial Engineering and Management", "Engineering"),
]
for slug, path, al_label, ib_label, name, field in PROGS:
    cu = f"{B}programmes/{path}/"
    fu = f"{cu}enrolment/tuition-fees/"
    ct, ft = flat(cu), flat(fu)
    dur = re.search(r"Duration (\d) years", ct).group(0)
    fac = re.search(r"Faculty (Science and Technology|Electrical Engineering Mathematics and Computer Science|Engineering Technology|Behavioural, Management & Social Sciences)", ct)
    nf = re.search(r"Numerus fixus (No, but mandatory matching applies|No)", ct).group(0)
    for q in ("Language English", dur, fac.group(0), nf):
        assert q in ct, (slug, q)
    inst = re.search(r"Overview of institutional tuition fees for this Bachelor's 2026-2027 \(Sep-Aug\) € [\d,]+ per year 2027-2028 \(Sep-Aug\) € ([\d,]+) per year", ft)
    stat = re.search(r"Overview of statutory tuition fees for this Bachelor's 2026-2027 \(Sep-Aug\) € [\d,]+ per year 2027-2028 \(Sep-Aug\) € ([\d,]+) per year", ft)
    assert inst and stat, slug
    fee, eu = int(inst.group(1).replace(",", "")), int(stat.group(1).replace(",", ""))
    al = subjects(rows(AL, al_label, "Admission requirements per bachelor"), al_label)
    ib = subjects(rows(IB, ib_label, "A high score in a Standard Level"), ib_label)
    alq = " ".join(rows(AL, al_label, "Admission requirements per bachelor"))
    ibq = " ".join(rows(IB, ib_label, "A high score in a Standard Level"))
    note_ib = [l for l in lines(IB) if l.startswith("*") and "Higher Level" in l] if any(s.endswith("*") for s in ib) else []
    al_txt = ", ".join(s.replace("GCE A2-Level ", "A-Level ") for s in al)
    ib_txt = ", ".join(s.replace(" *", "") for s in ib) + (f" ({note_ib[0].lstrip('* ')})" if note_ib else "")
    al_subj = [s.replace("GCE A2-Level ", "") for s in al if s.startswith("GCE A2-Level")]
    ib_subj = sorted({"Mathematics" if s.startswith("Mathematics") else s.split(" - ")[0].strip() for s in ib if s != "English"})
    mm = " Mandatory matching applies (no numerus fixus)." if "matching" in nf else ""
    write("nl-majors", {"uni": "nl-ut", "slug": slug,
        "sources": {
            "course": {"url": cu, "page": pid(cu), "title": ct.split(" Skip to main content")[0].strip(), "organization": "University of Twente",
                       "quotes": ["Language English", dur, fac.group(0), nf]},
            "a-level": {"url": AL, "page": pid(AL), "title": "GCSE & GCE A2-Levels | University of Twente", "organization": "University of Twente", "quotes": ALQ + [alq]},
            "ib": {"url": IB, "page": pid(IB), "title": "International Baccalaureate | University of Twente", "organization": "University of Twente", "quotes": IBQ + [ibq] + note_ib},
            "lang": {"url": LANG, "page": pid(LANG), "title": "Language requirements | University of Twente", "organization": "University of Twente", "quotes": LANGQ},
            "fees": {"url": fu, "page": pid(fu), "title": ft.split(" Skip to main content")[0].strip(), "organization": "University of Twente", "quotes": [inst.group(0), stat.group(0)]}},
        "program": {"name": name, "degree_type": "BSc", "field": field, "faculty": fac.group(1), "duration_years": int(dur.split()[1]), "languages": ["en"],
                    "entry_year": "2027-2028", "platform": "Studielink", "source": "course",
                    "summary": f"BSc {name}, {dur.split(' ', 1)[1]}, taught in English, Faculty of {fac.group(1)}.{mm}", "application_requirements": []},
        "costs": [{"residency": "international", "currency": "EUR", "tuition_annual": fee, "academic_year": "2027-2028 (non-EU/EEA institutional fee)", "source": "fees",
                   "living_from": "costProfile-nl-ut-cost-bsc-iba-international", "note": f"Institutional fee for non-EU/EEA students, 2027-2028: €{fee:,} a year."},
                  {"residency": "eu-eea", "currency": "EUR", "tuition_annual": eu, "academic_year": "2027-2028 (EU/EEA statutory fee)", "source": "fees",
                   "living_from": "costProfile-nl-ut-cost-bsc-iba-eu-eea", "note": f"Statutory fee 2027-2028: €{eu:,} a year."}],
        "admissions": [
            {"curriculum": "a-level", "source": "a-level", "required_subjects": al_subj, "tests": [], "english": ENG,
             "threshold": f"{name}: 3 (I)GCSEs (A-C or 4-9) and 3 full A-Levels (A-C), six different subjects; required: {al_txt}. Valid for the September 2027 intake."},
            {"curriculum": "ib", "source": "ib", "required_subjects": ib_subj, "tests": [], "english": ENG,
             "threshold": f"{name}: full IB Diploma; required: {ib_txt}. Valid for the September 2027 intake."}]})
    print(slug, fee, eu, "|", al_txt, "|", ib_txt)

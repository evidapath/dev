"""University of Sydney single degrees (written 2026-11-19) from the 2027 international guide PDF
(pdftotext without -layout, saved as .research-cache/pages/usyd-intl-guide-notes.txt): each
course's table row (CRICOS, duration, 2027 indicative Year 1 tuition fee per 1.0 EFTSL, IELTS,
TOEFL, ATAR, IB, GCE 3/4 A Levels, ...) and its course block (ATAR, IB, duration, assumed
knowledge). Column order is quoted from the table header.
  python3 -I scripts/research/gen/au_usyd.py
"""
import re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
PAGE = "usyd-intl-guide-notes"
URL = (PAGES / f"{PAGE}.url").read_text().strip()
T = re.sub(r"\s+", " ", (PAGES / f"{PAGE}.txt").read_text())
HEADER = ("Duration (full time in years) Commencing semester(s) 2027 indicative Year 1 tuition fee ($AUD)/1.0 EFTSL## "
          "English - IELTS Academic English - TOEFL iBT International ATAR IB Diploma GCE 3/4 A Levels")
INCR = "## Tuition fees are subject to annual increases."
ALEV = ("The first score listed is the requirement for three subjects; the second score is for four subjects. If there are more than four subjects, "
        "the best four will be used to calculate the aggregate. The aggregate is calculated from the A2 subjects based on A*=6, A=5, B=4, C=3, D=2, E=1.")
IBQ = "Entry is based on the total score for the completed International Baccalaureate (IB) Diploma."
for q in (HEADER, INCR, ALEV, IBQ):
    assert q in T, q
ROW = re.compile(r"(?P<cricos>\d{6}[A-Z]) (?P<dur>\d) (?P<sem>Feb/Aug|Feb) (?P<fee>\d{2},\d{3}) (?P<ielts>\d\. ?\d) \(\d\.\d\) \d+ \(\d+/\d+\) "
                 r"(?P<atar>[\d.]+) (?P<ib>\d+) (?P<a3>\d+)/(?P<a4>\d+) ")


def build(folder, slug, deg, name, field, extra_quotes=(), summary_extra=""):
    m = None
    for x in re.finditer(re.escape(deg) + " " + ROW.pattern, T):
        before = T[max(0, x.start() - 4):x.start()]
        if not before.endswith("and ") and not before.endswith(", "):
            assert m is None, f"{deg}: more than one row"
            m = x
    if m is None:
        # The plain copy prints a few rows without the course name: take the CRICOS code from the
        # -layout copy, where name and row share one line, and quote the plain row by that code.
        lay = [re.sub(r"\s+", " ", l).strip() for l in (PAGES / "usyd-intl-guide.txt").read_text().splitlines()]
        named = [l for l in lay if re.match(re.escape(deg) + " " + ROW.pattern, l + " ")]
        assert len(named) == 1, (deg, named)
        code = named[0][len(deg) + 1:].split(" ")[0]
        hits = list(re.finditer(ROW.pattern.replace(r"(?P<cricos>\d{6}[A-Z])", f"(?P<cricos>{code})"), T))
        assert len(hits) == 1, (deg, code, len(hits))
        m = hits[0]
        assert named[0].startswith(f"{deg} {m.group(0).strip()}"), (named[0], m.group(0))
    row = m.group(0).strip()
    g = m.groupdict()
    blk = re.search(rf"(?<!and ){re.escape(deg)} ATAR: {re.escape(g['atar'])} IB: {g['ib']} Entry: {g['sem']} Duration \(full time\): {g['dur']} years( Dalyell by invitation)?( Mathematics prerequisite (?:applies|may apply)‡)?( Prerequisites: [A-Za-z ]+?)? Assumed knowledge: (.+?)(?= (Majors|Programs|Program|Stream|Career|Combine|Recommended|Inherent|B [A-Z][^:.]{{0,80}}? ATAR:|You will))", T)
    assert blk, deg
    block, ak = blk.group(0), blk.group(4).rstrip(".")
    for q in extra_quotes:
        assert q in T, q
    fee = int(g["fee"].replace(",", ""))
    dur = int(g["dur"])
    pre = f" Sydney lists the prerequisite as{blk.group(3)[len(' Prerequisites:'):]} (an NSW subject)." if blk.group(3) else ""
    akt = f" Assumed knowledge (NSW subjects): {ak}.{pre}"
    write(folder, {"uni": "au-usyd", "slug": slug,
        "sources": {"guide": {"url": URL, "page": PAGE, "title": "University of Sydney International Guide, applying for 2027 entry (PDF)",
                              "organization": "The University of Sydney", "quotes": [HEADER, row, block, INCR, ALEV, IBQ, *extra_quotes]}},
        "program": {"name": name, "degree_type": "Bachelor", "field": field, "faculty": "", "duration_years": dur, "languages": ["en"],
                    "entry_year": "2027 entry", "platform": "", "source": "guide",
                    "summary": f"{re.sub(r'\bM ', 'Master of ', re.sub(r'\bB ', 'Bachelor of ', deg))} (CRICOS {g['cricos']}), {dur} years full time, starting {g['sem']}.{summary_extra}",
                    "application_requirements": []},
        "costs": [{"residency": "international", "currency": "AUD", "tuition_annual": fee, "academic_year": "2027 indicative Year 1 tuition fee (per 1.0 EFTSL, a full-time year)",
                   "source": "guide", "living_from": "costProfile-au-usyd-cost-becon-international",
                   "note": f"International, 2027 indicative Year 1 tuition fee: AUD {g['fee']} per 1.0 EFTSL (a full-time study load for a year). Sydney says tuition fees are subject to annual increases."}],
        "admissions": [
            {"curriculum": "a-level", "source": "guide", "required_subjects": [], "tests": [],
             "threshold": f"{name}: A-level aggregate {g['a3']} from three A2 subjects or {g['a4']} from four (A*=6, A=5, B=4, C=3, D=2, E=1). 2027 entry guide.{akt}"},
            {"curriculum": "ib", "source": "guide", "required_subjects": [], "tests": [],
             "threshold": f"{name}: IB Diploma total {g['ib']}. 2027 entry guide.{akt}"}]})
    print(slug, g["cricos"], dur, fee, "IB", g["ib"], "A", g["a3"], g["a4"], "|", ak[:60], pre)


SCI_MAJ = ["Biochemistry and Molecular Biology; Biology; Chemistry;", "Pharmacology; Physics; Physiology;"]
build("mathematics", "mathematical-sciences", "B Mathematical Sciences", "Mathematical Sciences", "Mathematics")
build("psychology", "psychology", "B Psychology", "Psychology", "Psychology")
for maj, folder in (("Biology", "biology"), ("Chemistry", "chemistry"), ("Physics", "physics")):
    build(folder, f"science-{folder}", "B Science", f"Science ({maj} major)", maj, SCI_MAJ, f" {maj} is one of the majors offered.")
build("biology", "medical-science", "B Science (Medical Science)", "Science (Medical Science)", "Medical Science")
build("humanities", "arts", "B Arts", "Arts", "Arts")
build("politics", "international-studies", "B International Studies", "International Studies", "International Relations")
build("politics", "ppe", "B Politics, Philosophy, and Economics", "Politics, Philosophy and Economics", "Politics, Philosophy and Economics")
build("business", "commerce", "B Commerce", "Commerce", "Business")
build("architecture", "design-in-architecture", "B Design in Architecture", "Design in Architecture", "Architecture")
build("pharmacy", "pharmacy", "B Pharmacy (Honours) and M Pharmacy Practice", "Pharmacy (Honours) and Master of Pharmacy Practice", "Pharmacy")
build("law", "arts-laws", "B Arts and B Laws", "Arts and Laws", "Law")

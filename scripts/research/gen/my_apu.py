"""Asia Pacific University of Technology & Innovation (APU), Kuala Lumpur: base records + three computing BSc (written 2026-11-26).

Source: each course page on apu.edu.my: "Full Time Duration 3 years Intake Date 25 March 2027 06 July 2027";
International fees RM34,900 (Year 1) + RM36,100 (Year 2) + RM37,500 (Year 3) = RM108,500 total (yearly
average our calculation), excluding 6% SST; entry (STPM, "STPM (A-Levels equivalent)", overseas 12th
Grade/A Level/HSC accepted); English (IELTS 5.0, TOEFL iBT 40, PTE 47). No living costs read. Information Technology not added: its page words the entry rule differently.
  python3 -I scripts/research/gen/my_apu.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, adm_all, slugify

ORG = "Asia Pacific University of Technology & Innovation"
FEE_Q = "International RM34,900 (USD9,185) Year 1 RM36,100 (USD9,500) Year 2 RM37,500 (USD9,870) Year 3 RM108,500 (USD28,555) Total for International"
COMMON = [FEE_Q, "For international student, fees indicated exclude the 6% Sales and Service Tax (SST) imposed by the Malaysian Government.",
          "Full Time Duration 3 years Intake Date 25 March 2027 06 July 2027",
          "STPM 2 Passes in STPM in Science stream with minimum Grade C (GPA 2.0) in Mathematics and one Science or ICT Subject.",
          "*Overseas qualification that are equivalent to 12th Grade/A Level/HSC are accepted.",
          "STPM (A-Levels equivalent)", "English Requirements International Students IELTS : 5.0 TOEFL IBT : 40 Pearson (PTE) : 47"]
P = [("52906b975c85", "Computer Science", "Bachelor of Science (Honours) in Computer Science", "Computer Science"),
     ("2cdae3fceac3", "Software Engineering", "in Software Engineering", "Computer Science"),
     ("90e94590d8fe", "Computer Science (Artificial Intelligence)", "(Artificial Intelligence)", "Computer Science")]
spec("my-apu", ORG, ["APU", "Asia Pacific University"], "private", "https://www.apu.edu.my", ("my", "Malaysia", "MYR"), ("my-kuala-lumpur", "Kuala Lumpur"),
     {"main": src(P[0][0], "BSc (Hons) in Computer Science | APU", ORG, ["The Asia Pacific University of Technology & Innovation (APU) is conveniently loca",
                                                                       "Bukit Jalil, 57000 Kuala Lumpur"])},
     [("international", "International students", "APU's international fee schedule on each course page (6% SST extra).", "main")])
ENG = {"test_name": "IELTS / TOEFL iBT / PTE", "min_score": "IELTS 5.0, TOEFL iBT 40 or PTE 47.", "source": "course"}
TH_A = ("{n}: APU lists STPM (which it calls A-Levels equivalent): two passes at grade C (GPA 2.0) or better, in Mathematics and one Science or ICT subject; "
        "overseas qualifications equivalent to 12th Grade / A Level / HSC are accepted.")
TH_O = "{n}: overseas qualifications equivalent to 12th Grade / A Level / HSC are accepted; no grade cut-off is published for them."
for page, name, name_q, field in P:
    prog("my-apu", f"bsc-{slugify(name)}", {"course": src(page, f"BSc (Hons) {name} | APU", ORG, COMMON + [name_q])},
         {"name": name, "degree_type": "BSc (Hons)", "field": field, "faculty": "", "duration_years": 3, "duration_source": "course", "languages": ["en"],
          "entry_year": "2027 intakes", "platform": "APU online application", "source": "course",
          "summary": f"BSc (Hons) {name}, APU, Kuala Lumpur; 3 years.", "application_requirements": []},
         [{"residency": "international", "currency": "MYR", "tuition_formula": "(1*34900+1*36100+1*37500)/3", "academic_year": "2027 intakes (course page)",
           "source": "course",
           "note": "International: RM34,900 (Year 1), RM36,100 (Year 2), RM37,500 (Year 3), RM108,500 in total; yearly average our calculation. "
                   "Fees exclude the 6% Sales and Service Tax (SST)."}],
         adm_all({"a-level": TH_A.format(n=name), "ib": TH_O.format(n=name), "us-hs": TH_O.format(n=name), "cbse": TH_O.format(n=name),
                  "international-other": TH_O.format(n=name)}, "course", english=ENG))
    print("wrote", name)

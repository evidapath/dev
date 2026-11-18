import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write
SUB="ca-majors"; U="ca-university-of-toronto"
FU="https://tuitionexplorer.registrar.utoronto.ca/index.php?academicYear=2026-27&sessionType=1&studyLevel=UG&residency=INT&campus=UTSG&faculty=ARTSC-UG"
ENG={"from_existing":"admissionsRequirement-ca-university-of-toronto-admreq-ba-economics-ib"}
UKG="Five different IGCSE/GCSE/Ordinary Level academic subjects and three different A Level/International A Level academic subjects."
USG="High School Diploma from an accredited high school. We expect competitive applicants to be enrolled in a rigorous academic course load, and to have taken the highest level of course available to them in prerequisite subjects."
IBG="Complete Diploma, including English."
def ut(slug,name,code,key,ib_rows,uk_rows,us_rows,ib_th,uk_th,us_th,ib_subj,uk_subj):
    url=f"https://future.utoronto.ca/program/{name.lower()}"
    t=f"{name} | Future Students, University of Toronto"
    srcs={"course":{"url":url,"page":f"ut-{key}-ib","title":t,"organization":"University of Toronto",
                    "quotes":["St. George campus Faculty of Arts & Science",f"{name} Work-integrated learning option available. HBSc Major, Minor, Specialist {code}" if name=="Psychology" else f"{name} HBSc Major, Minor, Specialist {code}",IBG,*ib_rows]},
          "uk":{"url":url,"page":f"ut-{key}-uk","title":t+" (British-patterned requirements)","organization":"University of Toronto","quotes":[UKG,*uk_rows]},
          "us":{"url":url,"page":f"ut-{key}-us","title":t+" (U.S.-patterned requirements)","organization":"University of Toronto","quotes":[USG,*us_rows]},
          "fees":{"url":FU,"page":"ut-fee-207","title":"Tuition Explorer 2026/27, Arts & Science, international | University of Toronto","organization":"University of Toronto",
                  "quotes":["Admission Streams Year 1: Commerce, Computer Science, Humanities, Life Sciences, Mathematical and Physical Sciences, and Social Sciences","Students with fewer than 4.0 credits completed $66,110.00 $2,100.29 $948.00 $69,158.29"]},
          "fees2":{"url":FU,"page":"ut-fee-199","title":"Tuition Explorer 2026/27, Arts & Science, international | University of Toronto","organization":"University of Toronto",
                  "quotes":["2026/27 Fall and Winter","(Honours) Bachelor of Science - Year 2 or Higher","Students with 4.0 or more credits completed $66,110.00 $2,100.29 $948.00 $69,158.29"]}}
    a=lambda cur,src,th,subj:{"curriculum":cur,"source":src,"threshold":f"{name} (St. George, Arts & Science, OUAC {code}): {th} Admission is competitive.","required_subjects":subj,"tests":[],"english":ENG}
    write(SUB,{"uni":U,"slug":slug,"sources":srcs,
      "program":{"name":name,"degree_type":"HBSc","field":"Biology" if name=="Biology" else name,"faculty":"Faculty of Arts & Science","duration_years":4,"languages":["en"],"entry_year":"2026-2027 (Fall 2027 entry)","platform":"OUAC","source":"course",
                 "summary":f"{name}, Honours Bachelor of Science (HBSc; major, minor or specialist), Faculty of Arts & Science, St. George campus. Apply through OUAC (code {code}).","application_requirements":[]},
      "college":{"from":"program-ca-university-of-toronto-ba-economics","quote":"St. George campus Faculty of Arts & Science","copy":[]},
      "costs":[{"residency":"international","currency":"CAD","tuition_annual":66110,"academic_year":"2026/27 (Arts & Science international program fee; Year 1 and Year 2 or higher)","source":["fees","fees2"],
                "fees_from":"costProfile-ca-university-of-toronto-cost-ba-economics-international","living_from":"costProfile-ca-university-of-toronto-cost-ba-economics-international",
                "note":"International program fee 2026/27: CAD 66,110 for Year 1 (all Arts & Science admission streams, including Life Sciences) and CAD 66,110 for the Honours BSc from Year 2. Incidental and system access fee CAD 2,100.29 and UHIP CAD 948 are extra."}],
      "admissions":[a("ib","course",ib_th,ib_subj),a("a-level","uk",uk_th,uk_subj),a("us-hs","us",us_th,["English"])]})
ut("hbsc-psychology","Psychology","TLG","psy",
   ["English English (HL / SL)","Biology Biology (HL / SL)","Math (Calculus) Mathematics: Applications and Interpretations HL / Analysis and Approaches SL / Analysis and Approaches HL","Chemistry RECOMMENDED Chemistry (HL / SL)","Physics RECOMMENDED Physics (HL / SL)"],
   ["English IGCSE / GCSE / O-level / AS / A Level English","Biology Biology AS / A-Level","Math (Calculus) Math AS / A-Level","Chemistry RECOMMENDED Chemistry AS / A-Level","Physics RECOMMENDED Physics AS / A-Level"],
   ["English Senior Year/Grade 12 level or AP/IB English","Biology Senior Year/Grade 12 level or AP/IB Biology","Math (Calculus) Senior Year/Grade 12 level or AP/IB Calculus","Chemistry RECOMMENDED Senior Year/Grade 12 level or AP/IB Chemistry"],
   "complete IB Diploma including English, with Biology (HL/SL) and Maths for calculus (AI HL, or AA SL/HL); Chemistry and Physics recommended.",
   "five different IGCSE/GCSE/O-Level subjects and three different A-Levels, including English (IGCSE or higher), Biology (AS/A-Level) and Maths (AS/A-Level); Chemistry and Physics recommended.",
   "a high school diploma from an accredited school, with senior-level (or AP/IB) English, Biology and Calculus; Chemistry and Physics recommended.",
   ["English","Biology","Mathematics"],["English","Biology","Mathematics"])
ut("hbsc-biology","Biology","TLG","bio",
   ["English English (HL / SL)","Biology Biology (HL / SL)","Math (Calculus) Mathematics: Applications and Interpretations HL / Analysis and Approaches SL / Analysis and Approaches HL","Chemistry Chemistry (HL / SL)"],
   ["English IGCSE / GCSE / O-level / AS / A Level English","Biology Biology AS / A-Level","Math (Calculus) Math AS / A-Level","Chemistry Chemistry AS / A-Level"],
   ["English Senior Year/Grade 12 level or AP/IB English","Biology Senior Year/Grade 12 level or AP/IB Biology","Math (Calculus) Senior Year/Grade 12 level or AP/IB Calculus","Chemistry Senior Year/Grade 12 level or AP/IB Chemistry"],
   "complete IB Diploma including English, with Biology, Chemistry (HL/SL) and Maths for calculus (AI HL, or AA SL/HL).",
   "five different IGCSE/GCSE/O-Level subjects and three different A-Levels, including English (IGCSE or higher), Biology, Chemistry and Maths (AS/A-Level).",
   "a high school diploma from an accredited school, with senior-level (or AP/IB) English, Biology, Calculus and Chemistry.",
   ["English","Biology","Chemistry","Mathematics"],["English","Biology","Chemistry","Mathematics"])
print("ok")

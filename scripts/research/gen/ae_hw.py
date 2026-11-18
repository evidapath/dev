import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write
SUB="ae-majors"; U="ae-heriot-watt-dubai"
ENG={"from_existing":"admissionsRequirement-ae-heriot-watt-dubai-admreq-bsc-cs-ib"}
STD=["Duration 3-4 years","Show all Year 1","We have standard entry requirements for all of our courses that you will have to meet.","Our entry criteria are listed below. However, please note that the final decision remains at the discretion of the course director after evaluating scores of individual relevant subjects.","All tuition fees inclusive of VAT."]
def hw(slug,url,page,title,name,deg,field,fee,rows,ths,subj,summary):
    adm=lambda cur,th:{"curriculum":cur,"source":"course","threshold":f"{title.split(' |')[0]}, Year 1 entry: {th} The final decision is at the course director's discretion.","required_subjects":subj,"tests":[],"english":ENG}
    write(SUB,{"uni":U,"slug":slug,
     "sources":{"course":{"url":url,"page":page,"title":title+" Dubai","organization":"Heriot-Watt University Dubai","quotes":[title.split(' |')[0],*STD,f"Status Full Time UAE and International AED {fee:,}",*rows]}},
     "program":{"name":name,"degree_type":deg,"field":field,"faculty":"","duration_years":4,"languages":["en"],"entry_year":"2027 intakes","platform":"Direct application (Heriot-Watt Dubai)","source":"course","summary":summary,"application_requirements":[]},
     "costs":[{"residency":"all-students","currency":"AED","tuition_annual":fee,"academic_year":"Fee shown on the course page in November 2026 (intake not stated)","source":"course","living_from":"costProfile-ae-heriot-watt-dubai-cost-bsc-cs-all-students",
               "note":f"AED {fee:,} a year, full time, UAE and international students, inclusive of VAT (course page; the page doesn't say which intake)."}],
     "admissions":[adm("a-level",ths[0]),adm("ib",ths[1]),adm("us-hs",ths[2]),adm("cbse",ths[3])]})
B="https://www.hw.ac.uk/dubai/study/undergraduate/"
ENGR=["GCE A-Level - CCC (or AABB at AS-Level), including mandatory subjects Math and Physics","CBSE/Other Indian Boards - 65%, including mandatory subjects Math and Physics",
      "American High School Diploma/SABIS - 70%, including mandatory subjects Math and Physics + SAT I – 1000 (500 English and 500 Math)",
      "International Baccalaureate Diploma Programme - 24 points (3 HL, including mandatory subjects Math and Physics and 3 SL)"]
ENGT=["GCE A-Level CCC (or AABB at AS-Level), including Maths and Physics.","IB Diploma, 24 points (3 HL including Maths and Physics, and 3 SL).",
      "American High School Diploma/SABIS 70% including Maths and Physics, plus SAT I 1000 (500 English and 500 Math).","CBSE/Other Indian Boards 65%, including Maths and Physics."]
hw("beng-civil-engineering",B+"civil-engineering","3015754099b3","BEng (Hons) Civil Engineering | Heriot-Watt University","Civil Engineering","BEng (Hons)","Engineering",82264,ENGR,ENGT,["Mathematics","Physics"],
   "BEng (Hons) Civil Engineering, Heriot-Watt University Dubai; 3-4 years (4 years from Year 1 entry, the entry route shown here).")
hw("beng-mechanical-engineering",B+"mechanical-engineering","831d011009df","BEng (Hons) Mechanical Engineering | Heriot-Watt University","Mechanical Engineering","BEng (Hons)","Engineering",82264,ENGR,ENGT,["Mathematics","Physics"],
   "BEng (Hons) Mechanical Engineering, Heriot-Watt University Dubai; 3-4 years (4 years from Year 1 entry, the entry route shown here).")
hw("ba-architecture",B+"architecture","577990533841","BA (Hons) Architecture | Heriot-Watt University","Architecture","BA (Hons)","Architecture",88920,
   ["GCE A-Level - CCC (or AABB at AS-Level)","CBSE/Other Indian Boards - 65%","American High School Diploma/SABIS - 70% + SAT I - 1000 (500 English and 500 Math)","International Baccalaureate Diploma Programme - 24 points (3 HL and 3 SL)."],
   ["GCE A-Level CCC (or AABB at AS-Level).","IB Diploma, 24 points (3 HL and 3 SL).","American High School Diploma/SABIS 70% plus SAT I 1000 (500 English and 500 Math).","CBSE/Other Indian Boards 65%."],[],
   "BA (Hons) Architecture, Heriot-Watt University Dubai; 3-4 years (4 years from Year 1 entry, the entry route shown here).")
print("ok")

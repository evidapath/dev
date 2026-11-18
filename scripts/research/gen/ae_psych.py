import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write
SUB="ae-majors"
# University of Birmingham Dubai, Psychology BSc
U="ae-birmingham-dubai"
adm=lambda cur,th,subj:{"curriculum":cur,"source":"course","threshold":f"Psychology BSc: {th}","required_subjects":subj,"tests":[]}
write(SUB,{"uni":U,"slug":"bsc-psychology",
 "sources":{"course":{"url":"https://www.birmingham.ac.uk/dubai/study/undergraduate/subjects/psychology-courses/psychology-bsc","page":"bf7bb1cfe56a","title":"Psychology BSc | University of Birmingham Dubai","organization":"University of Birmingham Dubai",
   "quotes":["Duration 3 years (full-time)","September 2027: AED 162,203 per year","This programme is accredited by the United Arab Emirates Ministry of Higher Education and Scientific Research.",
             "A Level AAA - ABB A Minimum of 5/B in GCSE Math’s or equivalent is also required.","IB 6,6,6 - 6,5,5 from 3 HL subjects is required.","85 - 75% CBSE","Number of A levels required: 3",
             "To study at the University, you must be able to demonstrate a good level of written and spoken English."]}},
 "program":{"name":"Psychology","degree_type":"BSc","field":"Psychology","faculty":"","duration_years":3,"languages":["en"],"entry_year":"September 2027 entry","platform":"Direct application (Birmingham Dubai admissions portal)","source":"course",
   "summary":"Psychology BSc, 3 years full-time, University of Birmingham Dubai; accredited by the UAE Ministry of Higher Education and Scientific Research.","application_requirements":[]},
 "costs":[{"residency":"all-students","currency":"AED","tuition_annual":162203,"academic_year":"September 2027 entry","source":"course","living_from":"costProfile-ae-birmingham-dubai-cost-bsc-cs-all-students",
           "note":"Psychology BSc fee: AED 162,203 per year for September 2027 entry (full-time)."}],
 "admissions":[adm("a-level","AAA - ABB from three A-Levels, with at least 5/B in GCSE Maths or equivalent.",[]),
               adm("ib","6,6,6 - 6,5,5 from three Higher Level subjects.",[]),
               adm("cbse","85 - 75% (CBSE).",[])]})
# Heriot-Watt University Dubai, BSc (Hons) Psychology
U="ae-heriot-watt-dubai"
ENG={"from_existing":"admissionsRequirement-ae-heriot-watt-dubai-admreq-bsc-cs-ib"}
adm=lambda cur,th:{"curriculum":cur,"source":"course","threshold":f"BSc (Hons) Psychology, Year 1 entry: {th} The final decision is at the course director's discretion.","required_subjects":[],"tests":[],"english":ENG}
write(SUB,{"uni":U,"slug":"bsc-psychology",
 "sources":{"course":{"url":"https://www.hw.ac.uk/dubai/study/undergraduate/psychology","page":"881389623751","title":"BSc (Hons) Psychology | Heriot-Watt University Dubai","organization":"Heriot-Watt University Dubai",
   "quotes":["BSc (Hons) Psychology","Duration 3-4 years","This programme is available for the January intake with Year 1 entry only.","September 2027 / January 2028 intake tuition fees Status Full Time UAE and International AED 87,010","All tuition fees inclusive of VAT.",
             "We have standard entry requirements for all of our courses that you will have to meet.",
             "Our normal entry criteria are listed below. However, please note that the final decision remains at the discretion of the course director after evaluating scores of individual relevant subjects.",
             "GCE A-Level - CCD (or BBBB at AS Level)","CBSE/Other Indian Boards – 70%","American High School Diploma/SABIS - 70% + SAT I – 1000 (500 English + 500 Math)",
             "International Baccalaureate Diploma Programme - 24 points (3 HL and 3 SL)"]}},
 "program":{"name":"Psychology","degree_type":"BSc (Hons)","field":"Psychology","faculty":"","duration_years":4,"languages":["en"],"entry_year":"September 2027 / January 2028 intake","platform":"Direct application (Heriot-Watt Dubai)","source":"course",
   "summary":"BSc (Hons) Psychology, Heriot-Watt University Dubai; 3-4 years (4 years from Year 1 entry, the entry route shown here).","application_requirements":[]},
 "costs":[{"residency":"all-students","currency":"AED","tuition_annual":87010,"academic_year":"September 2027 / January 2028 intake","source":"course","living_from":"costProfile-ae-heriot-watt-dubai-cost-bsc-cs-all-students",
           "note":"BSc (Hons) Psychology: AED 87,010 a year, UAE and international students, full time, September 2027 / January 2028 intake; inclusive of VAT."}],
 "admissions":[adm("a-level","GCE A-Level CCD (or BBBB at AS Level)."),adm("ib","IB Diploma, 24 points (3 HL and 3 SL)."),
               adm("us-hs","American High School Diploma/SABIS 70% plus SAT I 1000 (500 English + 500 Math)."),adm("cbse","CBSE/Other Indian Boards 70%.")]})
print("ok")

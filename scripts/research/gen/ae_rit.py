import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write
SUB="ae-majors"; U="ae-rit-dubai"
FEEQ="Bachelor of Science in Global Business Management Bachelor of Science in Psychology Bachelor of Science in Advertising and Public Relations Bachelor of Fine Arts in New Media Design 68,000"
ENG={"test_name":"Academic IELTS (or TOEFL / EmSAT English)","source":"eng",
     "min_score":"Full admission: Academic IELTS overall 6.5 and above, TOEFL iBT 79 and above, TOEFL ITP 550 and above, or EmSAT English 1550 and above. Conditional admission: IELTS 5.0 - 6.0, TOEFL iBT 61 - 78, TOEFL ITP 500 - 547, EmSAT 1100 - 1525.",
     "notes":"Students in English-medium international curricula may qualify for an exemption."}
adm=lambda cur,th:{"curriculum":cur,"source":"adm","threshold":f"BS Psychology: {th} A Math placement test is also considered; meeting the minimum doesn't guarantee direct admission.","required_subjects":[],"tests":[],"english":ENG}
write(SUB,{"uni":U,"slug":"bs-psychology",
 "sources":{
  "course":{"url":"https://www.rit.edu/dubai/bachelor-science-psychology","page":"2f557b1bf2ef","title":"Bachelor of Science in Psychology | RIT Dubai","organization":"RIT Dubai","quotes":["Total Credit Hours - 124","Fourth Year"]},
  "fees":{"url":"https://www.rit.edu/dubai/tuition-and-fees","page":"3be86f64f014","title":"Tuition and Fees | RIT Dubai","organization":"RIT Dubai","quotes":["Bachelor Tuition (per year)",FEEQ]},
  "adm":{"url":"https://www.rit.edu/dubai/sites/rit.edu.dubai/files/docs/Admissions%20Related/Admission%20Requirements%20Psychology.pdf","page":"rit-psy-adm","title":"Admission Requirements, Psychology (PDF) | RIT Dubai","organization":"RIT Dubai",
         "quotes":["The admission requirements for Psychology, based on the curriculum, are listed below.","Psychology students must appear for Math placement test prior to course registration.",
                   "Note: achieving the minimum requirements doesn’t guarantee direct admission to the program.",
                   "British Required Scores Minimum 5 IGCSE (C or above) and 2 As or 1 A level (D grade) Completion of Grade 12/ Year 13 Minimum average 70%",
                   "International Baccalaureate Required Scores Minimum 24 points",
                   "American/SABIS/ Canadian (*SAT is not required for Canadian curriculum) Required Scores Minimum 70% *SAT 1 Math of 450 (MOE Equivalency Requirement)",
                   "Pakistan/India Required Scores Minimum score 60%","United Arab Emirates Required Scores Elite 70% Advanced 70% General 75%"]},
  "eng":{"url":"https://www.rit.edu/dubai/undergraduate-admissions","page":"fc3cdd20e9da","title":"Undergraduate Admissions | RIT Dubai","organization":"RIT Dubai",
         "quotes":["Academic IELTS Overall 6.5 and above Overall 5.0 - 6.0 TOEFL ITP 550 and above 500 - 547 TOEFL IBT 79 and above 61 - 78 EmSAT - English 1550 and above 1100 - 1525",
                   "International Curricula (American, British, IB, Australian, Canadian and SABIS): Students enrolled in international curricula where English is the primary language of instruction may qualify for an exemption from the English Proficiency test"]}},
 "program":{"name":"Psychology","degree_type":"BS","field":"Psychology","faculty":"","duration_years":4,"languages":["en"],"entry_year":"2026-2027 (Fall 2027 entry)","platform":"RIT Dubai application","source":"course",
   "summary":"Bachelor of Science in Psychology, RIT Dubai; 124 total credit hours over a four-year course sequence.","application_requirements":[]},
 "college":{"from":"program-ae-rit-dubai-bs-global-business","quote":FEEQ,"copy":["costs"]},
 "costs":[],
 "admissions":[adm("a-level","British system: at least 5 IGCSEs (C or above) and 2 AS-Levels or 1 A-Level (D grade), Year 13 completed, minimum average 70%."),
               adm("ib","IB, minimum 24 points."),
               adm("us-hs","American/SABIS/Canadian: minimum 70%, plus SAT Math 450 (not needed for the Canadian curriculum)."),
               adm("cbse","Pakistan/India: minimum score 60%."),
               adm("uae-shs","UAE curriculum: Elite 70%, Advanced 70%, General 75%.")]})
print("ok")

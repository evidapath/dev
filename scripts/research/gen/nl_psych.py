import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write
SUB="nl-majors"
# --- University of Amsterdam, BSc Psychology (English track)
ENG_UVA={"test_name":"IELTS Academic (or accepted equivalent)","source":"app",
  "min_score":"CEFR C1. IELTS Academic 6.5 (each subscore 6); TOEFL iBT 92 (each subscore 22) on the scale used until 20 January 2026; Cambridge C1 Advanced 175; Cambridge C2 Proficiency 180.",
  "notes":"Exempt after fully English-taught secondary education in Australia, Canada (except Quebec), Ireland, New Zealand, the UK or the US, or with an IB Diploma with English as an exam subject."}
APPQ=["You can submit your enrolment application for the academic year 2027-2028 in Studielink from 1 October 2026 till 15 January 2027.",
  "We will have 270 places available for the English track in the academic year 2027-2028.",
  "Students with a foreign diploma are eligible to apply if their diploma is equivalent to the Dutch pre-university diploma (vwo-diploma) and includes: Mathematics English as part of your final examinations.",
  "The level of mathematics should be equivalent to at least the Dutch level of VWO mathematics: Wiskunde A.",
  "Applicants are therefore required to submit proof of sufficient proficiency in English (Common European Framework of Reference for Languages (CEFR): level C1).",
  "By completing fully English-taught secondary education in Australia, Canada (with the exception of Quebec), Ireland, New Zealand, the United Kingdom or the United States of America;",
  "By obtaining an International Baccalaureate DP diploma with English as an IB exam subject",
  "IELTS Academic 6.5 Each subscore: 6 TOEFL (iBT) Scoring scale: 0-120* 92 Each subscore: 22",
  "Cambridge C1 Advanced 175 Cambridge C2 Proficiency 180","*Scoring scale until 20 January 2026",
  "To be eligible for admission to the programme, you must participate in the selection process."]
th="a diploma equivalent to the Dutch pre-university (vwo) diploma, with Mathematics (at least VWO Wiskunde A level) and English among the final examinations. Numerus fixus: 270 places on the English track for 2027-2028, filled by a selection procedure."
adm=lambda cur:{"curriculum":cur,"source":"app","threshold":f"Psychology (English track): {th}","required_subjects":["Mathematics"],"tests":[],"english":ENG_UVA}
write(SUB,{"uni":"nl-uva","slug":"bsc-psychology",
 "sources":{
  "course":{"url":"https://www.uva.nl/en/programmes/bachelors/psychology/psychology.html","page":"923ff7557367","title":"Bachelor's Psychology - University of Amsterdam","organization":"University of Amsterdam",
            "quotes":["Language of instruction English","180 EC EC, 36 months","This Bachelor's programme has a numerus fixus. This means that you need to apply for the selection procedure by 15 January at the latest. The programme has 270 places available for the English track."]},
  "app":{"url":"https://www.uva.nl/en/bachelors/bachelorsprogrammes/psychology/application-and-admission/application-and-admission","page":"uva-psy-app","title":"Application process - Psychology - University of Amsterdam","organization":"University of Amsterdam","quotes":APPQ},
  "fees":{"url":"https://www.uva.nl/en/education/fees-and-funding/tuition-fees/tuition-fees.html","page":"uva-fee-fmg","title":"Tuition fees - University of Amsterdam","organization":"University of Amsterdam",
          "quotes":["2027-2028 institutional fee per faculty","Faculty of Social and Behavioural Sciences","Institutional fee for non-EEA students Bachelor's €16,670"]},
  "fmg":{"url":"https://www.uva.nl/en/organisation/faculty-of-social-and-behavioural-sciences/education","page":"af35bd0428c5","title":"Education - Faculty of Social and Behavioural Sciences - University of Amsterdam","organization":"University of Amsterdam",
         "quotes":["Our Bachelor's programmes are divided into four clusters: Bachelor's in Child Development and Education Bachelor's in Communication Science Bachelor's in Psychology"]},
  "statutory":{"url":"https://www.utwente.nl/en/education/bachelor/study-costs/tuition-fees/","page":"ef12a0412ae7","title":"Tuition fees bachelor's | University of Twente","organization":"University of Twente",
          "quotes":["This fee is set and subsidised by the Dutch government and may change each academic year.","2026-2027 (Sep-Aug) 2027-2028 (Sep-Aug) All bachelor's, except for University College Twente € 2,694 per year € 2,771 per year"]}},
 "program":{"name":"Psychology","degree_type":"BSc","field":"Psychology","faculty":"","duration_years":3,"languages":["en"],"entry_year":"2027-2028","platform":"Studielink","source":"course",
   "summary":"BSc Psychology (English track), 180 EC over 36 months. Numerus fixus with a selection procedure; apply in Studielink by 15 January.","application_requirements":[]},
 "costs":[{"residency":"international","currency":"EUR","tuition_annual":16670,"academic_year":"2027-2028 (non-EEA, Social and Behavioural Sciences bachelor)","source":["fees","fmg"],"living_from":"costProfile-nl-uva-cost-bsc-economics-international",
           "note":"Institutional fee for non-EEA students, 2027-2028: €16,670 a year for a Bachelor's in the Faculty of Social and Behavioural Sciences, which lists the Bachelor's in Psychology among its programmes."},
          {"residency":"eu-eea","currency":"EUR","tuition_annual":2771,"academic_year":"2027-2028 (EU/EEA statutory fee)","source":"statutory","living_from":"costProfile-nl-uva-cost-bsc-economics-eu-eea",
           "note":"Statutory fee 2027-2028: €2,771 a year, set by the Dutch government for every Dutch university (figure as published by the University of Twente). UvA's own fee page still shows €2,694 under 2027-2028."}],
 "admissions":[adm("a-level"),adm("ib"),adm("international-other")],
 "deadline":{"date":"2027-01-15","source":"app","round":"Numerus fixus application (Studielink)","note":"Apply in Studielink between 1 October 2026 and 15 January 2027; selection follows."}})
# --- University of Twente, BSc Psychology (English track)
ENG_UT={"test_name":"IELTS Academic (or accepted equivalent)","source":"lang",
  "min_score":"IELTS Academic 6.0 overall, at least 5.5 in each section; TOEFL iBT 90 (at least 21 per section, scale before January 2026) or 4.5 (new scale); Cambridge C1 Advanced or C2 Proficiency 169 (162 per section).",
  "notes":"An IB Diploma taught in English with an English exam subject exempts you from a test."}
UTQ=["Do you want to start the English track of Psychology? Make sure you apply via Studielink by 15 January 2027 , because applications after this date will not be accepted.",
     "This track has a numerus fixus , which means there are 250 places available and you will need to take part in a selection proce"]
def utadm(cur,th,subj): return {"curriculum":cur,"source":cur if cur!="international-other" else "req","threshold":f"Psychology (English track): {th} The English track has an intake restriction, so a selection procedure is part of admission.","required_subjects":subj,"tests":[],"english":ENG_UT}
write(SUB,{"uni":"nl-ut","slug":"bsc-psychology",
 "sources":{
  "course":{"url":"https://www.utwente.nl/en/education/bachelor/programmes/psychology/","page":"03fd311e253c","title":"Bachelor Psychology | University of Twente","organization":"University of Twente",
            "quotes":["Duration 3 years","Numerus fixus English track: 250 spots","Faculty Behavioural, Management & Social Sciences","You can choose either a (fully) English or Dutch track within the programme. Good to know: only the English-taught track has a numerus fixus."]},
  "apply":{"url":"https://www.utwente.nl/en/education/bachelor/programmes/psychology/enrolment/","page":"9c225c67cca4","title":"Application Psychology | University of Twente","organization":"University of Twente","quotes":UTQ},
  "req":{"url":"https://www.utwente.nl/en/education/bachelor/programmes/psychology/enrolment/admission-requirements/","page":"f30da47355ee","title":"Admission requirements Psychology | University of Twente","organization":"University of Twente",
         "quotes":["Please take into account that Psychology has an intake restriction for the English track and as a result participating in a selection procedure is needed.",
                   "You are admissible if you have an international secondary school diploma equivalent to the Dutch VWO (pre-university education) diploma ."]},
  "a-level":{"url":"https://www.utwente.nl/en/education/bachelor/application-admission/admission/diplomas/uk/","page":"d5b0a2e1f4f1","title":"GCSE & GCE A2-Levels | University of Twente","organization":"University of Twente",
         "quotes":["3 (I)GCSE / GCE O-Level with an A, B or C grade or 4 – 9 score, and 3 full GCE A2-Level with an A, B or C grade.","Students need to have six different subjects in (I)GCSE / GCE O-Level and A2-Level.","Psychology GCE A2-Level Mathematics English","These admission requirements are valid for the September 2027 intake."]},
  "ib":{"url":"https://www.utwente.nl/en/education/bachelor/admission/diplomas/international-baccalaureate/","page":"997b7f12aea9","title":"International Baccalaureate | University of Twente","organization":"University of Twente",
         "quotes":["Psychology Mathematics Applications and Interpretations -or- Mathematics Analysis and Approaches (on either Standard Level or Higher Level)"]},
  "lang":{"url":"https://www.utwente.nl/en/education/bachelor/application-admission/admission/language-requirements/","page":"979afa0dca25","title":"Language requirements | University of Twente","organization":"University of Twente",
         "quotes":["not older than two years, with an overall band score of at least 6.0, and a minimum score on each section of at least 5.5.",
                   "not older than two years, with an overall score of 90, and a minimum score on each section of at least 21.",
                   "not older than two years, with an overall score of 4.5, and a minimum score of 4.5 on reading, listening and writing.",
                   "obtained with an overall score of at least 169 and a minimum score on each section of at least 162.",
                   "TOEFL iBT (internet-based) certificate (before January 2026)",
                   "Cambridge C1 Advanced , formerly known as; Cambridge English Advanced (CAE).","Cambridge C2 Proficiency , formerly known as; Cambridge English Proficiency (CPE)."]},
  "fees":{"url":"https://www.utwente.nl/en/education/bachelor/programmes/psychology/enrolment/tuition-fees-interational/","page":"f2cd5beede0c","title":"Tuition fees Psychology | University of Twente","organization":"University of Twente",
         "quotes":["The Bachelor's in Psychology is an Alpha-Gamma programme.","2027-2028 (Sep-Aug) € 2,771 per year","Overview of institutional tuition fees for this Bachelor's 2026-2027 (Sep-Aug) € 12,300 per year 2027-2028 (Sep-Aug) € 12,652 per year"]}},
 "program":{"name":"Psychology","degree_type":"BSc","field":"Psychology","faculty":"Behavioural, Management & Social Sciences","duration_years":3,"languages":["en"],"entry_year":"2027-2028","platform":"Studielink","source":"course",
   "summary":"BSc Psychology, 3 years; English track with a numerus fixus of 250 places and a selection procedure (a Dutch track is also offered).","application_requirements":[]},
 "costs":[{"residency":"international","currency":"EUR","tuition_annual":12652,"academic_year":"2027-2028 (non-EU/EEA institutional fee)","source":"fees","living_from":"costProfile-nl-ut-cost-bsc-iba-international",
           "note":"Institutional fee for non-EU/EEA students, 2027-2028: €12,652 a year (Psychology is an Alpha-Gamma programme)."},
          {"residency":"eu-eea","currency":"EUR","tuition_annual":2771,"academic_year":"2027-2028 (EU/EEA statutory fee)","source":"fees","living_from":"costProfile-nl-ut-cost-bsc-iba-eu-eea",
           "note":"Statutory fee 2027-2028: €2,771 a year."}],
 "admissions":[utadm("a-level","3 (I)GCSEs (A-C or 4-9) and 3 full A-Levels (A-C), six different subjects, including A-Level Mathematics, plus English.",["Mathematics"]),
               utadm("ib","IB Diploma with Mathematics Applications and Interpretations or Analysis and Approaches (SL or HL).",["Mathematics"]),
               utadm("international-other","a secondary school diploma equivalent to the Dutch VWO diploma, plus Twente's English and mathematics requirements.",[])],
 "deadline":{"date":"2027-01-15","source":"apply","round":"Numerus fixus application (English track, Studielink)","note":"Applications after 15 January 2027 are not accepted; selection in February-March 2027."}})
print("ok")

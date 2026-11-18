import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write
SUB="ae-majors"; U="ae-canadian-university-dubai"
ADM={"url":"https://www.cud.ac.ae/prospective-students/undergraduate","page":"d709d1d380f5","title":"Undergraduate Admissions | Canadian University Dubai","organization":"Canadian University Dubai",
     "quotes":["Are holders of UAE secondary education certificate with passing grade in all subjects","British System: Completion of Year 13 / Grade 12 of schooling","Equivalency Certificate is Issued by Ministry of Education in the UAE.",
               "Provide a valid English Language Proficiency Certificate with a minimum score of IELTS Academic (Band 5.0), TOEFL iBT (61), TOEFL ITP (500)",
               "Applicants seeking admission to the Engineering program must meet the following subject-specific requirements:"]}
FEES={"url":"https://www.cud.ac.ae/fees","page":"5875657056d8","title":"Fees | Canadian University Dubai","organization":"Canadian University Dubai"}
ENG={"test_name":"IELTS Academic (or TOEFL)","source":"adm","min_score":"IELTS Academic 5.0, TOEFL iBT 61 or TOEFL ITP 500.","notes":"Not needed with official proof that your school taught in English, or 80% in English on the UAE Advanced Track."}
TH={"a-level":"British system: completion of Year 13 / Grade 12, with a UAE Ministry of Education equivalency certificate.",
    "ib":"IB: assessed under UAE Ministry of Education equivalency rules.",
    "us-hs":"American system: high school diploma with a UAE Ministry of Education equivalency certificate.",
    "uae-shs":"UAE secondary education certificate with a passing grade in all subjects."}
def cud(slug,url,page,name,deg,credits,feeq,cost,summary,extra=()):
    adm=lambda cur:{"curriculum":cur,"source":"adm","threshold":f"{name}: {TH[cur]} CUD lists subject-specific requirements only for Engineering.","required_subjects":[],"tests":[],"english":ENG}
    write(SUB,{"uni":U,"slug":slug,
     "sources":{"course":{"url":url,"page":page,"title":f"{name} | Canadian University Dubai","organization":"Canadian University Dubai","quotes":[f"{name} Degree Program","4 Years (8 Semesters)",f"{credits} Credit Hours",*extra]},
                "adm":ADM,"fees":{**FEES,"quotes":["*Estimated first-year costs based on full-time studies, including the application fee.","Cr Hrs per Year","VAT 5%",feeq]}},
     "program":{"name":"Psychology","degree_type":deg,"field":"Psychology","faculty":"","duration_years":4,"languages":["en"],"entry_year":"2026-2027 (Fall 2027 entry)","platform":"CUD online application","source":"course","summary":summary,"application_requirements":[]},
     "costs":[{**cost,"residency":"all-students","currency":"AED","mandatory_fees_annual":2236.5,"academic_year":"Rates on CUD's fee page in November 2026 (the page doesn't state the academic year)","source":"fees","living_from":"costProfile-ae-canadian-university-dubai-cost-bsc-cs-all-students"}],
     "admissions":[adm("a-level"),adm("ib"),adm("us-hs"),adm("uae-shs")]})
cud("ba-psychology","https://www.cud.ac.ae/programs/undergraduate/social-sciences/bachelor-of-arts-in-psychology","c885340573d2","Bachelor of Arts in Psychology","BA",123,
    "Bachelor of Arts in Psychology AED 2,140.00 AED 107.00 AED 2,247.00 AED 6,741.00 30 AED 0.00 USD AED 2,236.50",
    {"tuition_per_credit":2247.00,"credits_per_year":30,"note":"AED 2,247.00 per credit hour including 5% VAT (AED 2,140.00 before VAT) × 30 credit hours a year, plus AED 2,236.50 incidental fees."},
    "Bachelor of Arts in Psychology, 4 years (8 semesters), 123 credit hours.")
cud("bsc-psychology","https://www.cud.ac.ae/programs/undergraduate/health-sciences-digital-innovation-and-sustainability/psychology/bachelor-of-science-in-psychology","9983b453ecb9","Bachelor of Science in Psychology","BSc",129,
    "Bachelor of Science in Psychology AED 2,241.65 AED 112.08 AED 2,353.73 AED 7,061.20 30 AED 70,611.98 USD AED 2,236.50 USD AED 72,848.48",
    {"tuition_annual":70611.98,"note":"Tuition per year AED 70,611.98 (AED 2,353.73 per credit hour including 5% VAT × 30 credit hours), plus AED 2,236.50 incidental fees; total AED 72,848.48."},
    "Bachelor of Science in Psychology, 4 years (8 semesters), 129 credit hours.")
print("ok")

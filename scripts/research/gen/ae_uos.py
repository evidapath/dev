import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write
SUB="ae-majors"; U="ae-university-of-sharjah"
FU="https://www.sharjah.ac.ae/-/media/project/uos/sites/uos/admission/tuition-fees/ug--after-w-ch.pdf"
ADMU="https://www.sharjah.ac.ae/Admissions/bachelors-degree"
ENGQ="College of Engineering Programs Minimum average Required school subjects Required test Programs Bachelor of Science in Architectural Engineering Bachelor of Science in Chemical and Water Desalination Engineering Bachelor of Science in Civil Engineering Bachelor of Science in Electrical and Electronics Engineering Bachelor of Science in Industrial Engineering and Engineering Management Bachelor of Science in Mechanical Engineering Bachelor of Science in Mechatronics and Robotics Engineering Bachelor of Science in Nuclear Engineering Bachelor of Science in Sustainable and Renewable Energy Engineering Minimum average Advanced track: 75% General track: 85% Applied/Literary: not accepted Required school subjects At least 80% in Mathematics and Physics and in one science subject (Chemistry or Biology)."
def fees(row): return {"url":FU,"page":"uos-fee","title":"Tuition fees for undergraduates admitted from 2022/2023 (PDF) | University of Sharjah","organization":"University of Sharjah",
                       "quotes":["Tuition Fees for Students who have been admitted from Academic Year 2022/2023",row]}
def cost(name):
    return [{"residency":"all-students","currency":"AED","tuition_annual":63740,"academic_year":"Fee table for students admitted from 2022/2023 (current published table)","source":"fees",
             "living_from":"costProfile-ae-university-of-sharjah-cost-bsc-eng-all-students",
             "note":f"{name}: semester fee AED 31,870, annual fee AED 63,740, AED 2,656 per credit hour."}]
def eng(slug,path,page,name,credits,summary):
    write(SUB,{"uni":U,"slug":slug,
     "sources":{"course":{"url":f"https://www.sharjah.ac.ae/en/academics/degree/undergraduate/{path}","page":page,"title":f"Bachelor of Science in {name} | University of Sharjah","organization":"University of Sharjah",
                          "quotes":[f"Total Credit Hours {credits} Cr. Hrs. Duration 4 Years","Language English"]},
                "req":{"url":ADMU,"page":"d4a0572e3422","title":"Bachelor's degree admission | University of Sharjah","organization":"University of Sharjah","quotes":[ENGQ]},
                "fees":fees(f"Bachelor of Science in {name} 31,870 63,740 2,656")},
     "program":{"name":name,"degree_type":"BSc","field":"Engineering","faculty":"College of Engineering" if False else "","duration_years":4,"languages":["en"],"entry_year":"2026-2027 (Fall 2027 entry)","platform":"University of Sharjah online application","source":"course","summary":summary,"application_requirements":[]},
     "college":{"from":"program-ae-university-of-sharjah-bsc-eng","quote":ENGQ,"subjects_quote":ENGQ,"copy":["admissions"]},
     "costs":cost(f"Bachelor of Science in {name}"),"admissions":[]})
eng("bsc-civil-engineering","civil-engineering","706b615037d6","Civil Engineering",135,"Bachelor of Science in Civil Engineering, 4 years, 135 credit hours, taught in English.")
eng("bsc-electrical-electronics-engineering","electrical-and-electronics-engineering","1585ad40acfd","Electrical and Electronics Engineering",132,"Bachelor of Science in Electrical and Electronics Engineering, 4 years, 132 credit hours, taught in English.")
LAWQ=["Bachelor of Law in English Minimum average 75% in all tracks Required school subjects 70% in Mathematics Required test IELTS Academic: 5.5 TOEFL iBT: 61 TOEFL ITP: 500 PTE Academic: 44",
      "School grades stated on this page are those of the UAE curriculum (Advanced track). Grades from other curricula are converted to their UAE equivalent"]
ENG={"test_name":"IELTS Academic (or TOEFL / PTE)","source":"req","min_score":"IELTS Academic 5.5, TOEFL iBT 61, TOEFL ITP 500 or PTE Academic 44."}
la=lambda cur,th:{"curriculum":cur,"source":"req","threshold":f"Bachelor of Law in English: {th} Meeting the minimum doesn't guarantee a place.","required_subjects":["Mathematics"],"tests":[],"english":ENG}
write(SUB,{"uni":U,"slug":"llb-english",
 "sources":{"course":{"url":"https://www.sharjah.ac.ae/en/academics/degree/undergraduate/law-in-english","page":"96e7b778f515","title":"Bachelor of Law in English | University of Sharjah","organization":"University of Sharjah",
                      "quotes":["Total Credit Hours 125 Cr. Hrs. Duration 4 Years","Language English"]},
            "req":{"url":ADMU,"page":"d4a0572e3422","title":"Bachelor's degree admission | University of Sharjah","organization":"University of Sharjah","quotes":LAWQ},
            "fees":fees("Bachelor of Law in English 31,870 63,740 2,656")},
 "program":{"name":"Law (taught in English)","degree_type":"Bachelor of Law","field":"Law","faculty":"","duration_years":4,"languages":["en"],"entry_year":"2026-2027 (Fall 2027 entry)","platform":"University of Sharjah online application","source":"course",
   "summary":"Bachelor of Law in English, 4 years, 125 credit hours, College of Law.","application_requirements":[]},
 "costs":cost("Bachelor of Law in English"),
 "admissions":[la("uae-shs","UAE secondary certificate, minimum average 75% in all tracks, with at least 70% in Mathematics."),
               *[la(c,f"{n}: an average equivalent to 75% (Sharjah converts other curricula to the UAE scale), with the equivalent of 70% in Mathematics.")
                 for c,n in [("ib","IB Diploma"),("a-level","British curriculum"),("us-hs","American high school diploma"),("international-other","Other curricula")]]]})
print("ok")

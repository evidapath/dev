import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write
SUB="ca-majors"; U="ca-waterloo"
ENG={"from_existing":"admissionsRequirement-ca-waterloo-admreq-ba-economics-ib"}
R="https://uwaterloo.ca/future-students/admissions/admission-requirements/life-sciences/high-school/international-system/"
LS="Life Sciences (includes three majors: Biochemistry, Biology, Psychology) admission requirements for"
SRC={
 "ls":{"url":"https://uwaterloo.ca/future-students/programs/life-sciences","page":"01ae4abccc53","title":"Life Sciences | Undergraduate Programs | University of Waterloo","organization":"University of Waterloo",
       "quotes":["At Waterloo, Life Sciences is a group of three related majors.","When you apply to Waterloo, you'll select one of the majors and choose the co-op program or the regular system of study .","Degree: Bachelor of Science in your chosen major"]},
 "reg":{"url":"https://uwaterloo.ca/future-students/co-op/regular-system-study","page":"dda2d9fb70b1","title":"Regular system of study | Undergraduate Programs | University of Waterloo","organization":"University of Waterloo",
       "quotes":["In the regular system of study, you'll be in school between September and April each year and have your summers free to work, travel, and pursue your interests outside of school.","Finish your degree in four years, instead of five years as in co-op."]},
 "uk":{"url":R+"british-system","page":"1ac39d3a08d4","title":LS+" British System (A Levels) high school students | University of Waterloo","organization":"University of Waterloo",
       "quotes":["A Level Mathematics, minimum final grade of B. Two of Biology, Chemistry, or Physics (one must be at the A Level), minimum final grade of B. One other academic A Level, minimum final grade of B. GCSE-level English, minimum final grade of B/5.",
                 "Passes in at least five unique subjects, three of which must be at the Advanced Level"]},
 "ib":{"url":R+"ib","page":"ac3ee1821b85","title":LS+" IB students | University of Waterloo","organization":"University of Waterloo",
       "quotes":["Mathematics: Analysis and Approaches HL or SL - minimum 4. HL or SL English A - minimum 4 or HL English B, minimum 5. Two of Biology, Chemistry, or Physics, total 27","IB diploma required with six total IB courses; at least three must be HL.","Total scores exclude diploma points."]},
 "us":{"url":R+"american-system","page":"06261e3cf344","title":LS+" American (US) system high school students | University of Waterloo","organization":"University of Waterloo",
       "quotes":["AP Calculus or Grade 12 Calculus, minimum grade of 75%. Grade 12 English, minimum grade of 75%. Algebra (Pre-Calculus), minimum grade of 75%. Two of Biology, Chemistry, Physics, or Statistics. One other Grade 12 academic or AP course. Minimum overall Grade 12 average: 85% including the required courses."]},
 "dl":{"url":"https://uwaterloo.ca/future-students/admissions/deadlines","page":"058cab974011","title":"Application deadlines | Undergraduate Programs | University of Waterloo","organization":"University of Waterloo",
       "quotes":["Programs other than Engineering February 1, 2027 February 15, 2027"]},
 "fees":{"url":"https://uwaterloo.ca/finance/fee-schedule-international-undergraduate-students-fall-2026","page":"92cd8f540ce4","title":"Fee schedule for international undergraduate students, Fall 2026 | University of Waterloo","organization":"University of Waterloo",
       "quotes":["Fees below are for Fall 2026 term only.","University of Waterloo bills students one term at a time:","fall term – September to December","winter term – January to April",
                 "Science programs Faculty/ Program Price per 0.5 unit course Maximum tuition fee per term Work report marking fee Co-op fee Incidental fees (including HST) FT = 1.5 or more units PT = fewer than 1.5 units Regular Year 1 $5,059.20 $25,296.00 - - $1,190.59 FT"]}}
def wl(slug,url,page,title,quotes,name,field):
    srcs={"course":{"url":url,"page":page,"title":title,"organization":"University of Waterloo","quotes":quotes},**SRC}
    a=lambda cur,src,th,subj:{"curriculum":cur,"source":src,"threshold":f"{name} (Life Sciences, Faculty of Science): {th}","required_subjects":subj,"tests":[],"english":ENG}
    write(SUB,{"uni":U,"slug":slug,"sources":srcs,
      "program":{"name":name,"degree_type":"BSc","field":field,"faculty":"","duration_years":4,"languages":["en"],"entry_year":"2026-2027 (Fall 2027 entry)","platform":"OUAC","source":"course","duration_source":"reg",
                 "summary":f"{name}, Bachelor of Science, one of three Life Sciences majors (regular system of study; co-op also offered).","application_requirements":[]},
      "costs":[{"residency":"international","currency":"CAD","tuition_per_term":25296,"terms_per_year":2,"terms_evidence":["fall term – September to December","winter term – January to April"],
                "academic_year":"Fall 2026 rate (Science, regular, maximum tuition per term × fall and winter terms)","source":["fees","reg"],
                "mandatory_per_term":1190.59,"living_from":"costProfile-ca-waterloo-cost-bsc-cs-international",
                "note":"International, Science programs, Regular Year 1: maximum tuition CAD 25,296.00 per term (Fall 2026), billed one term at a time; regular students are in school September to April (fall and winter terms). Incidental fees CAD 1,190.59 per full-time term."}],
      "deadline":{"date":"2027-02-01","source":"dl","round":"Application (OUAC)","platform":"OUAC","note":"Programs other than Engineering. Documents due February 15, 2027."},
      "admissions":[a("a-level","uk","A-Level Maths (B), two of Biology, Chemistry or Physics (B, one at A-Level), one other A-Level (B) and GCSE English (B/5); passes in five subjects, three at A-Level.",["Mathematics","two of Biology, Chemistry, Physics"]),
                    a("ib","ib","IB Diploma (six courses, at least three HL) with Maths Analysis and Approaches (HL or SL, minimum 4), English A (minimum 4, or HL English B 5) and two of Biology, Chemistry or Physics; total 27, excluding diploma points.",["Mathematics","two of Biology, Chemistry, Physics"]),
                    a("us-hs","us","AP or Grade 12 Calculus, Grade 12 English and Pre-Calculus (each at least 75%), two of Biology, Chemistry, Physics or Statistics, one other Grade 12 academic or AP course; overall Grade 12 average at least 85%.",["Mathematics","English"])]})
wl("bsc-biology","https://uwaterloo.ca/future-students/programs/biology","34ac87da0fde","Biology degree | Undergraduate Programs | University of Waterloo",[],"Biology","Biology")
wl("bsc-psychology","https://uwaterloo.ca/future-students/programs/psychology-science","6cbd498cdffe","Psychology (Bachelor of Science) | Undergraduate Programs | University of Waterloo",["Psychology (Bachelor of Science)"],"Psychology","Psychology")
print("ok")

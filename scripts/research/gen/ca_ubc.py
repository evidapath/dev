import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write
SUB="ca-majors"
CAL={"url":"https://vancouver.calendar.ubc.ca/fees/tuition-fees/undergraduate","page":"ff6d5ef77a2c","title":"Undergraduate tuition fees | UBC Vancouver Academic Calendar","organization":"The University of British Columbia"}
ENG={"from_existing":"admissionsRequirement-ca-ubc-admreq-ba-economics-ib"}
UKG="Standing in at least six academic subject areas (GCSE, AS Levels, A Levels), including English, with at least three academic A Levels or six AS Levels."
UKE="A minimum grade of C in English Literature or English Language at the GCSE, AS, or A Level."
USG="Graduation from an academic or college preparation program at a US regionally accredited school."
USQ=["English (composition/literature) to the senior level.","Three years of mathematics to the junior level.","A minimum grade of B- in an English course to at least the junior level.",
     "Applicants who choose not to submit a standardized test score will not be disadvantaged."]
IBG="Completed IB Diploma, including at least three Higher Level courses."
def ubc(slug,url,page,uk,us,name,deg,field,fac,faculty_rate_label,intl_rate,dom_rate,credits_src,credits,credits_q,fees_from_i,fees_from_d,living_i,living_d,deg_quotes,uk_extra,us_extra,ib_extra,uk_th,us_th,ib_th,uk_subj,ib_subj,summary):
    srcs={"course":{"url":url,"page":page,"title":f"{name} at UBC's Vancouver campus","organization":"The University of British Columbia","quotes":["Program length 4 years",f"Faculty {fac}",f"Degree {deg}",IBG,*ib_extra]},
          "uk":{"url":url,"page":uk,"title":f"{name} at UBC's Vancouver campus (United Kingdom requirements)","organization":"The University of British Columbia","quotes":[UKG,UKE,*uk_extra]},
          "us":{"url":url,"page":us,"title":f"{name} at UBC's Vancouver campus (United States requirements)","organization":"The University of British Columbia","quotes":[USG,*USQ,*us_extra]},
          "fees":{**CAL,"quotes":[f"International per-credit rate (commenced in 2026S or later)",f"{faculty_rate_label} ${intl_rate:,.2f}","For international undergraduate students starting their degree programs in the 2026/27 academic year, tuition will increase by no more than 3% each year for the subsequent four years or until graduation from their current degree program, whichever comes first.",f"Domestic per-credit rate",f"{faculty_rate_label} ${dom_rate:,.2f}"]},
          "credits":{"url":credits_src[0],"page":credits_src[1],"title":credits_src[2],"organization":"The University of British Columbia","quotes":[credits_q]}}
    a=lambda cur,src,th,subj:{"curriculum":cur,"source":src,"threshold":f"{name}: {th}","required_subjects":subj,"tests":[],"english":ENG}
    write(SUB,{"uni":"ca-ubc","slug":slug,"sources":srcs,
      "program":{"name":name,"degree_type":deg_quotes,"field":field,"faculty":fac,"duration_years":4,"languages":["en"],"entry_year":"2026-2027 (Fall 2027 entry)","platform":"","source":"course","summary":summary,"application_requirements":[]},
      "costs":[{"residency":"international","currency":"CAD","tuition_per_credit":intl_rate,"degree_credits":credits,"academic_year":f"2026/27 rate for students starting in 2026 ({faculty_rate_label} CAD {intl_rate:,.2f} per credit × {credits} credits ÷ 4 years); 2027 starters' rate not yet published","source":["fees","credits","course"],
                "fees_from":fees_from_i,"living_from":living_i,
                "note":f"International per-credit rate for {faculty_rate_label} students starting in 2026/27: CAD {intl_rate:,.2f}. The degree needs {credits} credits over 4 years, so this is the yearly average. Rises by no more than 3% a year after the first year."},
               {"residency":"domestic","currency":"CAD","tuition_per_credit":dom_rate,"degree_credits":credits,"academic_year":f"2026/27 domestic rate ({faculty_rate_label} CAD {dom_rate:,.2f} per credit × {credits} credits ÷ 4 years)","source":["fees","credits","course"],
                "fees_from":fees_from_d,"living_from":living_d,
                "note":f"Domestic per-credit rate for {faculty_rate_label}, 2026/27: CAD {dom_rate:,.2f}, over the degree's {credits} credits and 4 years."}],
      "admissions":[a("a-level","uk",uk_th,uk_subj),a("ib","course",ib_th,ib_subj),a("us-hs","us",us_th,["English"])]})
BIO="https://you.ubc.ca/programs/biology-vancouver/"
ubc("bsc-biology",BIO,"862107469246","ubc-bio-uk","ubc-bio-us","Biology","Bachelor of Science","Biology","Faculty of Science","Science",1769.40,206.69,
    ("https://vancouver.calendar.ubc.ca/faculties-colleges-and-schools/faculty-science/bachelor-science/general-degree-requirements","493caa4f9e34","General degree requirements | Bachelor of Science | UBC Vancouver Academic Calendar"),120,
    "A major, combined major, double major, or General Science option requires a minimum of 120 credits but may require more.",
    "costProfile-ca-ubc-cost-bsc-cs-international","costProfile-ca-ubc-cost-bsc-cs-domestic","costProfile-ca-ubc-cost-bsc-cs-international","costProfile-ca-ubc-cost-bsc-cs-domestic","BSc",
    ["Degree-specific requirements: Science Math (A or AS Level) Chemistry (GCSE) Physics (GCSE; may be waived with grades of A in A-Level Math and A-Level Chemistry)"],
    ["Degree-specific requirements: Science Pre-Calculus (AP or high school Calculus is recommended if you’re pursuing a BSc) One year of Chemistry One year of Physics (may be waived with grades of A in Pre-Calculus Math and AP Chemistry)"],
    ["Degree-specific requirements: Science IB Math Analysis and Approaches SL or HL, or IB Math Applications and Interpretations HL (IB Math Applications and Interpretations SL, or IB Math Studies, are not acceptable) One of IB Biology, IB Chemistry, or IB Physics"],
    "at least six academic subjects (GCSE, AS, A-Level) including English, with at least three A-Levels (or six AS-Levels) and at least a C in English. Science: Maths at A or AS Level, plus GCSE Chemistry and Physics (Physics may be waived with A grades in A-Level Maths and Chemistry).",
    "a US diploma from a regionally accredited school, senior-level English, three years of maths and at least B- in English; SAT/ACT optional. Science: Pre-Calculus, a year of Chemistry and a year of Physics.",
    "completed IB Diploma with at least three Higher Level courses. Science: IB Maths Analysis and Approaches (SL or HL) or Applications and Interpretations HL, and one of IB Biology, Chemistry or Physics.",
    ["Mathematics"],["Mathematics","Biology, Chemistry or Physics"],
    "Biology, Bachelor of Science (major or honours), Faculty of Science, UBC Vancouver; 4 years.")
PSY="https://you.ubc.ca/programs/psychology-vancouver-ba/"
ubc("ba-psychology",PSY,"496ede999dfd","ubc-psy-uk","ubc-psy-us","Psychology","Bachelor of Arts","Psychology","Faculty of Arts","Arts",1717.68,206.69,
    ("https://vancouver.calendar.ubc.ca/faculties-colleges-and-schools/faculty-arts/bachelor-arts/degree-requirements-students-who-enter-program-202425-or-later","d2aa4d8e22cb","Degree requirements | Bachelor of Arts | UBC Vancouver Academic Calendar"),120,
    "A minimum of 72 of the 120 credits required for the Bachelor of Arts degree program must be Arts credit",
    "costProfile-ca-ubc-cost-ba-economics-international","costProfile-ca-ubc-cost-ba-economics-domestic","costProfile-ca-ubc-cost-ba-economics-international","costProfile-ca-ubc-cost-ba-economics-domestic","BA",
    ["Degree-specific requirements: Arts No specific courses required beyond those needed for general admission"],
    ["Degree-specific requirements: Arts No specific courses required beyond those needed for general admission"],
    ["Degree-specific requirements: Arts No specific courses required beyond those needed for general admission"],
    "at least six academic subjects (GCSE, AS, A-Level) including English, with at least three A-Levels (or six AS-Levels) and at least a C in English. Arts: no specific courses beyond general admission.",
    "a US diploma from a regionally accredited school, senior-level English, three years of maths and at least B- in English; SAT/ACT optional. Arts: no specific courses beyond general admission.",
    "completed IB Diploma with at least three Higher Level courses. Arts: no specific courses beyond general admission.",
    [],[],
    "Psychology, Bachelor of Arts (major or honours), Faculty of Arts, UBC Vancouver; 4 years.")
# More majors (2026-11-18): same faculty, so the same faculty-wide entry requirements, per-credit
# rate and credit total as Biology (Science) or Psychology (Arts); each page carries those lines.
import hashlib
SCI=dict(fac="Faculty of Science",rate_label="Science",intl=1769.40,
    credits=("https://vancouver.calendar.ubc.ca/faculties-colleges-and-schools/faculty-science/bachelor-science/general-degree-requirements","493caa4f9e34","General degree requirements | Bachelor of Science | UBC Vancouver Academic Calendar"),
    credits_q="A major, combined major, double major, or General Science option requires a minimum of 120 credits but may require more.",
    fi="costProfile-ca-ubc-cost-bsc-cs-international",fd="costProfile-ca-ubc-cost-bsc-cs-domestic",deg="Bachelor of Science",short="BSc")
ARTS=dict(fac="Faculty of Arts",rate_label="Arts",intl=1717.68,
    credits=("https://vancouver.calendar.ubc.ca/faculties-colleges-and-schools/faculty-arts/bachelor-arts/degree-requirements-students-who-enter-program-202425-or-later","d2aa4d8e22cb","Degree requirements | Bachelor of Arts | UBC Vancouver Academic Calendar"),
    credits_q="A minimum of 72 of the 120 credits required for the Bachelor of Arts degree program must be Arts credit",
    fi="costProfile-ca-ubc-cost-ba-economics-international",fd="costProfile-ca-ubc-cost-ba-economics-domestic",deg="Bachelor of Arts",short="BA")
import json as _j
_bio=_j.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"../../../fact-checks/research/courses-2026-11/ca-majors/ca-ubc-bsc-biology.json")))
_psy=_j.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"../../../fact-checks/research/courses-2026-11/ca-majors/ca-ubc-ba-psychology.json")))
def _extra(ref,src): return [q for q in ref["sources"][src]["quotes"] if q.startswith("Degree-specific requirements")]
def _th(ref,cur): return next(a["threshold"] for a in ref["admissions"] if a["curriculum"]==cur).split(": ",1)[1]
def _subj(ref,cur): return next(a["required_subjects"] for a in ref["admissions"] if a["curriculum"]==cur)
for slug,path,key,name,field,F,ref in [
    ("bsc-mathematics","mathematics-vancouver-bsc","mathematics","Mathematics","Mathematics",SCI,_bio),
    ("bsc-physics","physics-vancouver","physics","Physics","Physics",SCI,_bio),
    ("bsc-chemistry","chemistry-vancouver","chemistry","Chemistry","Chemistry",SCI,_bio),
    ("ba-history","history-vancouver","history","History","History",ARTS,_psy),
    # English: held; its page (static and browser) doesn't show the general IB requirement line.
    ("ba-international-relations","international-relations-vancouver","international-relations","International Relations","International Relations",ARTS,_psy),
    ("ba-philosophy","philosophy-vancouver","philosophy","Philosophy","Philosophy",ARTS,_psy),
    ("ba-political-science","political-science-vancouver","political-science","Political Science","Politics",ARTS,_psy)]:
    u=f"https://you.ubc.ca/programs/{path}/"
    ubc(slug,u,hashlib.sha1(u.encode()).hexdigest()[:12],f"ubc-{key}-uk",f"ubc-{key}-us",name,F["deg"],field,F["fac"],F["rate_label"],F["intl"],206.69,
        F["credits"],120,F["credits_q"],F["fi"],F["fd"],F["fi"],F["fd"],F["short"],
        _extra(ref,"uk"),_extra(ref,"us"),[q for q in ref["sources"]["course"]["quotes"] if q.startswith("Degree-specific requirements")],
        _th(ref,"a-level"),_th(ref,"us-hs"),_th(ref,"ib"),_subj(ref,"a-level"),_subj(ref,"ib"),
        f"{name}, {F['deg']} (major or honours), {F['fac']}, UBC Vancouver; 4 years.")

print("ok")

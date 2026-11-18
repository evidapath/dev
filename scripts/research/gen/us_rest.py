import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from us import major
# MIT: one admission to MIT; majors declared in the first or second year
REG={"reg":{"url":"https://registrar.mit.edu/registration-academics/academic-requirements/majors-minors/declaring-major","page":"b39aefafe459",
     "title":"Declaring a major | MIT Registrar's Office","organization":"MIT Registrar's Office",
     "quotes":["Most students declare a major in the spring term of their first year at MIT. Those who do not must decide on a major by the end of their sophomore year."]}}
MQ=REG["reg"]["quotes"][0]
for slug,url,page,title,q,name,field,course in [
  ("biology-7","https://catalog.mit.edu/degree-charts/biology-course-7/","f09bc6c86ec8","Biology (Course 7) | MIT Course Catalog","Biology (SB, Course 7)","Biology","Biology","Course 7"),
  ("brain-cognitive-sciences-9","https://catalog.mit.edu/degree-charts/brain-cognitive-sciences-course-9/","48733fab288e","Brain and Cognitive Sciences (Course 9) | MIT Course Catalog","Brain and Cognitive Sciences (SB, Course 9)","Brain and Cognitive Sciences","Brain and Cognitive Sciences","Course 9"),
  ("architecture-4","https://catalog.mit.edu/degree-charts/architecture-course-4/","4e3ca703d2f8","Architecture (Course 4) | MIT Course Catalog","Architecture (SB, Course 4)","Architecture","Architecture","Course 4")]:
    major("us-mit",slug,url,page,title,"Massachusetts Institute of Technology",[q],name,"SB",field,"",4,
          f"{name} ({course}), Bachelor of Science (SB). MIT students declare a major in the first or second year.","program-us-mit-econ-14-1",MQ,more_sources=REG)
# Princeton: apply to the University; A.B. concentrations
U="https://admission.princeton.edu/academics/degrees-departments"; PG="a7710418c6e9"; T="Degrees & Departments | Princeton Admission"; O="Princeton University"
PQ="Students apply to Princeton University, not to individual departments, programs or schools."
for slug,name,field,q in [("psychology","Psychology","Psychology","Psychology A rigorous understanding of human behavior and mental processes, encompassing sensation, perception, movement, language, reasoning, decision making and social interaction."),
                          ("molecular-biology","Molecular Biology","Biology","Molecular Biology An exploration of the central questions of 21st-century biology, on topics ranging from molecules to genomes."),
                          ("architecture","Architecture","Architecture","The four-year undergraduate program leads to an A.B. with a concentration in architecture and offers an introduction to the discipline of architecture within the framework of a liberal arts curriculum.")]:
    major("us-princeton",slug,U,PG,T,O,[PQ,"Bachelor of Arts (A.B.)",q],name,"AB",field,"",4,
          f"{name} concentration, Bachelor of Arts (A.B.). Students apply to Princeton University, not to a department.","program-us-princeton-ab-economics",PQ)
# Stanford: majors declared by the end of sophomore year
SB={"pol":{"url":"https://bulletin.stanford.edu/academic-polices/degree-requirements/undergraduate-major","page":"bb90f314bec2","title":"Undergraduate Majors | Stanford Bulletin","organization":"Stanford University",
    "quotes":["Undergraduates must select a major by the end of their sophomore year."]}}
SQ=SB["pol"]["quotes"][0]
major("us-stanford","psychology","https://bulletin.stanford.edu/programs/PSYCH-BA","54f18b2059d0","PSYCH-BA - Psychology (BA) | Stanford Bulletin","Stanford University",
      ["PSYCH-BA - Psychology (BA)","Psychology Undergraduate Matriculated BA - Bachelor of Arts"],"Psychology","BA","Psychology","",4,
      "Psychology, Bachelor of Arts (BA). Stanford undergraduates select a major by the end of sophomore year.","program-us-stanford-economics",SQ,more_sources=SB)
major("us-stanford","biology","https://bulletin.stanford.edu/programs/BIO-BS","b922e636ff38","BIO-BS - Biology (BS) | Stanford Bulletin","Stanford University",
      ["Biology Undergraduate Matriculated BS - Bachelor of Science"],"Biology","BS","Biology","",4,
      "Biology, Bachelor of Science (BS). Stanford undergraduates select a major by the end of sophomore year.","program-us-stanford-economics",SQ,more_sources=SB)
# Penn: College of Arts & Sciences majors (same school as Economics)
U="https://catalog.upenn.edu/undergraduate/arts-sciences/majors/"; PG="4eb0135784a0"; T="Majors | School of Arts & Sciences | University of Pennsylvania Catalog"; O="University of Pennsylvania"
for slug,name,field,q in [("psychology","Psychology","Psychology","Psychology, BA"),("biology","Biology","Biology","Biology, BA"),("architecture","Architecture","Architecture","Architecture, BA")]:
    major("us-upenn",slug,U,PG,T,O,["School of Arts & Sciences",q],name,"BA",field,"School of Arts & Sciences",4,
          f"{name}, BA, a major in Penn's School of Arts & Sciences (the same school as Economics).","program-us-upenn-economics","School of Arts & Sciences")
# Cornell: College of Arts and Sciences (same college as Economics)
major("us-cornell","psychology","https://courses.cornell.edu/programs/psychology-ba/","51524b652693","Psychology (BA) | Cornell University Courses of Study","Cornell University",
      ["The Psychology major is open to students in the College of Arts and Sciences."],"Psychology","BA","Psychology","College of Arts and Sciences",4,
      "Psychology (BA), open to students in the College of Arts and Sciences (the same college as Economics).","program-us-cornell-economics","The Psychology major is open to students in the College of Arts and Sciences.")
major("us-cornell","biological-sciences","https://courses.cornell.edu/programs/biological-sciences-ba/","e0bc8ea53a05","Biological Sciences (BA) | Cornell University Courses of Study","Cornell University",
      ["The program's curriculum, academic advising, and undergraduate research components are coordinated for students in both colleges by the Office of Undergraduate Biology","College of Arts and Sciences"],
      "Biological Sciences","BA","Biology","College of Arts and Sciences",4,
      "Biological Sciences (BA) in the College of Arts and Sciences (the same college as Economics); the major is also offered in the College of Agriculture and Life Sciences.","program-us-cornell-economics","College of Arts and Sciences")
# NYU: College of Arts and Science (same college as Economics)
for slug,url,page,title,name,field in [("psychology","https://bulletins.nyu.edu/undergraduate/arts-science/programs/psychology-ba/","65ebe405cb1a","Psychology (BA) | NYU Bulletins","Psychology","Psychology"),
                                        ("biology","https://bulletins.nyu.edu/undergraduate/arts-science/programs/biology-ba/","e3c9dbb3dc8e","Biology (BA) | NYU Bulletins","Biology","Biology")]:
    major("us-nyu",slug,url,page,title,"New York University",[f"{name} (BA)","College of Arts and Science"],name,"BA",field,"College of Arts and Science",4,
          f"{name} (BA), College of Arts and Science (the same college as Economics).","program-us-nyu-economics","College of Arts and Science")
# USC: Dornsife (same school as Economics)
major("us-usc","biological-sciences","https://dornsife.usc.edu/bisc/undergraduate/programs-of-study/","3f21cb635008","Programs of Study - Biological Sciences - USC Dornsife","USC Dornsife College of Letters, Arts and Sciences",
      ["The interdepartmental Biological Sciences program offers both B.A. and B.S. degree options.","B.S. in Biological Sciences"],"Biological Sciences","BS","Biology","",4,
      "Biological Sciences (B.S.; a B.A. is also offered), USC Dornsife (the same school as Economics).","program-us-usc-economics","The interdepartmental Biological Sciences program offers both B.A. and B.S. degree options.")
print("ok")
# ASU: these majors use the university's general first-year admission requirements
PQ="First-year student admission requirements for this program are the same as the university's first-year admission requirements."
major("us-asu","psychology","https://degrees.apps.asu.edu/bachelors/major/ASU00/LAPGSBS/psychology","5f9c385691a6","Psychology Degree, BS | College of Liberal Arts and Sciences | ASU","Arizona State University",
      ["Psychology Degree, BS | College of Liberal Arts and Sciences | ASU",PQ],"Psychology","BS","Psychology","The College of Liberal Arts and Sciences",4,
      "Psychology, BS (The College of Liberal Arts and Sciences, Tempe). First-year admission requirements are the university's general ones.","program-us-asu-bs-economics",PQ)
BQ="All students are required to meet general university admission requirements."
major("us-asu","biological-sciences","https://degrees.asu.edu/bachelors/major/ASU00/LABSCBS/biological-sciences","561ccc51b6a2","Biological Sciences Degree, BS | ASU","Arizona State University",
      ["Biological Sciences Degree, BS | ASU",BQ,"In the Bachelor of Science program in biological sciences program, you study the organization and processes of life, from molecules to ecosystems."],"Biological Sciences","BS","Biology","The College of Liberal Arts and Sciences",4,
      "Biological Sciences, BS (The College of Liberal Arts and Sciences, Tempe). Applicants meet the university's general admission requirements.","program-us-asu-bs-economics",BQ)
print("asu ok")

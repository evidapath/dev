import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write
SUB="ae-majors"; U="ae-aus"
FEEQ="Tuition for all majors is AED 110,876 per academic year."
FEES={"url":"https://www.aus.edu/admissions/bachelors-degrees/undergraduate-tuition-and-fees","page":"d6ebdade3863","title":"Undergraduate Tuition and Fees | American University of Sharjah","organization":"American University of Sharjah",
      "quotes":["Undergraduate Tuition and Fees for Academic Year 2026-2027*",FEEQ]}
REQ={"url":"https://www.aus.edu/admissions/bachelors-degrees/application-requirements","page":"22de3cd61421","title":"Application Requirements | American University of Sharjah","organization":"American University of Sharjah"}
ENGQ="Engineering majors Math and Physics Applicants must have completed math within the final three years of secondary education. The physics science subjects must be completed by at least Grade 11, with preference given to Grade 12."
ARCQ="Architecture & Interior Design Math and a Science subject"
def aus(slug,url,page,title,quotes,name,deg,field,years,summary,base,subjects_quote,reqs=(),extra_req_quotes=()):
    write(SUB,{"uni":U,"slug":slug,
      "sources":{"course":{"url":url,"page":page,"title":title,"organization":"American University of Sharjah","quotes":quotes},
                 "fees":FEES,"req":{**REQ,"quotes":[subjects_quote,*extra_req_quotes]}},
      "program":{"name":name,"degree_type":deg,"field":field,"faculty":"","duration_years":years,"languages":["en"],"entry_year":"2026-2027 (Fall 2027 entry)","platform":"AUS online application","source":"course","summary":summary,"application_requirements":list(reqs)},
      "college":{"from":base,"quote":FEEQ,"subjects_quote":subjects_quote,"copy":["admissions","costs"]},
      "costs":[],"admissions":[]})
B="https://www.aus.edu/cen/"
aus("bsche",B+"department-of-chemical-and-biological-engineering/bachelor-of-science-in-chemical-engineering","19aff0ba4800","Bachelor of Science in Chemical Engineering | American University of Sharjah",
    ["Our comprehensive curriculum consists of a four-year , 130-credit degree plan leading to the Bachelor of Science in Chemical Engineering"],
    "Chemical Engineering","BSc","Engineering",4,"Bachelor of Science in Chemical Engineering, a four-year, 130-credit degree plan.","program-ae-aus-bscoe",ENGQ)
aus("bsce",B+"department-of-civil-engineering/bachelor-of-science-in-civil-engineering","8877d4166288","Bachelor of Science in Civil Engineering | American University of Sharjah",
    ["this undergraduate degree in civil engineering takes about four years to complete"],
    "Civil Engineering","BSc","Engineering",4,"Bachelor of Science in Civil Engineering (BSCE); takes about four years to complete.","program-ae-aus-bscoe",ENGQ)
aus("bsee",B+"department-of-electrical-engineering/bachelor-of-science-in-electrical-engineering","4ea035719766","Bachelor of Science in Electrical Engineering | American University of Sharjah",
    ["This highly acclaimed four-year Bachelor of Science in Electrical Engineering (BSEE) degree program is based on"],
    "Electrical Engineering","BSc","Engineering",4,"Bachelor of Science in Electrical Engineering (BSEE), a four-year degree.","program-ae-aus-bscoe",ENGQ)
aus("barch","https://www.aus.edu/caad/department-of-architecture/bachelor-of-architecture","d7f806f8e743","Bachelor of Architecture | American University of Sharjah",
    ["Our rigorous five-year Bachelor of Architecture program is enhanced by on-the-job professional trainin"],
    "Architecture","BArch","Architecture",5,"Bachelor of Architecture, a five-year programme; applicants submit a portfolio.","program-ae-aus-bscs",ARCQ,
    reqs=[{"name":"Portfolio","description":"Applicants to the majors of architecture, design management and interior design should submit a portfolio.","source":"req","necessity":"required","type":"other"}],
    extra_req_quotes=["applicants to the majors of architecture, design management, and interior design should submit a portfolio."])
print("ok")

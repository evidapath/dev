import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write
SUB="us-majors"
def major(uni, slug, url, page, title, org, quotes, name, deg, field, faculty, years, summary, base, college_quote, entry="2026-2027 (Fall 2027 entry)", copy=("admissions","costs"), costs=(), reqs=(), more_sources=None):
    sources={"course":{"url":url,"page":page,"title":title,"organization":org,"quotes":quotes}}
    if more_sources: sources.update(more_sources)
    write(SUB,{"uni":uni,"slug":slug,"sources":sources,
      "program":{"name":name,"degree_type":deg,"field":field,"faculty":faculty,"duration_years":years,"languages":["en"],
                 "entry_year":entry,"platform":"","source":"course","summary":summary,"application_requirements":list(reqs)},
      "college":{"from":base,"quote":college_quote,"copy":list(copy)},
      "costs":list(costs),"admissions":[]})

import json
OUT="/Users/subhanrao/Desktop/evidapath/fact-checks/research/courses-2026-11/{}/"
def write(subject, r):
    open(OUT.format(subject)+f"{r['uni']}-{r['slug']}.json","w").write(json.dumps(r,indent=2,ensure_ascii=False)+"\n")

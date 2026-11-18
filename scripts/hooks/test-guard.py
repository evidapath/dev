#!/usr/bin/env python3
"""test-guard.py : check scripts/hooks/guard-bash.py blocks and allows what it should.
Run: python3 scripts/hooks/test-guard.py  (prints one line per case; exit 1 if any case is wrong).
The risky commands are only strings passed to the guard here; nothing is executed."""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
F = "--" + "force"  # spelled in two parts so this file's own text doesn't look like the command
CASES = [
    ("BLOCK", f"git push {F}"),
    ("BLOCK", "git push -f origin main"),
    ("BLOCK", "git commit --amend -m x"),
    ("BLOCK", "git reset --hard HEAD~1"),
    ("BLOCK", "cat .secret-patterns"),
    ("BLOCK", "head evidapath-navigator/.env.local"),
    ("BLOCK", "echo $TOKEN"),
    ("BLOCK", "scripts/apply-sanity-mutations.sh fact-checks/pending/x.ndjson"),
    ("BLOCK", 'curl -s -X POST "https://jxwrtsiz.api.sanity.io/v2024-01-01/data/mutate/staging" -d @b.json'),
    ("BLOCK", "npx wrangler@4 deploy"),
    ("BLOCK", "scripts/sync-ghl.sh --push"),
    ("ALLOW", "git commit -q -m x"),
    ("ALLOW", "git push -q"),
    ("ALLOW", 'curl -s -X POST "https://jxwrtsiz.api.sanity.io/v2024-01-01/data/mutate/staging?dryRun=true" -d @b.json'),
    ("ALLOW", "TOKEN=\"$(grep '^SANITY_READ_TOKEN=' evidapath-navigator/.env.local | cut -d= -f2-)\""),
    ("ALLOW", "scripts/sync-ghl.sh"),
    ("ALLOW", "python3 -I scripts/research/q.py 'count(*[_type==\"program\"])'"),
]
bad = 0
for want, cmd in CASES:
    r = subprocess.run([sys.executable, os.path.join(HERE, "guard-bash.py")],
                       input=json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}}), capture_output=True, text=True)
    got = "BLOCK" if r.returncode == 2 else "ALLOW"
    bad += got != want
    print("ok " if got == want else "BAD", want.ljust(5), cmd[:90])
sys.exit(1 if bad else 0)

#!/usr/bin/env python3
"""PreToolUse hook for Bash: blocks commands that break EvidaPath's standing rules.
Exit 2 = block; the message on stderr is shown to Claude. Edit this file to change a rule."""
import json, re, subprocess, sys

cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def block(msg):
    print(f"BLOCKED by scripts/hooks/guard-bash.py: {msg}", file=sys.stderr)
    sys.exit(2)

def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, cwd=ROOT).stdout

def has_secret(text):
    # scripts/hooks/secret-scan.sh: generic token shapes + private patterns from .secret-patterns
    r = subprocess.run(["sh", os.path.join(ROOT, "scripts/hooks/secret-scan.sh")], input=text, capture_output=True, text=True)
    return r.returncode != 0

# History is synced to AI Studio and the repo is public: never rewrite pushed history.
if re.search(r"\bgit\s+push\b[^|;&]*(\s--force\b|\s-f\b|\s--force-with-lease\b|\s\+\S)", cmd):
    block("force-push rewrites pushed history. Not allowed.")
if re.search(r"\bgit\s+commit\b[^|;&]*--amend\b", cmd) or re.search(r"\bgit\s+(rebase|filter-branch|filter-repo)\b", cmd):
    block("amend/rebase/filter rewrites history. Make a new commit instead.")
if re.search(r"\bgit\s+reset\s+--hard\b", cmd):
    block("git reset --hard discards work. Ask Subhan first.")

# Secrets: never print token files.
if re.search(r"\b(cat|less|more|head|tail|bat|nl|strings|open|code|nano|vim?|xxd|od)\b[^|;&]*(\.env\.local|\.dev\.vars|\.env\b|\.secret-patterns)", cmd):
    block("that would print a secrets file. Read single values with grep ... | cut into a variable, never to the screen.")
if re.search(r"\b(echo|printf|print)\b[^|;&]*\$\{?(TOKEN|SANITY_\w*TOKEN|ANTHROPIC_API_KEY)\b", cmd):
    block("that would print a token.")

# Subhan runs Sanity applies, deploys and GHL syncs. Claude dry-runs only.
if re.search(r"apply-sanity-mutations\.sh", cmd):
    block("Sanity applies are run by Subhan. Write the pending file, dry-run it, and give him the command.")
if re.search(r"/data/mutate/", cmd) and "dryRun=true" not in cmd:
    block("Sanity mutate without ?dryRun=true. Claude only dry-runs; Subhan applies.")
if re.search(r"\bwrangler(@\d+)?\s+deploy\b|sync-ghl\.sh\s+--push|\bsanity\s+(deploy|dataset\s+(import|delete))", cmd):
    block("deploys and GHL pushes are run by Subhan. Give him the command.")

# Secret scan on everything that is about to be committed or pushed.
if re.search(r"\bgit\s+commit\b", cmd):
    if has_secret(git("diff", "--cached")):
        block("the staged diff contains a secret or the test password. Unstage it.")
if re.search(r"\bgit\s+push\b", cmd):
    if has_secret(git("log", "-p", "@{u}..HEAD")):
        block("a commit about to be pushed contains a secret or the test password.")
sys.exit(0)

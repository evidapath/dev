# EvidaPath — Handoff Context

> For a fresh Claude Code session picking up this project mid-stream.

---

## What this project is

EvidaPath is a university-search and offer-vault platform for UAE students. Stack: TanStack Start (React, Cloudflare Workers), Sanity CMS (content), Supabase (student data). Live at evidapath.com.

Key constraint: **never publish hallucinated facts**. Every data field that isn't primary-source verified must be stored as `null` or a caveat string — not a plausible value.

---

## Active work: Batch-2 university import

**Goal:** Import 50 universities into Sanity as DRAFTS (not published). Suhail's requirement doc lists all 50 with required fields.

### Status — 16/50 done as drafts

| Done | Schools |
|------|---------|
| UAE (8/8) | AUS, UAEU, Khalifa, UOS, Birmingham Dubai, Heriot-Watt Dubai, RIT Dubai, Canadian U Dubai |
| US (8/9) | Princeton, MIT, Harvard, Stanford, UPenn, Cornell, NYU, USC |
| Remaining US | Purdue, ASU |

### Remaining (34 schools)

- **US (2):** Purdue, ASU
- **UK (7):** Cambridge, Imperial, UCL, Warwick, Manchester, Birmingham, Nottingham
- **Canada (5):** Waterloo, UBC, McGill, McMaster, Alberta
- **Germany (5):** RWTH Aachen, Heidelberg, TU Berlin, KIT, LMU Munich
- **Netherlands (3):** Eindhoven (TU/e), Amsterdam (UvA), Twente (UT)
- **Malaysia (4):** Malaya, Monash Malaysia, Nottingham Malaysia, Taylor's — **needs `country-my` created first**
- **Australia (4):** Melbourne, Sydney, Monash, UNSW — **needs `country-au` created first**

### Skip these (already in DB from Batch-1):
Oxford, Toronto, TU Munich, TU Delft, NYUAD

---

## Import tooling

**Main script:** `sanity-studio/scripts/import_universities.py`

```bash
# Dry run (safe, no writes):
python3 import_universities.py --school <id>

# Execute (writes to Sanity):
SANITY_TOKEN=<write-token> python3 import_universities.py --school <id> --execute
```

- The script builds the full university scaffold: uni doc + country ref + programs (CS/Engineering/Business/Economics where offered) + admissions + costs + scholarships + sources — all as Sanity **drafts** (`drafts.` prefix on _id).
- Internal refs use **base IDs** (no `drafts.` prefix) so they resolve correctly in both preview and after publishing.
- Each university in the script is a Python dict. Add new ones following the existing pattern (see `us-cornell`, `us-harvard` etc. for reference).

**Sanity project:** `jxwrtsiz`, dataset: `staging`

**Per-school data required (from Suhail's spec):**
1. Official name, country, city, website
2. Programs: CS / Engineering / Business / Economics (include only what the school offers — never fabricate)
3. Accepted qualifications (A-Level, IB, US HS, other)
4. Program-specific academic + language requirements
5. Deadlines, required tests, required docs
6. **International** tuition + mandatory fees + living cost (distinguish intl vs domestic)
7. Scholarships — mark as `automatic`, `need_based`, `competitive`, or `guaranteed`
8. Source URL + verification date + confidence per material field
9. Store uncertain/unavailable fields as `null` — **never fill in a plausible value**

---

## Previewing drafts locally

```bash
# In evidapath-navigator/:
SANITY_READ_TOKEN=<read-token> SANITY_PERSPECTIVE=drafts bun run dev
```

(vite doesn't auto-load `.dev.vars` so pass both inline. Read token CAN read drafts.)

Default perspective is `published` — prod stays safe, never accidentally shows unverified drafts.

---

## Key files

| File | Purpose |
|------|---------|
| `sanity-studio/scripts/import_universities.py` | Batch-2 importer |
| `evidapath-navigator/src/lib/sanity.server.ts` | Sanity GROQ client + adapter |
| `evidapath-navigator/src/lib/universities.functions.ts` | Server fn wrapper (mock fallback) |
| `evidapath-navigator/.dev.vars` | Local env vars (gitignored) — SANITY_READ_TOKEN |
| `evidapath-navigator/src/lib/mock-data.ts` | Legacy mock data (still used as fallback) |

---

## What's already wired (don't re-do)

- Universities page → reads Sanity (published perspective)
- Scholarships page → reads Sanity
- Discover / Find-my-path / Analyze → reads Sanity
- Applications + Offer Vault → writes Supabase, cost lookup from Sanity
- Auth → Supabase Auth, works on both localhost and prod
- 5 Batch-1 schools (NYUAD, Oxford, Toronto, TUM, Delft) → PUBLISHED in Sanity staging, full program coverage (CS/Eng/Business/Econ where applicable)

---

## The 9 review questions — run on EVERY step, without miss

Subhan + Suhail's standing rule. Questions 1–5 are theirs; 6–9 were added after each caught a real error.

1. Can it be done better?
2. Is this targeted at the correct user? (the student making a real, high-stakes decision)
3. If I reviewed this, what faults would I find, and how do I remove them?
4. Does this fit the requirements of what the site is for, and does it affect anything else?
5. Is this the best possible result? If not, how do I make it the best?
6. **Have I tested this against the real system, or am I assuming?** (assumption is where hallucination enters)
7. **Does every fact trace to a primary source, and does the UI show uncertainty instead of manufacturing certainty?** (Suhail's core principle — hard gate)
8. **If this is wrong, can I undo it, and what's the blast radius on live/student data?** (why we dry-run, stage before prod, respect safety blocks)
9. **Is this inside the current phase goal, or am I expanding beyond it?** (phase = one student, five universities, Discover→Analyze→Plan→Fund; nothing more)

Actually run them before acting, not just when reminded. When one changes the plan, say so out loud so Subhan sees the reasoning.

---

## Hard rules (don't break these)

1. **Import as DRAFTS only** — never call `publish_to_sanity.py` on batch-2 schools without explicit sign-off from Suhail
2. **No hallucinated data** — null > plausible placeholder
3. **Program-specific costs** — never use university-wide averages for program-level fields
4. **International tuition** — always international (not domestic/EU)
5. **Scholarship distinction** — guaranteed need-based aid ≠ competitive merit scholarship

---

## Tokens / secrets

- Sanity **write token**: Subhan/Suhail hold it — not in the repo. Pass via `SANITY_TOKEN=...` env var.
- Sanity **read token**: in `evidapath-navigator/.dev.vars` as `SANITY_READ_TOKEN` (gitignored).
- Supabase: Subhan is Owner — credentials in `.env.local` (gitignored).

---

## Next step

Continue Batch-2 with **Purdue + ASU** (US schools, no new country doc needed), then UK batch. Each uni takes ~6–8 primary-source lookups; do in controlled batches of 2–4, verify before moving on.

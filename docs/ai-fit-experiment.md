# AI fit (experiment)

An "AI fit check" panel on Find My Path that picks the programmes that fit a
student best: not just cheapest, but the most selective ones a strong student's
grades meet within budget, with subject evidence such as accreditation.
Experimental: off for everyone except allow-listed accounts.

## Switch on / off

Two server settings (never commit them):

| Setting | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your Claude API key |
| `AI_FIT_ALLOWLIST` | comma-separated emails that may see it, e.g. `evidapathtesting@gmail.com,you@example.com` |
| `AI_FIT_MODEL` (optional) | `claude-haiku-5-5` to use Haiku; anything else or unset = `claude-sonnet-5-5` |

- Locally: add the lines to `evidapath-navigator/.env.local` (the dev server reads secrets from there, not from `.dev.vars`), then restart `bun run dev`.
- Staging (Cloudflare): `npx wrangler@4 secret put ANTHROPIC_API_KEY` and `npx wrangler@4 secret put AI_FIT_ALLOWLIST` in `deploy/cloudflare`.
- GHL: More → Cloud → Secrets, same two names.

Off = remove `AI_FIT_ALLOWLIST` (or empty it). Nobody else sees anything. To
remove the experiment entirely, delete the files listed below and the
`<AiFitPanel>` block in `src/routes/find-my-path.tsx`.

## How it stays honest

1. **Facts first.** `src/lib/ai-fit.server.ts` builds a pack of facts from
   EvidaPath's checked data only: cost vs budget, entry requirement and its
   selectivity, English test, deadline, scholarships, visa rules, and
   accreditation from `src/lib/fit-evidence.ts` (ABET, Engineers Canada,
   UK Engineering Council, EQUIS; read on 2026-11-10 with source links).
   Each fact has an id.
2. **Strict instructions.** `src/lib/ai-fit.prompt.ts`: use only the facts; no
   rankings, prestige or reputation; every sentence cites fact ids; every number
   copied from a cited fact; missing facts are unknown, never a weakness; never
   predict admission; don't steer strong students to weaker fits just because
   they're cheaper. Model: `claude-sonnet-5-5` (it doesn't accept a temperature or a forced tool
   call, so the prompt requires the `submit_fit` call and nothing is shown without it).
3. **Checked in code.** Every sentence is removed unless it cites real fact
   ids that belong to that university, has no ranking or admission-prediction
   words, and every number in it appears in a cited fact. Invented universities,
   over-budget "best overall" picks and stretch picks without a caution are
   dropped. The panel shows how many statements were removed, and each reason
   shows the facts behind it.
4. **Comparisons are worked out in code.** Positions such as "the highest
   published requirement your band meets" or "the lowest all-in cost that fits
   your budget" are computed across the whole list and given as facts. The model
   may say "highest/lowest/cheapest" only when citing one, and "higher/lower than"
   only when citing both universities' figures and the direction is true.
5. **The summary is counted, not written.** The overall line ("46 programmes …
   16 fit your budget …") is produced by code. Gap notes must cite facts about one
   university and pass the same checks.

## Test results (2026-11-10)

13 live runs over 9 student profiles (Sonnet 5.5 and Haiku 5.5). No invented facts,
rankings or admission predictions survived. What testing changed: Sonnet 5.5
rejects `temperature` and forced tool choice; it needs ~2-3k thinking tokens;
true comparisons were being dropped (now computed in code); Haiku wrote a summary
that mixed up two universities (summary now counted in code). Sonnet stays the
default. It also exposed a decision-engine bug: Sharjah's "at least 24 of 45
points" was read as IB 45 (fixed). Known limit: US universities that publish no
grade cutoff (MIT, Stanford, Harvard …) can't be compared, so they rarely appear
as picks.

## Privacy

The student's answers (curriculum, grade band, subject, budget, citizenship,
languages) go to Anthropic. Name and email are not sent. Errors log the HTTP
status only.

## Files

- `src/lib/fit-evidence.ts`: accreditation evidence (sourced)
- `src/lib/ai-fit.prompt.ts`: the instructions and output schema
- `src/lib/ai-fit.server.ts`: fact pack, API call, validation
- `src/lib/ai-fit.functions.ts`: access check and run (allow-list enforced)
- `src/components/AiFitPanel.tsx`: the panel

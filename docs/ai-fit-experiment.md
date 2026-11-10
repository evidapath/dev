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

- Locally: add both lines to `evidapath-navigator/.dev.vars`.
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
   they're cheaper. Model: `claude-sonnet-5-5`, temperature 0, forced tool call.
3. **Checked in code.** Every sentence is removed unless it cites real fact
   ids that belong to that university, has no ranking or admission-prediction
   words, and every number in it appears in a cited fact. Invented universities,
   over-budget "best overall" picks and stretch picks without a caution are
   dropped. The panel shows how many statements were removed, and each reason
   shows the facts behind it.

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

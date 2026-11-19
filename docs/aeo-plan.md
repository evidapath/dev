# Answer and agent engine optimisation (AEO) plan

Goal: when a student asks ChatGPT, Claude, Perplexity, Gemini or Google's AI answers
something like "how much does Psychology at UBC cost for an international student" or
"what IB score do I need for Imperial Medicine", the answer quotes EvidaPath's verified
figure and links to it.

Answer engines can only cite what they can read. They read plain HTML (most AI crawlers
don't run JavaScript) and structured data (schema.org JSON-LD). So the plan is: put
every verified fact into server-rendered HTML, describe it with schema.org, shape pages
around the questions students actually ask (AnswerThePublic), and measure.

Rule carried over from the data work: a page or a JSON-LD block only states what the
Sanity record states, with its source and the date it was checked. Nothing is filled in
to make the markup look complete; an unpublished figure is left out, not guessed.

## Where things stand (checked 2026-11-17)

- Staging (`evidapath-staging.evidapath.workers.dev`) is server-rendered, but the
  university data is fetched in the browser afterwards. Fetched as a crawler,
  `/universities` shows "All countries 0": no universities, fees or programmes.
- No page has schema.org structured data (no `application/ld+json` anywhere in `src/`).
- There are no pages per university or per programme; 265 verified programmes at 53
  universities exist only inside list views.
- `/universities` still describes itself as data that "will be displayed as verified data
  is added".
- `robots.txt` allows everything and lists the sitemap; the sitemap lists the 10 or so
  app pages only. No `llms.txt`.
- The staging host serves the same pages as the future main site; canonicals already
  point to `evidapath.com`.
- `evidapath.com` itself is on the interim GHL site until the move to Cloudflare
  (domain lock ends around 2026-12-28), so this work lands on the Cloudflare app and
  goes live with that move.

## Progress (2026-11-19)

- `/universities` now loads its data on the server: the HTML a crawler gets carries the first page
  of university cards and, in JSON-LD, all 53 universities (`CollegeOrUniversity` in an
  `ItemList`) and all 459 programmes (`EducationalOccupationalProgram` with `provider`,
  `educationalCredentialAwarded`, `timeToComplete` and one tuition `Offer` per fee group). Built in
  `src/lib/structured-data.ts` from the records the page renders; illustrative fallback data and
  costs marked not re-checked are left out. Every property was checked against schema.org's own
  vocabulary file (`inLanguage` isn't defined for this type, so it isn't used).
- Every page carries `Organization` and `WebSite` JSON-LD.
- The out-of-date `/universities` description is rewritten.
- AnswerThePublic: first three seeds run (UAE, English):
  `fact-checks/aeo/answerthepublic/2026-11-19-uae.md`.
- Still to do: per-university and per-programme pages, sitemap from Sanity, staging `noindex`,
  robots.txt AI-crawler choice and `llms.txt` (decisions for Subhan), question pages, Rich
  Results Test / validator.schema.org runs on the deployed page.

## Phase 1: facts crawlers can read

1. Load the university data in the route loaders (server side), so the HTML of
   `/universities` and `/scholarships` already contains the names, fees and entry
   requirements.
2. Add one page per university (`/universities/<id>`) and per programme
   (`/universities/<id>/<programme>`). Each programme page states, in plain sentences:
   - yearly tuition per fee group, with currency and academic year;
   - living cost and its source;
   - entry requirement per curriculum (A-Level, IB, US, CBSE…), English level, tests;
   - deadline and application platform;
   - the source link for every figure and the "last checked" date;
   - what isn't published, said as such.
3. Generate `sitemap.xml` from Sanity (every university and programme page, with
   `lastmod` from the record's last check).
4. Rewrite the out-of-date page descriptions (`/universities` and others) from what the
   page now shows.
5. Keep staging out of search: `noindex` on the `workers.dev` host only.

## Phase 2: schema.org structured data

JSON-LD generated from the same record the page renders, so markup and page can't
disagree. Types and properties below are all on schema.org (checked against the
schema.org type pages on 2026-11-17).

| Page | Type | Properties used |
|---|---|---|
| Every page | `Organization` (EvidaPath), `WebSite` | `name`, `url`, `logo`, `sameAs` |
| University page | `CollegeOrUniversity` | `name`, `url` (the university's own site), `sameAs`, `address` (country, city) |
| Programme page | `EducationalOccupationalProgram` | `name`, `provider` (the `CollegeOrUniversity`), `educationalCredentialAwarded` (e.g. "BSc"), `timeToComplete` (ISO 8601, e.g. `P4Y`, `P3Y6M`), `numberOfCredits` where published, `programPrerequisites` (the entry requirement as text), `applicationDeadline`, `applicationStartDate` where published, `url` (official programme page), `offers` |
| Programme fee | `Offer` inside `offers` | `price`, `priceCurrency`, `category` ("Tuition, international students, per year"), `description` (fee group and academic year), `validFrom`, `url` (the fee source) |
| Question pages (Phase 3) | `FAQPage` → `Question` → `acceptedAnswer` | `name`, `acceptedAnswer.text` |
| Every page | `BreadcrumbList` | `itemListElement` |
| Cost database | `Dataset` | `name`, `description`, `creator`, `dateModified`, `license`, `distribution` (only if a public data file is offered, see Phase 4) |

Notes:
- Google shows FAQ rich results only for a small set of sites since 2023, so `FAQPage`
  is for answer engines reading the page, not for Google snippets.
- Validate every template with validator.schema.org and Google's Rich Results Test
  before release, and add a build check that the JSON-LD values equal the rendered
  values.
- Fields that the record marks unknown or unpublished are left out of the JSON-LD.

## Phase 3: the questions students ask (AnswerThePublic)

AnswerThePublic needs a free account to run searches. You create it and run the
searches; I don't create accounts or handle passwords.

1. Run AnswerThePublic for these seeds (language English; run each for the
   countries you target, e.g. UAE, India, UK, US):
   - cost of studying in UK / Canada / USA / Australia / Netherlands / Malaysia / UAE
   - international student tuition
   - IB requirements for university
   - A level requirements for university
   - study medicine abroad
   - study psychology abroad, study engineering abroad, study law abroad
   - scholarships for international students
   - university application deadlines
   - the 53 university names on their own (e.g. "UBC", "Taylor's University")
2. Export each result as CSV into `fact-checks/aeo/answerthepublic/` (one file per
   seed and country).
3. I then:
   - cluster the questions;
   - keep the ones EvidaPath can answer from verified records ("how much is…", "what
     grades do I need for…", "when is the deadline for…", "is X cheaper than Y…");
   - drop the rest, and list them separately as gaps.
4. For each kept cluster, a question page: the answer in the first one or two sentences
   (figure, university, year, source link), then the detail table, then related
   programmes. Marked up with `FAQPage`. Generated from Sanity, so a fee update changes
   the answer everywhere.
5. Re-run the same seeds every quarter and compare.

## Phase 4: agent access

1. `robots.txt`: name the AI crawlers explicitly so the choice is deliberate:
   - `GPTBot`, `OAI-SearchBot` (OpenAI);
   - `ClaudeBot` (Anthropic);
   - `PerplexityBot`;
   - `Google-Extended` (Gemini training).

   Decision for you: allow search/answer crawlers only, or training crawlers too.
2. `llms.txt` at the site root: a short plain-text guide to what EvidaPath covers, how
   figures are sourced, and links to the university and programme pages. It's an
   emerging convention, not a standard, but costs little.
3. Optional public data file (`/data/programmes.json`): one record per programme with
   its sources and check date, for agents that read data directly.

   Decision for you: whether to publish the data openly, and under what licence.

## Phase 5: measure

1. Google Search Console and Bing Webmaster Tools for `evidapath.com` after the move
   (you add the DNS verification).
2. A fixed list of 30 student questions, asked monthly in ChatGPT, Claude, Perplexity,
   Gemini and Google AI answers. Logged in `fact-checks/aeo/answer-checks/` with the date,
   whether EvidaPath is cited, and whether the figure quoted matches ours.
3. Server logs: hits from the AI crawlers named above, per page.

## Order and size

| Step | What | Size |
|---|---|---|
| 1 | Server-side data loading, programme and university pages, sitemap, descriptions, staging noindex | largest; ~2-3 sessions |
| 2 | JSON-LD templates and the build check | 1 session |
| 3 | robots.txt choice, llms.txt | small |
| 4 | Question pages from the AnswerThePublic exports | after you run the searches |
| 5 | Measurement set-up and first monthly check | small, then monthly |

Nothing here changes the live GHL site; it ships with the move to Cloudflare.

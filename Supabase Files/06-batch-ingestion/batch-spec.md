# EvidaPath batch ingestion contract (design only -- not executed)

**Standing constraint, repeated per the original synthesis instruction:
this document designs how a future batch of universities WOULD be
ingested under the V1.2 schema. No batch has been run. No sixth
university has been researched. This file and its two companions
(`example-batch-manifest.json`, `batch-output-contract.md`) are the
deliverable -- not a kickoff.**

## Why a batch contract, now

The five-university test set proved the V1.1→V1.2 pipeline end-to-end on
genuinely heterogeneous institutions (a Bologna-system Dutch university, a
collegiate British one, a Canadian provincial-tuition one, a German
Land-funded one with a qualification-recognition gate, and a US-style
liberal-arts UAE campus). Before scaling past five, the next real risk
isn't schema coverage -- V1.2 already resolved every recurring modeling
failure the test set exposed -- it's **process discipline at volume**:
running the same seven-phase pipeline 10-20 times without silently
degrading verification quality, source-hierarchy discipline, or
human-review gating. A batch contract exists to keep every run in a batch
to the same bar the five test-set runs were held to, not to loosen it for
throughput.

## Batch unit and naming

A **batch** is a named, fixed-size group of universities queued for the
full seven-phase pipeline, run one institution at a time (never
parallelized across institutions within a single agent session, to
preserve the same close, per-source verification discipline the test set
used). A batch is never organized globally by country -- naming instead
reflects the actual decision-relevant grouping a batch was assembled for:

```
{country}-{program-family}[-{region}]-{batch-number}
```

- `country`: ISO-lowercase country code or short slug matching this
  pipeline's existing canonical-ID country prefixes (`nl`, `gb`, `ca`,
  `de`, `ae`, ...). A batch spanning multiple countries uses the
  dominant/organizing country or a short multi-country slug agreed at
  batch-definition time (e.g. `eu-` for a genuinely pan-EU batch) --
  never left ambiguous.
- `program-family`: the representative program family this batch
  researches (default: `computer-science`, matching the test set's own
  scope-discipline rule of one representative program per institution
  unless told otherwise).
- `region` (optional): a sub-national qualifier when `country` alone is
  ambiguous or the batch is deliberately regional (e.g. a batch of
  California universities: `us-computer-science-california-001`).
- `batch-number`: zero-padded 3-digit sequence, per `country`+
  `program-family`+`region` combination, starting at `001`.

Examples: `ca-computer-science-001` (a Canadian CS batch), `de-computer-
science-002` (a second German CS batch, after `001` completes),
`us-computer-science-california-001` (a California-scoped batch).

## Batch size

Recommended first batch: **10 universities**, not 20. Rationale:
- The five-university test set already surfaced six new top-level
  entities and a dozen embedded-object refinements -- a real, non-trivial
  rate of schema learning per institution (roughly 1.2 new/refined
  concepts per university). A first production batch should be small
  enough that another V1.3-worthy structural finding doesn't have to
  propagate through 20 already-completed runs before anyone notices it.
- 10 institutions is enough to test the batch *process* itself (manifest
  handling, per-institution folder isolation, aggregate QA rollup, human-
  review queue volume) without compounding an undiscovered process gap
  across double that number.
- Once a 10-university batch completes cleanly against every
  `04-pipeline/*_v1_2.py` check (or its coverage gaps are as honestly
  disclosed as this synthesis's own), scaling the next batch to 15-20 is
  reasonable.

## What a batch does NOT change

- The seven-phase pipeline itself is unchanged per institution: research
  → extraction → normalization → verification → change-detection → Sanity
  preparation → reporting. A batch is an outer loop around unchanged
  per-institution discipline, not a shortcut through any phase.
- `HUMAN_REVIEW → APPROVED` still requires Suhail's explicit sign-off,
  every record, every institution, every batch -- no auto-promotion
  introduced by batching.
- No batch pushes to a live Sanity project on its own; Sanity import
  remains a separate, explicitly authorized step per
  `../05-sanity/import/import-readme.md`.
- One representative program per institution remains the default scope
  unless a batch is explicitly defined otherwise.

## Per-batch process (design)

1. **Define** the batch: write an `example-batch-manifest.json`-shaped
   manifest naming every institution, its target program, and its
   canonical-ID prefix in advance (prevents ID collisions being
   discovered mid-batch).
2. **Run** the seven-phase pipeline once per institution, in the existing
   `runs/{YYYY-MM-DD}_{university-id}_{program-short-slug}/` folder
   convention, completely independently -- one institution's CONFLICT or
   blocked source never stalls another's.
3. **Roll up**: after every institution in the batch reaches at least
   `04-verification`, run the V1.2 QA suite (`validate_normalized_records_v1_2.py`,
   `check_fields_supported_v1_2.py`, `check_verification_coverage_v1_2.py`)
   against each, and produce one aggregate batch-level QA summary (see
   `batch-output-contract.md`) -- the same per-institution checks used in
   this synthesis, not a new lighter bar for batches.
4. **Human review gate**: present the batch's aggregate summary (per-
   institution PASS/FAIL, HUMAN_REVIEW record counts, disclosed coverage
   gaps) for sign-off before any record in the batch is promoted past
   `HUMAN_REVIEW`.
5. **Sanity draft generation**: only after step 4, run
   `normalized_to_sanity_ndjson_v1_2.py --combine-dir` scoped to the
   batch's institutions, exactly as this synthesis did for the five-school
   set, still never pushed live without separate authorization.

## Explicit non-goals of this document

This is a design document, not an execution plan with a start date. It
does not authorize starting a batch, does not name which 10 universities
would be first, and does not change any of the standing constraints
(no sixth university researched, no batch begun, no live Sanity write)
that governed this entire V1.2 synthesis.

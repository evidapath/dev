# EvidaPath batch output contract (design only -- not executed)

Defines what a completed batch run must produce, so a future batch's
output is checkable by the same discipline this V1.2 synthesis applied to
the five-university test set -- not a new, looser bar invented for scale.

## Per-institution outputs (unchanged from the existing pipeline skill)

Every institution in a batch produces the exact same run-folder contract
already defined in the `evidapath-university-intelligence` skill:
`01-research/` through `07-reporting/`, nothing added or removed by
being part of a batch. A batch does not change what a single institution
run must produce -- only how many run at once and how their results are
rolled up afterward.

## Batch-level aggregate outputs (new, this is what batching adds)

A completed batch must produce, alongside the per-institution folders:

```
batches/{batch-id}/
  manifest.json                    -- the batch manifest (see example-batch-manifest.json), updated
                                       with real status/timestamps as the batch progresses
  aggregate-qa-summary.json        -- one row per institution per QA script:
                                       validate_normalized_records_v1_2 / check_fields_supported_v1_2 /
                                       check_verification_coverage_v1_2, each PASS/FAIL plus the
                                       underlying script's own --out JSON path
  human-review-queue.json          -- every record across the batch currently at record_status
                                       HUMAN_REVIEW, grouped by institution, for a single sign-off pass
                                       rather than one per institution
  batch-summary.md                 -- human-readable: institutions completed, programs researched,
                                       scholarships researched, total fields verified/missing,
                                       conflicts discovered, records blocked from publication,
                                       aggregate coverage-gap counts (in the same honest,
                                       non-fabricated spirit as this synthesis's own
                                       check_verification_coverage_v1_2.py findings)
```

## `aggregate-qa-summary.json` shape

```json
{
  "batch_id": "example-computer-science-001",
  "generated_at": "<derived from batch completion date, never datetime.now() at report-write time>",
  "institutions": [
    {
      "canonical_id": "...",
      "validate_normalized_records_v1_2": "PASS",
      "check_fields_supported_v1_2": "PASS",
      "check_verification_coverage_v1_2": "FAIL",
      "coverage_summary": {
        "not_covered_canonical": 0,
        "not_covered_absence": 0,
        "not_covered_extension": 0,
        "not_covered_new_entity": 0
      }
    }
  ],
  "batch_overall_result": "PASS_WITH_DISCLOSED_COVERAGE_GAPS | PASS | FAIL"
}
```
`batch_overall_result` is `FAIL` only for `validate_normalized_records_v1_2`
or `check_fields_supported_v1_2` failures (schema violations, broken
references, unsupported field claims -- structural problems that must be
fixed before proceeding). A `check_verification_coverage_v1_2` FAIL alone
produces `PASS_WITH_DISCLOSED_COVERAGE_GAPS`, mirroring exactly how this
five-school synthesis itself is being delivered: real, disclosed, backlog-
worthy gaps are not blocking defects, but they are never silently hidden
either.

## Definition of done for a batch

A batch is "done" (ready for its human-review sign-off gate) when every
institution has:
1. Reached at least `04-verification` in its own run folder.
2. `validate_normalized_records_v1_2.py` = PASS (0 schema violations, 0
   broken references, 0 duplicate IDs).
3. `check_fields_supported_v1_2.py` = PASS.
4. `check_verification_coverage_v1_2.py` result recorded (PASS or FAIL --
   a FAIL does not block batch completion but must appear in
   `batch-summary.md`, not be silently dropped).
5. Every `CONFLICT`-status record is present with its blocking source
   disagreement documented, not resolved by guessing.

A batch is "closed" only after Suhail's explicit sign-off on the human-
review queue, mirroring the single-run gate that already governs every
`HUMAN_REVIEW -> APPROVED` transition.

## What this contract does not authorize

Producing this contract does not start a batch, does not push any Sanity
draft live, and does not add a sixth university's real data anywhere in
this repository. It is the acceptance criteria a real batch would be
checked against, written down before scale so that scaling doesn't become
an excuse to quietly relax any check this five-university synthesis just
finished proving out.

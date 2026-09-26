# EvidaPath directory / collection strategy (design only)

## The core principle: geography is data, not folders

Every entity in the V1.2 schema already carries its own geography as
structured, queryable data: `Program.university_ref → University.country_ref
→ Country`, and `University.primary_city_ref → City`. This means public-
facing "browse by country" or "browse by region" views are **GROQ queries
against that data**, not a directory or folder structure that duplicates
records per geography. The moment a record is filed into a
country-specific folder AND has its own `country_ref` field, the two can
drift -- exactly the kind of duplicated-source-of-truth problem this
entire V1.2 synthesis was built to eliminate at the schema level. The
directory strategy below therefore treats every public "Collection" as a
**saved slice of the same underlying documents**, never a copy.

## Geography hierarchy (data, always)

```
Global
  -> Country            (country document)
    -> [optional Region]  (not yet a schema entity -- see "Region" below)
      -> University       (university document, country_ref -> Country)
        -> Campus          (campus document, city_ref -> City, country_ref -> Country)
          -> Program         (program document, university_ref -> University, campus_ref -> Campus | null)
```

`[optional Region]` is deliberately bracketed: none of the five test-set
institutions produced evidence that a sub-national "region" grouping is a
material, decision-relevant entity (the gap matrix never surfaced this as
a recurring modeling failure -- it only came up as an ergonomic want, "it
would be nice to browse by US state," never as something a student's
decision actually depended on). Per this synthesis's own promotion
criteria ("evidence before architecture"), no `Region` entity was added
to the V1.2 schema, and none should be added to the schema now on
speculation. If a future batch (e.g. a California-scoped batch, per
`../06-batch-ingestion/batch-spec.md`'s naming convention) demonstrates a
real, recurring need for a queryable sub-national region, that is new
evidence and can justify promoting `Region` in a future schema version --
exactly the same bar V1.2 itself was held to.

## Sanity "Collections" are queryable slices, never duplicate documents

A public Collection (e.g. "Computer Science in Canada," "Test-Optional
Universities," "Universities Under $30k Total Cost of Attendance") is
implemented as one of:

1. **A GROQ query saved/exposed to the frontend**, filtering the existing
   `program`/`university`/`costProfile` documents by their real reference
   fields and material facts (e.g. `*[_type == "program" &&
   university_ref->country_ref->_ref == "drafts.country-ca"]`). This is
   the default and preferred mechanism -- zero duplication, always
   current the moment an underlying document changes.
2. **A lightweight `collection` document** (not built in this synthesis --
   a design recommendation only) holding a name, description, and a
   stored query definition or an explicit array of document references,
   for collections whose membership isn't a clean field filter (e.g. an
   editorially curated "Editor's Picks" list). Even this stores
   *references*, never copies, of the underlying Program/University
   documents.

Neither mechanism was built in `05-sanity/` as part of this synthesis --
`document-types/` and `object-types/` are the schema for the source-of-
truth entities only. A `collection` document type is a genuinely separate,
frontend-facing concern layered on top, and should be scoped and designed
once real Collection use cases exist (batch #1's "browse by country/program
family" being the most obvious first candidate, since the batch-naming
convention itself is already organized that way).

## Why NOT a country-based folder/repository structure

Organizing `runs/` or a future production dataset primarily by country
(`runs/canada/toronto/...`, `runs/germany/tu-munich/...`) was considered
and rejected for the same reason a `Region` entity wasn't added
speculatively: it optimizes for a browsing pattern (looking at one
country at a time) at the cost of every other real pattern this dataset
already needs to support just as well -- browsing by program family
across countries (a batch's own organizing principle, per
`batch-spec.md`), by cost tier, by admission-decision-plan type, or by
verification status for QA triage. A flat `runs/{date}_{institution}_{program}/`
folder (the existing, unchanged convention) plus fully-structured,
cross-referenced Sanity documents supports every one of those access
patterns equally, through queries, not through which shelf a file physically
sits on.

## What this means for the existing `runs/` folder convention

No change recommended. `runs/{YYYY-MM-DD}_{university-id}_{program-slug}/`
remains the correct on-disk convention for the research pipeline's own
artifacts (it's an audit trail of *when and how* a record was produced,
not the production data model itself). The production "browse by
geography" experience is a Sanity/GROQ-level concern entirely separate
from how the pipeline's own working folders are named.

## Summary recommendation

- Keep geography as fully structured, referenced data (`Country` →
  `City`/`University` → `Campus` → `Program`), never duplicated into a
  folder hierarchy.
- Do not add a `Region` schema entity until a real batch demonstrates a
  recurring, decision-relevant need for one (none has yet).
- Build public Collections as saved queries (or, later, a lightweight
  `collection` document referencing existing documents) over the existing
  schema -- never as copied records.
- Leave the `runs/` folder convention exactly as it is; it is a pipeline
  audit trail, not the production data model.

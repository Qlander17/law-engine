# Pedagogical Contract schema

## What this is

`PedagogicalContract` (`services/models.py`) is a reusable schema for
teaching one important legal concept, rule, procedure, document, asset, or
transaction end-to-end. Where `StatuteSection` stores a normalized
statute and `TransactionLifecycle` (`services/transaction_lifecycle.py`)
walks a running fact pattern through several stages, `PedagogicalContract`
is the third reusable shape: a single, structured teaching unit for one
subject, covering everything a learner needs to actually recognize and use
that subject correctly -- not just its statutory text.

It does not replace `StatuteSection` or `TransactionLifecycle`. A
`PedagogicalContract` typically points back at a `StatuteSection` (via
`section_id`) and can reference the same fact pattern a lifecycle stage
uses (see the worked example below, which describes the same rule as
`transaction_lifecycle.py`'s "merchant-and-warranties" stage).

## Why it exists

A learner needs more than a citation and a paragraph of statutory text to
actually use a legal concept: they need to recognize it in a fact pattern,
know what it does, know what commonly goes wrong, know what it's confused
with, and know how sensitive the conclusion is to a changed fact. Writing
that out ad hoc for every concept produces inconsistent, incomplete
coverage. `PedagogicalContract` is the one reusable shape for that --
every future subject (a UCC provision, a procedural rule, a transaction
document, an asset class) gets built against the same fields, so gaps are
visible (an empty field) rather than silently missing.

## The fields

Grounding fields (required -- these are what keep the schema honest):

- `contract_id`, `subject_name`, `subject_kind` (`PedagogicalSubjectKind`:
  `CONCEPT` / `RULE` / `PROCEDURE` / `DOCUMENT` / `ASSET` / `TRANSACTION`)
- `authority_citation`, `authority_type`, `jurisdiction` -- the real
  citation this contract rests on
- `verification_status`, `confidence_label` -- reuses the existing
  `VerificationStatus`/`ConfidenceLabel` enums from `models.py` rather than
  a parallel trust system, so a caller-facing surface has exactly one place
  to check how sure the engine is
- `source_layer` (defaults to `ENACTMENT`, same default and same reasoning
  as `SourceManifest`)

Optional linking fields: `source_document_id`, `section_id`,
`governing_text_excerpt` (the real statutory/source text, when there is
one), `version_or_effective_date`.

Optional teaching fields (populate only what's relevant to the subject --
not every field applies to every kind of subject):

| Field | Question it answers |
|---|---|
| `what_it_is` | What is it? |
| `why_it_exists` | What problem does it solve? |
| `how_to_recognize` | How do you spot it in a fact pattern? |
| `what_it_does` | What rights or duties does it create? |
| `what_to_do_with_it` | What's the actual next action? |
| `timing_notes` | When does timing matter? |
| `signing_authentication_process` | How is it signed/authenticated/indorsed/transferred/filed? |
| `who_signs_or_acts` | Who acts, and in what capacity? |
| `what_can_go_wrong` | What are the common failure modes? |
| `commonly_confused_with` | What's the adjacent concept people mix it up with? |
| `fact_sensitivity` | What changes if one fact changes? (`list[FactSensitivityNote]`) |
| `metaphor` | A pedagogical illustration (`PedagogicalMetaphor`, see below) |

## The metaphor field is structurally separate on purpose

`metaphor` is a `PedagogicalMetaphor`, not a string reused from
`governing_text_excerpt`. It carries its own `illustration` text plus a
`disclaimer` and an `is_pedagogical_only` flag that both serialize with
it. This means a metaphor can never silently stand in for the governing
text -- they are different fields with a different type, and the metaphor
self-labels as non-authoritative wherever it travels. Never write legal
conclusions into `metaphor.illustration`; it exists purely to build
intuition, and it must never be the thing a caller cites as the rule.

## Worked example

`services/pedagogical_contract.py::build_implied_warranty_of_merchantability_contract()`
builds a real, fully populated `PedagogicalContract` for the implied
warranty of merchantability, grounded in the actually-ingested text of
**Va. Code Ann. § 8.2-314** (`services/retrieval.get_section("8.2-314")`).
It also cites § 8.2-104 (merchant definition) and § 8.2-313 (express
warranty) -- both real ingested sections -- and derives its § 8.2-316
(exclusion/modification) citation from § 8.2-314's own ingested text and
`cross_references`, rather than treating an un-ingested section as a data
source. Its metaphor (a sandwich-shop analogy) is clearly separate from
`governing_text_excerpt`, which holds the real statutory paragraph.

Run it directly to see the full populated JSON:

```
python3 -m services.pedagogical_contract
```

## Building a new one

1. Confirm the section(s) you need are actually ingested:
   `services.retrieval.get_section("<section_id>")` must return
   non-`None`. If it isn't ingested yet, don't invent its text -- either
   ingest it first or omit the field.
2. Add a `build_<subject>_contract()` function to
   `services/pedagogical_contract.py` (or a new module, if the subject
   doesn't belong in this file), following the same `_require_section`
   pattern used here and in `transaction_lifecycle.py`.
3. Populate only the teaching fields that genuinely apply to the subject.
   Leave the rest at their default (`None` / empty list) rather than
   filling them with filler text.
4. If you want an illustration, write it as a `PedagogicalMetaphor`, never
   into `governing_text_excerpt` or any citation-bearing field.
5. Add a test in `services/test_pedagogical_contract.py` (or alongside
   your new module) asserting the citation matches the real ingested
   section and that the metaphor, if present, is distinct from the
   governing text.
6. Run `python3 -m unittest discover -s services -p "test_*.py"` from
   `law-engine/` and confirm the full suite still passes.

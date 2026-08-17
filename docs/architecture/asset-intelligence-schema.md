# Asset Intelligence schema

`services/asset_intelligence.py` is a reusable schema for analyzing a
*type* of asset a person owns, is acquiring, or was transferred -- not one
specific transaction, but the general legal characteristics of an asset
class (a vehicle, an account receivable, real property, and so on).

## Why this exists

Different asset types answer the same basic legal questions very
differently:

- What actually counts as evidence of ownership?
- Does "who has it" (possession), "whose name is on the registry"
  (title), or "who has the technical/contractual ability to direct it"
  (control) matter most?
- Can it be used as collateral for a loan, and if so, how does a lender
  perfect and prioritize that interest?
- What body of law even governs it?

`AssetProfile` gives one consistent shape for answering all of these per
asset type, so the Learning Engine can teach "how do I think about this
kind of asset" as a reusable pattern instead of one-off trivia per item.

## The `AssetType` taxonomy

`VEHICLE`, `EQUIPMENT`, `INVENTORY`, `CONSUMER_GOODS`, `MONEY`,
`BANK_ACCOUNT`, `CHECK`, `PROMISSORY_NOTE`, `CONTRACT_RIGHTS`,
`ACCOUNTS_RECEIVABLE`, `DOCUMENT_OF_TITLE`, `INVESTMENT_ASSET`,
`DIGITAL_ASSET`, `REAL_PROPERTY`, `FIXTURES`, `OTHER`.

This taxonomy deliberately spans both UCC Article 9 personal-property
collateral categories (goods subtypes, accounts, instruments, etc.) *and*
non-UCC asset classes (real property) in the same enum, so the boundary
between "UCC governs this" and "UCC does not govern this at all" is
something the schema can represent and test, rather than something
assumed away by only modeling UCC collateral types.

## `AssetProfile` fields

| Field | Purpose |
|---|---|
| `legal_classification` | What this asset type actually is, legally. |
| `evidence_of_ownership` | What actually proves someone owns it (receipt, title, deed, possession...). |
| `title_concept` / `possession_concept` / `control_concept` | The three distinct ownership-adjacent concepts UCC/property law uses -- not every asset type uses all three the same way. |
| `transferability` / `assignability` | How ownership (or, for a right, the right itself) moves to someone else. |
| `security_interest_eligible` | Can this asset type serve as loan collateral at all? |
| `perfection_method` / `priority_notes` | If eligible: how a secured party locks in and ranks its claim. |
| `controlling_documents` | The real paperwork that actually matters for this asset type. |
| `record_retention_notes` | What to keep, and why. |
| `governing_bodies_of_law` | Real bodies of law (e.g. "UCC Article 2", "state real-property law") -- never an invented specific citation unless grounded. |
| `jurisdiction` | Which jurisdiction's version of that law this profile describes. |
| `common_mistakes` | Real, recurring misconceptions about this asset type. |
| `citation` / `section_id` | Populated **only** when a claim on this profile traces to a real ingested statutory section. |
| `citation_grounding_note` | Explicit disclosure of what is/isn't grounded -- required whenever `citation` is `None`. |

## Grounding discipline

Two of the five example profiles (`CONSUMER_GOODS`, `VEHICLE`) and the
`REAL_PROPERTY` contrast profile cite the real ingested "goods"
definition at Va. Code Ann. Section 8.2-105
(`services/retrieval.get_section("8.2-105")`) -- the same section
`transaction_lifecycle.py`'s threshold-scope stage already uses.

The other two example profiles (`ACCOUNTS_RECEIVABLE`,
`PROMISSORY_NOTE`) describe well-known, generally-accurate UCC Article 9
(and, for the note, Article 3) characteristics -- security-interest
eligibility, perfection method, priority -- **without** inventing a
citation. Article 9 is not yet ingested in this codebase as of this
module's creation (a separate, concurrent ingestion effort may add it
later); until then, `citation`/`section_id` stay `None` and
`citation_grounding_note` says so explicitly. `services/test_asset_intelligence.py`
asserts this discipline mechanically: every profile with a non-`None`
citation must trace to a real `get_section()` result, and every profile
without one must carry an explicit disclosure.

## The deliberate `REAL_PROPERTY` contrast

`build_real_property_profile()` exists specifically to teach a boundary,
not just to fill out the taxonomy: **UCC Article 2 (sale of goods) and
UCC Article 9 (secured transactions in personal property) do not govern
real property at all.**

- `security_interest_eligible=False` -- hard-coded, not left to a general
  heuristic, so a caller can never accidentally treat real property as
  UCC collateral.
- `perfection_method` explicitly states real property is "not applicable
  under UCC Article 9 at all" and that a mortgage/deed of trust is
  perfected by recording in the land records instead -- a wholly separate
  system from a UCC-1 filing.
- `priority_notes` explains real-property lien priority runs on
  recording-act rules, not Article 9's first-to-file-or-perfect rules.
- `governing_bodies_of_law` lists only `"state real-property law"` and
  `"state recording/land-records law"` -- no UCC entries at all.
- `common_mistakes` explicitly calls out the temptation to file a UCC-1
  against real property, and separately flags that **fixtures** (goods
  permanently attached to real property) straddle both regimes and have
  their own UCC "fixture filing" concept -- distinct from ordinary real
  property, and worth its own future profile rather than being folded
  into this one.

The profile still cites the real ingested Section 8.2-105 "goods"
definition -- not because Article 2 governs real property, but because
the cleanest way to prove real property falls *outside* that definition
is to point at the definition's own movability requirement and show land
doesn't meet it. `services/test_asset_intelligence.py` asserts both
halves of this: `security_interest_eligible` is `False`, and the profile
explicitly names *both* UCC Article 2 and UCC Article 9 as inapplicable
rather than leaving that as an inference for the reader.

## Related: contracts as assets

A contract's *payment right* is itself one of the asset types this
taxonomy touches (`ACCOUNTS_RECEIVABLE`, and potentially `CONTRACT_RIGHTS`
more broadly). `services/contract_rights.py` and
`docs/contracts-as-assets.md` dig into that specific case in more
depth -- distinguishing the document, the agreement, the rights it
creates, and the payment right specifically, including the four UCC
Article 9 payment-right sub-classifications (account, chattel paper,
instrument, payment intangible).

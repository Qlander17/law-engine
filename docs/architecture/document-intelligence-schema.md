# Document Intelligence — schema

`services/document_intelligence.py` is the foundation for a "Document
Identification Engine": a reusable schema for identifying and teaching
about a legal document type, plus one real interactive exercise. It does
not edit `services/models.py` — it only reads `models.py`'s existing enums
where relevant and defines its own new dataclasses/enums in its own module.

## The core principle: substance over title

A document's printed title — the word at the top of the page, or a
filename — is not what determines its legal character. What determines
it is the document's actual operative language and how it functions in
the transaction: who sent it, what it says, and what has (or hasn't)
happened yet.

**Real example, grounded in the ingested Article 2 text**
(`library/normalized/ucc/article-2-sections.json`): a document titled
"Purchase Order #4471," sent by a buyer to a seller, listing goods, a
quantity, and a proposed price, requesting "prompt shipment" — with the
seller having done nothing yet — is an **offer**, not a contract. Va.
Code Ann. § 8.2-206(1)(b) treats exactly this kind of document ("an
order or other offer to buy goods for prompt or current shipment") as
inviting the seller's acceptance by a prompt promise to ship or by
prompt shipment itself; Va. Code Ann. § 8.2-204 confirms no contract
exists until that acceptance (or other conduct showing agreement)
actually happens.

Flip one operative fact and the classification changes even though the
title on the page might not:

- If the same document were **signed by both parties** and stated final,
  no-further-acceptance-needed terms, it could function as the contract
  itself.
- If the same list of goods/prices were sent **by the seller, after** an
  informal agreement, to confirm and bill for what was sold, it would
  function as a confirmation/invoice under Va. Code Ann. § 8.2-207 (whose
  title is literally "Additional terms in acceptance or confirmation"),
  not as an offer.

This is why every `DocumentProfile` carries a `title_vs_substance_note`
field, and why the one interactive exercise this module ships
(`build_purchase_order_identification_exercise()`) is built around this
exact PO-vs-contract-vs-invoice distinction rather than a trivia-style
"name the document" question.

## `DocumentFamily`

A coarse-grained enum of document families the engine can identify:
`CONTRACT`, `PURCHASE_ORDER`, `INVOICE`, `SECURITY_AGREEMENT`,
`FINANCING_STATEMENT`, `PROMISSORY_NOTE`, `NEGOTIABLE_INSTRUMENT`,
`CHECK_DRAFT`, `GUARANTY`, `LEASE`, `BILL_OF_LADING`,
`WAREHOUSE_RECEIPT`, `TITLE_CERTIFICATE`, `ASSIGNMENT`, `OTHER`.

## `DocumentProfile`

Everything the engine knows about how to recognize and reason about one
document family:

| Field | Purpose |
|---|---|
| `identifying_features` | Observable traits that suggest this family |
| `required_elements` / `optional_elements` | What the document must vs. may contain |
| `legal_function` | What the document actually *does*, legally |
| `common_confusions` | Real, specific ways this family gets misidentified |
| `related_authorities` | Real citations only — see grounding rule below |
| `signature_authentication_rules` | How the document is authenticated |
| `transfer_indorsement_rules` | How (if at all) it's transferred |
| `filing_possession_control_consequences` | What perfection/priority mechanism, if any, attaches |
| `related_asset_types` | What kinds of collateral/subject-matter it typically involves |
| `title_vs_substance_note` | The substance-over-title caveat, specific to this family |
| `grounded_in_ingested_text` / `grounding_note` | Whether `related_authorities` traces to a real ingested section, and an honest explanation either way |

### The grounding rule: never invent a citation

This module follows the same discipline as
`services/pedagogical_contract.py` and `services/transaction_lifecycle.py`:
every citation traces to a real section retrieved live via
`services.retrieval.get_section()`, verified through each builder's own
`_require_section()` helper (which raises `DocumentIntelligenceError`
rather than silently substituting invented text if the section isn't
actually ingested).

**Three profiles are grounded** in the real, currently-ingested Article 2
text (`library/normalized/ucc/article-2-sections.json`, 11 sections
total):

1. **`PURCHASE_ORDER`** — Va. Code Ann. §§ 8.2-206, 8.2-204. § 8.2-206
   directly discusses "an order or other offer to buy goods for prompt or
   current shipment" — a purchase order, by function, is exactly this.
2. **`CONTRACT`** (sales contract for goods) — Va. Code Ann. §§ 8.2-204,
   8.2-105. § 8.2-204 ("Formation in general") is the most directly
   Article-2-discussed document of all: it's the section that defines how
   a contract for sale of goods comes into existence.
3. **`INVOICE`** — Va. Code Ann. § 8.2-207. The ingested text never uses
   the word "invoice" — this profile grounds the family **by function**,
   not by word match: § 8.2-207's title is literally "Additional terms in
   acceptance or confirmation," and discusses "a written confirmation"
   sent after an agreement, which is what a real-world invoice commonly
   is. The profile's `grounding_note` discloses this functional mapping
   explicitly rather than implying the statute uses the word "invoice."

**Three profiles are deliberately ungrounded** — real, well-known legal
document types that are Article 9 or Article 3 concepts, not yet
ingested into this system:

- `SECURITY_AGREEMENT`, `FINANCING_STATEMENT`, `PROMISSORY_NOTE` — each
  has `grounded_in_ingested_text=False`, an empty `related_authorities`
  list, and a `grounding_note` that says so explicitly. Their
  characteristics are well-known, generally-accurate legal content, but
  are not sourced from any real citation in this system yet — the gap is
  disclosed, never papered over with an invented section number.

`test_document_intelligence.py`'s `test_no_ungrounded_profile_invents_a_section_number`
enforces this mechanically: it scans every ungrounded profile's prose
fields for anything matching a Virginia Code Article 2 section-number
pattern and fails if one appears that isn't one of the 11 real ingested
sections.

## `DocumentIdentificationExercise`

A real, working "what kind of document is this?" exercise: a short
structured hypothetical plus an observed-feature list, a correct
`DocumentFamily` answer, and — following the same pattern already used by
`services/learning.py`'s `MultipleChoiceQuestion` and
`services/transaction_lifecycle.py`'s `LifecycleChoice` — an explanation
for **why the correct answer is correct AND why each wrong alternative is
wrong**, each citing real ingested text.

The one exercise this module ships
(`build_purchase_order_identification_exercise()`) presents the PO
hypothetical above with three choices: `PURCHASE_ORDER` (correct, §
8.2-206/§ 8.2-204), `CONTRACT` (wrong — no acceptance has happened yet, §
8.2-204), and `INVOICE` (wrong — wrong direction and timing relative to §
8.2-207's confirmation concept). It also carries a
`DocumentMetaphor` — a simplified, explicitly non-authoritative
illustration (an auction-bid analogy for "offer, not yet a deal"),
defined locally in this module rather than importing
`models.py`'s `PedagogicalMetaphor`.

## Why a local `DocumentMetaphor` instead of `models.PedagogicalMetaphor`

`services/models.py` already has a `PedagogicalMetaphor` dataclass with
the same shape and the same non-authoritative labeling convention. This
module intentionally does **not** import it — keeping the two modules
independent avoids coupling `document_intelligence.py` to the exact shape
of `models.py`'s dataclass. `DocumentMetaphor` copies the convention (an
`illustration`, a fixed `disclaimer`, and `is_pedagogical_only=True`)
without the dependency.

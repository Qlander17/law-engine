# UCC Authority Hierarchy — Design Note

Design/architecture note, written 2026-08-16. **No code was written or
changed for this note.** It records a decision/direction for future Law
Engine runs: the layered authority structure a multi-jurisdiction,
multi-regime commercial-law engine must eventually respect, so that
structure isn't lost or re-derived from scratch later. It builds directly
on research already done this project — `docs/ucc-source-licensing-audit.md`
(Model vs. Enactment licensing/provenance) and `docs/cisg-architecture-design.md`
(CISG as a separate regime) — rather than re-deriving either.

## Why this hierarchy needs to be written down now

Law Engine today ingests exactly one jurisdiction's UCC text (Virginia,
Title 8.2 and Title 8.9A — see `docs/ucc-orientation.md`). That's a
perfectly reasonable place to start, but it creates a specific risk as the
project grows: **the system's own convenience (only one state ingested) can
quietly become the system's implicit legal claim (that Virginia's law is
"the" UCC, or governs everything)**. Nothing in the current codebase makes
that mistake — `services/models.py`'s `SourceLayer` enum already keeps
`MODEL`/`ENACTMENT`/`INTERPRETATION` structurally separate, and
`docs/ucc-orientation.md` already states the Model/Enactment distinction
carefully. This note exists so that discipline survives contact with a
second state, a real interstate fact pattern, or an international sale —
none of which the codebase handles yet, and none of which should be handled
by silently defaulting to Virginia.

## 1. Model UCC — the national conceptual/reference baseline

The Uniform Law Commission (ULC) and American Law Institute (ALI) jointly
draft and promulgate the "official" UCC text and Article structure. It is
not law anywhere by itself — a uniform act has no legal force until a state
legislature enacts it (see `docs/ucc-orientation.md`, "Is the UCC itself
binding law?"). It is, however, the shared conceptual reference point:
Article numbering, section structure, and drafting purpose that every
state's enactment starts from and that Law Engine's own
`services/ucc_orientation.py` already uses for its `model_uc_citation`
fields (e.g. `"UCC Article 9"`) without treating that citation as binding
statutory text.

**Where this belongs in the data model, if ever ingested:**
`services/models.py`'s `SourceLayer.MODEL` enum value already exists for
exactly this — see `SourceManifest.source_layer`. **Not ingested today.**
No ALI/ULC official Model UCC text or official comment is stored anywhere
in `library/`, and `docs/ucc-source-licensing-audit.md` §1(a)/§3 explains
why that's a deliberate, licensing-driven choice, not an oversight: the
ALI/ULC official text and comments are copyrighted, "internal reference
only" material under this project's own licensing conventions, not
something to bulk-ingest or republish. If a future run does ingest Model
text for internal comparison purposes, it must be tagged
`SourceLayer.MODEL` and given a `licensing_status` following the
`"copyrighted -- ALI/ULC official text..."` convention already documented
in the licensing audit — never silently defaulting to the `ENACTMENT`
layer's current dataclass default.

## 2. State enactments — the actual binding statutory authority

What actually governs a real transaction is a specific state's own enacted
statute. Law Engine's real, ingested content is exactly this layer:
Virginia's Title 8.2 (11 sections, `services/ingestion.py`) and Title 8.9A
(13 sections, `services/ingestion_article9.py`), tagged
`SourceLayer.ENACTMENT` in `services/models.py` (the dataclass's own
default, since every `SourceManifest` ingested to date is a state
enactment).

**This must be said explicitly and will keep needing to be said explicitly
as the project grows: Virginia is the first ingested state, not "the
authoritative UCC."** Virginia's Title 8.2/8.9A is one jurisdiction's
enactment — closely tracking the ULC/ALI model text for most provisions,
but not guaranteed to match it or any other state's enactment section-for-
section (`docs/ucc-orientation.md` makes the same point: "a specific
section can and sometimes does diverge"). Law Engine must never:

- Conflate a Virginia enactment with "the Model text" (the two are
  different `SourceLayer` values for a real reason — see §1 above).
- Present Virginia's enacted rule as if it were universal or automatically
  the rule for a transaction connected to some other state.
- Silently default to Virginia's text for a transaction that has no real
  Virginia connection, just because Virginia happens to be the only
  ingested jurisdiction today.

The second and third points are exactly why §3 below (choice of law) is a
real, load-bearing gap, not a nice-to-have.

## 3. Choice of law — determining which jurisdiction's enacted law governs

Because every U.S. state has its own enactment (with real textual
variation), an interstate transaction requires an actual determination of
*which* state's enacted law governs — a question Law Engine cannot yet
answer for any real transaction, because it has only one state's text to
even offer as a candidate. The general (Article 1) framework for this
question, and the common-law fallback when the UCC's own rule doesn't
apply, are both real and well-settled:

### 3.1 UCC § 1-301 — party choice of law, subject to the reasonable-relation test

Current UCC § 1-301 ("Territorial Applicability; Parties' Power to Choose
Applicable Law") lets contracting parties designate which state's or
nation's law governs their transaction — but only where the transaction
**"bears a reasonable relation"** to the chosen jurisdiction. Where the
parties haven't validly chosen, § 1-301(b) falls back to the law selected
by the forum state's own conflict-of-laws principles.
([Cornell LII — UCC § 1-301](https://www.law.cornell.edu/ucc/1/1-301))

Virginia has enacted this provision as **§ 8.1A-301** — real, current, and
verified directly against the Commonwealth's own official code site — with
materially the same structure: a reasonable-relation-gated party-choice rule
in subsection (b), and a fallback to Virginia's own conflict-of-laws
principles in subsection (c) where the parties made no effective choice.
([Code of Virginia — § 8.1A-301](https://law.lis.virginia.gov/vacode/title8.1A/chapter3/section8.1A-301/))
**Not ingested** — Article 1 has zero ingested sections in Law Engine today
(`docs/ucc-orientation.md`'s own provenance table), so this citation is
real and verifiable but not yet backed by `services/retrieval.get_section()`.

### 3.2 Common-law fallback — Restatement (Second) of Conflict of Laws § 188

Where no UCC choice-of-law provision resolves the question at all (e.g. the
forum's own conflict-of-laws principles have to be applied under § 1-301(b)/(c)
above, or the dispute falls outside the UCC's scope entirely), the general
common-law doctrine most U.S. courts apply for contracts is the
**"most significant relationship"** test: the rights and duties on a given
contract issue are governed by the law of the state that, as to *that
issue*, has the most significant relationship to the transaction and the
parties — weighing the place of contracting, place of negotiation, place of
performance, location of the subject matter, and the parties' domicile/
residence/place of business.
([Restatement (Second) of Conflict of Laws § 188](https://advance.lexis.com/open/document/openwebdocview/-188-Law-Governing-in-Absence-of-Effective-Choice-by-the-Parties/?pdmfid=1000522&pddocfullpath=%2Fshared%2Fdocument%2Fanalytical-materials%2Furn%3AcontentItem%3A42GD-2R40-00YG-K07C-00000-00&pdcomponentid=12222))

**The structural point for Law Engine:** "which state's enacted UCC text
governs" is never something the engine may answer by defaulting to
whichever state happens to be ingested. It is a real, fact-dependent legal
determination — party choice first (§ 1-301, reasonable-relation-gated),
then a forum-specific conflict-of-laws analysis if the parties didn't
choose. Both steps require knowing the forum, which is itself a fact not
inferable from the transaction alone.

## 4. Article-specific conflict-of-laws rules can override the general rule

§ 1-301 itself already discloses that it is not the last word for every
Article. § 1-301(c) explicitly carves out a list of provisions — including
**"Sections 9-301 through 9-307"** — where, "[t]o the extent that [the UCC]
governs a transaction, if one of the [listed] provisions... specifies the
applicable law, that provision governs and a contrary agreement is
effective only to the extent permitted by the law so specified."
([Cornell LII — UCC § 1-301](https://www.law.cornell.edu/ucc/1/1-301);
confirmed against Virginia's own enactment,
[Code of Virginia — § 8.1A-301](https://law.lis.virginia.gov/vacode/title8.1A/chapter3/section8.1A-301/))
Virginia's enactment lists the same exception category (perfection of
security interests) among § 8.1A-301's own carve-outs.

### Worked example: Article 9's debtor-location rule (§ 9-301)

Article 9's own choice-of-law rule is a real, concrete illustration of just
how different an Article-specific rule can be from the general party-choice
rule: **§ 9-301** provides that, as a general matter, **the local law of the
jurisdiction where the debtor is located** governs perfection, the effect
of perfection or nonperfection, and priority of a security interest —
regardless of what the parties' contract says and regardless of where the
collateral itself is physically located, with narrower exceptions for
possessory security interests and a few specific collateral types (goods
covered by a certificate of title, as-extracted collateral tied to the
wellhead/minehead, etc.).
([Cornell LII — UCC § 9-301](https://www.law.cornell.edu/ucc/9/9-301))
"Debtor location" is itself a defined, rule-driven concept under § 9-307 —
an individual debtor's principal residence; an entity's chief executive
office if it has more than one place of business, or its place of
registration for a registered organization.
([Justia — NY UCC § 9-307, Location of Debtor](https://law.justia.com/codes/new-york/2015/ucc/article-9/part-3/sub-part-1/9-307/))

This is not a party-choice rule at all — it is a fixed, status-based rule
Article 9 deliberately substitutes for § 1-301's reasonable-relation/
party-choice framework, precisely because secured-lending priority needs a
single, predictable answer that competing creditors and searchers can rely
on without having to litigate reasonableness. **Neither of these
provisions — § 8.1A-301 (general choice of law) nor § 8.9A-301 (Article 9's
own choice-of-law rule) — is ingested in Law Engine today.** Article 9's own
13 ingested sections (`services/ingestion_article9.py`) cover attachment,
perfection, priority, and default, but not Part 3's choice-of-law
subpart (§§ 8.9A-301–307).

**The structural point for Law Engine:** a future multi-jurisdiction engine
cannot treat "which state's law governs" as a single, Article-1-level
question answered once per transaction. It must ask the question per
Article where a more specific Article displaces the general rule — Article 9
is the clearest, best-documented example, but § 1-301(c)'s own carve-out
list names several others (Article 2A leases, Article 4 bank deposits,
Article 4A funds transfers, Article 5 letters of credit, Article 6 bulk
sales, Article 8 investment securities) that a future implementation would
need to check individually rather than assuming Article 9 is the only
exception.

## 5. International sales — CISG as a separate regime, not another Article

For a qualifying international sale of goods, the governing law question
can bypass this entire UCC hierarchy altogether. The United Nations
Convention on Contracts for the International Sale of Goods (CISG) is a
**treaty**, not a state statute — `services/models.py`'s `AuthorityType.TREATY`
already anticipates this — and where it applies, it applies as
self-executing federal law that displaces the otherwise-applicable state's
UCC Article 2 under the Supremacy Clause, on a contract-by-contract basis
(not a blanket exemption from state commercial law). This is already fully
researched and schema-designed in `docs/cisg-architecture-design.md`,
including the real `CisgApplicabilityAssessment` dataclass already present
in `services/models.py` §Mission-12 scope (`transaction_id`,
`both_in_contracting_states`, `forum_is_article_95_declarant`,
`parties_opted_out_under_article_6`, `scope: TransactionScope`, etc.).

**This document is consistent with, not a replacement for, that existing
design.** The relationship between the two:

- This document's §§1–4 describe the hierarchy *within* U.S. domestic UCC
  law (Model → Enactment → choice of which enactment governs → Article-
  specific overrides of that choice).
- `docs/cisg-architecture-design.md` describes the separate, prior
  threshold question — *does CISG apply to this transaction at all,
  displacing the domestic UCC analysis entirely* — that has to be asked
  and answered **before** this document's §§1–4 even become relevant to an
  international sale of goods. `TransactionScope.INTERNATIONAL_CISG` /
  `INTERNATIONAL_NON_CISG` / `DOMESTIC_UCC` in `services/models.py` already
  encodes exactly this branch point.
- Neither document proposes merging CISG into the Article numbering as if
  it were "UCC Article 2, international edition." CISG's applicability
  test (places of business in different Contracting States, no Article 6
  opt-out, no Article 2 exclusion) is structurally unrelated to which
  *state's* UCC enactment would otherwise govern, and a future
  `services/cisg.py` module (proposed, not built) should stay a distinct
  module from any future multi-jurisdiction UCC choice-of-law module this
  document anticipates.

## What this unlocks — not yet built

This document captures a decision/direction only. No multi-jurisdiction
engine, no choice-of-law analysis code, and no second-state ingestion has
been built or started yet. Concretely, this note is meant to make the
following buildable in the future without re-deriving the reasoning
above:

- A future `ChoiceOfLawAssessment` dataclass (analogous in spirit to the
  existing `CisgApplicabilityAssessment`) modeling the § 1-301 reasonable-
  relation/party-choice analysis and the forum's own conflict-of-laws
  fallback, for a domestic interstate UCC transaction.
- A future second-state ingestion (a state other than Virginia), which
  would be the first real test of whether `ProvisionComparison` in
  `services/models.py` (currently unused with real data, since only one
  jurisdiction's enactment exists) actually works as designed for cross-
  jurisdiction section comparison.
- A future Article-9-specific conflicts module implementing §§ 8.9A-301–307
  (debtor-location perfection/priority rules), separate from any general
  § 8.1A-301 choice-of-law module, following this document's §4 finding
  that Article 9 cannot reuse the general Article 1 rule.
- A per-Article audit of which other Articles named in § 1-301(c)'s
  carve-out list (2A, 4, 4A, 5, 6, 8) have their own choice-of-law
  provisions that would need the same Article-specific treatment as
  Article 9 before a general-purpose choice-of-law engine could be called
  complete.

## Sources consulted

- [Cornell LII — UCC § 1-301 (Territorial Applicability; Parties' Power to Choose Applicable Law)](https://www.law.cornell.edu/ucc/1/1-301)
- [Code of Virginia — § 8.1A-301, Territorial applicability; parties' power to choose applicable law](https://law.lis.virginia.gov/vacode/title8.1A/chapter3/section8.1A-301/)
- [Cornell LII — UCC § 9-301 (Law Governing Perfection and Priority of Security Interests and Agricultural Liens)](https://www.law.cornell.edu/ucc/9/9-301)
- [Justia — 2015 New York UCC § 9-307, Location of Debtor](https://law.justia.com/codes/new-york/2015/ucc/article-9/part-3/sub-part-1/9-307/)
- [Restatement (Second) of Conflict of Laws § 188, Law Governing in Absence of Effective Choice by the Parties](https://advance.lexis.com/open/document/openwebdocview/-188-Law-Governing-in-Absence-of-Effective-Choice-by-the-Parties/?pdmfid=1000522&pddocfullpath=%2Fshared%2Fdocument%2Fanalytical-materials%2Furn%3AcontentItem%3A42GD-2R40-00YG-K07C-00000-00&pdcomponentid=12222)
- `law-engine/docs/ucc-source-licensing-audit.md` (internal, this repository — Model/Enactment licensing distinction, reused not re-derived)
- `law-engine/docs/cisg-architecture-design.md` (internal, this repository — CISG-as-separate-regime design, reused not re-derived)
- `law-engine/docs/ucc-orientation.md` (internal, this repository — Model/Enactment/Interpretation narrative and current ingestion-coverage facts)
- `law-engine/services/models.py` (internal, this repository, read-only — `SourceLayer`, `AuthorityType`, `CisgApplicabilityAssessment`, `TransactionScope` enums/dataclasses referenced above)
- `law-engine/services/ucc_orientation.py`, `law-engine/services/ingestion_article9.py` (internal, this repository, read-only — real ingested-coverage facts)

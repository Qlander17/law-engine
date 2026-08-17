# CISG Applicability-Analysis — Architecture Design Proposal

This document is **design-only** — it proposes what a future
`services/cisg.py` module could look like, in the same dataclass/`Enum`
style already established by `services/models.py`. No `.py` file has been
written or edited to implement it; a future implementation pass would
need to actually build it, decide where it plugs into
ingestion/verification, and write real tests.

## 1. What CISG is, and why it's architecturally different from the UCC work already done

The **United Nations Convention on Contracts for the International Sale of
Goods (CISG)**, done at Vienna on 11 April 1980, is a **treaty**, not a
statute — its `AuthorityType` in the existing model is already `TREATY`,
which the codebase's `models.py` enum already anticipates. Its official text
is maintained by **UNCITRAL** (the UN Commission on International Trade Law)
at
[uncitral.un.org — CISG text page](https://uncitral.un.org/en/texts/salegoods/conventions/sale_of_goods/cisg),
with a companion live ratification-status page at
[uncitral.un.org — CISG status page](https://uncitral.un.org/en/texts/salegoods/conventions/sale_of_goods/cisg/status).
As of the most recent check, **97 states** are Contracting States,
with Saudi Arabia (acceded 2023, in force 2024) and Rwanda (acceded 2023, in
force 2024) among the most recent accessions. UNCITRAL also publishes the
*travaux préparatoires* and an Official Records volume (UN Sales No.
E.81.IV.3), and notes that the UNCITRAL Secretariat's 1978 Commentary on the
Draft Convention remains the closest thing to an official commentary (it was
written before the 1980 diplomatic conference finalized the text, so it is
not a comment on the final Article numbering in every case).

UN treaty texts are UN copyright material but UNCITRAL makes the convention
text itself freely available for reading/reference on its own site; unlike
the ALI/ULC UCC situation (see the companion `ucc-source-licensing-audit.md`),
there is no state-enactment layer to source from instead — the treaty text
*is* the primary legal text, applied directly (in the U.S., as **self-
executing federal law** with Supremacy Clause force — see §5). A future
ingestion module should link/cite the UNCITRAL text page as
`official_source_url` rather than treat any secondary CISG compilation
(Pace/Cornell mirrors, however useful for research) as the source of record.

The reason CISG needs its **own module** rather than reusing the UCC
`StatuteSection` pipeline is that CISG raises a **threshold applicability
question that Article 2 of the UCC never has to ask**: *does this body of law
even apply to this transaction at all?* That determination has several
independent, real legal sub-questions, each with its own governing Article,
detailed below. A `services/cisg.py` module's core job is answering that
threshold question — not (at this stage) modeling CISG's substantive
sale-of-goods rules the way `StatuteSection` models UCC Article 2's rules.

## 2. The applicability question, decomposed

Real, CISG-specific questions a system must answer, each keyed to its own
Article:

### 2.1 Places of business in Contracting States — Article 1(1)(a)

CISG applies to contracts of sale of goods between parties whose **places of
business** are in different states, when those states are both Contracting
States. "Place of business" is not self-evident — Article 10 supplies the
test: where a party has more than one place of business, it's the one with
the **closest relationship to the contract and its performance**, judged by
circumstances known to or contemplated by both parties at or before
contract formation; where a party has no place of business, its **habitual
residence** substitutes. Liaison/representative offices count as places of
business.
([Article 10 case-law digest, Pace/CISG](https://www.cisg.law.pace.edu/cisg/text/digest-2012-10.html))

### 2.2 Private-international-law route — Article 1(1)(b), and the U.S. Article 95 reservation

Independent of 1(1)(a), CISG also applies where the rules of **private
international law** (conflict-of-laws rules) lead to the law of a Contracting
State — even if one or both parties' places of business are not themselves
in Contracting States. **Article 95** lets a state declare, at ratification,
that it will not be bound by 1(1)(b). The **United States made exactly that
declaration** (effective with U.S. ratification, in force 1 January 1988,
following ratification deposited 11 December 1986) — so U.S. courts apply
CISG **only** via 1(1)(a) (both parties' places of business in different
Contracting States), never via the conflict-of-laws route of 1(1)(b). Other
Article 95 declarants include (per the most recent check) Armenia, China,
Laos, Singapore, St. Vincent & the Grenadines, and Slovakia.
([CISG Advisory Council Opinion No. 15, on Art. 1(1)(b)/95](https://cisgac.com/opinions/cisgac-opinion-no-15/);
[2012 UNCITRAL Digest of Article 95 case law](https://www.cisg.law.pace.edu/cisg/text/digest-2012-95.html))

This is a real, jurisdiction-dependent fact a system must model per forum —
a French court and a U.S. court can reach different applicability
conclusions on the *identical* contract, because France did not make an
Article 95 declaration and the U.S. did.

### 2.3 Party opt-out — Article 6

Article 6 lets the parties **exclude** CISG application (party autonomy),
either wholly or by varying/derogating from most individual provisions.
Courts overwhelmingly hold that a **generic choice-of-law clause** (e.g.,
"this contract is governed by the laws of [U.S. state]") does **not**, by
itself, exclude CISG — because CISG is itself part of that state's law
(via Supremacy Clause incorporation, in the U.S. case) and continues to
govern unless the exclusion is *explicit*. Courts require real, affirmative
evidence of intent to exclude CISG specifically (e.g., "the UCC, and not the
CISG, shall govern," or "this contract is governed by the [domestic
non-uniform sales law of State X], to the exclusion of the CISG").
([CISG Advisory Council Opinion No. 16, Exclusion of the CISG under Art.
6](https://cisg-online.org/files/ac_op/CISG_Advisory_Council_Opinion_No_16.pdf);
[Transnational Litigation Blog — CISG Opt-Outs and Ascertaining Party
Intent](https://tlblog.org/cisg-opt-outs-and-ascertaining-party-intent-a-back-to-basics-perspective/))

### 2.4 Domestic vs. international transaction

CISG's whole premise (Article 1) is an **international** sale — parties with
places of business in *different* states. A transaction between two parties
whose places of business are both in the same country is, by definition,
domestic and governed by that country's own domestic sales law (in the U.S.,
UCC Article 2 as enacted by the relevant state) — CISG's applicability
analysis never even reaches Article 6 opt-out or Article 2 exclusions for a
purely domestic sale, because the threshold test in 2.1 already fails. This
should be the *first* gate a module checks, before evaluating opt-out or
subject-matter exclusions.

### 2.5 Article 2 subject-matter exclusions

Article 2 excludes several transaction types from CISG entirely, regardless
of the parties' locations:

- **Consumer goods** — goods bought for personal, family, or household use,
  **unless** the seller neither knew nor ought to have known the goods were
  bought for such use (i.e., not a flat exclusion — it turns on the seller's
  actual/constructive knowledge of the buyer's purpose).
- **Auctions** — sales by auction.
- **Execution/authority-of-law sales** — sales on execution or otherwise by
  authority of law (e.g., judicial/sheriff's sales).
- **Stocks, shares, investment securities, negotiable instruments, or
  money.**
- **Ships, vessels, hovercraft, or aircraft** — all of them, not just
  registrable ones, specifically to avoid line-drawing disputes over which
  vessels/aircraft would otherwise qualify.
- **Electricity** — excluded because many legal systems do not treat
  electricity as "goods" at all.

([CISG Article 2 — annotated text, Pace/CISG](https://www.cisg.law.pace.edu/cisg/text/anno-art-02.html);
[UNCITRAL Secretariat Commentary, Guide to CISG Article
2](https://cisgw3.law.pace.edu/cisg/text/secomm/secomm-02.html))

### 2.6 Interaction with domestic UCC Article 2 — not automatic supersession as a *general* matter, but real Supremacy Clause displacement when CISG applies

Two distinct claims need to be kept separate, since sources vary in
precision on this point:

1. When CISG **does** apply to a given contract (per §§2.1–2.5), it applies
   **as self-executing federal law**, and under the Supremacy Clause
   (U.S. Const. art. VI, cl. 2) it takes precedence over the otherwise-
   applicable state's UCC Article 2 — including displacing a contractual
   reference to "the laws of [state]" per the Article 6 analysis in §2.3,
   since CISG is deemed already incorporated into that state's law rather
   than something the parties chose *instead of* it.
   ([Gonzalo Law — When Will the CISG Take Precedence Over the
   UCC?](https://gonzalolaw.com/when-will-the-cisg-take-precedence-over-the-ucc/);
   [Pace/IICL — Attorney's Guide: Comparison Chart, UCC and
   CISG](https://iicl.law.pace.edu/sites/default/files/bibliography/ucc-cisg_1.pdf))
2. CISG does **not** "supersede" UCC Article 2 in general — it only
   *displaces* it for the specific contracts that independently satisfy the
   Article 1 applicability test and are not excluded under Article 2 or
   opted out under Article 6. Every domestic U.S. sale-of-goods contract
   remains governed by UCC Article 2 as always; CISG's supremacy is
   contract-by-contract, not a blanket amendment to state commercial law.
   This is exactly why a real applicability-analysis module is needed rather
   than a flag — the answer is per-transaction, not per-jurisdiction.

## 3. Proposed schema (design only — no `.py` file written)

Proposed for a future `services/cisg.py`, following `services/models.py`'s
existing `Enum` + frozen-ish `@dataclass` conventions (`str, Enum` subclasses,
`to_dict()` methods, no I/O in the model module itself — I/O would live in a
future `cisg_ingestion.py` or similar, mirroring `ingestion.py`'s separation
from `models.py`).

```python
# PROPOSED -- not implemented. Illustrative only.

class ContractingStateStatus(str, Enum):
    """Whether a given state is a CISG Contracting State as of the
    analysis date -- checked against the live UNCITRAL status page, never
    hard-coded as permanently true, since accessions are ongoing (e.g.,
    Saudi Arabia and Rwanda both acceded in 2023)."""

    CONTRACTING_STATE = "CONTRACTING_STATE"
    NOT_CONTRACTING_STATE = "NOT_CONTRACTING_STATE"
    STATUS_UNCHECKED = "STATUS_UNCHECKED"


class Article95Declarant(str, Enum):
    """Whether a Contracting State made the Article 95 declaration
    disclaiming Article 1(1)(b) (the private-international-law route).
    The United States is YES; most Contracting States are NO."""

    DECLARED = "DECLARED"          # e.g., United States, China, Singapore
    NOT_DECLARED = "NOT_DECLARED"  # e.g., France, Germany
    UNKNOWN = "UNKNOWN"


class ExclusionCategory(str, Enum):
    """Article 2's closed list of excluded transaction types. NONE means
    no Article 2 exclusion was found to apply -- it is not itself a
    finding that CISG applies, only that this particular gate passed."""

    NONE = "NONE"
    CONSUMER_GOODS = "CONSUMER_GOODS"                # Art. 2(a)
    AUCTION = "AUCTION"                               # Art. 2(b)
    EXECUTION_OR_AUTHORITY_OF_LAW = "EXECUTION_OR_AUTHORITY_OF_LAW"  # Art. 2(c)
    STOCKS_SECURITIES_NEGOTIABLE_INSTRUMENTS_MONEY = (
        "STOCKS_SECURITIES_NEGOTIABLE_INSTRUMENTS_MONEY"
    )                                                  # Art. 2(d)
    SHIPS_VESSELS_HOVERCRAFT_AIRCRAFT = "SHIPS_VESSELS_HOVERCRAFT_AIRCRAFT"  # Art. 2(e)
    ELECTRICITY = "ELECTRICITY"                       # Art. 2(f)


class OptOutFinding(str, Enum):
    """Article 6 exclusion analysis result -- deliberately not a bare
    boolean, mirroring VerificationStatus's refusal to collapse nuance.
    Courts require *explicit* intent (CISG-AC Opinion No. 16); a generic
    choice-of-law clause naming a U.S. state is NOT, by itself, an
    exclusion."""

    NO_OPT_OUT_FOUND = "NO_OPT_OUT_FOUND"
    EXPLICIT_OPT_OUT = "EXPLICIT_OPT_OUT"              # e.g., "CISG shall not apply"
    GENERIC_CHOICE_OF_LAW_ONLY = "GENERIC_CHOICE_OF_LAW_ONLY"  # insufficient per majority rule
    AMBIGUOUS = "AMBIGUOUS"                            # needs case-by-case intent analysis


@dataclass
class PartyPlaceOfBusiness:
    """One party's Article 10 place-of-business determination. Kept
    separate from a generic 'address' field because Article 10's test
    (closest relationship to contract/performance; habitual residence if
    no place of business) is a legal determination, not a mailing fact."""

    party_role: str  # "seller" | "buyer"
    country: str
    contracting_state_status: ContractingStateStatus
    multiple_places_of_business: bool = False
    closest_relationship_place: str | None = None  # Art. 10 tiebreak, if needed
    notes: str = ""


@dataclass
class CisgApplicabilityAnalysis:
    """One real, provenance-tracked applicability determination for one
    contract. Mirrors SourceManifest's spirit: never silently presents an
    inferred/likely applicability conclusion as settled. Every boolean-
    shaped legal question here is deliberately an Enum, not a bool, for
    the same reason ConfidenceLabel exists in models.py."""

    analysis_id: str
    seller: PartyPlaceOfBusiness
    buyer: PartyPlaceOfBusiness
    forum_state: str  # jurisdiction whose court/analysis this determination is for
    forum_article_95_declarant: Article95Declarant
    is_international_transaction: bool  # Art. 1 threshold: different states?
    exclusion_category: ExclusionCategory
    exclusion_notes: str = ""  # e.g., seller's actual/constructive knowledge for consumer-goods exclusion
    opt_out_finding: OptOutFinding = OptOutFinding.NO_OPT_OUT_FOUND
    opt_out_contract_clause_text: str | None = None
    applicability_conclusion: str = "UNDETERMINED"  # "APPLIES" | "DOES_NOT_APPLY" | "UNDETERMINED"
    conclusion_confidence: str = "UNVERIFIED"  # reuse models.ConfidenceLabel values
    analysis_timestamp: str = ""
    analyst_notes: str = ""

    def to_dict(self) -> dict:
        ...  # mirrors SourceManifest.to_dict()'s explicit-field pattern
```

Design notes, not prescriptions for a future implementer to treat as final:

- **`applicability_conclusion` and `conclusion_confidence` deliberately reuse
  the `models.py` philosophy** (see `ConfidenceLabel`: `LIKELY`, `VERIFIED`,
  `UNVERIFIED`, `CONFLICTING`) rather than inventing a parallel confidence
  system — a future `cisg.py` should probably import `ConfidenceLabel`
  directly from `services.models` rather than redefine it.
  `VerificationStatus` and `AuthorityType` from `models.py` should likewise
  be reused as-is for any `SourceManifest` built around the CISG treaty text
  itself (`authority_type=AuthorityType.TREATY`, already present in the
  existing enum — no change needed there).
- **`forum_state` and `forum_article_95_declarant` are separated from the
  parties' own countries** deliberately — because the Article 1(1)(b)
  analysis depends on *which court* (which forum's conflict-of-laws rules)
  is doing the analysis, not on where the parties are. A U.S. court and a
  German court could reach different applicability conclusions on an
  otherwise-identical fact pattern.
- **`ExclusionCategory.NONE` is a real finding, not an absence of one** — it
  records that the Article 2 exclusion gate was actually checked, matching
  this project's stated Mission 12 principle that "trust but verify" states
  should be explicit rather than assumed by omission.
- This schema intentionally stops at the *applicability* question. It does
  not attempt to model CISG's substantive rules (formation under Part II,
  obligations under Part III) — that would be a materially larger, separate
  design effort, out of scope for this audit per the task's own framing
  ("schema/architecture-level research — no full curriculum needed").

## 4. Where this would plug into the existing pipeline

If implemented, the natural analogue to `ingestion.py`'s pattern would be a
`cisg_ingestion.py` that:

1. Builds a `SourceManifest` for the CISG treaty text itself
   (`document_id="cisg-1980"`, `authority_type=AuthorityType.TREATY`,
   `jurisdiction="International (UNCITRAL)"`,
   `official_source_url="https://uncitral.un.org/en/texts/salegoods/conventions/sale_of_goods/cisg"`,
   `licensing_status` following the conventions proposed in the companion
   `ucc-source-licensing-audit.md` — likely a new prefix such as `"UN
   treaty text -- freely available via UNCITRAL, cite official source"`,
   since neither the "public domain state edict" nor the "ALI/ULC
   copyrighted" categories cleanly apply to a UN convention text).
2. Separately ingests the **live ratification-status data** (Contracting
   States, Article 95 declarants) from the UNCITRAL status page as its own,
   explicitly-dated `SourceManifest`, since that data changes over time
   (two accessions in 2023 alone) and must never be treated as a static fact
   baked into code without a retrieval timestamp.
3. Leaves `CisgApplicabilityAnalysis` records as a downstream, per-contract
   analysis artifact — not something ingested from a source document at all,
   but something a future analysis engine *produces*, referencing the treaty
   `SourceManifest` by `document_id` the same way `StatuteSection` references
   its `source_document_id`.

## Sources consulted

- [UNCITRAL — CISG text page (official)](https://uncitral.un.org/en/texts/salegoods/conventions/sale_of_goods/cisg)
- [UNCITRAL — CISG status page (Contracting States, declarations)](https://uncitral.un.org/en/texts/salegoods/conventions/sale_of_goods/cisg/status)
- [CISG Advisory Council Opinion No. 15 — Article 1(1)(b) / Article 95](https://cisgac.com/opinions/cisgac-opinion-no-15/)
- [CISG Advisory Council Opinion No. 16 — Exclusion of the CISG under Article 6](https://cisg-online.org/files/ac_op/CISG_Advisory_Council_Opinion_No_16.pdf)
- [2012 UNCITRAL Digest of Article 95 case law (Pace/CISG mirror)](https://www.cisg.law.pace.edu/cisg/text/digest-2012-95.html)
- [2012 UNCITRAL Digest of Article 10 case law (Pace/CISG mirror)](https://www.cisg.law.pace.edu/cisg/text/digest-2012-10.html)
- [CISG Article 2 — annotated text (Pace/CISG mirror)](https://www.cisg.law.pace.edu/cisg/text/anno-art-02.html)
- [UNCITRAL Secretariat Commentary — Guide to CISG Article 2](https://cisgw3.law.pace.edu/cisg/text/secomm/secomm-02.html)
- [Transnational Litigation Blog — CISG Opt-Outs and Ascertaining Party Intent: A Back-to-Basics Perspective](https://tlblog.org/cisg-opt-outs-and-ascertaining-party-intent-a-back-to-basics-perspective/)
- [Gonzalo Law — When Will the CISG Take Precedence Over the UCC?](https://gonzalolaw.com/when-will-the-cisg-take-precedence-over-the-ucc/)
- [Pace/IICL — Attorney's Guide: Comparison Chart, UCC and CISG (PDF)](https://iicl.law.pace.edu/sites/default/files/bibliography/ucc-cisg_1.pdf)
- `law-engine/services/models.py` (internal, this repository — reused enum/dataclass conventions)

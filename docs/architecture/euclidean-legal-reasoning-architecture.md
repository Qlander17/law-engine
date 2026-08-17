# Euclidean Legal Reasoning Architecture — Design Note

Working name "Euclidean" (proof-construction discipline, not a claim that law is actually axiomatic in the mathematical sense — see Non-Goals). This document originated as a design proposal; the Legal Proof Graph it describes is now implemented — see `services/legal_proof_graph.py` and `services/test_legal_proof_graph.py`. The design rationale below is unchanged and still describes the real, current implementation.

## Objective

Every real conclusion this system states must be **traceable backward** through a disciplined chain, the same way a geometric proof traces backward to its postulates:

```
DEFINITION -> AXIOM / ACCEPTED PREMISE -> GOVERNING AUTHORITY -> VERIFIED FACT -> INTERMEDIATE PROPOSITION -> CONCLUSION
```

A conclusion with a missing link in this chain is not a conclusion this system is allowed to assert with confidence — it is, at most, a `ConfidenceLabel.LIKELY` or `ConfidenceLabel.UNVERIFIED` hypothesis pending the missing link, using the same real enum `services/models.py` already defines rather than inventing a parallel severity scale. This reuses the same discipline `banking-mortgage-research-plan.md` already applied by hand (Part 2's "leaning X, but formally `UNRESOLVED / INSUFFICIENT EVIDENCE`" pattern) — this design's job is to make that discipline a structural property of the data model, not something a human has to remember to apply every time.

This is a **Law Engine-level** reasoning architecture, in the same relationship to Law Engine that `ghostos-mastery-engine-design.md` describes for the Mastery Engine's relationship to GhostOS: it sits *underneath* the pedagogical layer (`PedagogicalContract`, `TransactionLifecycle`), not beside it. A `LifecycleStage`'s `explanation` field is currently free text with a `citation` attached; this design proposes what a `LifecycleStage.explanation` would need to look like if it had to actually show its work.

## Reuse of the existing vocabulary (no parallel system)

Per the source discipline `services/models.py` already establishes, this design introduces **no new trust-labeling enums**. Every proof-chain node below carries the same fields a real ingested source already carries:

- `VerificationStatus` (`services/models.py:15-28`) — a Verified Fact's own epistemic state (`SOURCE_VERIFIED`, `CROSS_VERIFIED`, `TRUSTED_FOR_ANALYSIS`, `CONFLICT`, etc.).
- `ConfidenceLabel` (`services/models.py:31-40`) — the caller-facing label a Conclusion is required to carry; a Conclusion resting on any node below `TRUSTED_FOR_ANALYSIS` cannot claim `ConfidenceLabel.VERIFIED`.
- `SourceLayer` (`services/models.py:43-53`) — whether a Governing Authority node is MODEL, ENACTMENT, or INTERPRETATION text; a proof mixing layers without saying so is exactly the failure mode `SourceLayer` already exists to block.
- `AuthorityType` (`services/models.py:56-70`) — what *kind* of authority a Governing Authority node is; a `CLAIM_ALTERNATIVE_THEORY` (e.g. a "vapor money" theory, per `banking-mortgage-research-plan.md` Part 1.4) can populate a proof graph node honestly without ever being confused for a `STATUTE`-grade premise.

The only genuinely new concept this design adds is the **shape of the chain itself** — the six node kinds, their required edges, and the graph structure that stores them (`## The Legal Proof Graph` below). Everything else is composition of what already exists.

## The reasoning chain, node by node

### 1. DEFINITION

What does a material term actually mean, and where did that meaning come from? A term used loosely across a proof is exactly how the "shared classification does not imply equivalence" failure (below) gets smuggled in.

A Definition node must declare its **source** as one of three real kinds, matching how legal terms actually get their meaning:

- `STATUTORY` — a definition fixed by an actual enacted provision (e.g. `services/models.py`'s own `StatuteSection.defined_terms`, populated in `services/ingestion_article9.py:78,94-99` by regex extraction from real § 8.9A-102 text — not invented, not paraphrased).
- `CONTRACTUAL` — a definition fixed by the parties' own agreement (a defined term in a specific contract, binding only between those parties, and only for that document).
- `ORDINARY_LANGUAGE` — the term's plain meaning absent a controlling statutory or contractual definition — the weakest of the three, and the one most likely to silently drift between two different senses across a proof without either party noticing.

Two terms that look identical on the page can carry different Definition nodes depending on *which* body of law is asking. § 8.9A-102(47) defines `"Instrument"` for Article 9 purposes; that definition explicitly incorporates-by-reference `"Negotiable instrument" § 8.3A-104` — a different title's different definition, serving a different purpose. A proof that quietly uses "instrument" to mean the same thing in both places without checking is exactly the drift a Definition node's `source` field exists to catch (worked example below).

### 2. AXIOM / ACCEPTED PREMISE

A proposition the proof takes as given without independently proving it here — either because it is a genuinely foundational legal principle (contract requires offer, acceptance, and consideration), or because it is a premise the current proof *accepts arguendo* for scope reasons (e.g. "assume for this analysis that the parties are both merchants") without asserting it as an independently verified fact of the actual case. These two are structurally different and must never be conflated: an Axiom is a background legal principle; an Accepted Premise is a scoping assumption the proof is explicit about making. Collapsing them is how a conclusion ends up silently resting on an assumption dressed up as settled law.

### 3. GOVERNING AUTHORITY

What actual authority supports the proposition being asserted — reusing `AuthorityType` directly (`CONSTITUTION`, `STATUTE`, `REGULATION`, `COURT_RULE`, `CASE`, `TREATY`, `TREATISE`, `SECONDARY_AUTHORITY`, `CLAIM_ALTERNATIVE_THEORY`) and `SourceLayer` (`MODEL`/`ENACTMENT`/`INTERPRETATION`) to say which layer it belongs to. A Governing Authority node with `authority_type=STATUTE` but `source_layer=MODEL` (e.g. an LII-published uniform-text section, per `banking-mortgage-research-plan.md`'s own caveat at Part 1.2's third bullet) is not the same weight of authority as one enacted by a specific jurisdiction (`source_layer=ENACTMENT`) — the proof graph must carry that distinction on the node itself, not bury it in prose.

### 4. VERIFIED FACT

What facts must actually be true for the Governing Authority's rule to apply, and what is each fact's real status: **known** (established in the record), **assumed** (an Accepted Premise standing in for it), or **disputed** (contested, with the dispute itself recorded rather than silently resolved one way). A Verified Fact node reuses `VerificationStatus` for exactly this: a fact stuck at `DISCOVERED` or `RETRIEVED` cannot support a Conclusion claiming `ConfidenceLabel.VERIFIED`, regardless of how confident the surrounding prose sounds — this is the same discipline `banking-mortgage-research-plan.md` Part 2 already applied by hand to all seven claims it evaluated.

### 5. INTERMEDIATE PROPOSITION

A conclusion that is itself only a step toward the final Conclusion — the load-bearing intermediate rungs a real legal argument actually has (e.g. "the seller is a merchant" as a rung on the way to "an implied warranty of merchantability attached"). Modeling these explicitly, rather than jumping straight from facts to the final Conclusion, is what makes "does the conclusion actually follow from the premises" (below) a checkable question instead of a rhetorical one — each rung either has real support or it doesn't, and a missing rung is visible as a real gap in the graph rather than an invisible leap in prose.

### 6. CONCLUSION

The final asserted proposition, required to carry a `ConfidenceLabel` computed from — not merely accompanying — the weakest node anywhere in its backward chain. A Conclusion resting on one `UNVERIFIED` Verified Fact is `UNVERIFIED`, full stop, even if every other node in the chain is `TRUSTED_FOR_ANALYSIS`. This is the same "never presented as more certain than this" principle `ConfidenceLabel`'s own docstring already states (`services/models.py:31-40`) — this design's contribution is making the *computation* explicit (weakest-link, not average, not most-recent) rather than leaving it to whoever writes the Conclusion's prose to remember.

## Four checkable questions the chain must be able to answer

These map directly onto the reasoning-chain nodes above — they are not a separate framework, they are what a caller actually asks the graph.

### A. What does each material term mean?

Walk every Definition node touched by the proof and report its `source` (`STATUTORY` / `CONTRACTUAL` / `ORDINARY_LANGUAGE`). If the same term string appears with two different Definition nodes across the proof, that is flagged, not silently merged — see the "adverse argument" checks below.

### B. What proposition is being asserted, on what authority, and what facts does it require?

For a given Intermediate Proposition or Conclusion node: which Governing Authority node(s) support it, which Verified Fact node(s) does the authority's rule require, and for each required fact — known, assumed, or disputed. § 8.9A-203(b)'s attachment test is a clean real example already in the ingested text: a security interest is enforceable only if (1) value has been given, (2) the debtor has rights in the collateral, and (3) an authenticated security agreement (or equivalent) exists — three Verified Fact nodes, each independently markable known/assumed/disputed, feeding one Intermediate Proposition ("the security interest has attached").

### C. Does the conclusion actually follow? Is there an unstated premise? Is it broader than the premises support?

This is a **structural validity check** on the graph, not a semantic one — the design does not claim the system can independently verify legal reasoning is *correct* the way a theorem prover verifies a proof (see Non-Goals). What it can check mechanically:

- Every edge from a Conclusion or Intermediate Proposition node actually resolves to a real node in the graph (no proposition citing a fact or authority that isn't itself represented) — an **unstated premise** is exactly a proposition with a required-but-missing incoming edge, and the graph can surface that as a structural gap rather than a substantive judgment.
- The Conclusion's asserted scope does not exceed the union of what its Intermediate Propositions actually established — e.g. a Conclusion phrased about "assignments" in general, resting only on Intermediate Propositions about one specific, documented defect in one specific assignment, is broader than its premises support. `banking-mortgage-research-plan.md` Part 2's claim 6 read (Culhane/Yvanova allow standing to challenge a *specific* void assignment; the broader "securitization alone defeats enforceability" theory is not supported the same way) is a real example of exactly this scope-mismatch the graph should be able to flag mechanically: the Conclusion's stated scope vs. the union of its Intermediate Propositions' actual scope.

### D. What exception defeats the proposition? What if it's negated? Does the argument contradict itself?

Every Intermediate Proposition and Conclusion node carries an explicit `defeating_exceptions: list[str]` (edges to Governing Authority nodes that state a carve-out — a `NEGATED_BY` edge kind, not a note in prose). Negating a Conclusion and checking whether the negation, combined with the same Verified Facts, produces a second, contradictory Conclusion the graph can also derive is the mechanical form of "does this produce a contradiction" — if both a Conclusion and its negation trace to independently supported chains from the *same* undisputed facts, that is a structural signal the underlying rule is genuinely contested (matches `banking-mortgage-research-plan.md`'s own `JURISDICTION DEPENDENT` tier for claim 6), not a bug to silently resolve one way.

## Adverse-argument integrity checks

Three specific failure modes an adverse (or just careless) argument can introduce, each mapped to a structural check on the graph rather than left as prose vigilance:

1. **Inconsistent definitions across premises.** Same as check A above: if a proof's Intermediate Propositions or Conclusion reference a defined term, every reference must resolve to the *same* Definition node (or an explicit, stated reason the meaning changed — e.g. crossing from one title's defined term to another's). A term silently re-defined mid-argument is a real, structurally detectable defect, not just a stylistic one.
2. **Classification mistaken for equivalence.** The subject of the worked example immediately below — this is the design's core encoded principle, not an afterthought.
3. **Word-sense drift disguised as the same word.** A narrower case of (1): two Definition nodes can share a `term` string while differing in `source` or in the actual defining text — the graph treats these as genuinely distinct nodes connected only by string identity, never silently unified, so a proof that switches from one to the other mid-chain is visible as two nodes, not one.

## Worked example: shared classification does not imply complete equivalence

**Core principle, encoded structurally, not just stated in prose:** two things sharing a classification (a word, a category, a defined term) do not thereby share legal status, value, negotiability, acceptance as payment, legal-tender effect, ability to serve as collateral, or discharge rules. A proof graph must represent "X is classified as a Y" as its own edge, distinct from and never collapsing into, "X has all of Y's legal properties."

**The concrete pair.** Take a single physical promissory note. It can genuinely be *two different classified things at once*, governed by two different Articles, for two entirely different legal purposes:

- **Real, currently-ingested side (Article 9 — 13 sections, `library/normalized/ucc/article-9-sections.json`, Virginia's enacted Title 8.9A):** § 8.9A-102(47) defines **`"Instrument"`** as "a negotiable instrument or any other writing that evidences a right to the payment of a monetary obligation... and is of a type that in ordinary course of business is transferred by delivery" — and § 8.9A-102(65) further defines **`"Promissory note"`** as "an instrument that evidences a promise to pay a monetary obligation... and does not contain an acknowledgment by a bank that the bank has received for deposit a sum of money." This classification exists *for the purpose of Article 9 collateral typing* — it determines which of Article 9's several possible perfection methods applies to a security interest taken in the note as collateral (§ 8.9A-310(a)'s general filing rule, subject to exceptions in § 8.9A-310(b) for collateral types perfected other ways — the specific instrument-possession perfection rule itself, § 8.9A-313, is **not** among the 13 ingested sections, a real gap flagged below rather than assumed).

- **Real, NOT-currently-ingested side (Article 3):** § 8.9A-102(47) itself cross-references **`"Negotiable instrument" § 8.3A-104`** — Article 3's own definition, which governs a completely different question: whether the note is negotiable at all, who is a holder, who is a holder in due course, and how the note is enforced as between maker and holder (§ 3-301, per `banking-mortgage-research-plan.md` Part 1.2, directly fetched and confirmed live that run). **This codebase has not ingested Article 3** — confirmed directly via `services/retrieval.get_section()` returning `None` for real § 8.3A-1xx/3xx section IDs, and via `ls library/normalized/ucc/` showing only `article-2-sections.json` and `article-9-sections.json` exist (`banking-mortgage-research-plan.md` Part 1.2 item 1, Part 3 item 1). The Cornell LII citations that research plan found are real and directly fetched, but they are `SourceLayer.MODEL`-adjacent secondary republication of uniform text, not a jurisdiction's `ENACTMENT` — the same layer distinction this design's Governing Authority node structurally requires.

**Why this is the textbook shared-classification trap, not a hypothetical one.** Both "instrument" (Article 9 sense) and "negotiable instrument" (Article 3 sense) can be true of the *same physical note simultaneously* — and a proof that treats "it's an instrument" as settling both questions has silently collapsed two unrelated legal inquiries into one:

| Question | Governed by | Answered by Article 9's classification? |
|---|---|---|
| Is a security interest in this note perfected by filing or by possession? | Article 9 (§ 8.9A-310 general rule + exceptions; specific possession rule for instruments in § 8.9A-313, not ingested) | Yes — this is exactly what the Article 9 "Instrument" classification is *for* |
| Is the note negotiable — can a good-faith purchaser take free of certain defenses as a holder in due course? | Article 3 (§ 3-104 negotiability, § 3-302 HDC status — not ingested) | **No** — Article 9's classification borrows the term but does not answer this; Article 9's own definition explicitly says "a negotiable instrument **or any other writing**..." — Article 9's "Instrument" category is *broader* than Article 3's "negotiable instrument," precisely because they're built for different purposes |
| Who is entitled to enforce the note against the maker? | Article 3 (§ 3-301, directly fetched and confirmed — see above) | No — Article 9's perfection scheme says nothing about enforcement rights between maker and holder |
| Does taking a security interest in the note discharge the underlying obligation it secures? | Neither classification alone — a separate Article 9 discharge/default question (§§ 8.9A-601, 8.9A-609, 8.9A-610, all real, ingested) | No |

A proof graph asserting "this is an instrument, therefore [any Article-3-governed property]" without an independent Definition node, independent Governing Authority node, and independent Verified Fact chain for the Article 3 question is exactly the defect this design exists to make structurally visible — the `CLASSIFIED_AS` edge (below) is real and supportable; a hypothetical `EQUIVALENT_TO` edge asserting the two Articles' consequences are interchangeable would not be, and the graph's edge-kind vocabulary deliberately does not offer that edge as an option.

## The Legal Proof Graph — data structure design

Same style as `services/transaction_lifecycle.py` and `services/models.py`: real Python dataclasses, explicit `to_dict()`, explicit enums, no hidden defaults. This is the schema `services/legal_proof_graph.py` implements.

```python
"""Law Engine -- Legal Proof Graph.
Represents one real conclusion's backward-traceable proof chain:
DEFINITION -> AXIOM/ACCEPTED PREMISE -> GOVERNING AUTHORITY -> VERIFIED FACT
-> INTERMEDIATE PROPOSITION -> CONCLUSION. Reuses VerificationStatus,
ConfidenceLabel, SourceLayer, AuthorityType from services/models.py rather
than inventing a parallel trust system -- see
docs/euclidean-legal-reasoning-architecture.md for the reasoning."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from services.models import (
    AuthorityType,
    ConfidenceLabel,
    SourceLayer,
    VerificationStatus,
)


class ProofNodeKind(str, Enum):
    DEFINITION = "DEFINITION"
    AXIOM = "AXIOM"
    ACCEPTED_PREMISE = "ACCEPTED_PREMISE"
    GOVERNING_AUTHORITY = "GOVERNING_AUTHORITY"
    VERIFIED_FACT = "VERIFIED_FACT"
    INTERMEDIATE_PROPOSITION = "INTERMEDIATE_PROPOSITION"
    CONCLUSION = "CONCLUSION"


class DefinitionSource(str, Enum):
    STATUTORY = "STATUTORY"
    CONTRACTUAL = "CONTRACTUAL"
    ORDINARY_LANGUAGE = "ORDINARY_LANGUAGE"


class FactStatus(str, Enum):
    KNOWN = "KNOWN"
    ASSUMED = "ASSUMED"
    DISPUTED = "DISPUTED"


class ProofEdgeKind(str, Enum):
    """CLASSIFIED_AS is deliberately the only classification-relating edge
    kind offered -- there is no EQUIVALENT_TO, on purpose, per this
    document's shared-classification-does-not-imply-equivalence example."""

    DEFINES_TERM_IN = "DEFINES_TERM_IN"          # Definition -> node that uses the term
    SUPPORTS = "SUPPORTS"                          # GoverningAuthority -> Proposition/Conclusion
    REQUIRES_FACT = "REQUIRES_FACT"                # Proposition/Conclusion -> VerifiedFact
    RESTS_ON_PREMISE = "RESTS_ON_PREMISE"          # Proposition/Conclusion -> Axiom/AcceptedPremise
    DERIVES_FROM = "DERIVES_FROM"                  # Conclusion -> IntermediateProposition
    NEGATED_BY = "NEGATED_BY"                      # Proposition/Conclusion -> GoverningAuthority (exception)
    CLASSIFIED_AS = "CLASSIFIED_AS"                # entity -> Definition (classification only, never equivalence)


@dataclass
class DefinitionNode:
    node_id: str
    term: str
    source: DefinitionSource
    defining_text: str
    citation: str | None = None
    source_document_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "kind": ProofNodeKind.DEFINITION.value,
            "term": self.term,
            "source": self.source.value,
            "defining_text": self.defining_text,
            "citation": self.citation,
            "source_document_id": self.source_document_id,
        }


@dataclass
class PremiseNode:
    node_id: str
    kind: ProofNodeKind  # AXIOM or ACCEPTED_PREMISE only
    statement: str
    scope_note: str | None = None

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "kind": self.kind.value,
            "statement": self.statement,
            "scope_note": self.scope_note,
        }


@dataclass
class GoverningAuthorityNode:
    node_id: str
    authority_type: AuthorityType
    source_layer: SourceLayer
    citation: str
    rule_text: str
    source_document_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "kind": ProofNodeKind.GOVERNING_AUTHORITY.value,
            "authority_type": self.authority_type.value,
            "source_layer": self.source_layer.value,
            "citation": self.citation,
            "rule_text": self.rule_text,
            "source_document_id": self.source_document_id,
        }


@dataclass
class VerifiedFactNode:
    node_id: str
    statement: str
    status: FactStatus
    verification_status: VerificationStatus
    supporting_evidence: str | None = None

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "kind": ProofNodeKind.VERIFIED_FACT.value,
            "statement": self.statement,
            "status": self.status.value,
            "verification_status": self.verification_status.value,
            "supporting_evidence": self.supporting_evidence,
        }


@dataclass
class PropositionNode:
    node_id: str
    kind: ProofNodeKind  # INTERMEDIATE_PROPOSITION or CONCLUSION only
    statement: str
    required_fact_ids: list[str] = field(default_factory=list)
    supporting_authority_ids: list[str] = field(default_factory=list)
    resting_premise_ids: list[str] = field(default_factory=list)
    derives_from_proposition_ids: list[str] = field(default_factory=list)
    defeating_exception_authority_ids: list[str] = field(default_factory=list)
    confidence_label: ConfidenceLabel = ConfidenceLabel.UNVERIFIED

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "kind": self.kind.value,
            "statement": self.statement,
            "required_fact_ids": self.required_fact_ids,
            "supporting_authority_ids": self.supporting_authority_ids,
            "resting_premise_ids": self.resting_premise_ids,
            "derives_from_proposition_ids": self.derives_from_proposition_ids,
            "defeating_exception_authority_ids": self.defeating_exception_authority_ids,
            "confidence_label": self.confidence_label.value,
        }


@dataclass
class ProofEdge:
    from_node_id: str
    to_node_id: str
    edge_kind: ProofEdgeKind

    def to_dict(self) -> dict:
        return {
            "from_node_id": self.from_node_id,
            "to_node_id": self.to_node_id,
            "edge_kind": self.edge_kind.value,
        }


class LegalProofGraphError(Exception):
    """Raised for a real, unrecoverable graph-integrity failure -- an edge
    pointing at a node_id that doesn't exist in the graph, never silently
    dropped."""


@dataclass
class LegalProofGraph:
    graph_id: str
    conclusion_node_id: str
    definitions: list[DefinitionNode] = field(default_factory=list)
    premises: list[PremiseNode] = field(default_factory=list)
    authorities: list[GoverningAuthorityNode] = field(default_factory=list)
    facts: list[VerifiedFactNode] = field(default_factory=list)
    propositions: list[PropositionNode] = field(default_factory=list)
    edges: list[ProofEdge] = field(default_factory=list)

    def all_node_ids(self) -> set[str]:
        return (
            {n.node_id for n in self.definitions}
            | {n.node_id for n in self.premises}
            | {n.node_id for n in self.authorities}
            | {n.node_id for n in self.facts}
            | {n.node_id for n in self.propositions}
        )

    def check_no_dangling_edges(self) -> list[str]:
        """Structural check C from the design doc: every edge must resolve
        to a real node. Returns the list of dangling references found --
        never raises, so a caller can decide how to surface real gaps."""
        known = self.all_node_ids()
        problems = []
        for edge in self.edges:
            if edge.from_node_id not in known:
                problems.append(f"Edge references unknown from_node_id {edge.from_node_id!r}")
            if edge.to_node_id not in known:
                problems.append(f"Edge references unknown to_node_id {edge.to_node_id!r}")
        return problems

    def weakest_link_verification_status(self, proposition_id: str) -> VerificationStatus:
        """Real weakest-link computation for check D / the Conclusion's
        required ConfidenceLabel -- walks required_fact_ids only (a
        Conclusion's honesty is bounded by its facts' verification, per
        VerificationStatus's own ordering intent in services/models.py)."""
        prop = next((p for p in self.propositions if p.node_id == proposition_id), None)
        if prop is None:
            raise LegalProofGraphError(f"No proposition {proposition_id!r} in graph {self.graph_id!r}.")
        fact_statuses = [
            f.verification_status for f in self.facts if f.node_id in prop.required_fact_ids
        ]
        if not fact_statuses:
            raise LegalProofGraphError(
                f"Proposition {proposition_id!r} has no required_fact_ids -- "
                "cannot compute a real confidence without at least one traced fact."
            )
        ordering = list(VerificationStatus)
        return min(fact_statuses, key=lambda s: ordering.index(s))

    def to_dict(self) -> dict:
        return {
            "graph_id": self.graph_id,
            "conclusion_node_id": self.conclusion_node_id,
            "definitions": [n.to_dict() for n in self.definitions],
            "premises": [n.to_dict() for n in self.premises],
            "authorities": [n.to_dict() for n in self.authorities],
            "facts": [n.to_dict() for n in self.facts],
            "propositions": [n.to_dict() for n in self.propositions],
            "edges": [e.to_dict() for e in self.edges],
        }
```

Design notes on choices above, for whoever implements this:

- `weakest_link_verification_status` deliberately walks only `required_fact_ids`, not authorities or premises — an authority can be `SOURCE_VERIFIED` and a premise can be explicitly and honestly stated, but if the *fact* the rule needs is only `DISCOVERED`, the Conclusion is not more certain than that. This mirrors `banking-mortgage-research-plan.md` Part 2's own repeated pattern: strong-looking authority (UCC § 3-303) still capped the claim at `UNRESOLVED / INSUFFICIENT EVIDENCE` because the fact-level confirmation (a direct fetch of the statutory text itself) hadn't happened yet.
- `check_no_dangling_edges` returns a list rather than raising, on purpose — an incomplete graph (a real proof someone is still building) is a normal, honest state, same as an unpopulated `PedagogicalContract` field being "honest (we haven't written that part yet)" per that dataclass's own docstring (`services/models.py:300-315`). A dangling edge should be visible, not fatal.
- No `EQUIVALENT_TO` edge kind exists in `ProofEdgeKind` — this is the structural encoding of the shared-classification principle: the graph's vocabulary itself cannot express "these are the same" from "these share a classification," because the two must never be interchangeable in a real proof.

## Non-goals

- This design does not claim law is deductively axiomatic the way Euclidean geometry is — legal reasoning routinely involves balancing, policy judgment, and genuinely underdetermined questions (exactly what `banking-mortgage-research-plan.md`'s `JURISDICTION DEPENDENT` tier already exists to represent honestly). The proof-graph discipline is a tool for making a *stated* chain of reasoning checkable for structural completeness and consistency, not a claim that every legal question reduces to one.
- This design does not build an automated legal-reasoning engine that generates Conclusions on its own. Every node above is populated from real, human- or research-produced content (the same way `transaction_lifecycle.py`'s stages are hand-built from real ingested sections, not generated) — the graph's job is to make that content's dependencies explicit and checkable, not to originate legal conclusions itself.
- This design does not ingest UCC Article 3, or any other new source. The worked example above deliberately uses one already-ingested side (Article 9) and one honestly-flagged-as-not-ingested side (Article 3, sourced only from `banking-mortgage-research-plan.md`'s prior research) to demonstrate the shared-classification principle without overclaiming what this codebase currently contains.

## Smallest Useful Implementation Slice

**Build exactly one real `LegalProofGraph` instance for one existing, fully-ingested proposition — do not build the general graph-construction tooling yet, just the one instance and the dataclasses above.**

Target: the attachment test at **§ 8.9A-203(b)** (Va. Code Ann., already ingested in `library/normalized/ucc/article-9-sections.json`), which `transaction_lifecycle.py`'s sibling module `cross_article_lifecycle.py` already relies on informally. Concretely:

1. Three `VerifiedFactNode`s for the three § 8.9A-203(b) conditions (value given; debtor has rights in collateral; authenticated security agreement or equivalent) — each with a real `FactStatus` and `VerificationStatus`, using the fact pattern already present in `cross_article_lifecycle.py`'s existing scenario (no new scenario needed).
2. One `GoverningAuthorityNode` for § 8.9A-203(b) itself (`authority_type=STATUTE`, `source_layer=ENACTMENT`, citation and rule text pulled directly from the already-ingested `paragraphs` field — no new text to write, only re-shape existing ingested content).
3. One `IntermediateProposition` node ("the security interest has attached") with `required_fact_ids` pointing at the three facts above, and `weakest_link_verification_status` computed for real against the ingested data.
4. One `DefinitionNode` for `"Security agreement"` (§ 8.9A-102(74), already ingested, real text: "an agreement that creates or provides for a security interest") with `source=DefinitionSource.STATUTORY`, demonstrating the Definition-node shape end-to-end on one real, already-ingested term before attempting the harder Article 9/Article 3 "Instrument" cross-reference case from the worked example above.

This slice is deliberately chosen because it requires **zero new ingestion** — every fact, authority, and definition it needs already exists in `library/normalized/ucc/article-9-sections.json` — and it is small enough to hand-verify against the real statutory text in the same sitting it's built, the same "self-referential and immediately testable" property `ghostos-mastery-engine-design.md`'s own smallest-prototype section names as the reason for its pick.

## Verification

```
python3 -m unittest discover -s services -p "test_*.py"
```

"""Law Engine -- Legal Proof Graph (Live Run 1.43, follow-through on
docs/euclidean-legal-reasoning-architecture.md's design). Represents one
real conclusion's backward-traceable proof chain:
DEFINITION -> AXIOM/ACCEPTED PREMISE -> GOVERNING AUTHORITY -> VERIFIED FACT
-> INTERMEDIATE PROPOSITION -> CONCLUSION. Reuses VerificationStatus,
ConfidenceLabel, SourceLayer, AuthorityType from services/models.py rather
than inventing a parallel trust system -- see
docs/euclidean-legal-reasoning-architecture.md for the reasoning.

The dataclasses below are the design doc's own schema, implemented as
written. `build_attachment_proof_graph()` is the doc's "Smallest Useful
Implementation Slice": one real graph for the § 8.9A-203(b) attachment
test, built entirely from the 24 already-ingested Article 2 / Article 9
sections -- no new ingestion, no invented statutory text.

Scope note (disclosed, not silently narrowed): the design doc's slice
specifies an INTERMEDIATE_PROPOSITION node for "the security interest has
attached," not a CONCLUSION node -- this proof does not feed into a larger
asserted Conclusion, so no CONCLUSION-kind node is built this run, and no
VerificationStatus -> ConfidenceLabel mapping is invented for one (the
design doc specifies the weakest-link computation over VerificationStatus,
not a mapping to ConfidenceLabel -- that mapping is future work, not
implemented here). `LegalProofGraph.conclusion_node_id` points at the
intermediate proposition as this slice's practical endpoint.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.models import (
    AuthorityType,
    ConfidenceLabel,
    SourceLayer,
    VerificationStatus,
    verification_status_to_confidence_label,
    weakest_verification_status,
)
from services.retrieval import get_section
from services import ingestion_case_law


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
    kind offered -- there is no EQUIVALENT_TO, on purpose, per the design
    doc's shared-classification-does-not-imply-equivalence example.

    DISTINGUISHED_BY added Live Run 1.60, Mission 8, Phase 5, implementing
    docs/law-engine-authority-model-and-constitutional-flagship.md §2's
    real, disclosed new concept: two propositions (or the authorities
    behind them) can reach different results WITHOUT genuine adverse
    conflict, because a real, named factual/procedural/jurisdictional
    difference explains the divergence. This is structurally different
    from NEGATED_BY (genuine adverse authority actually cutting against a
    proposition) -- reusing NEGATED_BY for a merely-distinguishable
    authority would flatten exactly the distinction
    docs/law-engine-precedent-conflict-thesis.md §1's "factual
    distinction" / "procedural posture" categories exist to preserve."""

    DEFINES_TERM_IN = "DEFINES_TERM_IN"          # Definition -> node that uses the term
    SUPPORTS = "SUPPORTS"                          # GoverningAuthority -> Proposition/Conclusion
    REQUIRES_FACT = "REQUIRES_FACT"                # Proposition/Conclusion -> VerifiedFact
    RESTS_ON_PREMISE = "RESTS_ON_PREMISE"          # Proposition/Conclusion -> Axiom/AcceptedPremise
    DERIVES_FROM = "DERIVES_FROM"                  # Conclusion -> IntermediateProposition
    NEGATED_BY = "NEGATED_BY"                      # Proposition/Conclusion -> GoverningAuthority (exception)
    CLASSIFIED_AS = "CLASSIFIED_AS"                # entity -> Definition (classification only, never equivalence)
    DISTINGUISHED_BY = "DISTINGUISHED_BY"          # Proposition -> Proposition (or GoverningAuthority): a real, named, non-conflicting distinction, not genuine adverse authority


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
    # Two real fields added Live Run 1.60, Mission 8, Phase 5, implementing
    # docs/law-engine-authority-model-and-constitutional-flagship.md §2.
    # Defaulted so every existing caller (build_attachment_proof_graph's
    # statutory-only authority node) keeps working unchanged -- verified
    # directly by running the full suite after this change, not assumed.
    #
    # verification_status defaults to SOURCE_VERIFIED because every prior
    # GoverningAuthorityNode built in this module has come from a real,
    # SOURCE_VERIFIED-manifested statutory ingestion (services/models.py's
    # SourceManifest carries the real status per source; this default
    # matches that reality for the one existing caller, not an invented
    # blanket assumption). A judicial-holding-sourced node (Phase 5's new
    # flagship graph) sets this explicitly and honestly instead -- see
    # build_promissory_note_enforcement_proof_graph() below.
    verification_status: VerificationStatus = VerificationStatus.SOURCE_VERIFIED
    # Real, named summary of the court's own reasoning connecting the
    # underlying text to its holding -- design doc §2 point 3 ("WHAT
    # INTERPRETIVE STEP OCCURRED?"). None for a straightforward enacted
    # statute (there is no interpretive step -- the text simply applies);
    # required, in practice, for any judicial-holding-sourced node, since
    # "this case governs" is itself a claim that needs its own proof, not
    # an unexplained axiom (design doc §2's real, disclosed gap this field
    # closes).
    interpretive_step: str | None = None

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "kind": ProofNodeKind.GOVERNING_AUTHORITY.value,
            "authority_type": self.authority_type.value,
            "source_layer": self.source_layer.value,
            "citation": self.citation,
            "rule_text": self.rule_text,
            "source_document_id": self.source_document_id,
            "verification_status": self.verification_status.value,
            "interpretive_step": self.interpretive_step,
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

    def weakest_link_authority_verification_status(self, proposition_id: str) -> VerificationStatus:
        """Real, disclosed authority-chain counterpart to
        weakest_link_verification_status (Live Run 1.60, Mission 8, Phase
        5) -- walks supporting_authority_ids instead of required_fact_ids.
        This is the computation the design doc's Precedent Conflict Mapper
        extension actually needs: a proposition resting on a
        RETRIEVED-not-SOURCE_VERIFIED judicial holding must never report
        the same confidence as one resting purely on a SOURCE_VERIFIED
        statute, even if every fact in the proposition is itself fully
        known."""
        prop = next((p for p in self.propositions if p.node_id == proposition_id), None)
        if prop is None:
            raise LegalProofGraphError(f"No proposition {proposition_id!r} in graph {self.graph_id!r}.")
        authority_statuses = [
            a.verification_status for a in self.authorities if a.node_id in prop.supporting_authority_ids
        ]
        if not authority_statuses:
            raise LegalProofGraphError(
                f"Proposition {proposition_id!r} has no supporting_authority_ids -- "
                "cannot compute a real authority-chain confidence without at least one traced authority."
            )
        return weakest_verification_status(authority_statuses)

    def confidence_label_for_conclusion(self, conclusion_id: str) -> ConfidenceLabel:
        """Real confidence computation for a CONCLUSION node, reusing
        services/models.py's VerificationStatus -> ConfidenceLabel mapping
        (Phase 5's own explicit instruction), applied to this graph's own
        authority chain: walks every proposition the conclusion
        DERIVES_FROM, takes the weakest authority verification status
        across all of them, and maps that single weakest link to the
        ConfidenceLabel a caller-facing surface is allowed to show. Never
        computed from facts alone -- a conclusion resting on well-known
        facts but weakly-verified authority (exactly this flagship
        graph's real situation: RETRIEVED, not SOURCE_VERIFIED, case-law
        sources) must not be presented as more certain than the authority
        actually supports."""
        conclusion = next((p for p in self.propositions if p.node_id == conclusion_id), None)
        if conclusion is None:
            raise LegalProofGraphError(f"No proposition {conclusion_id!r} in graph {self.graph_id!r}.")
        if not conclusion.derives_from_proposition_ids:
            raise LegalProofGraphError(
                f"Proposition {conclusion_id!r} has no derives_from_proposition_ids -- "
                "cannot compute a real conclusion confidence without at least one traced premise."
            )
        weakest_per_premise = [
            self.weakest_link_authority_verification_status(premise_id)
            for premise_id in conclusion.derives_from_proposition_ids
        ]
        overall_weakest = weakest_verification_status(weakest_per_premise)
        return verification_status_to_confidence_label(overall_weakest)

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


def _require_section(section_id: str) -> dict:
    section = get_section(section_id)
    if section is None:
        raise LegalProofGraphError(
            f"No ingested section {section_id!r} -- cannot build a proof graph node without a real source."
        )
    return section


def build_attachment_proof_graph() -> LegalProofGraph:
    """The design doc's Smallest Useful Implementation Slice: one real
    LegalProofGraph for the § 8.9A-203(b) attachment test, reusing the
    exact fact pattern already present in
    cross_article_lifecycle.py's "attachment" stage (the equipment
    purchase scenario) rather than inventing a new one -- no new ingestion,
    every fact/authority/definition below is real, already-ingested
    content re-shaped into proof-graph nodes."""
    attachment_section = _require_section("8.9A-203")
    definitions_section = _require_section("8.9A-102")

    authority_attachment = GoverningAuthorityNode(
        node_id="authority-8.9a-203-b",
        authority_type=AuthorityType.STATUTE,
        source_layer=SourceLayer.ENACTMENT,
        citation=f'{attachment_section["citation"]}(b)',
        # Real ingested text, subsections (b) through (3)(A) -- the
        # signed-security-agreement enforceability path, matching the
        # equipment-purchase scenario's fact pattern (not the
        # possession/control paths in (B)-(E), which don't apply here).
        rule_text=" ".join(attachment_section["paragraphs"][1:6]),
        source_document_id=attachment_section["source_document_id"],
    )

    fact_value_given = VerifiedFactNode(
        node_id="fact-value-given",
        statement=(
            "The equipment dealer has given value: it financed the "
            "$40,000 purchase price of the equipment for the business."
        ),
        status=FactStatus.KNOWN,
        # TRUSTED_FOR_ANALYSIS, not SOURCE_VERIFIED/CROSS_VERIFIED: this
        # fact is stipulated by the illustrative equipment-purchase
        # scenario cross_article_lifecycle.py already builds (Stage 3,
        # "attachment"), not independently verified against a real
        # case record -- honest label for a pedagogical fact pattern
        # the engine treats as given for analysis.
        verification_status=VerificationStatus.TRUSTED_FOR_ANALYSIS,
        supporting_evidence=(
            'cross_article_lifecycle.py Stage 3 ("attachment") facts: '
            '"...the dealer has given value (the financed purchase price)."'
        ),
    )
    fact_debtor_rights = VerifiedFactNode(
        node_id="fact-debtor-rights-in-collateral",
        statement=(
            "The business (debtor) has rights in the equipment: it has "
            "taken possession of the equipment under the sale contract."
        ),
        status=FactStatus.KNOWN,
        verification_status=VerificationStatus.TRUSTED_FOR_ANALYSIS,
        supporting_evidence=(
            'cross_article_lifecycle.py Stage 3 ("attachment") facts: '
            '"The business has ... already taken possession of the equipment..."'
        ),
    )
    fact_signed_agreement = VerifiedFactNode(
        node_id="fact-signed-security-agreement",
        statement=(
            "The business has signed a security agreement describing the "
            "equipment as collateral."
        ),
        status=FactStatus.KNOWN,
        verification_status=VerificationStatus.TRUSTED_FOR_ANALYSIS,
        supporting_evidence=(
            'cross_article_lifecycle.py Stage 3 ("attachment") facts: '
            '"The business has signed the security agreement..."'
        ),
    )

    definition_security_agreement = DefinitionNode(
        node_id="def-security-agreement",
        term="Security agreement",
        source=DefinitionSource.STATUTORY,
        # Real ingested text of § 8.9A-102(74), no paraphrase.
        defining_text=next(
            p for p in definitions_section["paragraphs"] if p.startswith('(74) "Security agreement"')
        ),
        citation=f'{definitions_section["citation"]}(74)',
        source_document_id=definitions_section["source_document_id"],
    )

    proposition_attached = PropositionNode(
        node_id="prop-security-interest-attached",
        kind=ProofNodeKind.INTERMEDIATE_PROPOSITION,
        statement="The equipment dealer's security interest in the equipment has attached.",
        required_fact_ids=[
            fact_value_given.node_id,
            fact_debtor_rights.node_id,
            fact_signed_agreement.node_id,
        ],
        supporting_authority_ids=[authority_attachment.node_id],
    )

    edges = [
        ProofEdge(authority_attachment.node_id, proposition_attached.node_id, ProofEdgeKind.SUPPORTS),
        ProofEdge(proposition_attached.node_id, fact_value_given.node_id, ProofEdgeKind.REQUIRES_FACT),
        ProofEdge(proposition_attached.node_id, fact_debtor_rights.node_id, ProofEdgeKind.REQUIRES_FACT),
        ProofEdge(proposition_attached.node_id, fact_signed_agreement.node_id, ProofEdgeKind.REQUIRES_FACT),
        ProofEdge(
            definition_security_agreement.node_id,
            fact_signed_agreement.node_id,
            ProofEdgeKind.DEFINES_TERM_IN,
        ),
    ]

    return LegalProofGraph(
        graph_id="attachment-8.9a-203b-equipment-purchase-v1",
        # See module docstring's Scope note: this slice's endpoint is the
        # INTERMEDIATE_PROPOSITION itself, not a separate CONCLUSION node.
        conclusion_node_id=proposition_attached.node_id,
        definitions=[definition_security_agreement],
        authorities=[authority_attachment],
        facts=[fact_value_given, fact_debtor_rights, fact_signed_agreement],
        propositions=[proposition_attached],
        edges=edges,
    )


def build_promissory_note_enforcement_proof_graph() -> LegalProofGraph:
    """Live Run 1.60, Mission 8, Phase 5's own flagship graph -- "who is
    entitled to enforce a transferred promissory note" -- the direct
    implementation vehicle docs/law-engine-authority-model-and-
    constitutional-flagship.md §2 named for
    docs/law-engine-precedent-conflict-thesis.md §3's Precedent Conflict
    Mapper design.

    Real authority chain, nothing invented: the real, already-ingested
    Virginia § 8.3A-301 ("person entitled to enforce") and § 8.3A-308
    ("proof of signatures and status as holder in due course," the real
    Phase 1 gap-fill) statutory text; the two real, Phase 3/4-verified
    case-law manifests (Rodriguez v. Wells Fargo Bank, N.A., Fla. 4th DCA
    2015; Greene v. Trustee Services of Carolina, LLC -- the case Live Run
    1.59 knew as "In re Foreclosure of Kenley" -- N.C. App. 2016).

    Real, disclosed scope note: this graph represents the general
    doctrinal question (a hypothetical note, indorsed in blank, produced
    by the party in possession) rather than a single further-hypothetical
    new fact pattern -- Phase 6's Precedent Conflict Mapper applies THIS
    graph's real authority chain to a new, genuinely undecided fact
    pattern, rather than this graph itself inventing one.

    Why a DISTINGUISHED_BY edge, not NEGATED_BY, between the two
    propositions: Rodriguez and Greene do not actually disagree about the
    underlying substantive rule (indorsement-in-blank + possession =
    holder = person entitled to enforce -- the same concept Virginia's
    § 8.3A-301/104 already encodes). They differ on a real, named,
    non-conflicting distinction -- WHEN that status must be shown, and in
    what kind of proceeding (a Florida judicial-foreclosure complaint,
    tested at filing, vs. a North Carolina Chapter 45 power-of-sale
    hearing, tested at the hearing itself) -- exactly
    docs/law-engine-precedent-conflict-thesis.md §1's "procedural
    posture" and "jurisdiction" factors doing real explanatory work, not
    genuine adverse authority. Using NEGATED_BY here would misrepresent an
    honest, explicable divergence as if it were a real doctrinal conflict.
    """
    section_301 = _require_section("8.3A-301")
    section_308 = _require_section("8.3A-308")

    rodriguez_manifest = ingestion_case_law.build_rodriguez_manifest()
    greene_manifest = ingestion_case_law.build_greene_manifest()
    rodriguez_source = ingestion_case_law.load_rodriguez_source()
    greene_source = ingestion_case_law.load_greene_source()

    authority_statute_301 = GoverningAuthorityNode(
        node_id="authority-8.3a-301",
        authority_type=AuthorityType.STATUTE,
        source_layer=SourceLayer.ENACTMENT,
        citation=section_301["citation"],
        rule_text=section_301["paragraphs"][0],
        source_document_id=section_301["source_document_id"],
        verification_status=VerificationStatus.SOURCE_VERIFIED,
    )
    authority_statute_308 = GoverningAuthorityNode(
        node_id="authority-8.3a-308",
        authority_type=AuthorityType.STATUTE,
        source_layer=SourceLayer.ENACTMENT,
        # Real subsection (b) -- the text tying "producing the instrument"
        # to "prov[ing] entitlement to enforce the instrument under
        # § 8.3A-301" (see Phase 1's gap-check disclosure in
        # services/ingestion_article3.py's own module docstring).
        citation=f'{section_308["citation"]}(b)',
        rule_text=section_308["paragraphs"][1],
        source_document_id=section_308["source_document_id"],
        verification_status=VerificationStatus.SOURCE_VERIFIED,
    )
    authority_rodriguez = GoverningAuthorityNode(
        node_id="authority-rodriguez-fl-4dca-2015",
        authority_type=AuthorityType.JUDICIAL_HOLDING,
        source_layer=SourceLayer.INTERPRETATION,
        citation=rodriguez_manifest.citation,
        rule_text=rodriguez_source["holding_and_reasoning"]["quoted_language"][0],
        source_document_id=rodriguez_manifest.document_id,
        # Honest, disclosed downgrade -- see ingestion_case_law.py's own
        # module docstring: WebFetch-mediated retrieval (raw Bash network
        # egress is sandbox-denied this run) could not achieve
        # independently byte-verified capture of the complete opinion.
        verification_status=rodriguez_manifest.verification_status,
        interpretive_step=(
            "Florida's own enactment of the UCC holder/person-entitled-to-"
            "enforce concept (Fla. Stat. §§ 673.3011, 671.201(21)(a) -- "
            "the same underlying doctrine as Virginia's § 8.3A-301/104/308 "
            "above), applied through the court's own prior standing-at-"
            "filing precedent (McLean v. JP Morgan Chase, 79 So. 3d 170), "
            "led the court to require that a party suing as a SERVICER "
            "(rather than in its own name as holder) additionally prove, "
            "as of the filing date, real authority -- a power of attorney "
            "or pooling-and-servicing agreement -- to enforce the note on "
            "the true holder's behalf; bare possession of the note by the "
            "servicer's principal, without that proof in the record, does "
            "not establish the plaintiff-servicer's own standing."
        ),
    )
    authority_greene = GoverningAuthorityNode(
        node_id="authority-greene-nc-app-2016",
        authority_type=AuthorityType.JUDICIAL_HOLDING,
        source_layer=SourceLayer.INTERPRETATION,
        citation=greene_manifest.citation,
        rule_text=greene_source["holding_and_reasoning"]["quoted_language"][0],
        source_document_id=greene_manifest.document_id,
        verification_status=greene_manifest.verification_status,
        interpretive_step=(
            "North Carolina's own Chapter 45 power-of-sale foreclosure "
            "statute (N.C. Gen. Stat. § 45-21.16(d), requiring the party "
            "seeking to foreclose to show it is the holder of the note) "
            "and North Carolina's own UCC holder-by-possession concept "
            "(the same underlying doctrine as Virginia's § 8.3A-301/104/"
            "308 above) led the court to hold that, for a note indorsed "
            "IN BLANK, mere possession -- shown by production of the "
            "original note AT THE HEARING ITSELF -- is sufficient to "
            "prove holder status, with no separate requirement to also "
            "document the note's full chain of prior transfer, because "
            "the UCC's own text imposes no such requirement."
        ),
    )

    fact_note_indorsed_in_blank = VerifiedFactNode(
        node_id="fact-note-indorsed-in-blank-in-possession",
        statement=(
            "The promissory note at issue is indorsed in blank, and the "
            "party seeking to enforce it produces the original, in its "
            "own possession."
        ),
        status=FactStatus.ASSUMED,
        # Real, disclosed hypothetical fact pattern (the general doctrinal
        # question this graph represents), matching
        # build_attachment_proof_graph()'s own TRUSTED_FOR_ANALYSIS
        # convention for a stipulated fact pattern rather than a specific,
        # independently-verified real-world record.
        verification_status=VerificationStatus.TRUSTED_FOR_ANALYSIS,
        supporting_evidence=(
            "Stipulated hypothetical fact pattern, shared by both "
            "Rodriguez and Greene's real, underlying fact patterns "
            "(both involve a note indorsed in blank, physically "
            "produced by the party in possession)."
        ),
    )

    proposition_fl_timing = PropositionNode(
        node_id="prop-fl-standing-at-filing",
        kind=ProofNodeKind.INTERMEDIATE_PROPOSITION,
        statement=(
            "In a Florida judicial foreclosure action, a party enforcing "
            "a note as holder (or as a servicer acting for the holder) "
            "must prove its status/authority to enforce as of the date "
            "the complaint was filed; later-acquired proof does not cure "
            "an earlier gap."
        ),
        required_fact_ids=[fact_note_indorsed_in_blank.node_id],
        supporting_authority_ids=[
            authority_rodriguez.node_id,
            authority_statute_301.node_id,
            authority_statute_308.node_id,
        ],
    )
    proposition_nc_hearing = PropositionNode(
        node_id="prop-nc-holder-status-at-hearing",
        kind=ProofNodeKind.INTERMEDIATE_PROPOSITION,
        statement=(
            "In a North Carolina Chapter 45 power-of-sale foreclosure "
            "hearing, production of the original note -- indorsed in "
            "blank, in the party's possession -- AT THE HEARING ITSELF "
            "is sufficient to establish holder status; no separate proof "
            "of an earlier filing-date possession is required."
        ),
        required_fact_ids=[fact_note_indorsed_in_blank.node_id],
        supporting_authority_ids=[
            authority_greene.node_id,
            authority_statute_301.node_id,
        ],
    )

    conclusion = PropositionNode(
        node_id="conclusion-who-may-enforce-a-transferred-note",
        kind=ProofNodeKind.CONCLUSION,
        statement=(
            "Who is entitled to enforce a transferred promissory note, "
            "indorsed in blank, depends on the jurisdiction and the kind "
            "of proceeding: both Florida and North Carolina apply the "
            "same substantive UCC holder-by-possession rule, but the "
            "TIMING of when holder status/authority must be proven "
            "differs -- Florida requires proof as of the complaint's "
            "filing date; North Carolina accepts proof at the power-of-"
            "sale hearing itself. This is a real, explicable procedural-"
            "posture and jurisdiction distinction, not a genuine "
            "substantive conflict."
        ),
        derives_from_proposition_ids=[
            proposition_fl_timing.node_id,
            proposition_nc_hearing.node_id,
        ],
    )

    edges = [
        ProofEdge(authority_statute_301.node_id, proposition_fl_timing.node_id, ProofEdgeKind.SUPPORTS),
        ProofEdge(authority_statute_308.node_id, proposition_fl_timing.node_id, ProofEdgeKind.SUPPORTS),
        ProofEdge(authority_rodriguez.node_id, proposition_fl_timing.node_id, ProofEdgeKind.SUPPORTS),
        ProofEdge(authority_statute_301.node_id, proposition_nc_hearing.node_id, ProofEdgeKind.SUPPORTS),
        ProofEdge(authority_greene.node_id, proposition_nc_hearing.node_id, ProofEdgeKind.SUPPORTS),
        ProofEdge(proposition_fl_timing.node_id, fact_note_indorsed_in_blank.node_id, ProofEdgeKind.REQUIRES_FACT),
        ProofEdge(proposition_nc_hearing.node_id, fact_note_indorsed_in_blank.node_id, ProofEdgeKind.REQUIRES_FACT),
        # The real, non-conflicting distinction -- see module docstring's
        # "Why a DISTINGUISHED_BY edge, not NEGATED_BY" note.
        ProofEdge(proposition_fl_timing.node_id, proposition_nc_hearing.node_id, ProofEdgeKind.DISTINGUISHED_BY),
        ProofEdge(conclusion.node_id, proposition_fl_timing.node_id, ProofEdgeKind.DERIVES_FROM),
        ProofEdge(conclusion.node_id, proposition_nc_hearing.node_id, ProofEdgeKind.DERIVES_FROM),
    ]

    graph = LegalProofGraph(
        graph_id="promissory-note-enforcement-fl-nc-flagship-v1",
        conclusion_node_id=conclusion.node_id,
        authorities=[authority_statute_301, authority_statute_308, authority_rodriguez, authority_greene],
        facts=[fact_note_indorsed_in_blank],
        propositions=[proposition_fl_timing, proposition_nc_hearing, conclusion],
        edges=edges,
    )

    # Real confidence computation (Phase 5's own explicit instruction) --
    # honestly reflects that this conclusion's weakest link is the two
    # RETRIEVED-not-SOURCE_VERIFIED case-law sources, not the two
    # SOURCE_VERIFIED statutes.
    conclusion.confidence_label = graph.confidence_label_for_conclusion(conclusion.node_id)

    return graph

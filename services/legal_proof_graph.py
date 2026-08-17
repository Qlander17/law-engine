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
)
from services.retrieval import get_section


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
    doc's shared-classification-does-not-imply-equivalence example."""

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

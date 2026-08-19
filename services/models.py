"""Law Engine -- core provenance/verification data model (Live Run 1.37,
Missions 11-13). Every real, significant source or inference in Law Engine
carries one of these states explicitly -- the system must always be able
to say what it believes, why, from what source, and how sure it is. This
module has no I/O; see ingestion.py for building/persisting real records.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class VerificationStatus(str, Enum):
    """Trust-but-verify epistemic states (Mission 12). Progression is not
    strictly linear -- a source can jump straight to SOURCE_VERIFIED if
    ingested directly from an official government site, for example."""

    DISCOVERED = "DISCOVERED"
    RETRIEVED = "RETRIEVED"
    SOURCE_VERIFIED = "SOURCE_VERIFIED"
    AUTHORITY_CLASSIFIED = "AUTHORITY_CLASSIFIED"
    CURRENTNESS_CHECKED = "CURRENTNESS_CHECKED"
    CROSS_VERIFIED = "CROSS_VERIFIED"
    TRUSTED_FOR_ANALYSIS = "TRUSTED_FOR_ANALYSIS"
    CONFLICT = "CONFLICT"
    UNKNOWN = "UNKNOWN"


class ConfidenceLabel(str, Enum):
    """Required, coarse-grained labels a caller-facing surface must use --
    never presented as more certain than this. See Mission 12's explicit
    instruction that an inferred rule must never silently become a
    verified one."""

    LIKELY = "LIKELY"
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    CONFLICTING = "CONFLICTING"


class SourceLayer(str, Enum):
    """Which of the three conceptual UCC layers a source belongs to (Live
    Run 1.38, Mission 10). A state's enactment of Article 2 is one
    jurisdiction's version of the UCC, not "the UCC" itself -- these three
    layers must stay distinguishable so the system never silently calls a
    state enactment "the UCC" without naming the jurisdiction, and never
    presents one jurisdiction's variation as universal."""

    MODEL = "MODEL"                    # ULC/ALI official Uniform Commercial Code text
    ENACTMENT = "ENACTMENT"            # one jurisdiction's enacted statute
    INTERPRETATION = "INTERPRETATION"  # case law, official commentary, other interpretive material


class AuthorityType(str, Enum):
    """What KIND of authority a source is -- orthogonal to how verified it
    is. A CLAIM_ALTERNATIVE_THEORY can be fully SOURCE_VERIFIED (we
    correctly captured what the claim says) while never being VERIFIED as
    legally controlling.

    JUDICIAL_HOLDING / DICTA / PERSUASIVE_OPINION / COMMON_LAW_RULE /
    ADMINISTRATIVE_INTERPRETATION added Live Run 1.60, Mission 8, Phase 4,
    implementing the source-type refinement
    docs/law-engine-authority-model-and-constitutional-flagship.md §1
    designed: the prior generic CASE bucket doesn't distinguish a binding
    holding from dicta or from a persuasive out-of-hierarchy opinion --
    exactly the distinction the precedent-conflict thesis
    (docs/law-engine-precedent-conflict-thesis.md §1) is built on. CASE
    itself is left in place, unremoved, for any future source that is
    real but not yet classified into one of the five finer-grained kinds --
    a real, disclosed both/and, not a breaking rename."""

    CONSTITUTION = "CONSTITUTION"
    STATUTE = "STATUTE"
    REGULATION = "REGULATION"
    COURT_RULE = "COURT_RULE"
    CASE = "CASE"
    TREATY = "TREATY"
    TREATISE = "TREATISE"
    SECONDARY_AUTHORITY = "SECONDARY_AUTHORITY"
    CLAIM_ALTERNATIVE_THEORY = "CLAIM_ALTERNATIVE_THEORY"
    JUDICIAL_HOLDING = "JUDICIAL_HOLDING"
    DICTA = "DICTA"
    PERSUASIVE_OPINION = "PERSUASIVE_OPINION"
    COMMON_LAW_RULE = "COMMON_LAW_RULE"
    ADMINISTRATIVE_INTERPRETATION = "ADMINISTRATIVE_INTERPRETATION"


@dataclass
class SourceManifest:
    """One real, provenance-tracked source document. Original source
    documents are immutable (library/source/); this manifest describes
    one, never mutates the original bytes it hashes."""

    document_id: str
    title: str
    authority_type: AuthorityType
    jurisdiction: str
    citation: str
    official_source_url: str
    publisher: str
    retrieval_timestamp: str
    sha256_hash: str
    verification_status: VerificationStatus
    court: str | None = None
    publication_or_effective_date: str | None = None
    version: str = "1"
    superseded: bool = False
    licensing_status: str = "public domain -- state statute (edict of government)"
    # Defaults to ENACTMENT because every SourceManifest ingested to date is
    # a state's enacted statute (Virginia Title 8.2). A future MODEL-layer
    # source (ULC/ALI official text) or INTERPRETATION-layer source (a
    # case or official commentary) must set this explicitly -- it is not
    # inferred from authority_type, since a CASE could theoretically
    # populate any layer depending on what it's cited for.
    source_layer: SourceLayer = SourceLayer.ENACTMENT
    topics: list[str] = field(default_factory=list)
    cross_references: list[str] = field(default_factory=list)
    notes: str = ""
    # Three new fields (Live Run 1.60, Mission 8, Phase 4), implementing
    # docs/law-engine-authority-model-and-constitutional-flagship.md §1's
    # source-type model. All optional/defaulted to None so no existing
    # SourceManifest construction anywhere in the codebase breaks -- most
    # meaningful for a JUDICIAL_HOLDING source (a statute's binding_scope,
    # hierarchy_level, and override_mechanism are usually self-evident from
    # jurisdiction/authority_type alone; a case's are not).
    binding_scope: str | None = None       # who is actually bound (free text, per the design doc)
    # Integer rank within this authority's OWN system, not a cross-system
    # comparison -- 1 is that system's highest authority (e.g., a state's
    # highest court, or a constitution within its own sovereign), larger
    # numbers are lower (trial court > intermediate appellate > highest
    # court becomes 3 > 2 > 1). Per the design doc: "an integer ... capturing
    # court/authority rank within its own system."
    hierarchy_level: int | None = None
    override_mechanism: str | None = None  # how this specific authority can change

    def to_dict(self) -> dict:
        d = {
            "document_id": self.document_id,
            "title": self.title,
            "authority_type": self.authority_type.value,
            "jurisdiction": self.jurisdiction,
            "citation": self.citation,
            "official_source_url": self.official_source_url,
            "publisher": self.publisher,
            "retrieval_timestamp": self.retrieval_timestamp,
            "sha256_hash": self.sha256_hash,
            "verification_status": self.verification_status.value,
            "court": self.court,
            "publication_or_effective_date": self.publication_or_effective_date,
            "version": self.version,
            "superseded": self.superseded,
            "licensing_status": self.licensing_status,
            "source_layer": self.source_layer.value,
            "topics": self.topics,
            "cross_references": self.cross_references,
            "notes": self.notes,
            "binding_scope": self.binding_scope,
            "hierarchy_level": self.hierarchy_level,
            "override_mechanism": self.override_mechanism,
        }
        return d


@dataclass
class StatuteSection:
    """One real, normalized statutory section -- the machine-readable
    derivative of an immutable source document."""

    section_id: str
    title: str
    paragraphs: list[str]
    citation: str
    source_document_id: str
    topics: list[str] = field(default_factory=list)
    cross_references: list[str] = field(default_factory=list)
    defined_terms: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "section_id": self.section_id,
            "title": self.title,
            "paragraphs": self.paragraphs,
            "citation": self.citation,
            "source_document_id": self.source_document_id,
            "topics": self.topics,
            "cross_references": self.cross_references,
            "defined_terms": self.defined_terms,
        }


@dataclass
class ProvisionComparison:
    """Links one underlying UCC provision across the three layers (Mission
    10): the Model text, one or more jurisdictions' enactments of it,
    known textual differences between them, and interpretive material.
    `model_section_id` is None until a licensed Model-UCC source is
    actually ingested (see docs/ucc-source-licensing-audit.md) -- this
    dataclass exists so that gap is representable and queryable, not
    hidden."""

    provision_key: str  # stable identifier for "the same provision" across layers, e.g. "ucc-2-314-merchantability"
    model_section_id: str | None = None
    enactment_section_ids: dict[str, str] = field(default_factory=dict)  # jurisdiction -> section_id
    known_differences: list[str] = field(default_factory=list)
    interpretation_document_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "provision_key": self.provision_key,
            "model_section_id": self.model_section_id,
            "enactment_section_ids": self.enactment_section_ids,
            "known_differences": self.known_differences,
            "interpretation_document_ids": self.interpretation_document_ids,
        }


class TransactionScope(str, Enum):
    """Whether a sale-of-goods transaction is domestic or international
    (Mission 12). Never assume UCC Article 2 automatically governs --
    that's exactly the assumption this enum exists to block."""

    DOMESTIC_UCC = "DOMESTIC_UCC"          # both parties same country; UCC Article 2 analysis applies
    INTERNATIONAL_CISG = "INTERNATIONAL_CISG"  # CISG applies (or presumptively applies)
    INTERNATIONAL_NON_CISG = "INTERNATIONAL_NON_CISG"  # international, but CISG excluded/opted out -- domestic law of some forum applies instead
    UNDETERMINED = "UNDETERMINED"


@dataclass
class CisgApplicabilityAssessment:
    """Schema for a future CISG applicability-analysis module (Mission 12
    scope: schema/architecture only, no full curriculum this run -- see
    law-engine/docs/cisg-architecture-design.md for the reasoning). Models
    the real, disclosed CISG Article 1/2/6 applicability questions without
    asserting a legal conclusion the engine hasn't actually verified."""

    transaction_id: str
    seller_place_of_business_country: str
    buyer_place_of_business_country: str
    both_in_contracting_states: bool | None = None  # None = not yet determined
    # Article 1(1)(b) applicability (via private international law) is
    # forum-dependent, not a fact about the parties alone -- the US made
    # an Article 95 reservation disclaiming 1(1)(b), so a US court and a
    # non-reserving state's court can reach different applicability
    # conclusions on an identical contract. See
    # docs/cisg-architecture-design.md Part 2's forum-relative schema
    # (this dataclass is the smaller v1 in models.py; that doc proposes a
    # fuller v2 for a future dedicated services/cisg.py module).
    forum_country: str = ""
    forum_is_article_95_declarant: bool | None = None
    private_international_law_leads_to_contracting_state: bool | None = None
    parties_opted_out_under_article_6: bool = False
    is_consumer_goods_purchase: bool = False  # Article 2(a) exclusion
    other_article_2_exclusion: str | None = None  # e.g. "auction", "ships/vessels/aircraft", "electricity", "negotiable instruments/money"
    scope: TransactionScope = TransactionScope.UNDETERMINED
    reasoning_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "seller_place_of_business_country": self.seller_place_of_business_country,
            "buyer_place_of_business_country": self.buyer_place_of_business_country,
            "both_in_contracting_states": self.both_in_contracting_states,
            "forum_country": self.forum_country,
            "forum_is_article_95_declarant": self.forum_is_article_95_declarant,
            "private_international_law_leads_to_contracting_state": self.private_international_law_leads_to_contracting_state,
            "parties_opted_out_under_article_6": self.parties_opted_out_under_article_6,
            "is_consumer_goods_purchase": self.is_consumer_goods_purchase,
            "other_article_2_exclusion": self.other_article_2_exclusion,
            "scope": self.scope.value,
            "reasoning_notes": self.reasoning_notes,
        }


class PedagogicalSubjectKind(str, Enum):
    """What kind of thing a PedagogicalContract is teaching -- controls
    which fields a builder would typically populate (e.g. a DOCUMENT leans
    on signing_authentication_process; a CONCEPT usually leaves it blank),
    without making any field structurally mandatory, since not every field
    applies to every subject."""

    CONCEPT = "CONCEPT"
    RULE = "RULE"
    PROCEDURE = "PROCEDURE"
    DOCUMENT = "DOCUMENT"
    ASSET = "ASSET"
    TRANSACTION = "TRANSACTION"


@dataclass
class PedagogicalMetaphor:
    """A simplified, non-authoritative illustration used only to build
    intuition. Deliberately its own dataclass (rather than a string field
    reused for both purposes) so a caller can never structurally confuse
    an illustration with PedagogicalContract.governing_text_excerpt -- the
    two live in different fields with different types, and this one
    self-labels as pedagogical-only even if passed around out of context."""

    illustration: str
    disclaimer: str = (
        "This is a simplified teaching illustration, not a legal rule -- it "
        "never overrides governing_text_excerpt or authority_citation."
    )
    is_pedagogical_only: bool = True

    def to_dict(self) -> dict:
        return {
            "illustration": self.illustration,
            "disclaimer": self.disclaimer,
            "is_pedagogical_only": self.is_pedagogical_only,
        }


@dataclass
class FactSensitivityNote:
    """One "what changes if one fact changes" note -- deliberately a
    smaller shape than transaction_lifecycle.py's ChangedFactVariant
    (which also carries a required section_id) since a PedagogicalContract
    field may need to note fact-sensitivity even where citation is
    optional, e.g. a general drafting caution rather than a statutory
    cross-reference."""

    changed_fact: str
    effect: str
    citation: str | None = None

    def to_dict(self) -> dict:
        return {
            "changed_fact": self.changed_fact,
            "effect": self.effect,
            "citation": self.citation,
        }


@dataclass
class PedagogicalContract:
    """Reusable schema for teaching one important legal concept, rule,
    procedure, document, asset, or transaction end-to-end (Live Run 1.39).
    Every subject-specific teaching field is optional -- not every subject
    has a signing/indorsement process, and not every subject has a known
    point of confusion worth naming -- but the fields that ground the
    contract in a real, verifiable source (authority_citation,
    authority_type, jurisdiction, verification_status, confidence_label)
    are required, on the same principle as SourceManifest and
    ProvisionComparison above: an unpopulated pedagogical field is honest
    (we haven't written that part yet), but an invented citation is not.
    Reuses VerificationStatus/ConfidenceLabel rather than a parallel
    trust-labeling system, so a caller-facing surface has exactly one place
    to check how sure the engine is. See services/pedagogical_contract.py
    for a real, fully-populated example."""

    contract_id: str
    subject_name: str
    subject_kind: PedagogicalSubjectKind
    authority_citation: str
    authority_type: AuthorityType
    jurisdiction: str
    verification_status: VerificationStatus
    confidence_label: ConfidenceLabel
    source_layer: SourceLayer = SourceLayer.ENACTMENT
    source_document_id: str | None = None
    section_id: str | None = None
    governing_text_excerpt: str | None = None
    version_or_effective_date: str | None = None
    what_it_is: str | None = None
    why_it_exists: str | None = None
    how_to_recognize: list[str] = field(default_factory=list)
    what_it_does: str | None = None
    what_to_do_with_it: str | None = None
    timing_notes: str | None = None
    signing_authentication_process: str | None = None
    who_signs_or_acts: list[str] = field(default_factory=list)
    what_can_go_wrong: list[str] = field(default_factory=list)
    commonly_confused_with: list[str] = field(default_factory=list)
    fact_sensitivity: list[FactSensitivityNote] = field(default_factory=list)
    metaphor: PedagogicalMetaphor | None = None

    def to_dict(self) -> dict:
        return {
            "contract_id": self.contract_id,
            "subject_name": self.subject_name,
            "subject_kind": self.subject_kind.value,
            "authority_citation": self.authority_citation,
            "authority_type": self.authority_type.value,
            "jurisdiction": self.jurisdiction,
            "verification_status": self.verification_status.value,
            "confidence_label": self.confidence_label.value,
            "source_layer": self.source_layer.value,
            "source_document_id": self.source_document_id,
            "section_id": self.section_id,
            "governing_text_excerpt": self.governing_text_excerpt,
            "version_or_effective_date": self.version_or_effective_date,
            "what_it_is": self.what_it_is,
            "why_it_exists": self.why_it_exists,
            "how_to_recognize": self.how_to_recognize,
            "what_it_does": self.what_it_does,
            "what_to_do_with_it": self.what_to_do_with_it,
            "timing_notes": self.timing_notes,
            "signing_authentication_process": self.signing_authentication_process,
            "who_signs_or_acts": self.who_signs_or_acts,
            "what_can_go_wrong": self.what_can_go_wrong,
            "commonly_confused_with": self.commonly_confused_with,
            "fact_sensitivity": [n.to_dict() for n in self.fact_sensitivity],
            "metaphor": self.metaphor.to_dict() if self.metaphor is not None else None,
        }


def now_iso() -> str:
    return datetime.now().isoformat()


# Real ordering: index position reflects how much verification has
# actually happened, not a claim about likelihood of correctness --
# reused directly by legal_proof_graph.py's own weakest-link
# computations (list(VerificationStatus) gives this exact order).
_VERIFICATION_STATUS_ORDER: list[VerificationStatus] = list(VerificationStatus)

# Real mapping (Live Run 1.60, Mission 8, Phase 5), implementing the
# mapping services/legal_proof_graph.py's own docstring previously
# flagged as "future work, not implemented here." A caller-facing
# ConfidenceLabel must never overclaim relative to how a source was
# actually verified -- CONFLICT and UNKNOWN are never presented as
# anything but their own honest labels; a source that is merely
# DISCOVERED or RETRIEVED (not yet independently checked against its own
# claimed source) is UNVERIFIED, never LIKELY or VERIFIED, even if it
# turns out to be correct.
_VERIFICATION_STATUS_TO_CONFIDENCE_LABEL: dict[VerificationStatus, ConfidenceLabel] = {
    VerificationStatus.CONFLICT: ConfidenceLabel.CONFLICTING,
    VerificationStatus.UNKNOWN: ConfidenceLabel.UNVERIFIED,
    VerificationStatus.DISCOVERED: ConfidenceLabel.UNVERIFIED,
    VerificationStatus.RETRIEVED: ConfidenceLabel.UNVERIFIED,
    VerificationStatus.SOURCE_VERIFIED: ConfidenceLabel.LIKELY,
    VerificationStatus.AUTHORITY_CLASSIFIED: ConfidenceLabel.LIKELY,
    VerificationStatus.CURRENTNESS_CHECKED: ConfidenceLabel.LIKELY,
    VerificationStatus.CROSS_VERIFIED: ConfidenceLabel.VERIFIED,
    VerificationStatus.TRUSTED_FOR_ANALYSIS: ConfidenceLabel.VERIFIED,
}


def verification_status_to_confidence_label(status: VerificationStatus) -> ConfidenceLabel:
    """The real mapping a caller-facing surface must use to turn an
    internal VerificationStatus into the coarser ConfidenceLabel it's
    allowed to show a user -- never invented ad hoc at each call site."""
    return _VERIFICATION_STATUS_TO_CONFIDENCE_LABEL[status]


def weakest_verification_status(statuses: list[VerificationStatus]) -> VerificationStatus:
    """Real, shared weakest-link helper -- the same ordinal pattern
    services/legal_proof_graph.py's own weakest_link_verification_status
    already used for facts, factored out here so Phase 5's new
    authority-chain computation reuses it rather than re-deriving the
    ordering logic a second time."""
    if not statuses:
        raise ValueError("weakest_verification_status() requires at least one status.")
    return min(statuses, key=_VERIFICATION_STATUS_ORDER.index)

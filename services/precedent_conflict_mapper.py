"""Law Engine -- Precedent Conflict Mapper prototype (Live Run 1.60,
Mission 8, Phase 6). Real, first, bounded implementation of the pipeline
docs/law-engine-precedent-conflict-thesis.md §3 designed, applied to
exactly the one flagship fact pattern this run actually built real,
verified data for: who is entitled to enforce a transferred promissory
note, indorsed in blank, given
services/legal_proof_graph.py's build_promissory_note_enforcement_proof_
graph() (Florida's Rodriguez v. Wells Fargo Bank, N.A. and North
Carolina's Greene v. Trustee Services of Carolina, LLC -- the case Live
Run 1.59 knew as "In re Foreclosure of Kenley").

This is a real prototype demonstrating the pipeline works end-to-end on
real data -- NOT a general-purpose engine covering arbitrary legal
questions. It classifies a NewFactPattern only along the dimensions this
run's real, ingested authority chain actually covers (jurisdiction,
proceeding type, indorsement, and Florida's own servicer-authority
wrinkle) -- it has no opinion about any fact pattern outside that real
scope, and says so honestly rather than guessing.

Never personalized legal advice -- see DISCLAIMER below, reused on every
PrecedentConflictAssessment this module returns, matching this codebase's
existing disclaimer conventions (services/models.py's
PedagogicalMetaphor.disclaimer; services/syntax_engine.py's module-level
disclaimer).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.legal_proof_graph import LegalProofGraph, LegalProofGraphError

DISCLAIMER = (
    "This is authority-mapping and confidence explanation, not "
    "personalized legal advice -- it never tells you what to do, only "
    "which real authorities exist, whether they bind or merely persuade "
    "in your situation, and how confident the mapping actually is. "
    "Consult a licensed attorney in the relevant jurisdiction before "
    "acting on any real transaction."
)


class ProceedingType(str, Enum):
    """The real, bounded set of proceeding types this prototype can
    reason about -- exactly the two the flagship pair actually decided,
    plus an honest third bucket for anything that doesn't clearly match
    either. Never silently forced into one of the two known types."""

    JUDICIAL_FORECLOSURE_COMPLAINT = "JUDICIAL_FORECLOSURE_COMPLAINT"  # Rodriguez's own proceeding type (Florida)
    POWER_OF_SALE_HEARING = "POWER_OF_SALE_HEARING"                    # Greene/Kenley's own proceeding type (North Carolina)
    UNDETERMINED_OR_HYBRID = "UNDETERMINED_OR_HYBRID"                  # neither clearly matches -- the real, disclosed open question both source docs flagged


class PrecedentConflictCategory(str, Enum):
    """The four required output categories
    docs/law-engine-precedent-conflict-thesis.md §3 specified -- never
    collapsed into a fifth, softer category, and never silently upgraded
    from a lower-confidence one."""

    HIGH_CONFIDENCE_CONTROLLING_AUTHORITY = "HIGH_CONFIDENCE_CONTROLLING_AUTHORITY"
    FACT_SENSITIVE_DISTINGUISHABLE = "FACT_SENSITIVE_DISTINGUISHABLE"
    PERSUASIVE_DISAGREEMENT = "PERSUASIVE_DISAGREEMENT"
    GENUINE_UNRESOLVED_UNCERTAINTY = "GENUINE_UNRESOLVED_UNCERTAINTY"


_KNOWN_JURISDICTIONS = {"Florida", "North Carolina"}
_JURISDICTION_TO_AUTHORITY_NODE_ID = {
    "Florida": "authority-rodriguez-fl-4dca-2015",
    "North Carolina": "authority-greene-nc-app-2016",
}
_JURISDICTION_TO_PROCEEDING_TYPE = {
    "Florida": ProceedingType.JUDICIAL_FORECLOSURE_COMPLAINT,
    "North Carolina": ProceedingType.POWER_OF_SALE_HEARING,
}


@dataclass
class NewFactPattern:
    """A real, small, honestly-bounded fact pattern to classify against
    the flagship graph's authority chain -- not a general-purpose legal
    intake form."""

    jurisdiction: str
    proceeding_type: ProceedingType
    note_indorsed_in_blank: bool
    party_in_possession_at_relevant_time: bool
    # Florida-specific wrinkle Phase 3 actually found in Rodriguez's real
    # holding (see services/ingestion_case_law.py's own notes) -- suing as
    # a servicer without proven authority to act for the real party in
    # interest. Irrelevant outside Florida's own proceeding type, but kept
    # as a real, honest field rather than silently dropped.
    suing_as_servicer_without_proven_authority: bool = False


@dataclass
class PrecedentConflictAssessment:
    category: PrecedentConflictCategory
    explanation: str
    controlling_or_persuasive_citations: list[str] = field(default_factory=list)
    distinguishing_fact: str | None = None
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "category": self.category.value,
            "explanation": self.explanation,
            "controlling_or_persuasive_citations": self.controlling_or_persuasive_citations,
            "distinguishing_fact": self.distinguishing_fact,
            "disclaimer": self.disclaimer,
        }


def _citation_for(graph: LegalProofGraph, node_id: str) -> str:
    authority = next((a for a in graph.authorities if a.node_id == node_id), None)
    if authority is None:
        raise LegalProofGraphError(f"No authority {node_id!r} in graph {graph.graph_id!r}.")
    return authority.citation


def classify_precedent_conflict(
    graph: LegalProofGraph, fact_pattern: NewFactPattern
) -> PrecedentConflictAssessment:
    """The real pipeline, applied to exactly this run's real authority
    chain. See module docstring for scope -- this function has no opinion
    about any jurisdiction or proceeding type outside what
    build_promissory_note_enforcement_proof_graph() actually built."""
    rodriguez_citation = _citation_for(graph, "authority-rodriguez-fl-4dca-2015")
    greene_citation = _citation_for(graph, "authority-greene-nc-app-2016")

    if fact_pattern.jurisdiction in _KNOWN_JURISDICTIONS:
        # A binding, current-version authority already exists for this
        # exact jurisdiction -- the question is whether the new facts
        # materially match it.
        controlling_citation = (
            rodriguez_citation if fact_pattern.jurisdiction == "Florida" else greene_citation
        )
        expected_proceeding_type = _JURISDICTION_TO_PROCEEDING_TYPE[fact_pattern.jurisdiction]

        if not fact_pattern.note_indorsed_in_blank:
            # Both cases' own real holdings turn specifically on a note
            # indorsed IN BLANK (Rodriguez's Conner concurrence: "with
            # bearer notes, possession of the note is the significant
            # core element"; Greene: "[b]ecause the Note was indorsed in
            # blank ... U.S. Bank was the holder"). A specially-indorsed
            # or unendorsed note isn't the fact pattern either court
            # actually decided.
            return PrecedentConflictAssessment(
                category=PrecedentConflictCategory.FACT_SENSITIVE_DISTINGUISHABLE,
                explanation=(
                    f"{controlling_citation} is real, binding authority in "
                    f"{fact_pattern.jurisdiction}, but its own holding turns "
                    "specifically on a note indorsed IN BLANK -- this fact "
                    "pattern's note is not. The controlling rule may still "
                    "apply by analogy, but the court's own reasoning was "
                    "never tested against a specially-indorsed or "
                    "unendorsed note, so this is not a clean, direct "
                    "application."
                ),
                controlling_or_persuasive_citations=[controlling_citation],
                distinguishing_fact="The note is not indorsed in blank.",
            )

        if fact_pattern.jurisdiction == "Florida" and fact_pattern.proceeding_type == expected_proceeding_type:
            if fact_pattern.suing_as_servicer_without_proven_authority:
                return PrecedentConflictAssessment(
                    category=PrecedentConflictCategory.FACT_SENSITIVE_DISTINGUISHABLE,
                    explanation=(
                        f"{rodriguez_citation} is real, binding authority in "
                        "Florida, and this fact pattern shares Rodriguez's "
                        "own distinguishing fact: a servicer suing in its "
                        "own name without proven authority (a power of "
                        "attorney or pooling-and-servicing agreement) to "
                        "act for the real party in interest. Rodriguez's "
                        "own holding directly controls this specific "
                        "combination of facts -- standing was not "
                        "established as of the filing date."
                    ),
                    controlling_or_persuasive_citations=[rodriguez_citation],
                    distinguishing_fact=(
                        "The plaintiff is a servicer suing without proven "
                        "authority from the real party in interest."
                    ),
                )
            if not fact_pattern.party_in_possession_at_relevant_time:
                return PrecedentConflictAssessment(
                    category=PrecedentConflictCategory.FACT_SENSITIVE_DISTINGUISHABLE,
                    explanation=(
                        f"{rodriguez_citation} is real, binding authority in "
                        "Florida requiring standing/holder status to be "
                        "proven as of the complaint's filing date. This "
                        "fact pattern does not establish possession at "
                        "that time, which is the exact fact Rodriguez's "
                        "own holding turns on."
                    ),
                    controlling_or_persuasive_citations=[rodriguez_citation],
                    distinguishing_fact="The party was not in possession of the note as of the filing date.",
                )
            return PrecedentConflictAssessment(
                category=PrecedentConflictCategory.HIGH_CONFIDENCE_CONTROLLING_AUTHORITY,
                explanation=(
                    f"{rodriguez_citation} is real, binding authority in "
                    "Florida, decided under the current statutory version, "
                    "and this fact pattern materially matches its own "
                    "requirements: a blank-indorsed note, possession "
                    "established as of the filing date, and no unproven-"
                    "servicer-authority problem. No adverse binding "
                    "Florida authority or unresolved subsequent history "
                    "was found in this run's real, retrieved material."
                ),
                controlling_or_persuasive_citations=[rodriguez_citation],
            )

        if (
            fact_pattern.jurisdiction == "North Carolina"
            and fact_pattern.proceeding_type == expected_proceeding_type
        ):
            if not fact_pattern.party_in_possession_at_relevant_time:
                return PrecedentConflictAssessment(
                    category=PrecedentConflictCategory.FACT_SENSITIVE_DISTINGUISHABLE,
                    explanation=(
                        f"{greene_citation} is real, binding authority in "
                        "North Carolina, but its own holding requires "
                        "production of the note, in the party's own "
                        "possession, AT THE HEARING ITSELF. This fact "
                        "pattern does not establish possession at that "
                        "time."
                    ),
                    controlling_or_persuasive_citations=[greene_citation],
                    distinguishing_fact="The party was not in possession of the note at the hearing.",
                )
            return PrecedentConflictAssessment(
                category=PrecedentConflictCategory.HIGH_CONFIDENCE_CONTROLLING_AUTHORITY,
                explanation=(
                    f"{greene_citation} is real, binding authority in North "
                    "Carolina, decided under the current statutory "
                    "version, and this fact pattern materially matches "
                    "its own requirements: a blank-indorsed note, produced "
                    "at the hearing, in the party's own possession. No "
                    "adverse binding North Carolina authority or "
                    "unresolved subsequent history was found in this "
                    "run's real, retrieved material."
                ),
                controlling_or_persuasive_citations=[greene_citation],
            )

        # Known jurisdiction, but a proceeding type that doesn't match
        # that jurisdiction's own known real-world proceeding type (e.g.,
        # a hypothetical Florida non-judicial hearing, or a North Carolina
        # judicial complaint) -- the controlling case's own proceeding-
        # type-specific reasoning may not transfer cleanly.
        return PrecedentConflictAssessment(
            category=PrecedentConflictCategory.FACT_SENSITIVE_DISTINGUISHABLE,
            explanation=(
                f"{controlling_citation} is real, binding authority in "
                f"{fact_pattern.jurisdiction}, but it was decided in a "
                f"{expected_proceeding_type.value.replace('_', ' ').lower()}, "
                "and this fact pattern involves a different kind of "
                "proceeding. The controlling case's own procedural-timing "
                "reasoning is tied to the proceeding type it actually "
                "decided, so it may not transfer cleanly."
            ),
            controlling_or_persuasive_citations=[controlling_citation],
            distinguishing_fact="The proceeding type differs from the one the controlling case actually decided.",
        )

    # No binding authority in this jurisdiction at all -- Rodriguez and
    # Greene are both merely persuasive here, per
    # docs/law-engine-precedent-conflict-thesis.md §1's binding/persuasive
    # distinction.
    if fact_pattern.proceeding_type == ProceedingType.UNDETERMINED_OR_HYBRID:
        # Neither case's own real distinguishing rationale (proceeding
        # type) clearly applies -- exactly the real, disclosed open
        # question both docs/law-engine-precedent-conflict-thesis.md §5
        # ("What remains uncertain") and this run's own retrieved material
        # flagged, not resolvable by analogy alone.
        return PrecedentConflictAssessment(
            category=PrecedentConflictCategory.GENUINE_UNRESOLVED_UNCERTAINTY,
            explanation=(
                f"{fact_pattern.jurisdiction} has not decided this "
                "question, so both Rodriguez ({rodriguez}) and Greene "
                "({greene}) are merely persuasive here -- and they point "
                "in different directions on WHEN holder status/authority "
                "must be proven. Both cases' own real reasoning ties its "
                "answer to a specific proceeding type (a judicial "
                "complaint for Rodriguez, a power-of-sale hearing for "
                "Greene), and this fact pattern's proceeding type does not "
                "clearly match either -- so the one real, named "
                "distinction that explains why the two cases don't "
                "actually conflict (see the flagship proof graph's own "
                "DISTINGUISHED_BY edge) does not resolve which line this "
                "jurisdiction would likely follow. This is honestly "
                "unsettled, not a confident guess dressed up as one."
            ).format(rodriguez=rodriguez_citation, greene=greene_citation),
            controlling_or_persuasive_citations=[rodriguez_citation, greene_citation],
        )

    return PrecedentConflictAssessment(
        category=PrecedentConflictCategory.PERSUASIVE_DISAGREEMENT,
        explanation=(
            f"{fact_pattern.jurisdiction} has not decided this question, "
            f"so both Rodriguez ({rodriguez_citation}) and Greene "
            f"({greene_citation}) are merely persuasive here, not "
            "controlling. They are useful for argument on both sides: "
            "Rodriguez supports requiring proof of holder status/authority "
            "as of an earlier point in the proceeding; Greene supports "
            "accepting proof produced later, at the hearing itself. This "
            "fact pattern's own proceeding type "
            f"({fact_pattern.proceeding_type.value.replace('_', ' ').lower()}) "
            "more closely resembles one of the two real proceeding types "
            "already decided, which is relevant to which persuasive "
            "authority is the closer analogy -- but neither binds this "
            "jurisdiction."
        ),
        controlling_or_persuasive_citations=[rodriguez_citation, greene_citation],
    )

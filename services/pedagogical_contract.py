"""Law Engine -- real, populated PedagogicalContract example (Live Run
1.39). Builds one concrete instance of services.models.PedagogicalContract
for the implied warranty of merchantability, Va. Code Ann. Section
8.2-314, using the real ingested statutory text
(services/retrieval.get_section) rather than inventing statutory content.
This mirrors transaction_lifecycle.py's own pattern of requiring a real
ingested section before building anything that cites it.
"""

from __future__ import annotations

import sys
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.models import (
    AuthorityType,
    ConfidenceLabel,
    FactSensitivityNote,
    PedagogicalContract,
    PedagogicalMetaphor,
    PedagogicalSubjectKind,
    SourceLayer,
    VerificationStatus,
)
from services.retrieval import get_section


class PedagogicalContractError(Exception):
    """Raised when a real ingested section a builder depends on is
    missing -- never silently substituted with invented statutory text."""


def _require_section(section_id: str) -> dict:
    section = get_section(section_id)
    if section is None:
        raise PedagogicalContractError(
            f"No ingested section {section_id!r} -- cannot build a "
            "PedagogicalContract without a real source."
        )
    return section


def build_implied_warranty_of_merchantability_contract() -> PedagogicalContract:
    """Real, citation-backed PedagogicalContract for the implied warranty
    of merchantability, grounded in the actual ingested text of Va. Code
    Ann. Section 8.2-314 (library/normalized/ucc/article-2-sections.json)
    -- the same section already used as the correct-answer citation in
    transaction_lifecycle.py's "merchant-and-warranties" stage, so this
    contract and that lifecycle stage describe the same real rule from two
    different reusable schemas."""
    section = _require_section("8.2-314")
    merchant_section = _require_section("8.2-104")
    express_warranty_section = _require_section("8.2-313")

    governing_text_excerpt = section["paragraphs"][0]
    # 8.2-316 is not itself an ingested section (only the 11 sections
    # transaction_lifecycle.py's own docstring names are), but 8.2-314's
    # own ingested paragraph (1) directly names it -- "Unless excluded or
    # modified (§ 8.2-316)" -- so this citation is derived from real
    # ingested text, not invented. cross_references confirms the same
    # pointer independently.
    if "8.2-316" not in section["cross_references"]:
        raise PedagogicalContractError(
            "8.2-314's ingested cross_references no longer name 8.2-316 -- "
            "the disclaimer citation below would no longer be grounded in "
            "ingested data."
        )
    disclaimer_citation = section["citation"].replace(section["section_id"], "8.2-316")

    return PedagogicalContract(
        contract_id="implied-warranty-of-merchantability-va-8.2-314",
        subject_name="Implied warranty of merchantability",
        subject_kind=PedagogicalSubjectKind.RULE,
        authority_citation=section["citation"],
        authority_type=AuthorityType.STATUTE,
        jurisdiction="Commonwealth of Virginia",
        verification_status=VerificationStatus.SOURCE_VERIFIED,
        confidence_label=ConfidenceLabel.VERIFIED,
        source_layer=SourceLayer.ENACTMENT,
        source_document_id=section["source_document_id"],
        section_id=section["section_id"],
        governing_text_excerpt=governing_text_excerpt,
        version_or_effective_date="1964, c. 219.",
        what_it_is=(
            "A warranty that goods will be merchantable, implied by operation "
            "of law in a contract for sale -- it exists even though no one "
            "wrote it down or promised it out loud."
        ),
        why_it_exists=(
            "Without it, a buyer would have no protection unless they thought "
            "to negotiate an express promise about quality. The law instead "
            "assumes a merchant-seller impliedly stands behind goods of the "
            "kind they deal in, unless that assumption is displaced."
        ),
        how_to_recognize=[
            "The seller is a merchant with respect to goods of that kind "
            f'({merchant_section["citation"]} defines "merchant").',
            "There is a contract for the sale of goods.",
            "Nothing in the contract has excluded or modified the warranty "
            f'under {disclaimer_citation} (e.g. no "as is" or "with '
            'all faults" language, no conspicuous disclaimer of merchantability).',
        ],
        what_it_does=(
            "Creates an implied contractual promise, enforceable by the buyer, "
            "that the goods meet the six merchantability standards listed in "
            f'{section["citation"]}(2): passing without objection in the trade, '
            "fair average quality (for fungibles), fitness for ordinary "
            "purposes, even kind/quality/quantity within variations permitted "
            "by the agreement, adequate packaging/labeling, and conformity to "
            "any promises on the container or label."
        ),
        what_to_do_with_it=(
            "A buyer who receives nonmerchantable goods can treat the warranty "
            "as breached and pursue the buyer's remedies already modeled in "
            "transaction_lifecycle.py's delivery-and-remedies stage (Va. Code "
            "Ann. Section 8.2-711 and related sections). A seller who does not "
            f'want the warranty to attach must act under {disclaimer_citation} '
            "before or at contract formation, not after a dispute arises."
        ),
        timing_notes=(
            "The warranty attaches at the time of sale/contract formation, not "
            "at delivery -- whether the seller was a merchant \"with respect to "
            "goods of that kind\" is judged as of that same transaction. A "
            "disclaimer raised only after a defect surfaces is generally too "
            "late to have modified the contract."
        ),
        signing_authentication_process=None,
        who_signs_or_acts=[
            "Seller (must be a merchant with respect to goods of that kind for "
            "the warranty to attach -- see " + merchant_section["citation"] + ").",
            "Buyer (holds the right to enforce the warranty; no signature or "
            "acceptance formality is required to receive its protection).",
        ],
        what_can_go_wrong=[
            "Assuming the warranty applies to a private, non-merchant seller "
            "(a garage-sale or casual seller is not a merchant with respect to "
            "the goods they occasionally sell).",
            f'Missing an effective disclaimer under {disclaimer_citation} that already '
            "excluded the warranty before the dispute arose.",
            "Conflating merchantability (a baseline, implied floor) with an "
            "express warranty (an affirmative promise the seller actually "
            "made) -- the two arise from different sections and different "
            "seller conduct.",
        ],
        commonly_confused_with=[
            f'Express warranty ({express_warranty_section["citation"]}) -- created by '
            "the seller's own affirmation, promise, or description, not "
            "implied by merchant status alone.",
        ],
        fact_sensitivity=[
            FactSensitivityNote(
                changed_fact="The seller is a private individual, not a merchant dealing in goods of that kind.",
                effect=(
                    f'{section["citation"]}\'s implied warranty of merchantability '
                    "does not attach -- the merchant-seller requirement is not met. "
                    "An express warranty could still arise from the seller's own "
                    "statements under Section 8.2-313, but that is a different rule."
                ),
                citation=section["citation"],
            ),
            FactSensitivityNote(
                changed_fact='The listing said "sold as-is, all sales final."',
                effect=(
                    f'{disclaimer_citation} allows the implied warranty of '
                    "merchantability to be excluded by conspicuous language like "
                    '"as is" -- the warranty most likely never attaches.'
                ),
                citation=disclaimer_citation,
            ),
        ],
        metaphor=PedagogicalMetaphor(
            illustration=(
                "Think of it like buying a sandwich from a sandwich shop: even "
                "if the cashier never says a word about it, you reasonably "
                "expect the sandwich is actually fit to eat, because that's "
                "what a shop selling sandwiches implicitly stands behind. A "
                "friend selling you their half-eaten lunch off a park bench "
                "isn't making that same implicit promise."
            ),
        ),
    )


if __name__ == "__main__":
    contract = build_implied_warranty_of_merchantability_contract()
    import json

    print(json.dumps(contract.to_dict(), indent=2, ensure_ascii=False))

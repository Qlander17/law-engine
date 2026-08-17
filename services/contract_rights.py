"""Law Engine -- Contracts as assets/rights (Live Run 1.39/1.40). A
contract is not just "a piece of paper" -- the physical/electronic
document, the agreement it records, and the legal rights and obligations
that agreement creates are four distinct things that happen to travel
together most of the time but can be separated (a lost document doesn't
destroy the agreement; an assigned payment right can move to someone who
was never a party to the original agreement).

Same trust-but-verify discipline as asset_intelligence.py and
pedagogical_contract.py: the running "agreement" example is grounded in
the real ingested Va. Code Ann. Section 8.2-204 (the same contract-
formation section transaction_lifecycle.py's formation stage already
uses). The specific UCC Article 9 collateral classifications a payment
right can fall into (instrument, chattel paper, account, payment
intangible) are well-known, generally-accurate concepts, but Article 9 is
NOT yet ingested in this codebase -- those claims are explicitly labeled
ungrounded rather than cited to an invented section.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.retrieval import get_section

ARTICLE_9_PAYMENT_RIGHT_CLASSIFICATION_NOTE = (
    "UCC Article 9's specific collateral classifications for a payment "
    "right (instrument, chattel paper, account, payment intangible) are "
    "well-known, generally-accurate legal concepts, but Article 9 is not "
    "yet ingested in this codebase -- this classification is not traced "
    "to any specific ingested statutory section."
)


class ContractRightsError(Exception):
    """Raised when a builder's real ingested section dependency is
    missing -- never silently substituted with invented statutory text."""


@dataclass
class UccPaymentRightClassification:
    """One possible UCC Article 9 collateral classification for the
    payment right a contract creates. Deliberately its own dataclass
    (rather than a single string) so a caller must engage with WHY a
    given payment right falls into one bucket rather than another, instead
    of treating "UCC classification" as one flat label."""

    category: str  # "instrument" | "chattel paper" | "account" | "payment intangible"
    definition_summary: str
    distinguishing_feature: str
    example: str

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "definition_summary": self.definition_summary,
            "distinguishing_feature": self.distinguishing_feature,
            "example": self.example,
        }


@dataclass
class ContractAnatomy:
    """Splits "a contract" into its real, legally-distinct layers so a
    learner stops treating them as interchangeable. `citation`/`section_id`
    ground the_agreement_description in a real ingested statutory section
    when one exists; ucc_payment_right_classifications are disclosed as
    ungrounded (Article 9 is not yet ingested) via
    ucc_classification_grounding_note rather than assigned a fake
    citation.
    """

    contract_id: str
    subject_name: str
    physical_document_description: str
    the_agreement_description: str
    rights_and_obligations: list[str]
    payment_rights_description: str
    assignability: str
    ucc_payment_right_classifications: list[UccPaymentRightClassification]
    ucc_classification_grounding_note: str
    common_confusions: list[str]
    citation: str | None = None
    section_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "contract_id": self.contract_id,
            "subject_name": self.subject_name,
            "physical_document_description": self.physical_document_description,
            "the_agreement_description": self.the_agreement_description,
            "rights_and_obligations": self.rights_and_obligations,
            "payment_rights_description": self.payment_rights_description,
            "assignability": self.assignability,
            "ucc_payment_right_classifications": [c.to_dict() for c in self.ucc_payment_right_classifications],
            "ucc_classification_grounding_note": self.ucc_classification_grounding_note,
            "common_confusions": self.common_confusions,
            "citation": self.citation,
            "section_id": self.section_id,
        }


def _require_section(section_id: str) -> dict:
    section = get_section(section_id)
    if section is None:
        raise ContractRightsError(
            f"No ingested section {section_id!r} -- cannot build a "
            "ContractAnatomy that cites it without a real source."
        )
    return section


def build_laptop_sale_contract_anatomy() -> ContractAnatomy:
    """Reuses the real ingested Va. Code Ann. Section 8.2-204 (contract
    formation) -- the same section, and the same running used-laptop-sale
    fact pattern, as transaction_lifecycle.py's formation stage -- as the
    concrete "the agreement" example, so a learner can see the same real
    statute do double duty: forming the agreement, and (in this module)
    being distinguished from the paper and from the payment right it
    creates."""
    formation_section = _require_section("8.2-204")

    return ContractAnatomy(
        contract_id="laptop-sale-contract-anatomy-v1",
        subject_name="A used-laptop sale contract, split into its real legal layers",
        physical_document_description=(
            "The email thread itself -- the buyer's 'I'll take it for $800' "
            "message and the seller's reply/shipment. This is just evidence "
            "of the agreement, not the agreement itself: if the emails were "
            "deleted, the agreement they recorded would not automatically "
            "cease to exist (though proving it would become harder)."
        ),
        the_agreement_description=(
            f'The mutual assent itself -- what {formation_section["citation"]} '
            "calls a contract that \"may be made in any manner sufficient to "
            "show agreement, including conduct by both parties.\" This is the "
            "legal fact of a deal having been struck, which can exist even "
            "without the email thread (e.g. if the parties had instead shaken "
            "hands and the seller shipped the laptop)."
        ),
        rights_and_obligations=[
            "Seller's obligation to deliver a conforming laptop.",
            "Buyer's obligation to pay the $800 price.",
            "Seller's right to receive payment.",
            "Buyer's right to receive conforming goods (and, per the "
            "implied-warranty-of-merchantability rule this same fact "
            "pattern illustrates elsewhere in this codebase, a right that "
            "the laptop actually work).",
        ],
        payment_rights_description=(
            "The seller's right to receive the $800 is itself a distinct, "
            "separately-transferable asset from the laptop or the email "
            "thread -- a business seller could sell that payment right to a "
            "factoring company for immediate cash, entirely independent of "
            "whether the laptop has even shipped yet."
        ),
        assignability=(
            "The seller's right to receive payment is generally freely "
            "assignable to a third party (e.g. a factoring company) absent "
            "a contrary agreement; the seller's own duty to deliver a "
            "conforming laptop is not something the buyer can be forced to "
            "accept performance of from an unapproved substitute seller "
            "without the buyer's consent, since personal performance was "
            "reasonably expected here."
        ),
        ucc_payment_right_classifications=[
            UccPaymentRightClassification(
                category="account",
                definition_summary="A right to payment for goods sold, not yet evidenced by a note or chattel paper.",
                distinguishing_feature="No separate instrument or security agreement exists -- just the underlying sale record.",
                example="The $800 laptop-sale payment right in this example, before any note or financing paperwork is created.",
            ),
            UccPaymentRightClassification(
                category="chattel paper",
                definition_summary="A record evidencing both a payment right AND a security interest in specific goods.",
                distinguishing_feature="Combines a monetary obligation with a security interest in the very goods sold -- e.g. a retail installment sale contract.",
                example="If the seller instead sold the laptop on a financed installment plan secured by the laptop itself, that installment contract would be chattel paper, not a plain account.",
            ),
            UccPaymentRightClassification(
                category="instrument",
                definition_summary="A negotiable writing (like a promissory note) evidencing a right to payment.",
                distinguishing_feature="Possession/negotiation of the paper (or authoritative electronic record) itself carries special enforcement rights.",
                example="If the buyer had instead signed a standalone promissory note for the $800, that note -- not the laptop-sale agreement itself -- would be the instrument.",
            ),
            UccPaymentRightClassification(
                category="payment intangible",
                definition_summary="A general intangible under which the account debtor's principal obligation is to pay money, not otherwise classified as an account, chattel paper, or instrument.",
                distinguishing_feature="A catch-all for payment obligations that don't fit the other three narrower buckets.",
                example="A right to receive a lump-sum settlement payment unrelated to any sale of goods would typically be a payment intangible, not an account.",
            ),
        ],
        ucc_classification_grounding_note=ARTICLE_9_PAYMENT_RIGHT_CLASSIFICATION_NOTE,
        common_confusions=[
            "Treating 'the contract' and 'the document' as the same thing -- losing the paper/email does not erase the underlying agreement or the rights it created.",
            "Assuming a payment right can't be sold separately from the underlying goods or services -- it routinely is (factoring).",
            "Assuming every payment right is UCC 'chattel paper' -- it is only chattel paper when a security interest in specific goods is bundled with the payment obligation in the same record; otherwise it is typically just an account or payment intangible.",
        ],
        citation=formation_section["citation"],
        section_id=formation_section["section_id"],
    )


if __name__ == "__main__":
    import json

    print(json.dumps(build_laptop_sale_contract_anatomy().to_dict(), indent=2, ensure_ascii=False))

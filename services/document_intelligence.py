"""Law Engine -- Document Identification Engine foundation (Live Run 1.39).

A reusable schema for identifying and teaching about a legal document
type, plus one real interactive "what kind of document is this?"
exercise. Grounded, wherever possible, in the real ingested UCC Article 2
text (library/normalized/ucc/article-2-sections.json) via
services/retrieval.get_section() -- never an invented citation. Where a
document family is a real, well-known legal document type but is not
itself discussed by the 11 sections of Article 2 currently ingested (most
notably financing statements, promissory notes, and security agreements,
which are Article 9/3 concepts), its DocumentProfile is built with
generally-accurate legal characteristics but leaves its citation fields
empty and says so explicitly -- the same "unpopulated is honest, invented
is not" discipline services/pedagogical_contract.py and
services/transaction_lifecycle.py already apply to statutory content.

This module does not edit or import from services/models.py's dataclasses
directly (beyond its existing Enums, which are safe to import read-only)
to avoid a merge conflict with a concurrent edit to that file -- its own
PedagogicalMetaphor-shaped illustration is redefined locally below as
DocumentMetaphor.

The central teaching point of this whole module, per the product's own
"substance over title" discipline: a document's TITLE (what's printed at
the top of the page, or its filename) is not what determines its legal
character. What determines it is the document's actual operative
language and how it functions in the transaction -- a document titled
"Purchase Order" that is signed by both parties and states final agreed
terms can function as the contract itself; a document titled "Invoice"
sent before any agreement can function as an offer, not a bill for
payment already owed. See DocumentProfile.title_vs_substance_note on
every profile below, and the worked example in
docs/document-intelligence-schema.md.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.retrieval import get_section


class DocumentIntelligenceError(Exception):
    """Raised for real, unrecoverable construction errors -- e.g. a
    builder that depends on a real ingested section that isn't there.
    Never silently substituted with invented statutory content."""


class DocumentFamily(str, Enum):
    """Coarse-grained legal document families this engine can identify.
    Deliberately its own enum, not an extension of any models.py enum --
    none of models.py's existing enums model "kind of document," and
    models.py is off-limits for edits this run."""

    CONTRACT = "CONTRACT"
    PURCHASE_ORDER = "PURCHASE_ORDER"
    INVOICE = "INVOICE"
    SECURITY_AGREEMENT = "SECURITY_AGREEMENT"
    FINANCING_STATEMENT = "FINANCING_STATEMENT"
    PROMISSORY_NOTE = "PROMISSORY_NOTE"
    NEGOTIABLE_INSTRUMENT = "NEGOTIABLE_INSTRUMENT"
    CHECK_DRAFT = "CHECK_DRAFT"
    GUARANTY = "GUARANTY"
    LEASE = "LEASE"
    BILL_OF_LADING = "BILL_OF_LADING"
    WAREHOUSE_RECEIPT = "WAREHOUSE_RECEIPT"
    TITLE_CERTIFICATE = "TITLE_CERTIFICATE"
    ASSIGNMENT = "ASSIGNMENT"
    OTHER = "OTHER"


@dataclass
class DocumentProfile:
    """Everything the engine knows about how to recognize and reason
    about one document family. `related_authorities` must only ever
    contain real citations -- either pulled live from
    services/retrieval.get_section() (grounded_in_ingested_text=True) or,
    for a family Article 2 doesn't cover, left empty with
    grounded_in_ingested_text=False and an honest note explaining the gap
    (never a fabricated section number)."""

    family: DocumentFamily
    display_name: str
    identifying_features: list[str]
    required_elements: list[str]
    optional_elements: list[str]
    legal_function: str
    common_confusions: list[str]
    related_authorities: list[str] = field(default_factory=list)
    signature_authentication_rules: str = ""
    transfer_indorsement_rules: str = ""
    filing_possession_control_consequences: str = ""
    related_asset_types: list[str] = field(default_factory=list)
    title_vs_substance_note: str = (
        "A document's printed title/heading is not dispositive -- classify "
        "by what the document's actual operative language does (offer? "
        "acceptance? final agreed terms? a bare demand for payment?), not "
        "by the word printed at the top of the page."
    )
    grounded_in_ingested_text: bool = False
    grounding_note: str = ""

    def to_dict(self) -> dict:
        return {
            "family": self.family.value,
            "display_name": self.display_name,
            "identifying_features": self.identifying_features,
            "required_elements": self.required_elements,
            "optional_elements": self.optional_elements,
            "legal_function": self.legal_function,
            "common_confusions": self.common_confusions,
            "related_authorities": self.related_authorities,
            "signature_authentication_rules": self.signature_authentication_rules,
            "transfer_indorsement_rules": self.transfer_indorsement_rules,
            "filing_possession_control_consequences": self.filing_possession_control_consequences,
            "related_asset_types": self.related_asset_types,
            "title_vs_substance_note": self.title_vs_substance_note,
            "grounded_in_ingested_text": self.grounded_in_ingested_text,
            "grounding_note": self.grounding_note,
        }


@dataclass
class DocumentMetaphor:
    """A simplified, non-authoritative illustration, local to this module
    (mirrors services/models.py's PedagogicalMetaphor pattern/labeling
    convention but is not that class, to avoid depending on models.py
    while it may be under concurrent edit)."""

    illustration: str
    disclaimer: str = (
        "This is a simplified teaching illustration, not a legal rule -- "
        "it never overrides a DocumentProfile's real citations or a real "
        "document's actual operative language."
    )
    is_pedagogical_only: bool = True

    def to_dict(self) -> dict:
        return {
            "illustration": self.illustration,
            "disclaimer": self.disclaimer,
            "is_pedagogical_only": self.is_pedagogical_only,
        }


@dataclass
class DocumentIdentificationChoice:
    """One selectable answer in a DocumentIdentificationExercise -- the
    same "why correct AND why each wrong alternative is wrong" shape as
    services/learning.py's MultipleChoiceQuestion and
    services/transaction_lifecycle.py's LifecycleChoice."""

    family: DocumentFamily
    label: str
    is_correct: bool
    explanation: str

    def to_dict(self) -> dict:
        return {
            "family": self.family.value,
            "label": self.label,
            "is_correct": self.is_correct,
            "explanation": self.explanation,
        }


@dataclass
class DocumentIdentificationExercise:
    """A real, working "what kind of document is this?" interactive
    exercise: a short structured hypothetical/feature list, a correct
    DocumentFamily answer among plausible alternatives, and a
    why-correct/why-each-wrong-alternative-is-wrong explanation for
    every choice."""

    exercise_id: str
    title: str
    hypothetical: str
    observed_features: list[str]
    choices: list[DocumentIdentificationChoice]
    plain_language_summary: str
    metaphor: DocumentMetaphor | None = None

    def correct_choice(self) -> DocumentIdentificationChoice:
        correct = [c for c in self.choices if c.is_correct]
        if len(correct) != 1:
            raise DocumentIntelligenceError(
                f"Exercise {self.exercise_id!r} must have exactly one correct "
                f"choice, found {len(correct)}."
            )
        return correct[0]

    def answer(self, chosen_family: DocumentFamily) -> DocumentIdentificationChoice:
        for choice in self.choices:
            if choice.family == chosen_family:
                return choice
        raise DocumentIntelligenceError(
            f"{chosen_family!r} is not one of exercise {self.exercise_id!r}'s real choices."
        )

    def to_dict(self) -> dict:
        return {
            "exercise_id": self.exercise_id,
            "title": self.title,
            "hypothetical": self.hypothetical,
            "observed_features": self.observed_features,
            "choices": [c.to_dict() for c in self.choices],
            "plain_language_summary": self.plain_language_summary,
            "metaphor": self.metaphor.to_dict() if self.metaphor is not None else None,
        }


def _require_section(section_id: str) -> dict:
    section = get_section(section_id)
    if section is None:
        raise DocumentIntelligenceError(
            f"No ingested section {section_id!r} -- cannot build a "
            "grounded DocumentProfile without a real source."
        )
    return section


# ---------------------------------------------------------------------------
# Grounded DocumentProfile builders (real ingested Article 2 text)
# ---------------------------------------------------------------------------


def build_purchase_order_profile() -> DocumentProfile:
    """Grounded in Va. Code Ann. Section 8.2-206(1)(b)
    (library/normalized/ucc/article-2-sections.json), which discusses "an
    order or other offer to buy goods for prompt or current shipment"
    directly -- a purchase order, functionally, IS this "order... to buy
    goods." Article 2 doesn't use the phrase "purchase order," but it
    directly discusses the document by function (a buyer's order to buy),
    which is the substance-over-title point this whole module is built
    around."""
    offer_acceptance = _require_section("8.2-206")
    formation = _require_section("8.2-204")

    return DocumentProfile(
        family=DocumentFamily.PURCHASE_ORDER,
        display_name="Purchase Order",
        identifying_features=[
            "Issued by the buyer, addressed to a seller.",
            "Identifies specific goods, quantities, and (usually) a price.",
            "Requests shipment or delivery, often \"prompt or current shipment.\"",
            "Sent before the seller has done anything to accept.",
        ],
        required_elements=[
            "Identity of the buyer and seller.",
            "Description of the goods and quantity.",
            "Some manifestation that the buyer intends to be bound if accepted.",
        ],
        optional_elements=[
            "A PO number for internal tracking.",
            "A requested delivery date or shipping method.",
            "Payment terms the buyer is proposing.",
        ],
        legal_function=(
            f'A purchase order is ordinarily an offer, not yet a contract. {offer_acceptance["citation"]} '
            'treats "an order or other offer to buy goods for prompt or current shipment" as inviting '
            "acceptance either by the seller's prompt promise to ship or by the seller's prompt or "
            f'current shipment itself. Under {formation["citation"]}, no contract exists until that '
            "acceptance (or other conduct recognizing agreement) actually occurs -- the purchase order "
            "alone only proposes terms."
        ),
        common_confusions=[
            "Mistaking a purchase order for an already-binding contract -- it's usually just the offer "
            "half of formation, not the whole transaction.",
            "Assuming shipment of the exact goods ordered is the only way to accept -- "
            f'{offer_acceptance["citation"]} also treats shipment of nonconforming goods as an '
            "acceptance (creating a breach), unless the seller seasonably notifies the buyer the "
            "shipment is sent only as an accommodation.",
            "Confusing a purchase order (buyer-initiated, before delivery) with an invoice "
            "(commonly seller-sent, confirming/billing around or after delivery) -- direction and "
            "timing differ even though both are short, form-like commercial documents.",
        ],
        related_authorities=[offer_acceptance["citation"], formation["citation"]],
        signature_authentication_rules=(
            "Article 2 formation does not itself require a signature -- "
            f'{formation["citation"]} allows a contract to be shown "in any manner sufficient to show '
            'agreement, including conduct." A purchase order is commonly unsigned (e.g. a form or an '
            "email) and can still function as an offer. (A separate signed-writing requirement can "
            "apply above certain dollar thresholds under Article 2's statute-of-frauds section, but "
            "that section is not among the 11 sections currently ingested into this system, so it is "
            "deliberately not cited here by number.)"
        ),
        transfer_indorsement_rules=(
            "Not a negotiable instrument and not a document of title -- a purchase order (or the offer "
            "it makes) is not transferred by indorsement/negotiation. Any transfer of contract rights "
            "arising from it happens by ordinary assignment (see the ASSIGNMENT family), not negotiation."
        ),
        filing_possession_control_consequences=(
            "No filing, possession, or control regime attaches to a purchase order itself -- it is not "
            "collateral, a negotiable instrument, or a document of title, so none of Article 9's "
            "filing/possession/control priority rules are triggered by it."
        ),
        related_asset_types=["goods"],
        title_vs_substance_note=(
            "A document titled \"Purchase Order\" that is actually signed by both parties and states "
            "final, agreed terms (no further acceptance contemplated) can function as the contract "
            "itself, not merely an offer -- the label \"purchase order\" does not by itself fix its "
            f'legal role. What matters under {formation["citation"]} is whether agreement has actually '
            "been shown, by signature, conduct, or otherwise."
        ),
        grounded_in_ingested_text=True,
        grounding_note=(
            f'Directly grounded in the real ingested text of {offer_acceptance["citation"]} and '
            f'{formation["citation"]}.'
        ),
    )


def build_invoice_profile() -> DocumentProfile:
    """Grounded in Va. Code Ann. Section 8.2-207 (library/normalized/ucc/
    article-2-sections.json), whose title is literally "Additional terms
    in acceptance or confirmation" and whose paragraph (1) discusses "a
    written confirmation which is sent within a reasonable time." Article
    2's ingested text never uses the word "invoice" -- this profile
    grounds the family by FUNCTION, not by word match: a seller's
    invoice, in the real commercial pattern this section is written to
    cover, commonly IS the "written confirmation" 8.2-207 discusses (it
    is what a seller sends, often after or along with an oral or
    informal agreement, restating -- and sometimes adding to -- the
    agreed terms). That functional mapping is disclosed explicitly below
    rather than presented as if the statute names "invoices" by name."""
    confirmation = _require_section("8.2-207")

    return DocumentProfile(
        family=DocumentFamily.INVOICE,
        display_name="Invoice",
        identifying_features=[
            "Issued by the seller, addressed to the buyer.",
            "Itemizes goods delivered or to be delivered, with prices and a total amount due.",
            "Sent at or after shipment/delivery, or to confirm an already-informal agreement.",
            "Often contains boilerplate terms on the back or footer (payment terms, disclaimers) that "
            "were never separately negotiated.",
        ],
        required_elements=[
            "Identity of the seller and buyer.",
            "Description of goods/services and the amount owed.",
        ],
        optional_elements=[
            "Payment due date and accepted payment methods.",
            "Additional or different boilerplate terms (return policy, interest on late payment).",
        ],
        legal_function=(
            f'Functionally, an invoice sent after an informal or oral agreement is commonly the '
            f'"written confirmation" {confirmation["citation"]} discusses. {confirmation["citation"]} '
            "provides that such a confirmation \"operates as an acceptance even though it states terms "
            'additional to or different from those offered or agreed upon," unless acceptance was made '
            "expressly conditional on assent to those new terms. Between merchants, those additional "
            f'terms in the invoice become part of the contract under {confirmation["citation"]} unless '
            "the original offer limited acceptance to its own terms, the new term materially alters the "
            "deal, or a party objects within a reasonable time."
        ),
        common_confusions=[
            "Treating an invoice as a neutral receipt with no legal effect -- an invoice's boilerplate "
            f'terms can actually become binding contract terms under {confirmation["citation"]} if not '
            "objected to.",
            "Confusing an invoice (seller-sent, usually at/after delivery, primarily about payment) "
            "with a purchase order (buyer-sent, before delivery, primarily an offer to buy).",
            "Assuming an invoice is always the operative \"written confirmation\" -- if it's the FIRST "
            "writing in the deal (no prior oral/informal agreement existed), it functions as an offer "
            f'instead, and {confirmation["citation"]}\'s confirmation rule doesn\'t apply to it.',
        ],
        related_authorities=[confirmation["citation"]],
        signature_authentication_rules=(
            "No signature is required for an invoice to have the legal effect described above -- "
            f'{confirmation["citation"]} refers to a "written confirmation," not a signed one. An '
            "unsigned emailed or printed invoice can still add or alter terms under this rule."
        ),
        transfer_indorsement_rules=(
            "Not a negotiable instrument -- an invoice (a demand or record of an amount owed) is not "
            "transferred by indorsement. The underlying payment obligation it reflects can be assigned "
            "as an ordinary account receivable (see the ASSIGNMENT family), but the invoice document "
            "itself carries no negotiation mechanism."
        ),
        filing_possession_control_consequences=(
            "No filing/possession/control regime attaches to the invoice document itself. If the "
            "underlying receivable it reflects is used as collateral, Article 9's rules for accounts "
            "would govern that separate transaction -- not the invoice as a document."
        ),
        related_asset_types=["goods", "accounts receivable"],
        title_vs_substance_note=(
            "The ingested Article 2 text never uses the word \"invoice\" -- this profile grounds the "
            "family by what the document actually does (a seller's post-agreement confirming/billing "
            f'writing), which is what {confirmation["citation"]} calls a "written confirmation." A '
            "document titled \"Invoice\" that is actually the FIRST writing exchanged (no prior "
            "agreement) is not functioning as a confirmation at all -- it's an offer, and should be "
            "classified by that operative function, not its printed title."
        ),
        grounded_in_ingested_text=True,
        grounding_note=(
            f'Grounded in the real ingested text of {confirmation["citation"]} by function (the '
            '"written confirmation" it discusses), not by a literal word match on "invoice," which '
            "does not appear in the ingested Article 2 text. This mapping is disclosed here rather than "
            "presented as if the statute names invoices directly."
        ),
    )


def build_sales_contract_profile() -> DocumentProfile:
    """Grounded in Va. Code Ann. Sections 8.2-204 (Formation in general)
    and 8.2-105 (definition of "goods") -- the most directly-discussed
    document in the whole ingested Article 2 vertical slice, since 8.2-204
    IS the section that defines how "a contract for sale of goods" comes
    into existence."""
    formation = _require_section("8.2-204")
    goods = _require_section("8.2-105")

    return DocumentProfile(
        family=DocumentFamily.CONTRACT,
        display_name="Sales Contract (for goods)",
        identifying_features=[
            "States (or shows through conduct) that both parties agree to a sale of goods.",
            "Identifies, or makes identifiable, the goods, the parties, and typically a price.",
            "May be a single signed writing, a set of exchanged writings, or no writing at all -- "
            "conduct recognizing the deal can be enough.",
        ],
        required_elements=[
            "Two or more parties who intend to be bound.",
            f'Goods, as {goods["citation"]} defines them -- movable things identified to the contract.',
            "A reasonably certain basis for a remedy, even if some terms are left open.",
        ],
        optional_elements=[
            "A signature block.",
            "Delivery, payment, and warranty terms.",
            "A merger/integration clause.",
        ],
        legal_function=(
            f'{formation["citation"]} allows a contract for sale of goods to be formed "in any manner '
            'sufficient to show agreement, including conduct by both parties" -- the moment of making '
            "can be undetermined, and the contract doesn't fail for indefiniteness merely because some "
            "terms were left open, so long as the parties intended a contract and a remedy is "
            "reasonably certain."
        ),
        common_confusions=[
            "Assuming a contract must be one signed document -- under "
            f'{formation["citation"]} it can be conduct alone, or a set of exchanged writings.',
            "Assuming an open term (e.g. no fixed delivery date) means no contract exists yet -- "
            f'{formation["citation"]} tolerates open terms if intent to contract and a remedy basis '
            "are both present.",
            "Confusing the sales contract itself with a purchase order or invoice, which are often "
            "only one party's proposal or confirmation, not yet a document both parties have agreed to.",
        ],
        related_authorities=[formation["citation"], goods["citation"]],
        signature_authentication_rules=(
            f'{formation["citation"]} does not require a signature for formation -- conduct by both '
            "parties recognizing the contract's existence is sufficient. (A signed-writing requirement "
            "can still apply separately above certain dollar thresholds under Article 2's statute-of-"
            "frauds provision, but that section is not among the sections currently ingested into this "
            "system, so it is deliberately not cited here by number.)"
        ),
        transfer_indorsement_rules=(
            "A sales contract is not a negotiable instrument. Contract rights and duties can be "
            "assigned/delegated under ordinary contract-assignment principles (see the ASSIGNMENT "
            "family), not by indorsement or negotiation."
        ),
        filing_possession_control_consequences=(
            "No filing/possession/control regime attaches to a sales contract by itself. If the "
            "buyer's payment obligation is later secured by collateral, that's a separate Article 9 "
            "transaction layered on top of, not inherent in, the sales contract."
        ),
        related_asset_types=["goods"],
        grounded_in_ingested_text=True,
        grounding_note=(
            f'Directly grounded in the real ingested text of {formation["citation"]} and {goods["citation"]}.'
        ),
    )


# ---------------------------------------------------------------------------
# Ungrounded DocumentProfile builders (real legal document types, but NOT
# discussed by any of the 11 currently-ingested Article 2 sections -- these
# are Article 9/3 concepts. No section_id/citation is populated; the gap is
# disclosed explicitly rather than invented.
# ---------------------------------------------------------------------------


def build_security_agreement_profile() -> DocumentProfile:
    """NOT grounded in ingested text. A security agreement is an Article 9
    concept. Article 2 acknowledges the boundary exists -- Va. Code Ann.
    Section 8.2-102(3)(a) (real, ingested) says Article 2 "does not ...
    apply to a transaction that, even though in the form of an
    unconditional contract to sell or present sale, operates only to
    create a security interest" -- but 8.2-102 only excludes security
    transactions from Article 2, it does not itself define or discuss
    what a security agreement must contain. That substantive content
    would come from Article 9, which is not ingested, so this profile's
    `related_authorities` is deliberately left empty rather than citing
    8.2-102 as if it were the source of the security-agreement rules
    below."""
    return DocumentProfile(
        family=DocumentFamily.SECURITY_AGREEMENT,
        display_name="Security Agreement",
        identifying_features=[
            "Grants a security interest in described collateral to a secured party.",
            "Identifies the debtor, secured party, collateral, and the obligation secured.",
            "Signed (or otherwise authenticated) by the debtor.",
        ],
        required_elements=[
            "Language creating/granting a security interest (not just describing collateral).",
            "A reasonable description of the collateral.",
            "Authentication by the debtor.",
        ],
        optional_elements=[
            "After-acquired property clause.",
            "Cross-collateralization or cross-default clauses.",
        ],
        legal_function=(
            "Creates and evidences a security interest between debtor and secured party -- the "
            "agreement itself is what makes the interest enforceable against the debtor (attachment); "
            "it is a separate step from perfection against third parties, which typically requires "
            "filing a financing statement or taking possession/control."
        ),
        common_confusions=[
            "Confusing the security agreement (creates the interest between the two parties) with the "
            "financing statement (a public filing that perfects the interest against third parties) -- "
            "they are two different documents with two different purposes.",
            "Assuming a security agreement transfers ownership of the collateral -- it grants a lien-"
            "like interest, not title.",
        ],
        related_authorities=[],
        signature_authentication_rules=(
            "Requires authentication by the debtor (traditionally a signature; a security interest in "
            "goods generally cannot attach without it) -- this is a well-known, generally-accurate "
            "Article 9 characteristic, not something the currently-ingested Article 2 sections discuss."
        ),
        transfer_indorsement_rules=(
            "Not a negotiable instrument. The secured party's rights can be assigned; no indorsement "
            "chain applies."
        ),
        filing_possession_control_consequences=(
            "The security agreement alone only attaches the interest as between debtor and secured "
            "party. Perfecting it against third parties generally requires filing a financing "
            "statement, or, for some collateral types, taking possession or control instead."
        ),
        related_asset_types=["goods", "accounts", "equipment", "inventory"],
        grounded_in_ingested_text=False,
        grounding_note=(
            "NOT grounded in ingested statutory text. Security agreements are an Article 9 concept; "
            "Article 9 has not been ingested into this system. Va. Code Ann. Section 8.2-102(3)(a) is "
            "real and ingested, and does acknowledge that Article 2 excludes transactions that operate "
            "only to create a security interest, but it does not itself define security-agreement "
            "content, so it is not cited in related_authorities here to avoid implying it is the source "
            "of the rules described above. The characteristics above are well-known, generally-"
            "accurate Article 9 concepts, not sourced from any real citation in this system yet."
        ),
    )


def build_financing_statement_profile() -> DocumentProfile:
    """NOT grounded in ingested text -- an Article 9 concept, not
    discussed anywhere in the 11 ingested Article 2 sections."""
    return DocumentProfile(
        family=DocumentFamily.FINANCING_STATEMENT,
        display_name="Financing Statement (UCC-1)",
        identifying_features=[
            "A public filing (not a contract between the parties) identifying debtor, secured party, "
            "and collateral.",
            "Filed with a state filing office, not signed by hand in the traditional sense.",
        ],
        required_elements=[
            "Debtor's name (accuracy here is unusually strict -- a materially misleading debtor name "
            "can make the filing seriously misleading and ineffective).",
            "Secured party's (or representative's) name.",
            "Indication of the collateral covered.",
        ],
        optional_elements=[
            "Collateral description as broad as \"all assets.\"",
            "Additional debtor/secured-party addresses.",
        ],
        legal_function=(
            "Perfects a security interest by giving public notice of it, establishing priority against "
            "most later-arising competing claims to the same collateral. It does not itself create the "
            "security interest -- that's the security agreement's job."
        ),
        common_confusions=[
            "Confusing the financing statement (public notice/priority) with the security agreement "
            "(creates the interest) -- a financing statement with no underlying security agreement "
            "perfects nothing.",
            "Assuming the financing statement must be signed by the debtor -- it is authorized by the "
            "debtor (often through the security agreement itself), not necessarily hand-signed.",
        ],
        related_authorities=[],
        signature_authentication_rules=(
            "Generally does not require the debtor's signature on the filing itself -- it requires the "
            "debtor's authorization to file, commonly given in the security agreement. Well-known "
            "Article 9 characteristic, not sourced from ingested text."
        ),
        transfer_indorsement_rules="Not a negotiable instrument; not transferred by indorsement.",
        filing_possession_control_consequences=(
            "This document IS the filing mechanism -- its entire function is perfection-by-filing. "
            "Effectiveness/priority generally runs from the filing date, and errors in the debtor's "
            "name are judged by a search-logic standard that can invalidate an otherwise-complete "
            "filing."
        ),
        related_asset_types=["goods", "accounts", "equipment", "inventory", "general intangibles"],
        grounded_in_ingested_text=False,
        grounding_note=(
            "NOT grounded in ingested statutory text. Financing statements are an Article 9 concept; "
            "Article 9 has not been ingested into this system. No section number is cited above."
        ),
    )


def build_promissory_note_profile() -> DocumentProfile:
    """NOT grounded in ingested text -- an Article 3 (negotiable
    instruments) concept, not discussed anywhere in the 11 ingested
    Article 2 sections."""
    return DocumentProfile(
        family=DocumentFamily.PROMISSORY_NOTE,
        display_name="Promissory Note",
        identifying_features=[
            "An unconditional written promise to pay a fixed amount of money.",
            "Names (or is payable to) a payee, or is payable to bearer.",
            "Payable on demand or at a definite time.",
            "Signed by the person making the promise (the maker).",
        ],
        required_elements=[
            "Unconditional promise to pay a fixed sum.",
            "Payable on demand or at a definite time.",
            "Payable to order or to bearer (to be a negotiable instrument, rather than just a "
            "contract claim).",
            "Maker's signature.",
        ],
        optional_elements=["Interest rate.", "Collateral reference.", "Acceleration clause."],
        legal_function=(
            "Evidences a debt and, if it meets negotiability requirements, can be transferred by "
            "negotiation so that a good-faith transferee (a holder in due course) can take it free of "
            "many of the maker's personal defenses -- a stronger transfer right than an ordinary "
            "contract claim has."
        ),
        common_confusions=[
            "Assuming any IOU is automatically a negotiable instrument -- negotiability requires "
            "meeting specific formal requirements (unconditional, fixed amount, payable to order/"
            "bearer, etc.); a note that fails one of them is still an enforceable promise, just not a "
            "negotiable instrument with holder-in-due-course consequences.",
            "Confusing a promissory note (the debt instrument) with a security agreement (the "
            "collateral-granting document) -- a note is very often paired with a security agreement, "
            "but they are two separate documents with two separate legal functions.",
        ],
        related_authorities=[],
        signature_authentication_rules=(
            "Requires the maker's signature -- well-known Article 3 characteristic, not sourced from "
            "ingested text."
        ),
        transfer_indorsement_rules=(
            "If negotiable, transferred by negotiation: indorsement (and delivery, for an order "
            "instrument) or delivery alone (for a bearer instrument). A holder in due course can take "
            "free of many personal defenses the maker could raise against the original payee."
        ),
        filing_possession_control_consequences=(
            "Rights in the note as collateral are generally perfected by possession (or, for certain "
            "electronic notes, control), not by filing -- a well-known Article 9 characteristic for "
            "instruments as collateral, not sourced from ingested text."
        ),
        related_asset_types=["money", "payment obligations"],
        grounded_in_ingested_text=False,
        grounding_note=(
            "NOT grounded in ingested statutory text. Promissory notes and negotiability requirements "
            "are Article 3 concepts; Article 3 has not been ingested into this system. No section "
            "number is cited above."
        ),
    )


PROFILE_BUILDERS: dict[DocumentFamily, "callable[[], DocumentProfile]"] = {
    DocumentFamily.PURCHASE_ORDER: build_purchase_order_profile,
    DocumentFamily.INVOICE: build_invoice_profile,
    DocumentFamily.CONTRACT: build_sales_contract_profile,
    DocumentFamily.SECURITY_AGREEMENT: build_security_agreement_profile,
    DocumentFamily.FINANCING_STATEMENT: build_financing_statement_profile,
    DocumentFamily.PROMISSORY_NOTE: build_promissory_note_profile,
}


def build_all_profiles() -> list[DocumentProfile]:
    return [builder() for builder in PROFILE_BUILDERS.values()]


# ---------------------------------------------------------------------------
# Interactive exercise
# ---------------------------------------------------------------------------


def build_purchase_order_identification_exercise() -> DocumentIdentificationExercise:
    """Real, working "what kind of document is this?" exercise. The
    hypothetical is deliberately designed so that title alone
    ("Purchase Order #4471" printed at the top) is NOT what makes the
    right answer correct -- the operative facts (who sent it, what
    direction, before what event) are what do. Grounded in the real
    ingested text of 8.2-206 and 8.2-207 for the correct answer and the
    invoice distractor, and 8.2-204 for the contract distractor."""
    offer_acceptance = _require_section("8.2-206")
    confirmation = _require_section("8.2-207")
    formation = _require_section("8.2-204")

    return DocumentIdentificationExercise(
        exercise_id="what-kind-of-document-po-vs-invoice-vs-contract",
        title="What kind of document is this?",
        hypothetical=(
            "A buyer's purchasing department emails a document titled \"Purchase Order #4471\" to a "
            "seller. It lists 50 units of a specific part number, a requested price of $12/unit, and "
            "asks for \"prompt shipment.\" The seller has not yet responded in any way -- no shipment, "
            "no reply email, nothing."
        ),
        observed_features=[
            "Sent by the buyer, addressed to the seller.",
            "Lists specific goods, quantity, and a proposed price.",
            "Requests prompt shipment.",
            "No response or conduct from the seller yet.",
        ],
        choices=[
            DocumentIdentificationChoice(
                family=DocumentFamily.PURCHASE_ORDER,
                label="Purchase order -- an offer to buy, not yet a contract",
                is_correct=True,
                explanation=(
                    f'Correct. This matches {offer_acceptance["citation"]}\'s "order or other offer to '
                    'buy goods for prompt or current shipment" almost exactly -- it is an offer the '
                    "seller could accept by a prompt promise to ship or by prompt shipment itself. "
                    f'Because the seller has done nothing yet, {formation["citation"]} confirms no '
                    "contract has formed -- there's no conduct or agreement to point to yet, only the "
                    "buyer's proposal."
                ),
            ),
            DocumentIdentificationChoice(
                family=DocumentFamily.CONTRACT,
                label="Sales contract -- the deal is already done",
                is_correct=False,
                explanation=(
                    f'Wrong. {formation["citation"]} requires some manifestation of agreement -- by '
                    "conduct or otherwise -- for a contract to exist. Here only the buyer has acted; "
                    "the seller hasn't shipped, promised to ship, or done anything else showing "
                    "agreement. A one-sided proposal, however detailed, is an offer under "
                    f'{offer_acceptance["citation"]}, not yet a contract.'
                ),
            ),
            DocumentIdentificationChoice(
                family=DocumentFamily.INVOICE,
                label="Invoice -- confirming and billing for an already-agreed sale",
                is_correct=False,
                explanation=(
                    f'Wrong direction and timing. {confirmation["citation"]}\'s "written confirmation" '
                    "is characteristically sent to confirm an agreement that already exists (often by "
                    "the seller, at or after delivery, to bill for what was sold). Here nothing has "
                    "been agreed to yet, and the document runs buyer-to-seller proposing terms, not "
                    "seller-to-buyer confirming and billing for them."
                ),
            ),
        ],
        plain_language_summary=(
            "The word \"order\" in the title is a hint, but what actually makes this a purchase order "
            "(an offer) rather than a contract or an invoice is: who sent it (the buyer), what it does "
            "(proposes terms), and what hasn't happened yet (no seller response). Change any of those "
            "operative facts and the right classification can change too, regardless of the title "
            "printed at the top."
        ),
        metaphor=DocumentMetaphor(
            illustration=(
                "A purchase order is like raising your hand to bid at an auction: it says \"I'll take "
                "it, at this price\" -- but the deal isn't done until the auctioneer's hammer falls "
                "(the seller accepts). Nobody would say the auction is already over just because you "
                "raised your hand."
            ),
        ),
    )


if __name__ == "__main__":
    import json

    profiles = build_all_profiles()
    exercise = build_purchase_order_identification_exercise()
    print(json.dumps(
        {
            "profiles": [p.to_dict() for p in profiles],
            "exercise": exercise.to_dict(),
        },
        indent=2,
        ensure_ascii=False,
    ))

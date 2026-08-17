"""Law Engine -- Asset Intelligence foundation (Live Run 1.39/1.40). A
reusable schema for analyzing a type of asset a person owns, is acquiring,
or was transferred: what legally counts as ownership of it, how it moves
from one person to another, whether it can serve as loan collateral, and
what body of law actually governs it.

Same trust-but-verify discipline as pedagogical_contract.py and
transaction_lifecycle.py: a claim that traces to a specific ingested
statutory section must cite that real section (via
services/retrieval.get_section) and never invent one. Article 9 (secured
transactions) is NOT yet ingested in this codebase as of this module's
creation -- a profile that describes generally-accurate, well-known
Article 9 characteristics (security-interest eligibility, perfection
method, priority) does so WITHOUT inventing a specific ingested citation:
`citation` stays None and `citation_grounding_note` says so explicitly.
This lets the schema be useful today and get citations filled in later
once a real Article 9 ingestion effort lands, without ever presenting an
unverified legal claim as a sourced one in the meantime.
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

ARTICLE_9_NOT_YET_INGESTED_NOTE = (
    "Article 9 (secured transactions) is not yet ingested in this codebase. "
    "The characteristics below are well-known, generally-accurate legal "
    "concepts, not a claim traced to any specific ingested statutory "
    "section -- citation/section_id are left None until a real Article 9 "
    "ingestion effort lands."
)


class AssetIntelligenceError(Exception):
    """Raised when a profile claims to be grounded in a real ingested
    section that does not actually exist -- never silently substituted
    with invented statutory text."""


class AssetType(str, Enum):
    """The kind of asset an AssetProfile describes. Deliberately broad --
    this taxonomy spans both UCC Article 9 collateral categories (goods
    subtypes, accounts, instruments, chattel paper, etc.) and non-UCC
    asset classes (real property, digital assets) precisely so the
    boundary between them is representable rather than assumed away."""

    VEHICLE = "VEHICLE"
    EQUIPMENT = "EQUIPMENT"
    INVENTORY = "INVENTORY"
    CONSUMER_GOODS = "CONSUMER_GOODS"
    MONEY = "MONEY"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    CHECK = "CHECK"
    PROMISSORY_NOTE = "PROMISSORY_NOTE"
    CONTRACT_RIGHTS = "CONTRACT_RIGHTS"
    ACCOUNTS_RECEIVABLE = "ACCOUNTS_RECEIVABLE"
    DOCUMENT_OF_TITLE = "DOCUMENT_OF_TITLE"
    INVESTMENT_ASSET = "INVESTMENT_ASSET"
    DIGITAL_ASSET = "DIGITAL_ASSET"
    REAL_PROPERTY = "REAL_PROPERTY"
    FIXTURES = "FIXTURES"
    OTHER = "OTHER"


@dataclass
class AssetProfile:
    """One real, reusable legal-intelligence profile for a type of asset.

    `citation`/`section_id` are populated ONLY when a field on this profile
    actually traces to a real ingested statutory section -- e.g. a
    CONSUMER_GOODS profile can cite Va. Code Ann. Section 8.2-105's real,
    ingested "goods" definition. When a profile instead describes
    generally-accurate but not-yet-ingested law (most Article 9 material,
    as of this module's creation), `citation`/`section_id` stay None and
    `citation_grounding_note` must say so explicitly -- an unpopulated
    citation is honest; an invented one is not.
    """

    asset_type: AssetType
    legal_classification: str
    evidence_of_ownership: list[str]
    title_concept: str
    possession_concept: str
    control_concept: str
    transferability: str
    assignability: str
    security_interest_eligible: bool
    perfection_method: str | None
    priority_notes: str
    controlling_documents: list[str]
    record_retention_notes: str
    governing_bodies_of_law: list[str]
    jurisdiction: str
    common_mistakes: list[str]
    citation: str | None = None
    section_id: str | None = None
    citation_grounding_note: str = ""

    def to_dict(self) -> dict:
        return {
            "asset_type": self.asset_type.value,
            "legal_classification": self.legal_classification,
            "evidence_of_ownership": self.evidence_of_ownership,
            "title_concept": self.title_concept,
            "possession_concept": self.possession_concept,
            "control_concept": self.control_concept,
            "transferability": self.transferability,
            "assignability": self.assignability,
            "security_interest_eligible": self.security_interest_eligible,
            "perfection_method": self.perfection_method,
            "priority_notes": self.priority_notes,
            "controlling_documents": self.controlling_documents,
            "record_retention_notes": self.record_retention_notes,
            "governing_bodies_of_law": self.governing_bodies_of_law,
            "jurisdiction": self.jurisdiction,
            "common_mistakes": self.common_mistakes,
            "citation": self.citation,
            "section_id": self.section_id,
            "citation_grounding_note": self.citation_grounding_note,
        }


def _require_section(section_id: str) -> dict:
    section = get_section(section_id)
    if section is None:
        raise AssetIntelligenceError(
            f"No ingested section {section_id!r} -- cannot build an "
            "AssetProfile that cites it without a real source."
        )
    return section


def build_consumer_goods_profile() -> AssetProfile:
    """Grounded in the real, ingested "goods" definition at Va. Code Ann.
    Section 8.2-105 (the same section transaction_lifecycle.py's
    threshold-scope stage already uses). Article 9's own further
    subclassification of "consumer goods" (used or bought for primarily
    personal, family, or household purposes) is well-known but NOT yet
    ingested here -- see citation_grounding_note."""
    goods_section = _require_section("8.2-105")
    return AssetProfile(
        asset_type=AssetType.CONSUMER_GOODS,
        legal_classification=(
            'A "good" under UCC Article 2 -- '
            f'{goods_section["citation"]} defines "goods" as things movable '
            "at the time of identification to the contract for sale. Once "
            "bought and used primarily for personal, family, or household "
            'purposes, Article 9 (not yet ingested) further classifies the '
            'same physical item as "consumer goods" for secured-transaction '
            "purposes."
        ),
        evidence_of_ownership=[
            "Purchase receipt or invoice",
            "Bill of sale (for higher-value items)",
            "Manufacturer's warranty registration",
            "Possession itself, absent contrary evidence",
        ],
        title_concept=(
            "Title passes to the buyer at the time and place the seller "
            "completes performance with reference to physical delivery of "
            "the goods, absent an agreement otherwise -- ordinary consumer "
            "purchases rarely have a separate certificate-of-title system."
        ),
        possession_concept=(
            "Possession is the ordinary, primary evidence of ownership for "
            "consumer goods -- there is usually no title-registry system, "
            "so who physically holds the item is doing most of the "
            "evidentiary work."
        ),
        control_concept=(
            "Not a distinct legal concept for ordinary tangible consumer "
            "goods (unlike a deposit account or investment asset) -- "
            "possession and title concepts do the necessary work."
        ),
        transferability="Freely transferable by delivery plus intent to pass title; no registry filing required.",
        assignability="N/A in the contract-rights sense -- a good itself is sold/gifted, not assigned.",
        security_interest_eligible=True,
        perfection_method=(
            "Generally by filing a UCC-1 financing statement; a purchase-"
            "money security interest in consumer goods can perfect "
            "automatically on attachment without filing in many "
            "jurisdictions (well-known Article 9 concept, not yet ingested)."
        ),
        priority_notes=(
            "Well-known Article 9 priority concepts (first-to-file-or-"
            "perfect, PMSI superpriority) generally apply; not yet grounded "
            "in an ingested citation."
        ),
        controlling_documents=["Purchase receipt/invoice", "Bill of sale", "Any express or implied warranty terms"],
        record_retention_notes="Keep the receipt/invoice for warranty and return-window purposes; no long-term registry record exists for most consumer goods.",
        governing_bodies_of_law=["UCC Article 2 (sale of goods)", "UCC Article 9 (as collateral, not yet ingested)"],
        jurisdiction="Commonwealth of Virginia",
        common_mistakes=[
            'Assuming a "goods" classification requires the buyer to be a business -- it does not.',
            "Treating a sales receipt as if it were a certificate of title.",
            "Assuming consumer-goods status is permanent -- if repurposed for business use, Article 9 reclassifies the same item as equipment or inventory.",
        ],
        citation=goods_section["citation"],
        section_id=goods_section["section_id"],
        citation_grounding_note=(
            "legal_classification's Article-2 'goods' claim is grounded in "
            f'the real ingested {goods_section["citation"]}. '
            + ARTICLE_9_NOT_YET_INGESTED_NOTE
        ),
    )


def build_vehicle_profile() -> AssetProfile:
    """A motor vehicle is "goods" under the same ingested Article 2
    definition, but -- unlike most consumer goods -- ownership evidence
    runs through a state certificate-of-title registry, not mere
    possession. Article 9 perfection for a titled vehicle is also
    special-cased (notation on the certificate of title, not a UCC-1
    filing, in most states) -- described generally, not yet grounded in an
    ingested citation."""
    goods_section = _require_section("8.2-105")
    return AssetProfile(
        asset_type=AssetType.VEHICLE,
        legal_classification=(
            f'"Goods" under {goods_section["citation"]} (a movable, '
            "identified thing) -- but unlike ordinary consumer goods, most "
            "US jurisdictions layer a statutory certificate-of-title "
            "registry on top, so ownership is not just a possession "
            "question."
        ),
        evidence_of_ownership=[
            "State-issued certificate of title (primary evidence)",
            "Bill of sale",
            "DMV/registration records",
        ],
        title_concept=(
            "Legal title is tracked by a state certificate-of-title "
            "registry, distinct from physical possession -- a lender can "
            "be shown as lienholder on the same certificate without "
            "possessing the vehicle."
        ),
        possession_concept="Physical possession matters for use and risk of loss, but is secondary to the certificate of title as ownership evidence.",
        control_concept="N/A in the deposit-account/investment-asset sense; the certificate-of-title system substitutes for a control regime.",
        transferability="Transferred by delivery of an assigned certificate of title (endorsed by the seller) plus delivery of the vehicle; re-registration with the state DMV is required to complete the public record.",
        assignability="N/A -- a vehicle itself is sold, not assigned as a contract right.",
        security_interest_eligible=True,
        perfection_method=(
            "In most states, perfection of a security interest in a titled "
            "vehicle occurs by notation of the lien on the certificate of "
            "title (a title-registry system), not by a general UCC-1 "
            "financing-statement filing -- a well-known Article 9/state "
            "vehicle-code characteristic, not yet grounded in an ingested "
            "citation."
        ),
        priority_notes="A lien noted on the certificate of title generally has priority over a later UCC-1 filing against the same vehicle; not yet grounded in an ingested citation.",
        controlling_documents=["Certificate of title", "Bill of sale", "Lien release (once loan is paid off)"],
        record_retention_notes="Keep the certificate of title and any lien-release document indefinitely -- both are needed to prove clear ownership on resale.",
        governing_bodies_of_law=["UCC Article 2 (sale of goods)", "state motor-vehicle title law", "UCC Article 9 (as collateral, not yet ingested)"],
        jurisdiction="Commonwealth of Virginia",
        common_mistakes=[
            "Treating a bill of sale alone as sufficient proof of clear title -- a lender's lien can still be noted on the certificate.",
            "Assuming a standard UCC-1 filing perfects a vehicle lien the same way it perfects a lien on equipment or inventory.",
            "Forgetting that possession of the vehicle (e.g. a buyer who took delivery but never got the title transferred) is not the same as owning it.",
        ],
        citation=goods_section["citation"],
        section_id=goods_section["section_id"],
        citation_grounding_note=(
            "legal_classification's Article-2 'goods' claim is grounded in "
            f'the real ingested {goods_section["citation"]}. The '
            "certificate-of-title and Article 9 perfection claims are "
            "well-known but not yet grounded in an ingested citation."
        ),
    )


def build_accounts_receivable_profile() -> AssetProfile:
    """An account receivable is a payment right, not a physical thing --
    Article 9 governs it as collateral ("accounts") but Article 9 is not
    yet ingested in this codebase, so every Article-9-specific claim below
    is disclosed as ungrounded rather than cited to a specific section."""
    return AssetProfile(
        asset_type=AssetType.ACCOUNTS_RECEIVABLE,
        legal_classification=(
            'A payment right owed to a business for goods sold or services '
            'rendered, not yet evidenced by an instrument or chattel paper. '
            'Well-known Article 9 term of art: an "account." Not yet '
            "grounded in an ingested citation -- see citation_grounding_note."
        ),
        evidence_of_ownership=[
            "Invoice issued to the account debtor",
            "Sales/service ledger or accounting records",
            "Underlying contract or purchase order",
        ],
        title_concept="No physical title concept -- ownership is simply the right to collect, held by whoever the account debtor actually owes.",
        possession_concept="Not possessable -- an account is intangible; nothing to physically hold.",
        control_concept="N/A in the deposit-account/investment-asset sense (accounts are not a 'control' collateral category).",
        transferability="Freely transferable by sale or assignment; notice to the account debtor is generally advisable (though not always legally required) so payment is redirected correctly.",
        assignability="Assignable -- selling accounts receivable (factoring) is a routine commercial financing transaction built entirely on this assignability.",
        security_interest_eligible=True,
        perfection_method="Generally by filing a UCC-1 financing statement describing the accounts as collateral -- well-known, not yet grounded in an ingested citation.",
        priority_notes="First-to-file-or-perfect generally governs competing claims to the same accounts; not yet grounded in an ingested citation.",
        controlling_documents=["Invoice", "Underlying sale/service contract", "Assignment or factoring agreement, if sold"],
        record_retention_notes="Retain invoices and payment records for the underlying commercial relationship and for any later collection or audit dispute.",
        governing_bodies_of_law=["UCC Article 9 (as collateral, not yet ingested)", "general contract law governing the underlying sale/service"],
        jurisdiction="Commonwealth of Virginia",
        common_mistakes=[
            'Treating "accounts receivable" as if it were the underlying contract itself, rather than the payment right the contract creates.',
            "Assuming an account can be perfected by possession -- it cannot, since there is nothing tangible to possess.",
            "Forgetting to notify the account debtor after a factoring sale, risking payment going to the wrong party.",
        ],
        citation=None,
        section_id=None,
        citation_grounding_note=ARTICLE_9_NOT_YET_INGESTED_NOTE,
    )


def build_promissory_note_profile() -> AssetProfile:
    """A promissory note is a negotiable instrument -- governed by UCC
    Article 3 (not yet ingested) for its negotiability rules, and by
    Article 9 (also not yet ingested) when used as loan collateral."""
    return AssetProfile(
        asset_type=AssetType.PROMISSORY_NOTE,
        legal_classification=(
            'A negotiable "instrument" evidencing an unconditional promise '
            "to pay a fixed sum of money -- the physical/electronic note "
            "itself is the thing that must be possessed and transferred to "
            "enforce the payment right, distinguishing it from a plain "
            "account. Well-known UCC Article 3/9 classification, not yet "
            "grounded in an ingested citation."
        ),
        evidence_of_ownership=["The note itself (possession is central)", "Any allonge or endorsement chain", "Loan/security agreement referencing the note"],
        title_concept="Ownership of the payment right generally travels with rightful possession of the note, especially once properly endorsed -- unlike an account, the paper (or its authoritative electronic equivalent) itself matters.",
        possession_concept="Possession is central -- enforcing a note typically requires being a 'holder' in physical or authoritative-electronic possession of it, not merely being the party owed money.",
        control_concept="For an electronic note, 'control' (an Article 9 concept analogous to possession of a paper note) generally substitutes for physical possession -- not yet grounded in an ingested citation.",
        transferability="Transferable by negotiation -- delivery of the note, plus endorsement if payable to a specific person (order paper).",
        assignability="Can also be assigned like an ordinary contract right, though negotiation (delivery + endorsement) carries stronger legal protections for a good-faith transferee than a mere assignment.",
        security_interest_eligible=True,
        perfection_method="Perfection of a security interest in a note (an 'instrument') generally requires the secured party to take possession (or control, if electronic) -- filing alone is typically not enough for priority against certain later claimants. Well-known, not yet grounded in an ingested citation.",
        priority_notes="A holder in due course of a negotiable note can take free of many claims/defenses that would otherwise apply -- a materially different priority regime than for a plain account. Not yet grounded in an ingested citation.",
        controlling_documents=["The promissory note itself", "Any allonge (attached endorsement page)", "Underlying loan or security agreement"],
        record_retention_notes="Retain the original note (or authoritative electronic record) itself -- unlike an account, losing the paper can materially impair the ability to enforce payment.",
        governing_bodies_of_law=["UCC Article 3 (negotiable instruments, not yet ingested)", "UCC Article 9 (as collateral, not yet ingested)"],
        jurisdiction="Commonwealth of Virginia",
        common_mistakes=[
            "Treating a promissory note the same as an ordinary account receivable -- the possession/negotiation rules are materially different.",
            "Assuming a photocopy of the note is as good as the original for enforcement purposes.",
            "Filing a UCC-1 alone and assuming that perfects a security interest in the note, without also taking possession or control.",
        ],
        citation=None,
        section_id=None,
        citation_grounding_note=ARTICLE_9_NOT_YET_INGESTED_NOTE.replace(
            "Article 9 (secured transactions)", "Article 3 (negotiable instruments) and Article 9 (secured transactions)"
        ),
    )


def build_real_property_profile() -> AssetProfile:
    """Deliberate non-UCC contrast profile. Exists specifically to teach
    the boundary that UCC Article 2 (sales of goods) and UCC Article 9
    (secured transactions in personal property) do NOT govern real
    property -- real property is fee simple/leasehold/easement land law,
    recorded in a land-records/deed system, not a UCC filing system. This
    function must never mark security_interest_eligible True under a UCC
    theory; see test_asset_intelligence.py for an explicit assertion of
    that boundary."""
    goods_section = _require_section("8.2-105")
    return AssetProfile(
        asset_type=AssetType.REAL_PROPERTY,
        legal_classification=(
            "Land and things permanently affixed to it -- explicitly NOT "
            f'"goods" under {goods_section["citation"]}\'s own definition, '
            "which is limited to things movable at the time of "
            "identification to the contract. Real property is governed by "
            "state real-property/land law, not UCC Article 2 (sales of "
            "goods) and not UCC Article 9 (security interests in personal "
            "property). This profile exists specifically to mark that "
            "boundary, not to describe a UCC asset category."
        ),
        evidence_of_ownership=[
            "Recorded deed in the land records of the county/city where the property is located",
            "Title insurance policy/commitment",
            "Chain-of-title abstract",
        ],
        title_concept=(
            "Title to real property is a fee-simple, leasehold, or other "
            "estate/interest recognized by real-property law, transferred "
            "by a properly executed and delivered deed -- not by delivery "
            "of a movable thing, and not by any UCC mechanism."
        ),
        possession_concept="Possession (occupancy) is legally relevant (e.g. adverse possession, landlord-tenant law) but is NOT the primary evidence of ownership -- the recorded deed is.",
        control_concept="N/A as a UCC Article 9 'control' collateral category -- real property is never UCC collateral, so this concept does not apply to it at all.",
        transferability="Transferred by a validly executed, delivered, and (for protection against later purchasers) recorded deed -- an entirely different formality regime than UCC Article 2 goods transfers.",
        assignability="A leasehold interest or contract right to purchase real property (e.g. an option or purchase contract) can be assignable per its own terms, but the fee interest itself is conveyed by deed, not 'assigned.'",
        security_interest_eligible=False,
        perfection_method=(
            "Not applicable under UCC Article 9 at all -- real property is "
            "expressly outside Article 9's scope. A lien on real property "
            "(a mortgage or deed of trust) is instead perfected by "
            "recording the security instrument in the land records, a "
            "wholly separate real-property recording system, not a UCC-1 "
            "filing."
        ),
        priority_notes=(
            "Real-property lien priority is generally governed by "
            "recording-act rules (e.g. first-in-time/first-to-record, "
            "subject to notice/race-notice variations) in the land-records "
            "system -- NOT by UCC Article 9's first-to-file-or-perfect "
            "collateral priority rules, which never apply to real property."
        ),
        controlling_documents=["Deed", "Mortgage or deed of trust (if financed)", "Title insurance policy", "Survey/plat"],
        record_retention_notes="Retain the recorded deed, title insurance policy, and closing documents indefinitely -- these are the chain-of-title record for as long as the property is owned.",
        governing_bodies_of_law=["state real-property law", "state recording/land-records law"],
        jurisdiction="Commonwealth of Virginia",
        common_mistakes=[
            "Assuming UCC Article 9 can be used to perfect a security interest against real property -- it cannot; a mortgage/deed of trust recorded in the land records is required instead.",
            'Treating fixtures (goods permanently attached to real property) as automatically real property -- fixtures actually straddle both regimes and have their own UCC "fixture filing" rules, distinct from ordinary real property.',
            "Confusing possession/occupancy of land with legal title to it.",
            f'Miscategorizing land as "goods" under {goods_section["citation"]} because it is being bought and sold -- the definition\'s own movability requirement excludes it.',
        ],
        citation=goods_section["citation"],
        section_id=goods_section["section_id"],
        citation_grounding_note=(
            f'The non-UCC contrast is grounded in the real ingested '
            f'{goods_section["citation"]} "goods" definition itself (real '
            "property falls outside it because it is not movable) -- this "
            "is the one real citation this profile needs, precisely "
            "because the whole point is what does NOT apply."
        ),
    )


def build_all_profiles() -> list[AssetProfile]:
    return [
        build_consumer_goods_profile(),
        build_vehicle_profile(),
        build_accounts_receivable_profile(),
        build_promissory_note_profile(),
        build_real_property_profile(),
    ]


if __name__ == "__main__":
    import json

    print(json.dumps([p.to_dict() for p in build_all_profiles()], indent=2, ensure_ascii=False))

"""Law Engine -- UCC Orientation learning layer (Live Run 1.40/1.41).

A real, typed "start here" data structure meant to sit in front of the
`/learn` UI, before a learner drops into individual ingested statute
sections (today: 11 Article 2 sections and 13 Article 9 sections -- see
services/ingestion.py and services/ingestion_article9.py). Answers, for a
total newcomer: what the UCC is, why something like it needed to exist,
what "uniform" actually means procedurally, whether the UCC itself is
binding law, why it's split into Articles, how the Articles interact in a
real transaction, and why a businessperson/lawyer/lender/borrower/
merchant/investor should care.

Same trust-but-verify, never-invent-a-citation discipline as
asset_intelligence.py and document_intelligence.py: every structural/
historical claim below traces to a real source (see `SOURCES` and each
ArticleOverview's own notes), and every `model_uc_citation` is a real
Article designation (e.g. "UCC Article 9"), never a fabricated section
number. Real, current research grounding this module is written up in
docs/ucc-orientation.md (learner-facing) and reuses the licensing/
enactment research already done in docs/ucc-source-licensing-audit.md
(the government-edicts-doctrine / Georgia v. Public.Resource.Org
reasoning for why a state's *enactment* -- not the ALI/ULC "official"
text -- is Law Engine's real, republishable source layer).

`related_asset_types`/`related_document_families` reuse the real, existing
AssetType (services/asset_intelligence.py) and DocumentFamily
(services/document_intelligence.py) enums -- read-only imports, no new
parallel taxonomy invented. Where no real enum member represents a given
Article's subject matter yet (e.g. Article 5's letter of credit, Article
8's security entitlement), the list is left empty and
`asset_document_mapping_note` says so explicitly, the same "unpopulated is
honest, invented is not" pattern those two modules already use.

Does NOT import from or edit services/models.py -- a concurrent task may
be editing it. This module's own dataclasses are self-contained.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.asset_intelligence import AssetType
from services.document_intelligence import DocumentFamily
from services.retrieval import load_sections


class UccOrientationError(Exception):
    """Raised for real, unrecoverable construction errors in this module
    (e.g. a caller asking for an UccArticle that isn't one of the 11 real
    ArticleOverview records this module builds)."""


class UccArticle(str, Enum):
    """The 11 real, currently-enacted-in-some-form UCC Articles this
    module builds a full ArticleOverview for. Article 12 (Controllable
    Electronic Records, added by the 2022 amendments) is real and current
    -- confirmed enacted in Virginia as Title 8.12 -- but is deliberately
    NOT one of these 11; see UccOrientation.article_12_note instead, per
    this module's own scoping instruction."""

    ARTICLE_1 = "1"
    ARTICLE_2 = "2"
    ARTICLE_2A = "2A"
    ARTICLE_3 = "3"
    ARTICLE_4 = "4"
    ARTICLE_4A = "4A"
    ARTICLE_5 = "5"
    ARTICLE_6 = "6"
    ARTICLE_7 = "7"
    ARTICLE_8 = "8"
    ARTICLE_9 = "9"


@dataclass
class ArticleOverview:
    """Everything a total newcomer needs to orient to one real UCC
    Article before reading any actual statutory section. Every narrative
    field is Law Engine's own plain-language explanation (never copied
    commercial study-aid text); every citation-shaped field
    (`model_uc_citation`, `virginia_enactment_title`) is a real,
    verifiable designation, never invented."""

    article: UccArticle
    display_name: str
    model_uc_citation: str
    subject_matter: str
    why_separate_article: str
    practical_problem_solved: str
    real_world_example: str
    connects_to_article: UccArticle
    cross_article_connection_note: str
    virginia_enactment_title: str | None
    virginia_enactment_note: str
    has_ingested_coverage: bool
    ingested_coverage_note: str
    related_asset_types: list[AssetType] = field(default_factory=list)
    related_document_families: list[DocumentFamily] = field(default_factory=list)
    asset_document_mapping_note: str = ""

    def to_dict(self) -> dict:
        return {
            "article": self.article.value,
            "display_name": self.display_name,
            "model_uc_citation": self.model_uc_citation,
            "subject_matter": self.subject_matter,
            "why_separate_article": self.why_separate_article,
            "practical_problem_solved": self.practical_problem_solved,
            "real_world_example": self.real_world_example,
            "connects_to_article": self.connects_to_article.value,
            "cross_article_connection_note": self.cross_article_connection_note,
            "virginia_enactment_title": self.virginia_enactment_title,
            "virginia_enactment_note": self.virginia_enactment_note,
            "has_ingested_coverage": self.has_ingested_coverage,
            "ingested_coverage_note": self.ingested_coverage_note,
            "related_asset_types": [a.value for a in self.related_asset_types],
            "related_document_families": [d.value for d in self.related_document_families],
            "asset_document_mapping_note": self.asset_document_mapping_note,
        }


@dataclass
class UccOrientation:
    """The top-level "why does uniform commercial law exist at all"
    narrative plus all 11 real ArticleOverview records and an honest note
    on the real, current Article 12 gap. `sources` lists the real URLs
    this module's factual/structural claims were checked against (see
    docs/ucc-orientation.md for the full annotated provenance section)."""

    why_uniform_commercial_law_exists: str
    what_uniform_means_in_practice: str
    is_the_ucc_itself_binding_law: str
    why_split_into_articles: str
    articles: list[ArticleOverview]
    article_12_note: str
    sources: list[str] = field(default_factory=list)

    def get_article(self, article: UccArticle) -> ArticleOverview:
        for overview in self.articles:
            if overview.article == article:
                return overview
        raise UccOrientationError(f"{article!r} is not one of this orientation's real ArticleOverview records.")

    def to_dict(self) -> dict:
        return {
            "why_uniform_commercial_law_exists": self.why_uniform_commercial_law_exists,
            "what_uniform_means_in_practice": self.what_uniform_means_in_practice,
            "is_the_ucc_itself_binding_law": self.is_the_ucc_itself_binding_law,
            "why_split_into_articles": self.why_split_into_articles,
            "articles": [a.to_dict() for a in self.articles],
            "article_12_note": self.article_12_note,
            "sources": self.sources,
        }


def _count_ingested_sections(section_id_prefix: str) -> int:
    """Real, live count of ingested sections whose section_id starts with
    the given prefix (e.g. "8.2-" or "8.9A-") -- read from the real
    normalized library, not hand-typed, so this module's
    `ingested_coverage_note` values can never drift stale against a
    future re-ingestion."""
    return sum(1 for section_id in load_sections() if section_id.startswith(section_id_prefix))


ARTICLE_9_CONNECTION_NOTE = (
    "Article 2 governs the sale of goods (transfer of ownership for a price); Article 9 governs "
    "taking a security interest in goods (or other personal property) as loan collateral. The same "
    "physical good -- e.g. a piece of equipment -- can be the subject of both an Article 2 sale and an "
    "Article 9 security interest in the same transaction, and the two bodies of rules answer different "
    "questions about it (was there a valid sale and what are the warranty/remedy consequences, vs. did "
    "a security interest attach/perfect and who has priority in the collateral). "
    "services/cross_article_lifecycle.py demonstrates this with a real, six-stage equipment-purchase-"
    "on-credit lifecycle citing real ingested sections from both Articles."
)


def _build_article_1() -> ArticleOverview:
    return ArticleOverview(
        article=UccArticle.ARTICLE_1,
        display_name="Article 1 -- General Provisions",
        model_uc_citation="UCC Article 1",
        subject_matter=(
            "General definitions (e.g. \"agreement,\" \"good faith,\" \"conspicuous\") and interpretive "
            "principles that apply across every other UCC Article, plus rules on how the Code should be "
            "construed and how parties can vary its provisions by agreement."
        ),
        why_separate_article=(
            "Every other Article relies on a shared set of basic terms and interpretive rules -- if each "
            "Article defined \"good faith\" or \"agreement\" independently, the same word could mean "
            "different things in a sales dispute (Article 2) than in a secured-lending dispute (Article "
            "9). Article 1 exists specifically so that foundational vocabulary and interpretive "
            "principles live in one place and stay consistent everywhere else in the Code."
        ),
        practical_problem_solved=(
            "Prevents inconsistent or duplicated definitions across the other Articles, and states the "
            "Code's own baseline interpretive rules (liberal construction to promote its underlying "
            "purposes, and an obligation of good faith in every contract's performance and enforcement) "
            "so a court or drafter isn't left guessing which article's version of a shared term controls."
        ),
        real_world_example=(
            "A court deciding whether a seller acted in \"good faith\" under an Article 2 sales dispute "
            "looks to Article 1's own general definition of good faith (honesty in fact and the "
            "observance of reasonable commercial standards of fair dealing) -- Article 2's ingested text "
            "does not redefine the term itself."
        ),
        connects_to_article=UccArticle.ARTICLE_2,
        cross_article_connection_note=(
            "Article 1's definitions and interpretive principles apply to every other Article, including "
            "the real, ingested Article 2 sections this system already has -- it is the one Article every "
            "other Article \"connects to\" by design, not by any single transaction-specific link."
        ),
        virginia_enactment_title="Title 8.1A (Uniform Commercial Code -- General Provisions)",
        virginia_enactment_note=(
            "Virginia enacts Article 1 as Title 8.1A, not Title 8.1 -- the \"A\" suffix marks it as the "
            "post-1990s-revision numbering (Virginia, like most states, renumbered Article 1 with an "
            "\"A\" when it enacted the Uniform Law Commission's revised Article 1)."
        ),
        has_ingested_coverage=False,
        ingested_coverage_note=(
            "Not yet ingested into Law Engine. Only Article 2 (11 sections) and Article 9 (13 sections) "
            "have real, ingested Virginia statutory text as of this module's creation."
        ),
        related_asset_types=[],
        related_document_families=[],
        asset_document_mapping_note=(
            "Article 1 is cross-cutting general provisions and definitions -- it does not itself govern "
            "any specific AssetType or DocumentFamily. The real asset/document mappings live in the "
            "substantive Articles (2, 9, etc.) that Article 1's definitions support."
        ),
    )


def _build_article_2() -> ArticleOverview:
    return ArticleOverview(
        article=UccArticle.ARTICLE_2,
        display_name="Article 2 -- Sales",
        model_uc_citation="UCC Article 2",
        subject_matter=(
            "The sale of goods -- movable personal property -- between a buyer and a seller: contract "
            "formation, warranties, performance/delivery, risk of loss, breach, and remedies."
        ),
        why_separate_article=(
            "Selling a couch -- transferring ownership of it for a price -- raises a distinct set of "
            "legal questions (was there a valid offer and acceptance? does it come with an implied "
            "warranty of merchantability? who bears the risk if it's damaged in transit? what can the "
            "buyer do if it's defective?) from taking a security interest in that same couch as loan "
            "collateral (Article 9's subject, not Article 2's). Article 2 needed its own body of rules "
            "tailored to the sale transaction specifically, distinct from general common-law contract "
            "doctrine (which developed mostly around land and services, not fungible movable goods sold "
            "in volume) and distinct from Article 9's financing-focused rules."
        ),
        practical_problem_solved=(
            "Standardizes contract formation for goods (including the \"battle of the forms\" problem "
            "when a buyer's and seller's form contracts have conflicting boilerplate), fills in default "
            "warranty and risk-of-loss terms so parties don't have to negotiate every detail from "
            "scratch, and gives both merchants and consumers a predictable set of remedies when a sale "
            "of goods goes wrong."
        ),
        real_world_example=(
            "Buying a laptop from a retailer: Article 2 is what supplies the implied warranty that the "
            "laptop is fit for ordinary use (merchantability), governs when the seller's title/risk of "
            "loss passes to the buyer, and determines the buyer's remedies (rejection, revocation of "
            "acceptance, damages) if the laptop turns out to be defective."
        ),
        connects_to_article=UccArticle.ARTICLE_9,
        cross_article_connection_note=ARTICLE_9_CONNECTION_NOTE,
        virginia_enactment_title="Title 8.2 (Commercial Code -- Sales)",
        virginia_enactment_note=(
            "Virginia enacts Article 2 as plain Title 8.2 (no \"A\" suffix) -- this is the Article Law "
            "Engine's own real ingestion (services/ingestion.py) already sources directly from, at "
            "https://law.lis.virginia.gov/vacode/title8.2/."
        ),
        has_ingested_coverage=True,
        ingested_coverage_note=(
            f"TRUE -- {_count_ingested_sections('8.2-')} real Virginia Code Title 8.2 sections are "
            "ingested (services/ingestion.py), covering scope, merchant status, contract formation, "
            "offer/acceptance, warranties, and breach/remedies. This is a real, disclosed subset of the "
            "full Article, not full coverage."
        ),
        related_asset_types=[AssetType.CONSUMER_GOODS, AssetType.VEHICLE, AssetType.INVENTORY, AssetType.EQUIPMENT],
        related_document_families=[DocumentFamily.CONTRACT, DocumentFamily.PURCHASE_ORDER, DocumentFamily.INVOICE],
        asset_document_mapping_note=(
            "All four AssetTypes and all three DocumentFamilies listed are real, existing enum members "
            "from services/asset_intelligence.py and services/document_intelligence.py, several of which "
            "(CONSUMER_GOODS, PURCHASE_ORDER, INVOICE, CONTRACT) are already directly grounded in this "
            "same ingested Article 2 text in those modules."
        ),
    )


def _build_article_2a() -> ArticleOverview:
    return ArticleOverview(
        article=UccArticle.ARTICLE_2A,
        display_name="Article 2A -- Leases",
        model_uc_citation="UCC Article 2A",
        subject_matter=(
            "Leases of goods -- a lessor gives a lessee the right to possess and use goods for a term in "
            "exchange for rent, without transferring ownership -- including consumer-lease protections "
            "and how to tell a genuine lease apart from a sale disguised as a lease (a security interest "
            "in the form of a lease)."
        ),
        why_separate_article=(
            "A lease is economically and legally different from a sale: the lessor keeps ownership and "
            "expects the goods back, the lessee never becomes the owner, and default/remedy questions "
            "run on a different track than Article 2's buyer/seller remedies. Article 2A largely mirrors "
            "Article 2's structure (warranties, performance, default) but tailored to the lease "
            "relationship, and adds a real, fact-intensive test for distinguishing a true lease from a "
            "security interest dressed up as one -- a distinction that matters enormously, since a "
            "\"lease\" that's really a disguised sale-on-credit is actually governed by Article 9, not "
            "Article 2A."
        ),
        practical_problem_solved=(
            "Gives lessors and lessees of goods (equipment leases, vehicle leases, etc.) their own "
            "predictable default warranty/remedy rules, and gives courts a real test for recharacterizing "
            "a mislabeled \"lease\" as the secured sale it actually is, protecting a lessee's expectation "
            "that a true lease ends with simply returning the goods, not owing a deficiency balance."
        ),
        real_world_example=(
            "Leasing a car for three years: Article 2A governs the lease terms, implied warranties, and "
            "what happens if the car is defective -- a materially different set of default rules than "
            "Article 2 would supply if the same car were purchased outright."
        ),
        connects_to_article=UccArticle.ARTICLE_9,
        cross_article_connection_note=(
            "Whether a transaction labeled a \"lease\" is really a true Article 2A lease or is instead a "
            "security interest in the form of a lease (and therefore governed by Article 9's attachment/ "
            "perfection/priority rules instead) is itself a real, recurring cross-Article classification "
            "question -- the label on the document does not control, the economic substance does."
        ),
        virginia_enactment_title="Title 8.2A (Commercial Code -- Leases)",
        virginia_enactment_note="Virginia enacts Article 2A as Title 8.2A, following the standard \"Title 8.<article>A\" pattern for this Article.",
        has_ingested_coverage=False,
        ingested_coverage_note=(
            "Not yet ingested into Law Engine. Only Article 2 (11 sections) and Article 9 (13 sections) "
            "have real, ingested Virginia statutory text as of this module's creation."
        ),
        related_asset_types=[AssetType.VEHICLE, AssetType.EQUIPMENT],
        related_document_families=[DocumentFamily.LEASE],
        asset_document_mapping_note=(
            "VEHICLE, EQUIPMENT, and LEASE are real, existing enum members from services/"
            "asset_intelligence.py and services/document_intelligence.py -- no new taxonomy invented."
        ),
    )


def _build_article_3() -> ArticleOverview:
    return ArticleOverview(
        article=UccArticle.ARTICLE_3,
        display_name="Article 3 -- Negotiable Instruments",
        model_uc_citation="UCC Article 3",
        subject_matter=(
            "What makes a written promise or order to pay money (a check, a promissory note, a draft) a "
            "\"negotiable instrument\"; how such instruments are transferred (negotiation, indorsement); "
            "and the special protection a good-faith transferee (a \"holder in due course\") gets against "
            "many defenses the original obligor could otherwise raise."
        ),
        why_separate_article=(
            "A negotiable instrument is designed to function like a reliable, transferable substitute for "
            "money or credit -- that only works if there's a formal, predictable set of requirements for "
            "what counts as negotiable and strong legal protection for someone who takes the instrument in "
            "good faith. Ordinary contract-assignment law doesn't give a transferee that kind of "
            "protection, so Article 3 needed its own, more rigid formal rules distinct from both Article "
            "2's flexible sale-of-goods formation rules and ordinary contract law."
        ),
        practical_problem_solved=(
            "Makes checks, notes, and drafts reliably transferable in commerce by giving a good-faith "
            "holder-in-due-course protection from many of the maker's or drawer's personal defenses -- "
            "without this, instruments would carry too much transfer risk to function as a practical "
            "payment or credit mechanism."
        ),
        real_world_example=(
            "Writing a personal check to pay a contractor, or a business signing a promissory note "
            "payable to a lender -- Article 3 supplies the negotiability rules for both, and determines "
            "what happens if the check or note is later transferred to someone else."
        ),
        connects_to_article=UccArticle.ARTICLE_4,
        cross_article_connection_note=(
            "A check is a negotiable instrument (Article 3's subject) that also has to move through the "
            "banking system to be collected and paid -- Article 4 governs that collection/settlement "
            "process (provisional credit, final settlement, forged/altered-item allocation), so a single "
            "check transaction routinely implicates both Articles."
        ),
        virginia_enactment_title="Title 8.3A (Commercial Code -- Negotiable Instruments)",
        virginia_enactment_note=(
            "Virginia enacts Article 3 as Title 8.3A. The Article's own official title changed from "
            "\"Commercial Paper\" to \"Negotiable Instruments\" in the ULC/ALI's 1990 revision -- Virginia's "
            "Title 8.3A reflects the current, post-1990 name."
        ),
        has_ingested_coverage=False,
        ingested_coverage_note=(
            "Not yet ingested into Law Engine. Only Article 2 (11 sections) and Article 9 (13 sections) "
            "have real, ingested Virginia statutory text as of this module's creation."
        ),
        related_asset_types=[AssetType.PROMISSORY_NOTE, AssetType.CHECK],
        related_document_families=[DocumentFamily.PROMISSORY_NOTE, DocumentFamily.NEGOTIABLE_INSTRUMENT, DocumentFamily.CHECK_DRAFT],
        asset_document_mapping_note=(
            "PROMISSORY_NOTE, CHECK, NEGOTIABLE_INSTRUMENT, and CHECK_DRAFT are all real, existing enum "
            "members from services/asset_intelligence.py and services/document_intelligence.py -- no new "
            "taxonomy invented."
        ),
    )


def _build_article_4() -> ArticleOverview:
    return ArticleOverview(
        article=UccArticle.ARTICLE_4,
        display_name="Article 4 -- Bank Deposits and Collections",
        model_uc_citation="UCC Article 4",
        subject_matter=(
            "The bank-customer relationship and the mechanics of collecting and paying checks and other "
            "items through the banking system: provisional vs. final settlement, a bank's rights and "
            "duties on forged or altered items, and deadlines for a customer to report problems."
        ),
        why_separate_article=(
            "Whether a check is negotiable at all (Article 3's question) is a different problem from how "
            "that check actually moves and settles between the depositary bank, intermediary banks, and "
            "the payor bank -- a process with its own timing, provisional-credit, and loss-allocation "
            "rules that Article 3's negotiability framework doesn't address. Article 4 needed its own "
            "rules for the banking-system mechanics specifically."
        ),
        practical_problem_solved=(
            "Gives banks and customers predictable rules for when deposited funds become final "
            "(vs. merely provisional, subject to being reversed if the check bounces), and allocates loss "
            "when a check turns out to be forged or altered -- without this, every deposit would carry "
            "open-ended uncertainty about whether the money is really the customer's yet."
        ),
        real_world_example=(
            "Depositing a check: the bank often gives \"provisional credit\" right away, but that credit "
            "can be reversed if the check is later returned unpaid -- Article 4 is what defines that "
            "provisional-vs-final distinction and the deadlines around it."
        ),
        connects_to_article=UccArticle.ARTICLE_3,
        cross_article_connection_note=(
            "Article 4's bank-collection rules operate on instruments whose negotiability and transfer "
            "rules come from Article 3 -- the two Articles routinely govern the same check at different "
            "points in its life (issuance/transfer under Article 3, collection/settlement under Article 4)."
        ),
        virginia_enactment_title="Title 8.4 (Commercial Code -- Bank Deposits and Collections)",
        virginia_enactment_note="Virginia enacts Article 4 as plain Title 8.4 (no \"A\" suffix).",
        has_ingested_coverage=False,
        ingested_coverage_note=(
            "Not yet ingested into Law Engine. Only Article 2 (11 sections) and Article 9 (13 sections) "
            "have real, ingested Virginia statutory text as of this module's creation."
        ),
        related_asset_types=[AssetType.BANK_ACCOUNT, AssetType.CHECK],
        related_document_families=[DocumentFamily.CHECK_DRAFT],
        asset_document_mapping_note=(
            "BANK_ACCOUNT, CHECK, and CHECK_DRAFT are real, existing enum members from services/"
            "asset_intelligence.py and services/document_intelligence.py -- no new taxonomy invented."
        ),
    )


def _build_article_4a() -> ArticleOverview:
    return ArticleOverview(
        article=UccArticle.ARTICLE_4A,
        display_name="Article 4A -- Funds Transfers",
        model_uc_citation="UCC Article 4A",
        subject_matter=(
            "Wholesale, bank-to-bank electronic funds transfers (wire transfers) -- how a \"payment "
            "order\" is accepted, when a transfer is complete, and how errors, delays, and fraudulent "
            "payment orders are handled between banks and their business customers."
        ),
        why_separate_article=(
            "A wire transfer has no check, note, or other physical/negotiable item involved at all -- "
            "it's a chain of electronic payment orders between banks. Neither Article 3 (which assumes an "
            "instrument) nor Article 4 (which assumes a collected item) fits that structure, so Article "
            "4A needed its own rules built around the payment-order/acceptance model, largely developed "
            "because large-value wire transfers move enormous sums almost instantly and needed clear, "
            "bank-industry-workable loss-allocation rules distinct from consumer electronic-transfer law "
            "(which is governed separately, by federal Regulation E, not Article 4A)."
        ),
        practical_problem_solved=(
            "Allocates the risk of a fraudulent, erroneous, or delayed wire transfer between the "
            "originator, the banks involved, and the beneficiary, and gives a bank a defense when it "
            "followed a commercially reasonable security procedure -- without this, high-value business "
            "wire transfers would carry unpredictable, potentially bank-crippling liability exposure."
        ),
        real_world_example=(
            "A business wiring $500,000 to a supplier's bank account to close a large purchase -- Article "
            "4A is what governs when that payment order is accepted, when the transfer is legally "
            "complete, and who bears the loss if it's intercepted by fraud or sent to the wrong account."
        ),
        connects_to_article=UccArticle.ARTICLE_4,
        cross_article_connection_note=(
            "Article 4A and Article 4 both govern moving money between banks, but on different payment "
            "rails -- Article 4A for electronic payment orders (wires), Article 4 for check-based "
            "collection -- and a single commercial relationship (e.g. a business's banking relationship) "
            "routinely uses both."
        ),
        virginia_enactment_title="Title 8.4A (Commercial Code -- Funds Transfers)",
        virginia_enactment_note="Virginia enacts Article 4A as Title 8.4A.",
        has_ingested_coverage=False,
        ingested_coverage_note=(
            "Not yet ingested into Law Engine. Only Article 2 (11 sections) and Article 9 (13 sections) "
            "have real, ingested Virginia statutory text as of this module's creation."
        ),
        related_asset_types=[AssetType.MONEY, AssetType.BANK_ACCOUNT],
        related_document_families=[],
        asset_document_mapping_note=(
            "MONEY and BANK_ACCOUNT are real, existing AssetType members. No existing DocumentFamily "
            "member represents a wire transfer's \"payment order\" (it's an electronic message between "
            "banks, not a document family document_intelligence.py currently models) -- left empty rather "
            "than inventing a new DocumentFamily value."
        ),
    )


def _build_article_5() -> ArticleOverview:
    return ArticleOverview(
        article=UccArticle.ARTICLE_5,
        display_name="Article 5 -- Letters of Credit",
        model_uc_citation="UCC Article 5",
        subject_matter=(
            "Letters of credit -- a bank's independent promise, issued on a buyer/applicant's behalf, to "
            "pay a seller/beneficiary who presents documents conforming to the letter of credit's own "
            "terms, regardless of disputes under the underlying sale contract."
        ),
        why_separate_article=(
            "A letter of credit's entire value depends on the \"independence principle\": the issuing "
            "bank's obligation to pay is judged solely against the documents presented, not against "
            "whether the underlying goods contract was actually performed. That's a fundamentally "
            "different kind of obligation than an ordinary Article 2 sales contract or an Article 3 "
            "negotiable instrument, so it needed its own Article to state and protect that independence."
        ),
        practical_problem_solved=(
            "Lets a seller get paid by presenting conforming documents to a creditworthy bank, without "
            "having to trust a buyer's own creditworthiness or wait out a dispute over whether the "
            "underlying goods actually met the contract -- substituting bank credit risk for buyer credit "
            "risk, which is especially valuable when buyer and seller don't know or trust each other well "
            "(classically, international sales)."
        ),
        real_world_example=(
            "An exporter shipping goods overseas gets paid by presenting a bill of lading and invoice to "
            "the buyer's bank under a letter of credit -- the bank pays on the documents alone, without "
            "second-guessing whether the goods themselves actually matched the underlying sales contract."
        ),
        connects_to_article=UccArticle.ARTICLE_7,
        cross_article_connection_note=(
            "The documents a beneficiary presents to draw on a letter of credit are frequently Article 7 "
            "documents of title (a bill of lading, a warehouse receipt) -- Article 5 governs whether the "
            "bank must pay on presentation, while Article 7 governs what those underlying documents "
            "themselves legally represent and how they transfer rights to the goods."
        ),
        virginia_enactment_title="Title 8.5A (Uniform Commercial Code -- Letters of Credit)",
        virginia_enactment_note="Virginia enacts Article 5 as Title 8.5A.",
        has_ingested_coverage=False,
        ingested_coverage_note=(
            "Not yet ingested into Law Engine. Only Article 2 (11 sections) and Article 9 (13 sections) "
            "have real, ingested Virginia statutory text as of this module's creation."
        ),
        related_asset_types=[],
        related_document_families=[],
        asset_document_mapping_note=(
            "No existing AssetType or DocumentFamily member represents a letter of credit itself -- left "
            "empty rather than inventing a new taxonomy value. (A letter of credit's underlying "
            "presentation documents commonly ARE Article 7's DOCUMENT_OF_TITLE / BILL_OF_LADING / "
            "WAREHOUSE_RECEIPT, which is why Article 5's cross-reference above points to Article 7.)"
        ),
    )


def _build_article_6() -> ArticleOverview:
    return ArticleOverview(
        article=UccArticle.ARTICLE_6,
        display_name="Article 6 -- Bulk Transfers / Bulk Sales",
        model_uc_citation="UCC Article 6 -- withdrawn by the ULC in 1989; repealed or never enacted in the large majority of states",
        subject_matter=(
            "(Historical) Required a merchant selling substantially all of its inventory outside the "
            "ordinary course of business to give advance notice to its creditors, so they could act to "
            "protect their claims before the merchant disappeared with the sale proceeds."
        ),
        why_separate_article=(
            "The specific fact pattern Article 6 targeted -- a merchant secretly liquidating its entire "
            "stock in a single \"bulk\" sale and vanishing before unpaid suppliers could collect -- wasn't "
            "addressed by ordinary Article 2 sale-of-goods rules (which don't require notifying third-"
            "party creditors of a sale at all) or by Article 9 (which protects a secured creditor's own "
            "collateral, not unsecured trade creditors generally). It needed its own notice-to-creditors "
            "mechanism, layered on top of an otherwise ordinary Article 2 sale of the inventory."
        ),
        practical_problem_solved=(
            "(Historical) Gave a merchant's unsecured trade creditors advance warning of a bulk "
            "liquidation so they could intervene before the proceeds disappeared -- a fraud-prevention "
            "tool for a specific 20th-century pattern of \"midnight sale\" abuse."
        ),
        real_world_example=(
            "(Historical) A retail store owner selling the store's entire inventory to a buyer overnight "
            "and closing up shop, leaving unpaid suppliers with no notice and an empty company to collect "
            "from -- Article 6 required advance notice to those creditors before such a sale could bind "
            "them."
        ),
        connects_to_article=UccArticle.ARTICLE_9,
        cross_article_connection_note=(
            "The ULC's own 1989 study concluded that other, more modern creditor-protection tools -- "
            "fraudulent/voidable-transfer law (now the Uniform Voidable Transactions Act in most states) "
            "and Article 9's own security-interest perfection/priority regime -- give creditors better "
            "protection than Article 6's notice mechanism ever did, without burdening ordinary bulk-sale "
            "transactions; that overlap with Article 9's function is a real part of why Article 6 was "
            "withdrawn/repealed rather than kept alongside it."
        ),
        virginia_enactment_title=None,
        virginia_enactment_note=(
            "Virginia has no current Title 8.6 -- confirmed directly against the live Code of Virginia "
            "table of contents (law.lis.virginia.gov/vacode/) this run, which lists Title 8.5A followed "
            "directly by Title 8.7, with no Title 8.6 present. This is the real, practical nuance the "
            "product-vision directive asked to be verified rather than assumed: Article 6 is NOT "
            "presented here as a still-standard, currently-enacted Article in Virginia."
        ),
        has_ingested_coverage=False,
        ingested_coverage_note=(
            "Not ingested, and not expected to be -- Virginia has no enacted Article 6 text to ingest. "
            "Only Article 2 (11 sections) and Article 9 (13 sections) have real, ingested Virginia "
            "statutory text as of this module's creation."
        ),
        related_asset_types=[AssetType.INVENTORY],
        related_document_families=[],
        asset_document_mapping_note=(
            "INVENTORY is a real, existing AssetType member. No existing DocumentFamily member represents "
            "a bulk-sale creditor notice -- left empty rather than inventing a new taxonomy value."
        ),
    )


def _build_article_7() -> ArticleOverview:
    return ArticleOverview(
        article=UccArticle.ARTICLE_7,
        display_name="Article 7 -- Documents of Title",
        model_uc_citation="UCC Article 7",
        subject_matter=(
            "Negotiable and non-negotiable documents of title -- bills of lading (issued by a carrier) "
            "and warehouse receipts (issued by a warehouse) -- and who bears risk and holds rights in "
            "goods while they sit in a bailee's hands."
        ),
        why_separate_article=(
            "A document of title lets someone deal with goods held by a third-party bailee (a carrier or "
            "warehouse) by transferring the document itself, without physically moving the goods -- a "
            "mechanism Article 2's ordinary delivery-based transfer rules don't address at all. Article 7 "
            "needed its own rules for what the document legally represents, how a negotiable document "
            "transfers rights by negotiation (similar in spirit to Article 3's negotiable instruments, but "
            "for goods-in-custody rather than money obligations), and how a bailee's own duties and "
            "liability work."
        ),
        practical_problem_solved=(
            "Lets goods sitting in a warehouse or in transit be bought, sold, or pledged as loan "
            "collateral by dealing with the paper (or electronic equivalent) representing them, instead "
            "of physically moving the goods for every transaction -- essential for storage, shipping, and "
            "commodity/warehouse financing to function efficiently."
        ),
        real_world_example=(
            "A farmer stores grain in a public warehouse and receives a negotiable warehouse receipt; that "
            "receipt can then be sold or pledged as loan collateral without the grain itself ever moving, "
            "because transferring the receipt transfers the rights Article 7 says it represents."
        ),
        connects_to_article=UccArticle.ARTICLE_9,
        cross_article_connection_note=(
            "A document of title is itself a real Article 9 collateral category -- a security interest in "
            "goods covered by a negotiable document of title can be perfected by the secured party taking "
            "possession or control of the document itself, rather than the underlying goods, tying "
            "Article 7's document-transfer mechanism directly into Article 9's perfection rules."
        ),
        virginia_enactment_title="Title 8.7 (Commercial Code -- Warehouse Receipts, Bills of Lading and Other Documents of Title)",
        virginia_enactment_note="Virginia enacts Article 7 as plain Title 8.7 (no \"A\" suffix).",
        has_ingested_coverage=False,
        ingested_coverage_note=(
            "Not yet ingested into Law Engine. Only Article 2 (11 sections) and Article 9 (13 sections) "
            "have real, ingested Virginia statutory text as of this module's creation."
        ),
        related_asset_types=[AssetType.DOCUMENT_OF_TITLE, AssetType.INVENTORY],
        related_document_families=[DocumentFamily.BILL_OF_LADING, DocumentFamily.WAREHOUSE_RECEIPT],
        asset_document_mapping_note=(
            "DOCUMENT_OF_TITLE, INVENTORY, BILL_OF_LADING, and WAREHOUSE_RECEIPT are all real, existing "
            "enum members from services/asset_intelligence.py and services/document_intelligence.py -- no "
            "new taxonomy invented."
        ),
    )


def _build_article_8() -> ArticleOverview:
    return ArticleOverview(
        article=UccArticle.ARTICLE_8,
        display_name="Article 8 -- Investment Securities",
        model_uc_citation="UCC Article 8",
        subject_matter=(
            "Ownership, transfer, and pledging of securities (stocks, bonds), including the modern "
            "\"indirect holding system\" where most investors hold securities through a chain of "
            "brokers/clearing agencies rather than possessing a physical certificate."
        ),
        why_separate_article=(
            "Modern securities are overwhelmingly held indirectly through brokerage accounts, not as "
            "physical certificates in the investor's own possession -- neither Article 2's \"goods\" "
            "framework nor Article 3's negotiable-instrument framework fits an intangible interest tracked "
            "electronically through a chain of intermediaries. Article 8 needed its own \"security "
            "entitlement\" concept and its own rules for how such indirectly-held interests are created, "
            "transferred, and pledged as collateral."
        ),
        practical_problem_solved=(
            "Gives investors, brokers, and lenders a reliable legal framework for buying, selling, and "
            "borrowing against securities held in brokerage accounts, where there is no physical "
            "certificate changing hands for almost any transaction."
        ),
        real_world_example=(
            "Buying shares of stock through a brokerage account: the investor doesn't receive a physical "
            "stock certificate -- Article 8 defines the investor's legal \"security entitlement\" against "
            "the broker instead, which is what actually gets bought, sold, or pledged."
        ),
        connects_to_article=UccArticle.ARTICLE_9,
        cross_article_connection_note=(
            "Investment property (securities and security entitlements) is a real Article 9 collateral "
            "category, and a security interest in it can be perfected by \"control\" of the securities "
            "account -- an Article 8 concept -- rather than by filing, linking the two Articles directly "
            "for any loan secured by an investment portfolio."
        ),
        virginia_enactment_title="Title 8.8A (Commercial Code -- Investment Securities)",
        virginia_enactment_note=(
            "Virginia enacts Article 8 as Title 8.8A (with the \"A\" suffix, reflecting the ULC/ALI's "
            "revised Article 8 adopted to address the modern indirect-holding system) -- confirmed "
            "directly against the live Code of Virginia table of contents this run, since the plain "
            "\"Title 8.8\" (no suffix) numbering some naive extrapolations of the pattern would predict is "
            "not what Virginia actually uses."
        ),
        has_ingested_coverage=False,
        ingested_coverage_note=(
            "Not yet ingested into Law Engine. Only Article 2 (11 sections) and Article 9 (13 sections) "
            "have real, ingested Virginia statutory text as of this module's creation."
        ),
        related_asset_types=[AssetType.INVESTMENT_ASSET],
        related_document_families=[],
        asset_document_mapping_note=(
            "INVESTMENT_ASSET is a real, existing AssetType member. No existing DocumentFamily member "
            "represents a security or security entitlement -- left empty rather than inventing a new "
            "taxonomy value."
        ),
    )


def _build_article_9() -> ArticleOverview:
    return ArticleOverview(
        article=UccArticle.ARTICLE_9,
        display_name="Article 9 -- Secured Transactions",
        model_uc_citation="UCC Article 9",
        subject_matter=(
            "Creation (attachment), public notice (perfection), ranking among competing claimants "
            "(priority), and enforcement (default, repossession, disposition of collateral) of security "
            "interests in personal property."
        ),
        why_separate_article=(
            "Taking a security interest in a couch as loan collateral raises an entirely different set of "
            "legal questions -- did the interest attach, was it perfected, who has priority against other "
            "creditors, what happens on default -- than selling that same couch outright (Article 2's "
            "subject). \"Selling a couch\" and \"borrowing against a couch\" are legally distinct "
            "transactions even when the same physical good and the same two parties are involved, and "
            "Article 9 needed its own comprehensive framework for the financing side specifically."
        ),
        practical_problem_solved=(
            "Gives lenders a reliable, priority-ranked claim against a debtor's personal property, making "
            "secured lending (equipment financing, inventory floor-plan financing, accounts-receivable "
            "financing, etc.) practical at a lower cost/risk than unsecured lending, while giving debtors "
            "and competing creditors predictable rules for how competing claims to the same collateral are "
            "resolved."
        ),
        real_world_example=(
            "A bank financing a business's purchase of manufacturing equipment: it takes a security "
            "interest in the equipment, files a UCC-1 financing statement to perfect it, and -- as a "
            "purchase-money security interest -- gets priority over the business's other, earlier, broader "
            "lenders specifically as to that equipment if the business later defaults."
        ),
        connects_to_article=UccArticle.ARTICLE_2,
        cross_article_connection_note=ARTICLE_9_CONNECTION_NOTE,
        virginia_enactment_title="Title 8.9A (Commercial Code -- Secured Transactions)",
        virginia_enactment_note=(
            "Virginia enacts Article 9 as Title 8.9A -- the Article Law Engine's own real ingestion "
            "(services/ingestion_article9.py) already sources directly from, at "
            "https://law.lis.virginia.gov/vacode/title8.9A/."
        ),
        has_ingested_coverage=True,
        ingested_coverage_note=(
            f"TRUE -- {_count_ingested_sections('8.9A-')} real Virginia Code Title 8.9A sections are "
            "ingested (services/ingestion_article9.py), covering scope/definitions, security-agreement "
            "effectiveness, attachment, after-acquired property/future advances, perfection, the filing "
            "requirement, priority (including purchase-money priority), and default/repossession/"
            "disposition. This is a real, disclosed subset of the full Article (which runs through Part "
            "8; this covers Parts 1-3 and 6, plus one Part 5 filing-trigger section), not full coverage."
        ),
        related_asset_types=[
            AssetType.VEHICLE,
            AssetType.EQUIPMENT,
            AssetType.INVENTORY,
            AssetType.CONSUMER_GOODS,
            AssetType.ACCOUNTS_RECEIVABLE,
            AssetType.PROMISSORY_NOTE,
        ],
        related_document_families=[DocumentFamily.SECURITY_AGREEMENT, DocumentFamily.FINANCING_STATEMENT],
        asset_document_mapping_note=(
            "All six AssetTypes and both DocumentFamilies are real, existing enum members from services/"
            "asset_intelligence.py and services/document_intelligence.py -- every one of those AssetType "
            "profiles already marks security_interest_eligible=True and discusses Article 9 perfection/"
            "priority concepts directly (mostly still flagged there as not-yet-grounded-in-an-ingested-"
            "citation, since that module predates this Article 9 ingestion)."
        ),
    )


_ARTICLE_BUILDERS: dict[UccArticle, "callable[[], ArticleOverview]"] = {
    UccArticle.ARTICLE_1: _build_article_1,
    UccArticle.ARTICLE_2: _build_article_2,
    UccArticle.ARTICLE_2A: _build_article_2a,
    UccArticle.ARTICLE_3: _build_article_3,
    UccArticle.ARTICLE_4: _build_article_4,
    UccArticle.ARTICLE_4A: _build_article_4a,
    UccArticle.ARTICLE_5: _build_article_5,
    UccArticle.ARTICLE_6: _build_article_6,
    UccArticle.ARTICLE_7: _build_article_7,
    UccArticle.ARTICLE_8: _build_article_8,
    UccArticle.ARTICLE_9: _build_article_9,
}


def build_all_article_overviews() -> list[ArticleOverview]:
    """Real, complete set of 11 ArticleOverview records, in Article order
    (1, 2, 2A, 3, 4, 4A, 5, 6, 7, 8, 9). Article 12 is deliberately not
    included here -- see build_ucc_orientation()'s article_12_note."""
    return [_ARTICLE_BUILDERS[article]() for article in UccArticle]


ARTICLE_12_NOTE = (
    "UCC Article 12 (Controllable Electronic Records) is real and current -- added by the 2022 UCC "
    "Amendments to address digital-asset transactions (e.g. virtual currency, NFTs), jointly approved by "
    "the ALI and ULC. It is deliberately NOT one of this module's 11 full ArticleOverview records (the "
    "product-vision directive scoped this orientation to the 11 pre-2022 Articles plus a note on 12, not "
    "a full profile). What IS verified, real, and current as of this module's creation: Virginia has "
    "enacted the 2022 amendments -- confirmed both by docs/ucc-source-licensing-audit.md's prior research "
    "(25 jurisdictions including Virginia, as of February 2025) and directly against the live Code of "
    "Virginia table of contents this run, which lists a real Title 8.12 (\"Controllable Electronic "
    "Records\"). Law Engine has NOT ingested any Title 8.12 text -- has_ingested_coverage for Article 12 "
    "would be False, same as every Article besides 2 and 9. Adoption elsewhere is still actively in "
    "progress state-by-state (33 jurisdictions as of the most recent check in the licensing audit); check "
    "the ULC's own live enactment tracker (uniformlaws.org) before relying on any other state's status."
)


WHY_UNIFORM_COMMERCIAL_LAW_EXISTS = (
    "Before the UCC, commercial law -- the rules for selling goods, using negotiable instruments like "
    "checks and notes, and borrowing against personal property as collateral -- was ordinary state common "
    "law and scattered state statutes, and it did not match up well from state to state. A business "
    "operating in more than one state, or simply contracting with a party in another state, could not "
    "count on the same rules applying to the same transaction depending on which state's law governed -- "
    "a real, practical drag on interstate commerce as the American economy became more national over the "
    "20th century. The Uniform Law Commission (ULC, then named the National Conference of Commissioners "
    "on Uniform State Laws) had existed since 1892 specifically to develop model state legislation for "
    "exactly this kind of problem, and had already produced earlier, narrower uniform acts on negotiable "
    "instruments and sales. Comprehensive work on a single, unified commercial code began around 1940, "
    "as a joint project of the ULC and the American Law Institute (ALI); the first complete draft was "
    "presented to the states in 1951, after roughly a decade of drafting. The Uniform Commercial Code's "
    "own current text states its purposes plainly: \"to simplify, clarify, and modernize the law "
    "governing commercial transactions,\" \"to permit the continued expansion of commercial practices "
    "through custom, usage, and agreement of the parties,\" and \"to make uniform the law among the "
    "various jurisdictions\" (UCC Section 1-103(a)). Uniformity was never valued for its own sake -- it "
    "was, and is, valued because a business (or a lender, borrower, merchant, or investor) can enter a "
    "contract with real confidence that materially the same rules will apply whether the other party, "
    "the goods, or the money are in the same state or a different one."
)

WHAT_UNIFORM_MEANS_IN_PRACTICE = (
    "\"Uniform\" describes the ULC/ALI's own drafting goal and the model text they jointly promulgate -- "
    "it does NOT mean the UCC is automatically, uniformly binding law everywhere. A uniform act, upon "
    "approval by the ULC, is not law anywhere; it is a model statute proposed to all fifty state "
    "legislatures. \"No uniform law is effective until a state legislature adopts it,\" and each "
    "legislature that does adopt one is free to enact it word-for-word, modify specific provisions, or "
    "decline to adopt it at all -- which is exactly why real, state-to-state variation exists today "
    "despite the \"uniform\" name (this project's own SourceLayer enum in services/models.py -- MODEL vs. "
    "ENACTMENT vs. INTERPRETATION -- exists specifically so a state's actual enactment is never silently "
    "presented as if it were identical to, or the same thing as, the ULC/ALI's model text). In practice, "
    "most states' enactments track the model text closely for most provisions, but a specific section can "
    "and sometimes does diverge -- so a real legal question always has to be answered against the "
    "specific enacting state's own statute, never against the model text alone."
)

IS_THE_UCC_ITSELF_BINDING_LAW = (
    "No -- not directly, and this is one of the most commonly misunderstood points for a newcomer. The "
    "ALI/ULC's own \"official\" Uniform Commercial Code text is a jointly copyrighted model act; by "
    "itself it binds no one. What actually governs a real transaction is the specific state's own "
    "enacted statute -- e.g. Virginia's Title 8.2 for a Virginia sale-of-goods dispute -- which a state "
    "legislature adopted (usually closely following, but not required to exactly copy, the ULC/ALI model "
    "text). Once a state legislature enacts its own version, that enacted statutory text becomes a "
    "public-domain government edict under the government-edicts doctrine most recently restated by the "
    "U.S. Supreme Court in Georgia v. Public.Resource.Org, Inc., 590 U.S. 255 (2020) (\"no one can own the "
    "law\") -- which is exactly why Law Engine's own real ingestion (services/ingestion.py, services/"
    "ingestion_article9.py) sources Virginia's enacted Title 8.2 and Title 8.9A text directly from "
    "law.lis.virginia.gov, rather than the ALI/ULC's separately-copyrighted official text. See docs/"
    "ucc-source-licensing-audit.md for the full research behind that sourcing choice, including the real "
    "limits on what the edicts doctrine does and doesn't cover (it doesn't make the ALI/ULC's own "
    "official comments public domain, for instance, even for a section a state has enacted)."
)

WHY_SPLIT_INTO_ARTICLES = (
    "Each Article addresses a distinct kind of commercial transaction that raises genuinely different "
    "legal questions -- forming a contract to sell goods (Article 2) is not the same problem as making a "
    "check transferable with strong protection for a good-faith holder (Article 3), which is not the same "
    "problem as ranking competing lenders' claims to the same collateral (Article 9). Splitting the Code "
    "into Articles by transaction type lets each one develop the specific rules its own transaction "
    "actually needs (warranty and delivery rules for a sale; negotiability and holder-in-due-course rules "
    "for an instrument; attachment/perfection/priority rules for secured lending) without those rules "
    "colliding or having to awkwardly generalize across unrelated fact patterns -- while Article 1's "
    "shared definitions and interpretive principles keep the whole set internally consistent. This is "
    "also precisely why a single real transaction commonly draws on more than one Article at once (see "
    "each ArticleOverview's connects_to_article/cross_article_connection_note below, and services/"
    "cross_article_lifecycle.py's real, working equipment-purchase-on-credit example spanning Article 2 "
    "and Article 9) -- the Articles are organized by subject matter, not by transaction, so a real "
    "transaction routinely has to be read across more than one of them."
)

SOURCES = [
    "https://www.uniformlaws.org/acts/ucc",
    "https://www.law.cornell.edu/ucc/1/1-103",
    "https://www.law.cornell.edu/ucc",
    "https://www.law.cornell.edu/ucc/9",
    "https://www.law.cornell.edu/ucc/3",
    "https://www.law.cornell.edu/ucc/6",
    "https://law.lis.virginia.gov/vacode/",
    "https://law.lis.virginia.gov/vacode/title8.1A/",
    "https://www.supremecourt.gov/opinions/19pdf/18-1150_7m58.pdf",
    "https://www.willkie.com/publications/2024/08/ucc-article-12-controllable-electronic-records",
    "law-engine/docs/ucc-source-licensing-audit.md (internal, this repository -- prior real research on "
    "state-enactment sourcing and 2022-amendment adoption status, reused rather than re-derived)",
    "law-engine/services/ingestion.py, law-engine/services/ingestion_article9.py, "
    "law-engine/services/cross_article_lifecycle.py (internal, this repository -- real ingested-coverage "
    "facts and the real cross-Article lifecycle pattern this module's connection notes describe)",
]


def build_ucc_orientation() -> UccOrientation:
    return UccOrientation(
        why_uniform_commercial_law_exists=WHY_UNIFORM_COMMERCIAL_LAW_EXISTS,
        what_uniform_means_in_practice=WHAT_UNIFORM_MEANS_IN_PRACTICE,
        is_the_ucc_itself_binding_law=IS_THE_UCC_ITSELF_BINDING_LAW,
        why_split_into_articles=WHY_SPLIT_INTO_ARTICLES,
        articles=build_all_article_overviews(),
        article_12_note=ARTICLE_12_NOTE,
        sources=SOURCES,
    )


if __name__ == "__main__":
    import json

    print(json.dumps(build_ucc_orientation().to_dict(), indent=2, ensure_ascii=False))

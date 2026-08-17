"""Law Engine -- Asset / Liability / Rights Intelligence (extends the
Asset Intelligence foundation in services/asset_intelligence.py).

Core principle this module exists to teach: a single obligation is a
liability to the party who owes it and, AT THE SAME TIME, in the SAME
instrument, an asset/right to the party it is owed to. A loan is a
liability to the borrower and a receivable/payment right to the lender.
A security interest is a burden on the debtor's collateral and a real,
valuable property right for the secured party. services/asset_intelligence.py
already answers "what do I own" for a type of asset; this module adds the
other half -- for one real instrument or relationship, what does EACH
side actually have, in the correct legal vocabulary for that side (obligor
vs. obligee generally; debtor vs. secured party in the UCC Article 9
sense; account debtor for a payment obligation on an account; assignor
vs. assignee on a transfer)? Loose phrasing like "equity in a liability"
is never correct and is never used here -- see
services/test_obligation_perspective.py's banned-phrase check.

Same trust-but-verify discipline as asset_intelligence.py,
contract_rights.py, and document_intelligence.py: a claim that traces to
a real ingested statutory section cites that real section (via
services/retrieval.get_section) and never invents one. Article 9 (secured
transactions) has 13 real sections ingested in this codebase as of this
module's creation (services/ingestion_article9.py) -- the security-
interest and account-receivable examples below cite real sections from
that set. Article 3 (negotiable instruments) and Article 2A (leases) have
NO ingested content at all -- the promissory-note and lease examples
below describe well-known, generally-accurate law without inventing a
citation, and say so explicitly via `grounding_note`.

This module does not edit asset_intelligence.py, contract_rights.py, or
document_intelligence.py -- it is a new, additive module that imports
DocumentFamily from document_intelligence.py read-only, to cross-reference
which real document family evidences each example instrument.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.document_intelligence import DocumentFamily
from services.retrieval import get_section

ARTICLE_3_NOT_YET_INGESTED_NOTE = (
    "Article 3 (negotiable instruments) is not yet ingested in this "
    "codebase. The characteristics below are well-known, generally-"
    "accurate legal concepts, not a claim traced to any specific ingested "
    "statutory section -- citation/section_id are left None."
)

ARTICLE_2A_NOT_INGESTED_NOTE = (
    "Article 2A (leases of goods) has no ingested content in this "
    "codebase at all -- unlike Article 9, not even a partial section set "
    "has been ingested for Article 2A. Every claim below is a well-known, "
    "generally-accurate Article 2A concept, not sourced from any real "
    "ingested statutory text. citation/section_id stay None."
)


class ObligationPerspectiveError(Exception):
    """Raised when a builder's real ingested section dependency is
    missing, or a caller asks for a role this instrument doesn't assign
    -- never silently substituted with invented statutory text or a
    fabricated role."""


class PerspectiveRole(str, Enum):
    """Which side of an obligation a given field/role assignment is
    describing. Deliberately includes both the general obligor/obligee
    vocabulary (works for any obligation) and the more specific UCC
    Article 9 vocabulary (debtor/secured party/account debtor) and
    transfer vocabulary (assignor/assignee) -- because using the general
    pair where a more precise term of art applies is exactly the kind of
    loose language this module exists to avoid."""

    OBLIGOR = "OBLIGOR"
    OBLIGEE = "OBLIGEE"
    DEBTOR = "DEBTOR"
    SECURED_PARTY = "SECURED_PARTY"
    ACCOUNT_DEBTOR = "ACCOUNT_DEBTOR"
    ASSIGNOR = "ASSIGNOR"
    ASSIGNEE = "ASSIGNEE"


@dataclass
class RoleAssignment:
    """Which real party, in this one concrete instrument, occupies a
    given PerspectiveRole -- and, where two roles describe the same
    party wearing two hats (e.g. the debtor on a secured loan is also
    the obligor on the underlying debt), the description says so
    explicitly rather than leaving the reader to infer it."""

    role: PerspectiveRole
    description: str

    def to_dict(self) -> dict:
        return {"role": self.role.value, "description": self.description}


@dataclass
class ObligationPerspective:
    """One real instrument or relationship, described from BOTH sides at
    once. `citation`/`section_id` are populated ONLY when a claim on this
    profile actually traces to a real ingested statutory section -- when
    it instead describes generally-accurate but not-yet-ingested law
    (Article 3 and Article 2A, as of this module's creation), they stay
    None and `grounding_note` says so explicitly -- an unpopulated
    citation is honest; an invented one is not.
    """

    instrument_id: str
    instrument_name: str
    role_assignments: list[RoleAssignment]
    what_the_obligor_owns_or_owes: str
    what_the_obligee_is_owed_or_owns: str
    the_right_the_obligee_has_against_the_obligor: str
    the_right_if_any_the_obligor_has_against_the_obligee: str
    evidencing_document: str
    is_transferable: bool
    transfer_notes: str
    is_secured: bool
    collateral_description: str | None
    priority_notes: str
    what_changes_on_assignment_or_transfer: str
    what_happens_on_default: str
    applicable_ucc_articles: list[str]
    citation: str | None = None
    section_id: str | None = None
    grounded_in_ingested_text: bool = False
    grounding_note: str = ""

    def role(self, role: PerspectiveRole) -> RoleAssignment:
        for assignment in self.role_assignments:
            if assignment.role == role:
                return assignment
        raise ObligationPerspectiveError(
            f"Instrument {self.instrument_id!r} does not assign role {role!r}."
        )

    def to_dict(self) -> dict:
        return {
            "instrument_id": self.instrument_id,
            "instrument_name": self.instrument_name,
            "role_assignments": [r.to_dict() for r in self.role_assignments],
            "what_the_obligor_owns_or_owes": self.what_the_obligor_owns_or_owes,
            "what_the_obligee_is_owed_or_owns": self.what_the_obligee_is_owed_or_owns,
            "the_right_the_obligee_has_against_the_obligor": self.the_right_the_obligee_has_against_the_obligor,
            "the_right_if_any_the_obligor_has_against_the_obligee": self.the_right_if_any_the_obligor_has_against_the_obligee,
            "evidencing_document": self.evidencing_document,
            "is_transferable": self.is_transferable,
            "transfer_notes": self.transfer_notes,
            "is_secured": self.is_secured,
            "collateral_description": self.collateral_description,
            "priority_notes": self.priority_notes,
            "what_changes_on_assignment_or_transfer": self.what_changes_on_assignment_or_transfer,
            "what_happens_on_default": self.what_happens_on_default,
            "applicable_ucc_articles": self.applicable_ucc_articles,
            "citation": self.citation,
            "section_id": self.section_id,
            "grounded_in_ingested_text": self.grounded_in_ingested_text,
            "grounding_note": self.grounding_note,
        }


def _require_section(section_id: str) -> dict:
    section = get_section(section_id)
    if section is None:
        raise ObligationPerspectiveError(
            f"No ingested section {section_id!r} -- cannot build an "
            "ObligationPerspective that cites it without a real source."
        )
    return section


# ---------------------------------------------------------------------------
# Example 1: Promissory note (unsecured) -- borrower is OBLIGOR, lender is
# OBLIGEE. NOT grounded: Article 3 (negotiable instruments) is not ingested.
# ---------------------------------------------------------------------------


def build_promissory_note_perspective() -> ObligationPerspective:
    """An unsecured promissory note: the simplest OBLIGOR/OBLIGEE pair,
    deliberately kept unsecured (no collateral) so it contrasts cleanly
    with the secured-transaction example below, where the same generic
    obligor/obligee pair is joined by the more specific debtor/secured-
    party roles."""
    return ObligationPerspective(
        instrument_id="promissory-note-unsecured-v1",
        instrument_name="Promissory note (unsecured)",
        role_assignments=[
            RoleAssignment(
                PerspectiveRole.OBLIGOR,
                "Borrower -- the maker of the note, who signed the unconditional promise to pay.",
            ),
            RoleAssignment(
                PerspectiveRole.OBLIGEE,
                "Lender -- the payee named in the note, who is owed repayment.",
            ),
        ],
        what_the_obligor_owns_or_owes=(
            "The borrower owes the unpaid principal balance plus any accrued "
            "interest the note specifies -- an unconditional promise to pay a "
            "fixed sum, not a conditional or contingent one. This is a "
            "liability on the borrower's own balance sheet."
        ),
        what_the_obligee_is_owed_or_owns=(
            "The lender owns the payment right the note evidences -- a real, "
            "affirmative asset (a receivable) on the lender's own balance "
            "sheet, not merely the absence of a debt. While lawfully holding "
            "the note, the lender can enforce that right directly against "
            "the borrower and can sell or pledge the note itself as its own "
            "separate asset."
        ),
        the_right_the_obligee_has_against_the_obligor=(
            "The right to demand and collect payment according to the "
            "note's terms, and, on default, to accelerate the balance (if "
            "the note has an acceleration clause) and sue the borrower for "
            "the full amount owed."
        ),
        the_right_if_any_the_obligor_has_against_the_obligee=(
            "The borrower has no payment right against the lender under the "
            "note itself -- only defenses (e.g. payment already made, fraud "
            "in the inducement, failure of consideration) that can be "
            "raised if sued. Those personal defenses can be cut off if the "
            "note is negotiated to a good-faith holder in due course, a "
            "materially stronger transfer right than an ordinary contract "
            "assignment carries."
        ),
        evidencing_document=DocumentFamily.PROMISSORY_NOTE.value,
        is_transferable=True,
        transfer_notes=(
            "Transferable by negotiation -- delivery of the note, plus "
            "indorsement if payable to a specific payee (order paper); "
            "delivery alone suffices if payable to bearer. A good-faith "
            "transferee who takes the note under negotiation's formal "
            "requirements can become a holder in due course, taking free of "
            "many of the borrower's personal defenses -- a materially "
            "stronger transfer mechanism than a plain contract assignment."
        ),
        is_secured=False,
        collateral_description=None,
        priority_notes=(
            "Unsecured -- the lender has no claim against specific "
            "collateral, only a general unsecured claim against the "
            "borrower's assets generally. In the borrower's bankruptcy or a "
            "race among creditors, this claim ranks behind any secured "
            "creditor's claim to specific collateral and pro rata with "
            "other unsecured creditors."
        ),
        what_changes_on_assignment_or_transfer=(
            "If the lender assigns the note (rather than negotiates it), "
            "the assignee steps into the lender's shoes as obligee but "
            "generally takes subject to the borrower's existing defenses -- "
            "unlike negotiation to a holder in due course. Either way, the "
            "borrower's underlying payment obligation to whoever now holds "
            "the note is unchanged in amount; only who may enforce it changes."
        ),
        what_happens_on_default=(
            "The lender may accelerate the balance (if the note allows it), "
            "demand full payment, and sue the borrower for the unpaid "
            "principal, accrued interest, and (if the note provides for it) "
            "collection costs and attorney's fees. Because this note is "
            "unsecured, the lender has no collateral to repossess -- only a "
            "money judgment to pursue and, if obtained, ordinary judgment-"
            "creditor collection remedies against the borrower's assets."
        ),
        applicable_ucc_articles=["Article 3 (negotiable instruments)"],
        citation=None,
        section_id=None,
        grounded_in_ingested_text=False,
        grounding_note=ARTICLE_3_NOT_YET_INGESTED_NOTE,
    )


# ---------------------------------------------------------------------------
# Example 2: UCC Article 9 security interest -- DEBTOR and SECURED PARTY,
# not just generic obligor/obligee. Grounded in the same real ingested
# Article 9 sections services/cross_article_lifecycle.py already uses for
# its equipment-purchase-on-credit fact pattern.
# ---------------------------------------------------------------------------


def build_security_interest_perspective() -> ObligationPerspective:
    """Reuses cross_article_lifecycle.py's real equipment-purchase-on-
    credit fact pattern (a business buys equipment on credit; the dealer
    takes a purchase-money security interest in the equipment itself) as
    the concrete instrument. This is the clearest real demonstration of
    the core principle: the SAME security interest is a burden on the
    debtor's equipment and a real, valuable, enforceable property right
    for the secured party -- not a metaphor, an actual Article 9 legal
    fact, grounded here in the same real ingested sections
    cross_article_lifecycle.py's later stages already cite."""
    attachment = _require_section("8.9A-203")
    pmsi_priority = _require_section("8.9A-324")
    repossession = _require_section("8.9A-609")
    disposition = _require_section("8.9A-610")
    debtor_obligor_rights = _require_section("8.9A-601")

    return ObligationPerspective(
        instrument_id="security-interest-equipment-pmsi-v1",
        instrument_name="UCC Article 9 security interest (purchase-money, equipment)",
        role_assignments=[
            RoleAssignment(
                PerspectiveRole.OBLIGOR,
                "The business, in its capacity as obligor on the underlying secured debt for the equipment's purchase price -- the same party as the debtor below.",
            ),
            RoleAssignment(
                PerspectiveRole.OBLIGEE,
                "The equipment dealer, in its capacity as obligee of that debt -- the same party as the secured party below.",
            ),
            RoleAssignment(
                PerspectiveRole.DEBTOR,
                "The business -- the party that granted the security interest in the equipment it purchased. 'Debtor' is Article 9's own term for whoever has an interest (other than a security interest) in the collateral, not necessarily the same person as the obligor on every occasion, though here they coincide.",
            ),
            RoleAssignment(
                PerspectiveRole.SECURED_PARTY,
                "The equipment dealer -- the party holding the purchase-money security interest in the equipment.",
            ),
        ],
        what_the_obligor_owns_or_owes=(
            "The business (debtor/obligor) owes the unpaid balance of the "
            "equipment's purchase price -- a liability. It also owns the "
            "equipment itself, but that ownership is now burdened: the "
            f'equipment is collateral, and under {attachment["citation"]} '
            "the secured party's interest is enforceable against the "
            "business once value has been given, the business has rights "
            "in the collateral, and an authenticated security agreement "
            "describes it -- all three of which are true here."
        ),
        what_the_obligee_is_owed_or_owns=(
            "The equipment dealer (secured party/obligee) is owed the "
            "unpaid purchase-money debt, and separately owns a real, "
            "enforceable security interest in the equipment -- a genuine "
            "property right in specific collateral, not merely a claim "
            "against the business generally. This is the same instrument's "
            "other side: the business's burden IS the dealer's asset."
        ),
        the_right_the_obligee_has_against_the_obligor=(
            f'Under {attachment["citation"]}, once the security interest '
            "has attached, the secured party's interest is enforceable "
            "against the debtor -- meaning the dealer can look to the "
            "equipment itself, not just the business generally, to satisfy "
            "the debt, and, on default, take possession of it "
            f'({repossession["citation"]}) and dispose of it in a '
            f'commercially reasonable manner ({disposition["citation"]}).'
        ),
        the_right_if_any_the_obligor_has_against_the_obligee=(
            f'{debtor_obligor_rights["citation"]}(d) confirms that, after '
            "default, \"a debtor and an obligor have the rights provided in "
            "this part and by agreement of the parties\" -- the business is "
            "not without recourse just because it defaulted. The specific "
            "content of those rights (e.g. redemption of the collateral "
            "before disposition, any surplus after a commercially "
            "reasonable sale) is well-known Article 9 law, but the specific "
            "sections spelling out redemption and surplus mechanics are not "
            "among the 13 Article 9 sections currently ingested in this "
            "codebase, so those specific mechanics are not cited by number "
            "here -- only the general existence of debtor/obligor rights "
            f'after default, which {debtor_obligor_rights["citation"]}(d) '
            "itself states."
        ),
        evidencing_document=DocumentFamily.SECURITY_AGREEMENT.value,
        is_transferable=True,
        transfer_notes=(
            "The secured party's rights under the security agreement (the "
            "debt and the security interest securing it) can generally be "
            "assigned to a third party without the debtor's consent for the "
            "assignment to be effective, though the debtor's payment "
            "obligation and the collateral itself are unaffected by who "
            "currently holds the secured party's position. The specific "
            "Article 9 provisions governing assignment of a secured "
            "obligation are not among the sections currently ingested in "
            "this codebase; this is a well-known, generally-accurate "
            "characteristic, not traced to a specific ingested citation."
        ),
        is_secured=True,
        collateral_description=(
            "The manufacturing equipment purchased with the secured "
            "party's financing (purchase-money collateral) -- the same "
            "equipment-purchase-on-credit fact pattern used in "
            "services/cross_article_lifecycle.py."
        ),
        priority_notes=(
            f'{pmsi_priority["citation"]}(a): a perfected purchase-money '
            "security interest in goods other than inventory or livestock "
            "has priority over a conflicting security interest in the same "
            "goods, even one that is earlier in time and broader in scope "
            "(e.g. an earlier-filed blanket lien covering \"all equipment, "
            "now owned or later acquired\") -- the equipment dealer's PMSI "
            "wins over such a lender's earlier claim to this specific "
            "equipment, provided the PMSI is properly perfected."
        ),
        what_changes_on_assignment_or_transfer=(
            "If the secured party sells or assigns its rights under the "
            "security agreement to a third-party lender, that assignee "
            "generally succeeds to the secured party's rights -- including "
            "the right to enforce against the debtor and the priority "
            "position the original secured party held -- but the debtor's "
            "underlying obligation (amount owed, collateral pledged) does "
            "not change merely because who holds the secured party's "
            "position changed."
        ),
        what_happens_on_default=(
            f'{repossession["citation"]}: after default, the secured party '
            "may take possession of the collateral (through self-help, if "
            "it can be done without breach of the peace, or through "
            f'judicial process). {disposition["citation"]}: the secured '
            "party may then sell, lease, license, or otherwise dispose of "
            "the collateral, but every aspect of the disposition -- "
            "method, manner, time, place, and terms -- must be commercially "
            f'reasonable. {debtor_obligor_rights["citation"]}(d) confirms '
            "the debtor/obligor retains statutory rights during this "
            "process, not just obligations."
        ),
        applicable_ucc_articles=["Article 9"],
        citation=attachment["citation"],
        section_id=attachment["section_id"],
        grounded_in_ingested_text=True,
        grounding_note=(
            f'Grounded in the real ingested text of {attachment["citation"]} '
            f'(attachment/enforceability), {pmsi_priority["citation"]} (PMSI '
            f'priority), {repossession["citation"]} (post-default '
            f'repossession), {disposition["citation"]} (disposition of '
            f'collateral), and {debtor_obligor_rights["citation"]}(d) '
            "(debtor/obligor rights after default) -- the same real Article "
            "9 sections services/cross_article_lifecycle.py's equipment-"
            "purchase-on-credit lifecycle already cites. The specific "
            "mechanics of assigning a secured party's position, and the "
            "specific content of the debtor's post-default rights beyond "
            "their bare existence, are well-known but not traced to any "
            "specific ingested citation, as noted inline above."
        ),
    )


# ---------------------------------------------------------------------------
# Example 3: Account receivable / account debtor relationship. Grounded in
# the real ingested defined-terms text of Va. Code Ann. Section 8.9A-102 --
# both "Account" (paragraph (2)) and "Account debtor" (paragraph (3)) are
# real, ingested statutory definitions, verified directly against the
# section's paragraph text rather than assumed from the section's
# defined_terms convenience index (which lists "Account debtor" but not
# "Account" as its own entry -- see grounding_note for why that index gap
# does not mean the definition itself is ungrounded).
# ---------------------------------------------------------------------------


def build_account_receivable_perspective() -> ObligationPerspective:
    """A business sells goods on credit and later factors (sells) the
    resulting account to a factoring company. Deliberately carries the
    ASSIGNOR/ASSIGNEE roles (the factoring sale) alongside ACCOUNT_DEBTOR
    (the customer who owes on the account) and the general OBLIGOR/OBLIGEE
    pair, cross-referencing document_intelligence.py's real, grounded
    INVOICE profile as the evidencing document."""
    definitions = _require_section("8.9A-102")

    account_definition_text = (
        '"Account," except as used in "account for," "account statement," '
        '"account to," "commodity account" in paragraph (14), "customer\'s '
        'account," "deposit account" in paragraph (29), "on account of," '
        'and "statement of account," means a right to payment of a '
        "monetary obligation, whether or not earned by performance, for "
        "property that has been or is to be sold, leased, licensed, "
        "assigned, or otherwise disposed of, or for services rendered or "
        "to be rendered, among other listed categories."
    )
    account_debtor_definition_text = (
        '"Account debtor" means a person obligated on an account, chattel '
        "paper, or general intangible."
    )
    if not any(p.startswith('(2) "Account,"') for p in definitions["paragraphs"]):
        raise ObligationPerspectiveError(
            f'{definitions["section_id"]}\'s ingested paragraph (2) no '
            'longer starts with the "Account" definition this profile '
            "quotes -- the grounding below would no longer trace to real "
            "ingested text."
        )
    if not any(p.startswith('(3) "Account debtor"') for p in definitions["paragraphs"]):
        raise ObligationPerspectiveError(
            f'{definitions["section_id"]}\'s ingested paragraph (3) no '
            'longer starts with the "Account debtor" definition this '
            "profile quotes -- the grounding below would no longer trace "
            "to real ingested text."
        )

    return ObligationPerspective(
        instrument_id="account-receivable-account-debtor-v1",
        instrument_name="Account receivable, later sold to a factor (account debtor relationship)",
        role_assignments=[
            RoleAssignment(
                PerspectiveRole.OBLIGOR,
                "The customer, in its general capacity as the party who owes payment for goods sold on credit -- the same party as the account debtor below.",
            ),
            RoleAssignment(
                PerspectiveRole.OBLIGEE,
                "The business (before any factoring sale) or the factoring company (after one) -- whichever party currently holds the right to collect the account.",
            ),
            RoleAssignment(
                PerspectiveRole.ACCOUNT_DEBTOR,
                f'The customer -- {definitions["citation"]}(3) defines "account debtor" as '
                '"a person obligated on an account, chattel paper, or general intangible."',
            ),
            RoleAssignment(
                PerspectiveRole.ASSIGNOR,
                "The business -- the original seller, who sells (assigns) the account to a factoring company for immediate cash.",
            ),
            RoleAssignment(
                PerspectiveRole.ASSIGNEE,
                "The factoring company -- the buyer of the account, who now holds the right to collect from the account debtor.",
            ),
        ],
        what_the_obligor_owns_or_owes=(
            "The customer (account debtor/obligor) owes the unpaid invoice "
            "amount for goods already sold or services already rendered -- "
            "an ordinary unsecured payment obligation, distinct from a "
            "security interest, unless one is separately granted."
        ),
        what_the_obligee_is_owed_or_owns=(
            f'The business (originally) owns the account itself -- {definitions["citation"]}'
            '(2)\'s "right to payment of a monetary obligation... for '
            'property that has been or is to be sold... or services '
            'rendered" -- a real, separately transferable asset distinct '
            "from the goods sold or the invoice document that records the "
            "sale. By selling that asset to a factor, the business converts "
            "it into immediate cash; the factor (now the obligee) owns the "
            "same payment right going forward."
        ),
        the_right_the_obligee_has_against_the_obligor=(
            "The right to demand and collect the invoiced amount from the "
            "account debtor. After the factoring sale, that right belongs "
            "to the assignee (the factor), who can generally enforce it "
            "directly against the account debtor once the account debtor "
            "has been notified of the assignment -- the specific Article 9 "
            "enforcement and notification mechanics beyond the bare "
            f'"account"/"account debtor" definitions in {definitions["citation"]} '
            "are well-known but not among the sections currently ingested "
            "in this codebase, so they are not cited by number here."
        ),
        the_right_if_any_the_obligor_has_against_the_obligee=(
            "The account debtor generally may assert against the assignee "
            "(the factor) the same defenses and claims it could have "
            "asserted against the assignor (the original business) arising "
            "from the underlying sale -- e.g. that the goods were "
            "nonconforming -- absent an enforceable agreement not to assert "
            "such defenses. This is a well-known Article 9 concept, not "
            "traced to a specific ingested citation."
        ),
        evidencing_document=DocumentFamily.INVOICE.value,
        is_transferable=True,
        transfer_notes=(
            "Freely transferable by sale or assignment (factoring is a "
            "routine commercial financing transaction built entirely on "
            "this assignability); notifying the account debtor of the "
            "assignment is not always legally required but is strongly "
            "advisable so payment is redirected to the assignee correctly."
        ),
        is_secured=False,
        collateral_description=None,
        priority_notes=(
            "Well-known Article 9 first-to-file-or-perfect priority "
            "concepts generally govern competing claims to the same "
            "account (e.g. if the business also used its accounts as loan "
            "collateral for a different lender); the specific priority "
            f'sections are not among the sections currently ingested here beyond {definitions["citation"]}\'s own definitions, so priority mechanics are not cited by number.'
        ),
        what_changes_on_assignment_or_transfer=(
            "Before the factoring sale, the business (assignor) is the "
            "obligee with the right to collect. After the sale, the "
            "factor (assignee) is the obligee instead -- the account "
            "debtor's underlying payment obligation is unchanged in amount, "
            "but who may lawfully collect it, and who bears the risk of "
            "the account debtor's nonpayment, both shift to the assignee."
        ),
        what_happens_on_default=(
            "If the account debtor fails to pay, the current obligee "
            "(the business, or the factor if the account was sold) can "
            "pursue ordinary collection remedies -- demand, then suit on "
            "the underlying sale contract. Because this account is not "
            "itself pledged as collateral for a loan in this example "
            "(is_secured=False), Article 9's default/repossession sections "
            "(which govern a secured party's remedies against collateral) "
            "do not apply to this specific relationship -- an unpaid, "
            "unsecured account is enforced through general commercial "
            "collection and contract remedies instead."
        ),
        applicable_ucc_articles=["Article 9"],
        citation=definitions["citation"],
        section_id=definitions["section_id"],
        grounded_in_ingested_text=True,
        grounding_note=(
            f'The "Account" and "Account debtor" role/asset definitions '
            f'above are grounded in the real ingested paragraph text of '
            f'{definitions["citation"]} -- specifically paragraph (2) '
            f'({account_definition_text[:60]}...) and paragraph (3) '
            f'({account_debtor_definition_text}). Note: the section\'s own '
            'defined_terms convenience index lists "Account debtor" as a '
            'separate entry but does NOT separately list "Account" itself '
            "(likely because its definition text begins with an \"except as "
            'used in ..." qualifier rather than a clean term line) -- this '
            "profile verified the \"Account\" definition directly against "
            "the section's real ingested paragraph (2) text rather than "
            "assuming it from the defined_terms index, per "
            "services/test_obligation_perspective.py's verification. "
            "Everything beyond the bare definitions (assignment mechanics, "
            "priority mechanics, collection remedies) is well-known but not "
            "traced to a specific ingested citation, as noted inline above."
        ),
    )


# ---------------------------------------------------------------------------
# Example 4: Lease obligation (UCC Article 2A). NOT grounded -- Article 2A
# has no ingested content in this codebase at all.
# ---------------------------------------------------------------------------


def build_lease_obligation_perspective() -> ObligationPerspective:
    """An equipment lease: lessee pays rent for use of goods the lessor
    continues to own. Deliberately illustrates that a TRUE lease is not a
    security interest at all -- the lessor never gave up title, so there
    is no separate lien/collateral layered on top the way there is in the
    security-interest example above; Article 1's economic-realities test
    can recharacterize a "lease" that functions like a financed sale as a
    disguised security interest instead, at which point it would stop
    being a true lease and Article 9 (not Article 2A) would govern it."""
    return ObligationPerspective(
        instrument_id="equipment-lease-obligation-v1",
        instrument_name="Equipment lease obligation (true lease)",
        role_assignments=[
            RoleAssignment(
                PerspectiveRole.OBLIGOR,
                "Lessee -- obligated to pay rent for use of the leased equipment. Article 2A's own vocabulary is 'lessee'/'lessor,' not part of this module's shared PerspectiveRole taxonomy; this profile maps the lessee onto the generic OBLIGOR role rather than inventing a LESSEE role.",
            ),
            RoleAssignment(
                PerspectiveRole.OBLIGEE,
                "Lessor -- owed the rent payments and retains ownership of the leased equipment throughout the lease term. Mapped onto the generic OBLIGEE role for the same reason noted above.",
            ),
        ],
        what_the_obligor_owns_or_owes=(
            "The lessee owes periodic rent payments for the lease term. "
            "The lessee owns only a leasehold/right-to-use interest in the "
            "equipment for that term -- not title, and not (in a true "
            "lease) any equity building toward ownership."
        ),
        what_the_obligee_is_owed_or_owns=(
            "The lessor is owed the rent stream and owns the leased "
            "equipment outright -- title never transferred, so there is no "
            "separate collateral interest to track the way there is in the "
            "security-interest example above: the lessor's ownership right "
            "already is the asset, not a lien layered on someone else's "
            "asset."
        ),
        the_right_the_obligee_has_against_the_obligor=(
            "The right to collect rent as it comes due, and, on the "
            "lessee's default, to terminate the lease, repossess the "
            "equipment (it already belongs to the lessor), and pursue "
            "damages for any unpaid rent and other losses caused by the "
            "default -- well-known, generally-accurate Article 2A "
            "characteristics, not sourced from ingested text."
        ),
        the_right_if_any_the_obligor_has_against_the_obligee=(
            "The lessee's right to quiet possession and use of the "
            "equipment for the lease term, and, if the lessor breaches "
            "(e.g. delivers non-conforming goods or wrongfully interferes "
            "with possession), remedies against the lessor -- or, in a "
            "finance lease, potentially limited warranty pass-through "
            "rights against the equipment's supplier instead of the "
            "lessor. Well-known, generally-accurate Article 2A concepts, "
            "not sourced from ingested text."
        ),
        evidencing_document=DocumentFamily.LEASE.value,
        is_transferable=True,
        transfer_notes=(
            "The lessor's reversionary ownership interest can generally be "
            "sold or assigned (subject to the existing lease); the "
            "lessee's leasehold interest is often restricted from "
            "assignment by the lease's own anti-assignment clause. "
            "Well-known, generally-accurate Article 2A concept, not "
            "sourced from ingested text."
        ),
        is_secured=False,
        collateral_description=None,
        priority_notes=(
            "A TRUE lease creates no security interest at all -- the "
            "lessor's ownership was never given up, so there is nothing "
            "to perfect or prioritize as collateral. If the economic "
            "substance of the arrangement instead functions as a financed "
            "sale (e.g. the lessee is obligated to pay the full value of "
            "the goods and can become the owner for little or no "
            "additional consideration), Article 1's recharacterization "
            "test can treat it as a disguised security interest instead, "
            "at which point Article 9 -- not Article 2A -- would actually "
            "govern it. This distinction is exactly why this profile "
            "keeps is_secured=False rather than treating a lease as "
            "automatically some form of secured transaction."
        ),
        what_changes_on_assignment_or_transfer=(
            "If the lessor sells the equipment subject to the existing "
            "lease, the buyer generally takes subject to the lessee's "
            "rights under the lease. If the lessee is permitted to assign "
            "its leasehold interest, the assignee steps into the lessee's "
            "shoes for remaining rent obligations, subject to the lease's "
            "own terms."
        ),
        what_happens_on_default=(
            "On the lessee's default, the lessor may terminate the lease, "
            "repossess the equipment, and recover damages (e.g. unpaid "
            "rent, the difference between the lease rate and a "
            "replacement lease's rate). On the lessor's default (e.g. "
            "failure to deliver conforming goods), the lessee may have "
            "rights to reject, revoke acceptance, or seek damages. "
            "Well-known, generally-accurate Article 2A concepts, not "
            "sourced from ingested text."
        ),
        applicable_ucc_articles=["Article 2A (leases)"],
        citation=None,
        section_id=None,
        grounded_in_ingested_text=False,
        grounding_note=ARTICLE_2A_NOT_INGESTED_NOTE,
    )


def build_all_perspectives() -> list[ObligationPerspective]:
    return [
        build_promissory_note_perspective(),
        build_security_interest_perspective(),
        build_account_receivable_perspective(),
        build_lease_obligation_perspective(),
    ]


if __name__ == "__main__":
    import json

    print(json.dumps([p.to_dict() for p in build_all_perspectives()], indent=2, ensure_ascii=False))

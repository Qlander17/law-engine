"""Law Engine -- first genuine Article 2 -> Article 9 cross-Article
transaction lifecycle (Live Run 1.39, Mission 15).

Reuses the exact LifecycleStage/LifecycleChoice/ChangedFactVariant/
TransactionLifecycle shapes from transaction_lifecycle.py (Article-2-only,
Live Run 1.38) rather than redefining them -- Objective Mode
(services/learning.py's LearningPathOrganization.OBJECTIVE) means a path
crosses whatever authority is actually relevant to the real task, and the
lifecycle SHAPE doesn't change just because the underlying sections now
span two Articles. What changes is which real sections a stage cites.

Scenario: equipment purchased on credit, secured by the equipment itself
(a purchase-money security interest) -- chosen over the vehicle-financing
alternative because Virginia's own real, ingested Article 9 text
(§ 8.9A-324(b)-(c)) draws a materially different PMSI-perfection rule for
INVENTORY specifically, while equipment falls under the simpler general
PMSI rule in § 8.9A-324(a) -- the cleaner, less special-cased
demonstration the directive asked for. Every stage traces to one of the
13 real ingested Article 9 sections (services/ingestion_article9.py) or
the pre-existing 11 real ingested Article 2 sections
(services/ingestion.py) -- no invented statutory content, matching
transaction_lifecycle.py's own established discipline.

The progression deliberately does NOT force every Article 9 doctrine into
this one story -- default/priority-dispute complexity belongs to
docs/ucc-scenario-matrix.md's separate "default/repossession/priority
dispute" scenario, not bolted onto a first-purchase narrative artificially.
"""

from __future__ import annotations

import sys
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.retrieval import get_section
from services.transaction_lifecycle import (
    ChangedFactVariant,
    LifecycleChoice,
    LifecycleStage,
    TransactionLifecycle,
    TransactionLifecycleError,
)


def _require_section(section_id: str) -> dict:
    section = get_section(section_id)
    if section is None:
        raise TransactionLifecycleError(
            f"No ingested section {section_id!r} -- cannot build a cross-Article lifecycle stage without a real source."
        )
    return section


def build_equipment_purchase_on_credit_lifecycle() -> TransactionLifecycle:
    """Real, evolving lifecycle: a business buys equipment on credit, the
    seller/lender takes a purchase-money security interest in the
    equipment itself. Stages 1-2 are Article 2 (the sale); stages 3-5
    cross into Article 9 (the financing) -- the genuine cross-Article
    demonstration Mission 15 asked for."""
    formation = _require_section("8.2-204")
    merchant = _require_section("8.2-104")
    security_agreement = _require_section("8.9A-201")
    attachment = _require_section("8.9A-203")
    perfection = _require_section("8.9A-308")
    filing = _require_section("8.9A-310")
    pmsi_priority = _require_section("8.9A-324")
    repossession = _require_section("8.9A-609")
    disposition = _require_section("8.9A-610")

    stage_1 = LifecycleStage(
        stage_id="equipment-purchase-formation",
        title="A business buys equipment -- on credit",
        facts=(
            "A small manufacturing business agrees to buy a $40,000 piece of "
            "production equipment from an equipment dealer. The business can't "
            "pay cash up front, so the dealer agrees to finance the purchase "
            "itself, taking a security interest in the equipment as collateral "
            "for the unpaid price."
        ),
        question="Is there a binding contract for the equipment sale, even though payment is deferred?",
        choices=[
            LifecycleChoice(
                label="Yes -- deferred payment doesn't defeat contract formation; the parties' agreement and conduct establish it",
                is_correct=True,
                outcome=f'{formation["citation"]} allows a contract to be shown by conduct and doesn\'t require full payment up front -- a financed sale is still a real contract for the sale of goods under Article 2, same as a cash sale.',
                section_id="8.2-204", citation=formation["citation"],
            ),
            LifecycleChoice(
                label="No -- since payment is deferred, this isn't really an Article 2 sale until the balance is paid off",
                is_correct=False,
                outcome=f'{formation["citation"]} draws no such distinction -- the sale-of-goods contract forms at agreement, independent of when/how payment happens. The financing arrangement is a separate, additional layer (Article 9), not a reason the sale itself isn\'t real yet.',
                section_id="8.2-204", citation=formation["citation"],
            ),
        ],
        explanation=f'{formation["citation"]}: a contract for sale of goods may be made in any manner sufficient to show agreement; deferred/financed payment doesn\'t change that.',
        section_id="8.2-204", citation=formation["citation"],
        changed_fact_variants=[
            ChangedFactVariant(
                changed_fact="What if the equipment dealer is not in the business of dealing in this kind of equipment -- just a one-off private seller?",
                effect=f'Merchant status under {merchant["citation"]} affects which warranty/battle-of-forms rules apply later, but not whether a contract exists here -- formation under {formation["citation"]} doesn\'t depend on merchant status.',
                section_id="8.2-104", citation=merchant["citation"],
            ),
        ],
    )

    stage_2 = LifecycleStage(
        stage_id="security-agreement-effectiveness",
        title="The financing becomes its own agreement -- crossing into Article 9",
        facts=(
            "Alongside the sale, the business and the dealer sign a security "
            "agreement: the business grants the dealer a security interest in "
            "the equipment until the price is paid in full."
        ),
        question="Is that security agreement effective on its own terms, separate from the underlying sale contract?",
        choices=[
            LifecycleChoice(
                label="Yes -- a security agreement is effective according to its own terms, between the parties and against third parties, subject to the UCC's own rules",
                is_correct=True,
                outcome=f'{security_agreement["citation"]} says exactly this: a security agreement is effective according to its terms between the parties, against purchasers of the collateral, and against creditors, except as otherwise provided in the UCC.',
                section_id="8.9A-201", citation=security_agreement["citation"],
            ),
            LifecycleChoice(
                label="No -- a security interest isn't real until the equipment dealer files paperwork with the state",
                is_correct=False,
                outcome=f'That confuses effectiveness ({security_agreement["citation"]}) with perfection (a separate, later question -- see the next stage). The security agreement is already effective between the parties before any filing happens.',
                section_id="8.9A-201", citation=security_agreement["citation"],
            ),
        ],
        explanation=f'{security_agreement["citation"]}: a security agreement is effective according to its terms between the parties, against purchasers of the collateral, and against creditors.',
        section_id="8.9A-201", citation=security_agreement["citation"],
    )

    stage_3 = LifecycleStage(
        stage_id="attachment",
        title="Does the security interest actually attach to the equipment?",
        facts=(
            "The business has signed the security agreement, has already taken "
            "possession of the equipment, and the dealer has given value (the "
            "financed purchase price)."
        ),
        question="Has the security interest attached to the equipment?",
        choices=[
            LifecycleChoice(
                label="Yes -- value has been given, the debtor has rights in the collateral, and (via the signed agreement) it's enforceable",
                is_correct=True,
                outcome=f'{attachment["citation"]} requires value given, the debtor having rights in the collateral, and an enforceable agreement (here, the signed security agreement) -- all three are satisfied, so the interest attaches.',
                section_id="8.9A-203", citation=attachment["citation"],
            ),
            LifecycleChoice(
                label="No -- attachment requires the financing statement to be filed first",
                is_correct=False,
                outcome=f'{attachment["citation"]}\'s attachment requirements (value, rights in collateral, enforceable agreement) say nothing about filing -- filing is a perfection concept (next stage), not an attachment requirement.',
                section_id="8.9A-203", citation=attachment["citation"],
            ),
        ],
        explanation=f'{attachment["citation"]}: a security interest is enforceable against the debtor and third parties only if value has been given, the debtor has rights in the collateral, and (among other paths) an authenticated security agreement describes the collateral.',
        section_id="8.9A-203", citation=attachment["citation"],
    )

    stage_4 = LifecycleStage(
        stage_id="perfection-and-filing",
        title="Attachment isn't enough on its own -- what about other creditors?",
        facts=(
            "The equipment dealer wants its interest to be effective not just "
            "against the business, but against the business's other creditors "
            "and a later buyer of the equipment."
        ),
        question="What must the dealer do to perfect its security interest in the equipment?",
        choices=[
            LifecycleChoice(
                label="File a financing statement -- the general rule for perfecting a security interest in equipment",
                is_correct=True,
                outcome=f'{filing["citation"]} states the general rule: a financing statement must be filed to perfect a security interest, unless a specific exception applies (none of which fit ordinary equipment). {perfection["citation"]} confirms perfection requires both attachment AND satisfying the applicable perfection requirement -- filing, here.',
                section_id="8.9A-310", citation=filing["citation"],
            ),
            LifecycleChoice(
                label="Nothing further -- attachment alone already protects the dealer against everyone",
                is_correct=False,
                outcome=f'{perfection["citation"]} draws attachment and perfection as separate requirements -- an attached-but-unperfected security interest is vulnerable to competing claims that a perfected one would beat. Filing (or another perfection method) is a real, separate step.',
                section_id="8.9A-308", citation=perfection["citation"],
            ),
        ],
        explanation=f'{perfection["citation"]}: a security interest is perfected if it has attached and all applicable perfection requirements are satisfied. {filing["citation"]}: a financing statement must be filed to perfect, absent an exception.',
        section_id="8.9A-310", citation=filing["citation"],
    )

    stage_5 = LifecycleStage(
        stage_id="pmsi-priority",
        title="Why does it matter that this loan paid for the equipment itself?",
        facts=(
            "The business already has a different lender with a broader, "
            "earlier-filed security interest covering \"all equipment, now "
            "owned or later acquired.\" The equipment dealer's interest was "
            "created and perfected later, but specifically financed this "
            "particular piece of equipment."
        ),
        question="Does the earlier, broader lender automatically outrank the equipment dealer's later interest?",
        choices=[
            LifecycleChoice(
                label="No -- a perfected purchase-money security interest in equipment has priority over a conflicting security interest in the same goods, even one that's earlier and broader",
                is_correct=True,
                outcome=f'{pmsi_priority["citation"]}(a): a perfected purchase-money security interest in goods other than inventory or livestock has priority over a conflicting security interest in the same goods -- the equipment dealer\'s PMSI wins over the earlier blanket lien on this specific equipment.',
                section_id="8.9A-324", citation=pmsi_priority["citation"],
            ),
            LifecycleChoice(
                label="Yes -- first to file or perfect always wins, no exceptions",
                is_correct=False,
                outcome=f'{pmsi_priority["citation"]} is itself the real, statutory exception to first-in-time priority for purchase-money interests -- "always" is exactly what this section refutes for goods like equipment.',
                section_id="8.9A-324", citation=pmsi_priority["citation"],
            ),
        ],
        explanation=f'{pmsi_priority["citation"]}(a): a perfected purchase-money security interest in goods other than inventory or livestock has priority over a conflicting security interest in the same goods.',
        section_id="8.9A-324", citation=pmsi_priority["citation"],
        changed_fact_variants=[
            ChangedFactVariant(
                changed_fact="What if the collateral were inventory instead of equipment?",
                effect=(
                    f'{pmsi_priority["citation"]}(b) imposes extra requirements for inventory PMSI priority -- perfection before the debtor receives possession, AND a signed notification sent to the holder of the conflicting interest -- a materially stricter path than the general equipment rule in subsection (a).'
                ),
                section_id="8.9A-324", citation=pmsi_priority["citation"],
            ),
        ],
    )

    stage_6 = LifecycleStage(
        stage_id="default-and-disposition",
        title="The business defaults -- what can the equipment dealer do?",
        facts="The business falls behind on payments and is now in default under the security agreement.",
        question="What can the equipment dealer (secured party) do about the equipment?",
        choices=[
            LifecycleChoice(
                label="Take possession of the equipment and dispose of it in a commercially reasonable manner",
                is_correct=True,
                outcome=f'{repossession["citation"]}: after default, a secured party may take possession of the collateral. {disposition["citation"]}: the secured party may then sell, lease, license, or otherwise dispose of it, but every aspect of the disposition must be commercially reasonable.',
                section_id="8.9A-609", citation=repossession["citation"],
            ),
            LifecycleChoice(
                label="Nothing without a court order -- self-help repossession is never allowed",
                is_correct=False,
                outcome=f'{repossession["citation"]} contemplates both judicial and nonjudicial process -- self-help repossession is a real, recognized path under Article 9 (subject to real breach-of-peace limits not modeled in this ingested subset), not categorically unavailable.',
                section_id="8.9A-609", citation=repossession["citation"],
            ),
        ],
        explanation=f'{repossession["citation"]}: after default, a secured party may take possession of the collateral. {disposition["citation"]}: disposition must be commercially reasonable in method, manner, time, and place.',
        section_id="8.9A-610", citation=disposition["citation"],
    )

    return TransactionLifecycle(
        lifecycle_id="equipment-purchase-on-credit-v1",
        title="Equipment purchase on credit: Article 2 sale -> Article 9 financing",
        stages=[stage_1, stage_2, stage_3, stage_4, stage_5, stage_6],
    )

"""Law Engine -- Mini-Simulations (Live Run 1.49).

The real, Chairman-corrected implementation of Task-First pedagogy:
situation-first, action-oriented, multi-step, with facts accumulating
across steps as one continuous problem rather than independent quiz
questions. Extends the EXISTING Task/TaskOption architecture from
services/tasks.py -- a Simulation is an ordered chain of Tasks (using the
prerequisite_task_id/next_task_id fields that already exist), not a new
parallel schema. See docs/task-first-pedagogy-and-task-ladder-
architecture.md's "Correction, Live Run 1.49" section for the full
rationale.

Real, deliberate design choice: this simulation reuses the SAME
competency (recognize + respond to nonconforming goods, § 8.2-601) as
Live Run 1.48's Task 3 -- against a genuinely different variant
(restaurant equipment under time pressure, not phone cases). That is
exactly what the corrected pedagogy calls "repetition": the same
professional skill, a different real fact pattern -- not a flaw, the
point.
"""

from __future__ import annotations

import sys
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.tasks import Task, TaskOption


def build_riverside_bistro_simulation() -> list[Task]:
    """A real, bounded, 3-step simulation. No step opens with "which
    Article applies" -- every step is a real business decision under
    real, accumulating facts. Doctrine (§ 8.2-601, § 8.2-207, § 8.2-314)
    is introduced only in the feedback/reasoning after the learner has
    already acted, per the corrected DO-first cycle."""

    step_1 = Task(
        task_id="sim-bistro-1-delivery",
        scenario=(
            "You own Riverside Bistro, opening in four days. You emailed an order for six commercial "
            "ovens to a restaurant-supply company; they shipped the ovens along with an invoice, and "
            "neither side ever signed a combined contract. The ovens just arrived: two are visibly "
            "dented, one is the wrong model entirely, and three are exactly what you ordered. You're "
            "standing in your kitchen looking at the shipment right now."
        ),
        learner_role="small-business owner (restaurant)",
        objective="Decide what to do with this shipment right now.",
        facts_provided=[
            "6 ovens ordered; 2 arrived dented, 1 is the wrong model, 3 are correct.",
            "You open in 4 days.",
            "No single signed contract document exists -- only your order email and their invoice.",
        ],
        documents_provided=["Your original order email", "The supplier's invoice"],
        options=[
            TaskOption(
                option_id="accept-all-no-recourse",
                label="Accept all six ovens as-is -- a deal is a deal, and you don't want to jeopardize your relationship with the supplier before opening.",
                is_correct=False,
                consequence="You now own 3 damaged/wrong ovens outright, with a much weaker position to do anything about them later.",
                plain_language_feedback=(
                    "You don't have to accept nonconforming goods just because a deal exists. Keeping the "
                    "relationship smooth doesn't require giving up a real right you already have."
                ),
            ),
            TaskOption(
                option_id="accept-conforming-reject-rest",
                label="Accept the 3 correct ovens; reject the 2 dented ones and the wrong-model one.",
                is_correct=True,
                consequence=(
                    "You keep the 3 usable ovens for opening day and formally reject the other 3 -- "
                    "the supplier now has to deal with the rejected units, not you."
                ),
                plain_language_feedback=(
                    "You're allowed to split a shipment exactly this way: keep what conforms, reject what "
                    "doesn't, rather than an all-or-nothing choice."
                ),
            ),
            TaskOption(
                option_id="reject-everything",
                label="Reject the entire shipment, including the 3 correct ovens, since the order clearly wasn't handled properly.",
                is_correct=False,
                consequence="You lose the 3 good ovens too, four days before opening, when you didn't need to.",
                plain_language_feedback=(
                    "Rejecting everything is a real, available option -- but it's not required, and here it "
                    "costs you 3 perfectly good ovens you actually need for Friday."
                ),
            ),
            TaskOption(
                option_id="say-nothing-keep-using",
                label="Say nothing to the supplier and just start using whichever ovens work, dealing with it later if it becomes a problem.",
                is_correct=False,
                consequence="Using the goods without ever formally accepting or rejecting them can itself count as acceptance -- of all of them, including the damaged and wrong-model units.",
                plain_language_feedback=(
                    "This is the real, common mistake: continuing to use nonconforming goods without ever "
                    "formally accepting or rejecting them can forfeit your cleaner options."
                ),
            ),
        ],
        governing_sections=["8.2-601"],
        professional_terminology={
            "reject": "A buyer's formal refusal to accept goods that fail to conform to the contract.",
            "commercial unit": "A unit of goods commercial usage treats as a single whole for sale/division purposes.",
        },
        reasoning_chain=[
            "§ 8.2-601: if goods or tender of delivery fail in any respect to conform, the buyer may reject the whole, accept the whole, or accept any commercial unit(s) and reject the rest.",
            "2 dented ovens + 1 wrong-model oven are each their own commercial unit(s), separable from the 3 conforming ovens.",
            "Accepting the 3 conforming ovens and rejecting the other 3 uses the statute's own named middle option.",
        ],
        common_mistakes=[
            "Treating this as a forced all-or-nothing choice.",
            "Continuing to use nonconforming goods without ever formally accepting or rejecting them.",
        ],
        difficulty=2,
        next_task_id="sim-bistro-2-invoice-terms",
        prerequisite_task_id=None,
        business_or_personal_context="Riverside Bistro, opening in 4 days.",
        time_pressure="Opening night is in 4 days.",
        parties_involved=["Riverside Bistro (you)", "the restaurant-supply company"],
        competency_id="recognize-and-respond-to-nonconforming-goods",
    )

    step_2 = Task(
        task_id="sim-bistro-2-invoice-terms",
        scenario=(
            "After sorting out the ovens, you notice the supplier's invoice includes a line your "
            "original order email never mentioned: \"All sales final. No warranty, express or implied.\" "
            "You and the supplier are both in the restaurant-equipment business regularly."
        ),
        learner_role="small-business owner (restaurant)",
        objective="Decide whether that \"no warranty, all sales final\" language is actually part of your deal.",
        facts_provided=[
            "The 'no warranty, all sales final' term never appeared in your original order email.",
            "Both you and the supplier deal in restaurant equipment as a regular part of your business.",
            "You already resolved the delivery itself in the previous step.",
        ],
        options=[
            TaskOption(
                option_id="automatically-binding",
                label="Yes -- once you accept any part of the shipment, whatever the invoice says automatically becomes binding.",
                is_correct=False,
                consequence="You'd give up real leverage you actually have over a term you never agreed to.",
                plain_language_feedback="Accepting goods doesn't automatically mean accepting every term a later document adds.",
            ),
            TaskOption(
                option_id="never-binding",
                label="No -- since it wasn't in your original order, it can never become part of the deal no matter what.",
                is_correct=False,
                consequence="You'd overstate your position and be caught off guard if a court or the supplier disagrees.",
                plain_language_feedback=(
                    "Between two businesses that both regularly deal in this kind of goods, an additional term "
                    "in a confirmation CAN become part of the deal -- it's not automatically excluded either."
                ),
            ),
            TaskOption(
                option_id="depends-materially-alters",
                label="It depends -- since you're both merchants, this term could become part of the deal unless you object, but a total warranty disclaimer likely counts as a \"material alteration\" you're not stuck with by default.",
                is_correct=True,
                consequence="You have a real, grounded basis to push back on this specific term rather than accepting or panicking.",
                plain_language_feedback=(
                    "Between merchants, additional terms in a confirmation become part of the deal unless the "
                    "offer limited acceptance to its own terms, the new term materially alters the deal, or you "
                    "object -- and eliminating all warranty protection is exactly the kind of term courts "
                    "typically treat as a material alteration."
                ),
            ),
            TaskOption(
                option_id="irrelevant-after-rejection",
                label="It doesn't matter either way, since you already rejected part of the shipment in the last step.",
                is_correct=False,
                consequence="You'd wrongly treat two separate legal questions as if resolving one resolved the other.",
                plain_language_feedback=(
                    "Rejecting the nonconforming ovens and evaluating the invoice's warranty language are two "
                    "separate issues -- resolving one doesn't resolve the other."
                ),
            ),
        ],
        governing_sections=["8.2-207", "8.2-104"],
        professional_terminology={
            "material alteration": "A proposed additional term significant enough that it does not automatically become part of the deal just because no one objected.",
            "between merchants": "A transaction where both parties are chargeable with the knowledge/skill of merchants -- a real, specific legal status, not just \"two businesses.\"",
        },
        reasoning_chain=[
            "§ 8.2-104(3): 'between merchants' applies when both parties are chargeable with merchant-level knowledge/skill -- true here.",
            "§ 8.2-207(2): between merchants, additional terms become part of the contract unless the offer limited acceptance to its own terms, the term materially alters the deal, or a timely objection is made.",
            "A blanket 'no warranty, all sales final' term eliminates protections the buyer would otherwise have -- the kind of term that materially alters the deal.",
            "-> the disclaimer is not automatically part of the deal just because it appeared on the invoice.",
        ],
        common_mistakes=[
            "Assuming any term on an invoice automatically binds the buyer.",
            "Assuming a term not in the original offer can never become binding between merchants.",
        ],
        difficulty=3,
        next_task_id="sim-bistro-3-warranty-claim",
        prerequisite_task_id="sim-bistro-1-delivery",
        business_or_personal_context="Riverside Bistro, opening in 4 days.",
        parties_involved=["Riverside Bistro (you)", "the restaurant-supply company"],
        competency_id="evaluate-conflicting-additional-terms",
    )

    step_3 = Task(
        task_id="sim-bistro-3-warranty-claim",
        scenario=(
            "One week after opening, one of the three ovens you accepted develops a cracked heating "
            "element and stops heating food evenly -- it's now unusable for dinner service. You call the "
            "supplier. They point to the invoice's \"no warranty, all sales final\" language and refuse to help."
        ),
        learner_role="small-business owner (restaurant), transfer",
        objective="Decide your real position, using what you already worked out about the invoice terms.",
        facts_provided=[
            "The oven is one of the 3 you accepted, not one you rejected.",
            "It failed within a week of opening, during ordinary use.",
            "The supplier is relying on the same disclaimer language from the previous step.",
        ],
        hidden_or_irrelevant_facts=[
            "Whether the oven's failure was dramatic or gradual is not what determines your legal position here.",
        ],
        options=[
            TaskOption(
                option_id="supplier-is-right",
                label="The supplier is right -- the invoice disclaimed all warranties, so you have no claim.",
                is_correct=False,
                consequence="You'd give up a real claim based on a term you already had good reason to doubt was ever binding.",
                plain_language_feedback="This treats the disclaimer as settled and binding, which the previous step's analysis doesn't support.",
            ),
            TaskOption(
                option_id="likely-still-have-implied-warranty",
                label="Because the disclaimer likely never validly became part of the deal, and a merchant seller of ovens implicitly promises they're fit for ordinary use, you likely still have a real claim.",
                is_correct=True,
                consequence="You have real, grounded leverage to push back on the supplier's refusal instead of just accepting it.",
                plain_language_feedback=(
                    "A merchant seller of goods like these implicitly promises they're fit for their ordinary "
                    "use, unless that promise was validly excluded -- and the previous step's analysis is exactly "
                    "why this disclaimer is doubtful."
                ),
            ),
            TaskOption(
                option_id="too-late-already-accepted",
                label="You have no claim because you already accepted this oven -- you can't raise anything after acceptance.",
                is_correct=False,
                consequence="You'd wrongly assume acceptance of goods forecloses every later claim about a hidden defect.",
                plain_language_feedback="Accepting goods at delivery doesn't waive every later claim about a defect that wasn't apparent at the time.",
            ),
            TaskOption(
                option_id="unrelated-to-earlier-steps",
                label="This is a completely separate issue with no connection to the invoice-terms question from before.",
                is_correct=False,
                consequence="You'd miss the real, direct connection between the two issues and argue from a weaker position.",
                plain_language_feedback="This is the same disclaimer from the previous step, now actually being invoked -- the two issues are directly connected, not separate.",
            ),
        ],
        governing_sections=["8.2-314", "8.2-207"],
        professional_terminology={
            "implied warranty of merchantability": "A promise, implied by law when the seller is a merchant, that goods are fit for their ordinary purpose -- unless validly excluded.",
        },
        reasoning_chain=[
            "§ 8.2-314(1): unless excluded or modified, a warranty of merchantability is implied when the seller is a merchant with respect to goods of that kind.",
            "The restaurant-supply company, regularly dealing in commercial ovens, is a merchant with respect to ovens.",
            "The previous step already found the 'no warranty' disclaimer doubtful as a material alteration under § 8.2-207 -- it likely never validly excluded this implied warranty.",
            "-> the implied warranty of merchantability likely still applies, and a cracked heating element that stops the oven heating evenly is a real basis for a claim under it.",
        ],
        common_mistakes=[
            "Treating a disclaimer as automatically effective without checking whether it validly became part of the deal.",
            "Assuming acceptance forecloses every later claim.",
        ],
        difficulty=4,
        next_task_id=None,
        prerequisite_task_id="sim-bistro-2-invoice-terms",
        business_or_personal_context="Riverside Bistro, one week after opening.",
        parties_involved=["Riverside Bistro (you)", "the restaurant-supply company"],
        competency_id="evaluate-warranty-claim-against-a-disputed-disclaimer",
    )

    steps = [step_1, step_2, step_3]
    for step in steps:
        step.validate()
    return steps

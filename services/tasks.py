"""Law Engine -- Task Ladder, first real implementation (Live Run 1.48).

Live Run 1.47B designed the Task-First pedagogy and Task Ladder schema
(docs/task-first-pedagogy-and-task-ladder-architecture.md) but deliberately
did not implement it. This is that implementation -- the smallest real,
learner-facing vertical slice, not another design document.

Same anti-fabrication discipline as learning.py: every Task's
`governing_sections` must resolve to a real, currently-ingested
StatuteSection (via services.retrieval.get_section) -- a Task citing a
section that doesn't exist fails at build time, not silently at render
time. Wrong-answer distractors don't carry their own citation (same
convention learning.py's MultipleChoiceQuestion already uses) -- only the
real, correct answer is required to trace to real ingested text.
"""

from __future__ import annotations

import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.retrieval import get_section


class TaskError(Exception):
    """Raised for a real, structural Task problem -- most importantly, a
    governing_sections entry that doesn't resolve to a real ingested
    section. Never silently dropped or substituted."""


@dataclass
class TaskOption:
    """One selectable action/answer. `is_correct` decides the branch of
    feedback the learner sees; only the correct option's reasoning needs
    to cite real authority -- a wrong option is a plausible distractor,
    not a claim about the law."""

    option_id: str
    label: str
    is_correct: bool
    consequence: str  # what happens in the fact pattern if chosen -- cycle step 2 (OBSERVE)
    plain_language_feedback: str  # cycle step 3 (EXPLAIN IN PLAIN LANGUAGE)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Task:
    task_id: str
    scenario: str
    learner_role: str
    objective: str
    facts_provided: list[str]
    options: list[TaskOption]
    governing_sections: list[str]
    professional_terminology: dict[str, str] = field(default_factory=dict)  # term -> plain-language gloss
    reasoning_chain: list[str] = field(default_factory=list)  # step-by-step, cites governing_sections
    common_mistakes: list[str] = field(default_factory=list)
    documents_provided: list[str] = field(default_factory=list)
    hidden_or_irrelevant_facts: list[str] = field(default_factory=list)
    difficulty: int = 1
    next_task_id: str | None = None
    prerequisite_task_id: str | None = None

    # Live Run 1.49 -- simulation fields, extending Task rather than a
    # second parallel schema (see docs/task-first-pedagogy-and-task-
    # ladder-architecture.md's "Simulation fields" section). All
    # optional: a plain Task leaves these at their defaults; a real
    # multi-step simulation (services/simulations.py) populates the ones
    # that apply.
    business_or_personal_context: str = ""
    time_pressure: str = ""
    financial_stakes: str = ""
    documents_not_yet_obtained: list[str] = field(default_factory=list)
    parties_involved: list[str] = field(default_factory=list)
    discoverable_actions: list[str] = field(default_factory=list)
    business_effect: str = ""
    legal_effect: str = ""
    evidence_created_preserved_or_lost: str = ""
    rights_created_waived_or_preserved: str = ""
    deadlines: list[str] = field(default_factory=list)
    escalation_point: str = ""
    competency_id: str = ""
    next_variant_ids: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.options:
            raise TaskError(f"Task {self.task_id!r} has no options.")
        if sum(1 for o in self.options if o.is_correct) != 1:
            raise TaskError(f"Task {self.task_id!r} must have exactly one correct option.")
        if not self.governing_sections:
            raise TaskError(f"Task {self.task_id!r} has no governing_sections -- every Task must cite real authority.")
        for section_id in self.governing_sections:
            if get_section(section_id) is None:
                raise TaskError(
                    f"Task {self.task_id!r} cites {section_id!r}, which is not a real, currently-ingested "
                    "section -- refusing to build a Task against invented or not-yet-ingested authority."
                )

    def governing_citations(self) -> list[str]:
        return [get_section(sid)["citation"] for sid in self.governing_sections]

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id, "scenario": self.scenario, "learner_role": self.learner_role,
            "objective": self.objective, "facts_provided": self.facts_provided,
            "options": [o.to_dict() for o in self.options],
            "governing_sections": self.governing_sections, "governing_citations": self.governing_citations(),
            "professional_terminology": self.professional_terminology,
            "reasoning_chain": self.reasoning_chain, "common_mistakes": self.common_mistakes,
            "documents_provided": self.documents_provided,
            "hidden_or_irrelevant_facts": self.hidden_or_irrelevant_facts,
            "difficulty": self.difficulty, "next_task_id": self.next_task_id,
            "prerequisite_task_id": self.prerequisite_task_id,
            "business_or_personal_context": self.business_or_personal_context,
            "time_pressure": self.time_pressure, "financial_stakes": self.financial_stakes,
            "documents_not_yet_obtained": self.documents_not_yet_obtained,
            "parties_involved": self.parties_involved,
            "discoverable_actions": self.discoverable_actions,
            "business_effect": self.business_effect, "legal_effect": self.legal_effect,
            "evidence_created_preserved_or_lost": self.evidence_created_preserved_or_lost,
            "rights_created_waived_or_preserved": self.rights_created_waived_or_preserved,
            "deadlines": self.deadlines, "escalation_point": self.escalation_point,
            "competency_id": self.competency_id, "next_variant_ids": self.next_variant_ids,
        }


def build_article_2_consumer_to_operator_ladder() -> list[Task]:
    """The real, first Task Ladder slice: 4 linked tasks, ordinary consumer
    through operations/procurement, then a transfer task -- grounded only
    in the real, currently-ingested Article 2 sections (8.2-102 through
    8.2-711). Task 3 uses exactly the 3 real options § 8.2-601 itself
    enumerates (reject the whole / accept the whole / accept some and
    reject the rest) plus one real, common, plausible-but-wrong distractor
    (silently keep using nonconforming goods without ever accepting or
    rejecting) -- not a manufactured fourth option for its own sake, per
    the Chairman's explicit instruction not to pad to four artificially."""

    task_1 = Task(
        task_id="a2-t1-buy-a-laptop",
        scenario=(
            "You walk into an electronics store and buy a laptop for personal use, paying cash "
            "and taking it home the same day."
        ),
        learner_role="ordinary consumer",
        objective="Identify whether UCC Article 2 applies to this purchase, and why.",
        facts_provided=[
            "You paid money for a laptop.",
            "The laptop is a physical, movable object.",
            "You are buying it for personal use, not resale.",
        ],
        options=[
            TaskOption(
                option_id="applies-goods", label="Yes -- Article 2 applies because a laptop is \"goods.\"",
                is_correct=True,
                consequence="You're right to check this first -- everything else in this transaction depends on it.",
                plain_language_feedback=(
                    "A laptop is a real, physical, movable thing you can pick up and carry -- exactly what "
                    "the statute means by \"goods.\" Article 2 governs sales of goods, so it applies here."
                ),
            ),
            TaskOption(
                option_id="doesnt-apply-service", label="No -- buying something in a store is a service, not a sale of goods.",
                is_correct=False,
                consequence="You walk away without checking your real rights if the laptop turns out to be defective.",
                plain_language_feedback=(
                    "Handing over cash for a physical item is the textbook example of a sale of goods, not a "
                    "service -- there's no service being performed on your behalf here, just a transfer of an object."
                ),
            ),
            TaskOption(
                option_id="doesnt-apply-digital", label="No -- electronics like laptops are excluded from Article 2.",
                is_correct=False,
                consequence="You'd be wrong about a real, important legal protection you actually have.",
                plain_language_feedback=(
                    "There's no electronics exclusion. The statute's own \"goods\" definition turns on whether "
                    "something is movable and identified -- not on what category of product it is."
                ),
            ),
        ],
        governing_sections=["8.2-102", "8.2-105"],
        professional_terminology={
            "goods": "The legal term for a movable, physical thing that can be bought and sold under Article 2.",
            "scope": "Which transactions a statute actually governs.",
        },
        reasoning_chain=[
            "§ 8.2-102: Article 2 applies to \"transactions in goods.\"",
            "§ 8.2-105(1): \"Goods\" means things that are movable at the time of identification to the contract.",
            "A laptop is a movable, physical object being sold for money -> it is \"goods\" -> Article 2 applies.",
        ],
        common_mistakes=[
            "Assuming Article 2 only covers large/commercial purchases -- it applies to a single consumer purchase just as much.",
            "Confusing a sale of goods with a service contract.",
        ],
        difficulty=1,
        next_task_id="a2-t2-order-inventory",
    )

    task_2 = Task(
        task_id="a2-t2-order-inventory",
        scenario=(
            "You run a small retail shop. You email a supplier ordering 200 phone cases, and the supplier "
            "ships them with an invoice attached. Neither side signed a single combined contract document."
        ),
        learner_role="small-business buyer",
        objective="Inspect the real commercial documents and determine your basic rights and obligations.",
        facts_provided=[
            "You emailed an order; the supplier shipped goods and an invoice in response.",
            "No single signed contract document exists.",
            "The supplier regularly sells phone cases as part of its business.",
        ],
        documents_provided=["Your email order", "The supplier's invoice"],
        options=[
            TaskOption(
                option_id="contract-formed-by-conduct", label="A real contract formed -- the order and shipment together show agreement.",
                is_correct=True,
                consequence="You correctly treat this as a binding deal -- both sides now have real obligations.",
                plain_language_feedback=(
                    "You don't need one signed master document. Sending an order and then shipping/accepting "
                    "goods in response is exactly the kind of conduct the statute says can form a contract."
                ),
            ),
            TaskOption(
                option_id="no-contract-no-signature", label="No contract exists -- nothing was ever signed by both parties.",
                is_correct=False,
                consequence="You'd wrongly treat a real, binding deal as if it weren't one.",
                plain_language_feedback=(
                    "A signature isn't required. The statute is explicit that conduct recognizing a contract's "
                    "existence -- like ordering and then shipping/accepting goods -- is enough."
                ),
            ),
            TaskOption(
                option_id="no-contract-open-terms", label="No contract exists -- price, delivery date, and other terms were never pinned down.",
                is_correct=False,
                consequence="You'd overestimate how much certainty the law actually requires before a deal is binding.",
                plain_language_feedback=(
                    "Leaving some terms open doesn't defeat contract formation as long as the parties intended "
                    "to deal and there's a reasonably certain basis for a remedy if something goes wrong."
                ),
            ),
        ],
        governing_sections=["8.2-104", "8.2-204"],
        professional_terminology={
            "merchant": "A person or business that regularly deals in the kind of goods involved, or otherwise holds itself out as having relevant expertise.",
            "formation": "The legal moment/mechanism by which a contract comes into existence.",
        },
        reasoning_chain=[
            "§ 8.2-204(1): A contract for sale may be made in any manner sufficient to show agreement, including conduct by both parties.",
            "§ 8.2-204(3): A contract doesn't fail for indefiniteness merely because some terms are left open.",
            "Ordering, then shipping and accepting goods, is conduct recognizing a deal -> a real contract formed.",
            "§ 8.2-104(1): the supplier, dealing in phone cases as its business, is a \"merchant\" -- relevant to what obligations attach next.",
        ],
        common_mistakes=[
            "Assuming a contract always needs one signed document.",
            "Assuming open terms automatically void a deal.",
        ],
        difficulty=2,
        prerequisite_task_id="a2-t1-buy-a-laptop",
        next_task_id="a2-t3-nonconforming-delivery",
    )

    task_3 = Task(
        task_id="a2-t3-nonconforming-delivery",
        scenario=(
            "The 200 phone cases arrive, but 60 of them are the wrong color -- not what you ordered. "
            "The rest are correct. You need to decide what to do with the shipment."
        ),
        learner_role="operations/procurement",
        objective="Choose your real, legally available response to a nonconforming delivery.",
        facts_provided=[
            "200 units ordered; 60 arrived nonconforming, 140 arrived as ordered.",
            "The shipment is a single delivery, not an installment contract.",
            "Nothing in your deal changes the ordinary rules on delivery.",
        ],
        hidden_or_irrelevant_facts=[
            "The supplier's reason for shipping the wrong color is not legally relevant to which options are available to you.",
        ],
        options=[
            TaskOption(
                option_id="reject-whole", label="Reject the whole shipment.",
                is_correct=False,
                consequence="You send back all 200 units, including the 140 that were correct -- a real, available option, but not the only one, and not chosen here as \"the\" answer since two other real options also exist.",
                plain_language_feedback="This is a real, legally available choice -- but it's not your only one, and rejecting everything isn't required just because part of the shipment was wrong.",
            ),
            TaskOption(
                option_id="accept-whole", label="Accept the whole shipment as-is.",
                is_correct=False,
                consequence="You keep all 200 units, including the 60 wrong-color ones, without formally addressing the defect.",
                plain_language_feedback="Also real and available -- but it means living with the nonconforming units unless you separately pursue a remedy for them.",
            ),
            TaskOption(
                option_id="accept-conforming-reject-rest", label="Accept the 140 correct units; reject the 60 nonconforming ones.",
                is_correct=True,
                consequence="You keep what you can use and send back only the defective units -- the statute names this exact option.",
                plain_language_feedback=(
                    "The statute gives you this precise middle option: accept whichever commercial unit(s) "
                    "conform and reject the rest, rather than an all-or-nothing choice."
                ),
            ),
            TaskOption(
                option_id="keep-using-silently", label="Keep using all 200 units without formally accepting or rejecting anything.",
                is_correct=False,
                consequence="You lose the clean benefit of any of the statute's real options by never actually exercising one.",
                plain_language_feedback=(
                    "This is the real, common mistake: continuing to use nonconforming goods without ever "
                    "formally accepting or rejecting can itself function as acceptance, forfeiting your cleaner options."
                ),
            ),
        ],
        governing_sections=["8.2-601"],
        professional_terminology={
            "commercial unit": "A unit of goods that commercial usage treats as a single whole for sale/division purposes.",
            "nonconforming": "Goods or delivery that fail to match the contract in some respect.",
            "reject": "A buyer's formal refusal to accept goods that fail to conform to the contract.",
        },
        reasoning_chain=[
            "§ 8.2-601: if goods or tender of delivery fail in any respect to conform, the buyer may (a) reject the whole, (b) accept the whole, or (c) accept any commercial unit(s) and reject the rest.",
            "60 nonconforming units + 140 conforming units is exactly the fact pattern (c) addresses.",
            "Accepting the 140 and rejecting the 60 uses the statute's own named middle option.",
        ],
        common_mistakes=[
            "Treating this as a forced all-or-nothing choice between full acceptance and full rejection.",
            "Continuing to use nonconforming goods without ever formally accepting or rejecting them.",
        ],
        difficulty=3,
        prerequisite_task_id="a2-t2-order-inventory",
        next_task_id="a2-t4-transfer-warranty",
    )

    task_4 = Task(
        task_id="a2-t4-transfer-warranty",
        scenario=(
            "A different supplier ships you 50 industrial shelving units. Their catalog description said "
            "\"heavy-duty, rated for 500 lbs per shelf.\" When they arrive, several shelves visibly bow under "
            "far less weight."
        ),
        learner_role="operations/procurement (transfer)",
        objective=(
            "Apply what you already know about nonconforming goods to a NEW fact pattern that also raises "
            "a concept you haven't been told about yet -- recognize it yourself."
        ),
        facts_provided=[
            "The supplier's catalog described the shelving as \"rated for 500 lbs per shelf.\"",
            "The delivered shelves bow well under that weight.",
            "This is a different product and a different supplier than the earlier tasks.",
        ],
        options=[
            TaskOption(
                option_id="just-nonconforming-delivery", label="Treat this only as a nonconforming-delivery problem, exactly like the phone cases.",
                is_correct=False,
                consequence="You'd miss a second, independent problem: the catalog's own description created a promise the shelves don't keep.",
                plain_language_feedback=(
                    "The delivery-response menu (reject/accept/accept-and-reject-part) still applies -- but "
                    "there's more going on here than just nonconformity at delivery."
                ),
            ),
            TaskOption(
                option_id="description-created-warranty", label="The catalog's \"rated for 500 lbs\" description created an express warranty the shelves failed to meet.",
                is_correct=True,
                consequence="You correctly spot that a specific factual description became part of the deal, and the goods didn't match it.",
                plain_language_feedback=(
                    "A seller's description of goods, made part of the basis of the bargain, creates an express "
                    "warranty that the goods will match that description -- the seller didn't need to use the word "
                    "\"warranty\" for this to count."
                ),
            ),
            TaskOption(
                option_id="no-legal-issue-just-bad-luck", label="There's no separate legal issue here -- products sometimes just don't perform as expected.",
                is_correct=False,
                consequence="You'd give up a real, statute-backed claim by treating a specific, factual promise as mere bad luck.",
                plain_language_feedback=(
                    "A specific, factual capacity claim like \"rated for 500 lbs\" is exactly the kind of "
                    "affirmation the statute treats as creating an express warranty -- not just marketing puffery."
                ),
            ),
        ],
        governing_sections=["8.2-601", "8.2-313"],
        professional_terminology={
            "express warranty": "A promise about the goods, created by the seller's own affirmation, description, or sample, that becomes part of the deal.",
            "basis of the bargain": "A statement specific and factual enough that it became part of what the buyer was actually promised.",
        },
        reasoning_chain=[
            "Same delivery-response menu as Task 3 (§ 8.2-601) still applies to the nonconforming shelves.",
            "§ 8.2-313(1)(b): a description of the goods made part of the basis of the bargain creates an express warranty that the goods conform to it.",
            "\"Rated for 500 lbs per shelf\" is a specific, factual description, not vague opinion -> it created an express warranty.",
            "The shelves bowing under far less weight -> the express warranty was breached, independent of the ordinary nonconformity analysis.",
        ],
        common_mistakes=[
            "Missing that a catalog description (not just a spoken promise) can create a warranty.",
            "Treating every product failure as \"just bad luck\" rather than checking whether a specific factual claim was made.",
        ],
        difficulty=4,
        prerequisite_task_id="a2-t3-nonconforming-delivery",
        next_task_id=None,
    )

    tasks = [task_1, task_2, task_3, task_4]
    for task in tasks:
        task.validate()
    return tasks

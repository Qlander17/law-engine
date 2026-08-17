"""Law Engine -- Transaction Lifecycle feature (Live Run 1.38, Mission 16).

The first real, evolving transaction lifecycle in the Learning Engine: a
consumer goods purchase, progressing through real events (threshold
scope question -> formation -> merchant status & warranties -> delivery,
rejection & remedies) rather than isolated quiz questions. Every stage's
facts, question, correct choice, explanation, and changed-fact variant
trace to one of the 11 real Virginia-enacted Article 2 sections already
ingested (library/normalized/ucc/article-2-sections.json) -- no legal
conclusion in this module is hard-coded without a `section_id`/`citation`
pointing at its real source, per this run's own explicit requirement.

Scenario chosen: an ordinary consumer goods purchase (a used laptop sale),
per the directive's stated preference, since it's the one scenario every
one of the 11 already-ingested sections can genuinely support without
inventing statutory content that hasn't actually been ingested. See
docs/ucc-scenario-matrix.md scenario 1 and docs/ucc-practical-curriculum.md
Module 1-4 for how this fits the broader curriculum.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.retrieval import get_section

LIFECYCLES_DIR = _LAW_ENGINE_ROOT / "library" / "normalized" / "lifecycles"


class TransactionLifecycleError(Exception):
    """Raised for real, unrecoverable lifecycle errors -- an unknown stage
    or an unknown choice, never silently ignored."""


@dataclass
class LifecycleChoice:
    label: str
    is_correct: bool
    outcome: str
    section_id: str
    citation: str


@dataclass
class ChangedFactVariant:
    changed_fact: str
    effect: str
    section_id: str
    citation: str

    def to_dict(self) -> dict:
        return {
            "changed_fact": self.changed_fact,
            "effect": self.effect,
            "section_id": self.section_id,
            "citation": self.citation,
        }


@dataclass
class LifecycleStage:
    stage_id: str
    title: str
    facts: str
    question: str
    choices: list[LifecycleChoice]
    explanation: str
    section_id: str
    citation: str
    changed_fact_variants: list[ChangedFactVariant] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "stage_id": self.stage_id,
            "title": self.title,
            "facts": self.facts,
            "question": self.question,
            "choices": [
                {"label": c.label, "is_correct": c.is_correct, "outcome": c.outcome,
                 "section_id": c.section_id, "citation": c.citation}
                for c in self.choices
            ],
            "explanation": self.explanation,
            "section_id": self.section_id,
            "citation": self.citation,
            "changed_fact_variants": [v.to_dict() for v in self.changed_fact_variants],
        }


@dataclass
class LifecycleAnswer:
    stage_id: str
    chosen_label: str
    is_correct: bool
    outcome: str


@dataclass
class TransactionLifecycle:
    lifecycle_id: str
    title: str
    stages: list[LifecycleStage]

    def stage_at(self, index: int) -> LifecycleStage:
        if not 0 <= index < len(self.stages):
            raise TransactionLifecycleError(f"No stage at index {index} in {self.lifecycle_id!r} ({len(self.stages)} stages).")
        return self.stages[index]

    def answer(self, index: int, chosen_label: str) -> LifecycleAnswer:
        stage = self.stage_at(index)
        for choice in stage.choices:
            if choice.label == chosen_label:
                return LifecycleAnswer(
                    stage_id=stage.stage_id, chosen_label=chosen_label,
                    is_correct=choice.is_correct, outcome=choice.outcome,
                )
        raise TransactionLifecycleError(f"{chosen_label!r} is not a real choice at stage {stage.stage_id!r}.")

    def to_dict(self) -> dict:
        return {
            "lifecycle_id": self.lifecycle_id,
            "title": self.title,
            "stages": [s.to_dict() for s in self.stages],
        }


def _require_section(section_id: str) -> dict:
    section = get_section(section_id)
    if section is None:
        raise TransactionLifecycleError(f"No ingested section {section_id!r} -- cannot build a lifecycle stage without a real source.")
    return section


def build_consumer_goods_purchase_lifecycle() -> TransactionLifecycle:
    """Real, evolving consumer-goods-purchase lifecycle grounded entirely
    in the 11 real ingested Article 2 sections. Each stage progresses the
    same running fact pattern (a buyer purchasing a used laptop from an
    electronics-store seller) rather than presenting unrelated quiz items."""
    threshold = _require_section("8.2-105")
    formation = _require_section("8.2-204")
    acceptance_mode = _require_section("8.2-206")
    battle_of_forms = _require_section("8.2-207")
    merchant = _require_section("8.2-104")
    express_warranty = _require_section("8.2-313")
    implied_warranty = _require_section("8.2-314")
    delivery = _require_section("8.2-601")
    buyer_remedies = _require_section("8.2-711")
    seller_remedies = _require_section("8.2-703")

    stage_1 = LifecycleStage(
        stage_id="threshold-scope",
        title="Is this even an Article 2 transaction?",
        facts=(
            "A buyer emails a local electronics store asking to buy a specific "
            "used laptop the store has listed for $800."
        ),
        question="Is a laptop \"goods\" under Article 2, making this a sale-of-goods transaction?",
        choices=[
            LifecycleChoice(
                label="Yes -- a laptop is a movable, identified thing, so it's \"goods\"",
                is_correct=True,
                outcome=f'{threshold["citation"]} defines "goods" as things movable at the time of identification to the contract -- a specific physical laptop fits this directly.',
                section_id="8.2-105", citation=threshold["citation"],
            ),
            LifecycleChoice(
                label="No -- Article 2 only covers goods sold between businesses, not to an individual buyer",
                is_correct=False,
                outcome=f'{threshold["citation"]}\'s definition of "goods" turns on what\'s being sold (a movable, identified thing), not on whether the buyer is a business -- nothing in the definition excludes an individual buyer.',
                section_id="8.2-105", citation=threshold["citation"],
            ),
        ],
        explanation=f'{threshold["citation"]}: "Goods" means all things (including specially manufactured goods) which are movable at the time of identification to the contract for sale.',
        section_id="8.2-105", citation=threshold["citation"],
    )

    stage_2 = LifecycleStage(
        stage_id="formation",
        title="Is there a binding contract?",
        facts=(
            "The buyer's email said \"I'll take it for $800.\" The seller never signed "
            "anything -- they just shipped the laptop the next day."
        ),
        question="Does a binding contract exist without a signed writing?",
        choices=[
            LifecycleChoice(
                label="Yes -- shipping the laptop is conduct showing agreement, and open/unwritten terms don't defeat formation",
                is_correct=True,
                outcome=f'{formation["citation"]} allows a contract to be shown "in any manner sufficient to show agreement, including conduct by both parties," and tolerates open terms if the parties intended a contract and a remedy is reasonably certain.',
                section_id="8.2-204", citation=formation["citation"],
            ),
            LifecycleChoice(
                label="No -- without a signed writing covering every term, there's no contract yet",
                is_correct=False,
                outcome=f'{formation["citation"]} explicitly rejects this: a sale-of-goods contract can be shown by conduct, and doesn\'t fail for indefiniteness merely because some terms were left open.',
                section_id="8.2-204", citation=formation["citation"],
            ),
        ],
        explanation=f'{formation["citation"]}: a contract for sale of goods may be made in any manner sufficient to show agreement, including conduct by both parties which recognizes the existence of such a contract.',
        section_id="8.2-204", citation=formation["citation"],
        changed_fact_variants=[
            ChangedFactVariant(
                changed_fact=(
                    "What if, instead of just shipping, the seller had replied with a written "
                    "confirmation adding a new term -- \"all sales final, no returns\" -- and both "
                    "the buyer and seller are merchants dealing in goods of this kind?"
                ),
                effect=(
                    f'{acceptance_mode["citation"]} treats a seasonable expression of acceptance as an '
                    f'acceptance even with additional terms; {battle_of_forms["citation"]} then asks whether '
                    'that new term became part of the contract -- between merchants it does, UNLESS the offer '
                    'expressly limited acceptance to its own terms, the new term materially alters the deal '
                    '(a no-returns clause plausibly would), or the buyer objects within a reasonable time.'
                ),
                section_id="8.2-207", citation=battle_of_forms["citation"],
            ),
        ],
    )

    stage_3 = LifecycleStage(
        stage_id="merchant-and-warranties",
        title="What protections come with the purchase?",
        facts=(
            "The seller is a retail electronics store that regularly buys and resells used "
            "laptops. Nothing in the listing said \"as-is\" or disclaimed any warranty."
        ),
        question="Does the buyer get any warranty protection even though nothing was promised in writing?",
        choices=[
            LifecycleChoice(
                label="Yes -- because the seller is a merchant dealing in these goods, an implied warranty of merchantability attaches automatically",
                is_correct=True,
                outcome=f'{merchant["citation"]} makes this seller a "merchant" (occupational dealing in goods of the kind); {implied_warranty["citation"]} then implies a warranty of merchantability by operation of law for a merchant-seller unless excluded/modified.',
                section_id="8.2-314", citation=implied_warranty["citation"],
            ),
            LifecycleChoice(
                label="No -- without an express written warranty, the buyer has no protection at all",
                is_correct=False,
                outcome=f'This misses {implied_warranty["citation"]}: the warranty of merchantability is implied automatically for a merchant-seller -- the buyer doesn\'t need an express written warranty to get it.',
                section_id="8.2-314", citation=implied_warranty["citation"],
            ),
        ],
        explanation=f'{implied_warranty["citation"]}: a warranty that the goods shall be merchantable is implied in a contract for their sale if the seller is a merchant with respect to goods of that kind.',
        section_id="8.2-314", citation=implied_warranty["citation"],
        changed_fact_variants=[
            ChangedFactVariant(
                changed_fact="What if the seller were a private individual selling their own personal laptop, not a store?",
                effect=(
                    f'{implied_warranty["citation"]}\'s implied warranty of merchantability requires a '
                    'merchant-seller -- a private, non-merchant seller does not automatically give one. '
                    f'But if that private seller described the laptop\'s condition ("battery holds a full '
                    f'charge"), {express_warranty["citation"]} can still create an express warranty from that '
                    'affirmation or description, regardless of merchant status.'
                ),
                section_id="8.2-313", citation=express_warranty["citation"],
            ),
        ],
    )

    stage_4 = LifecycleStage(
        stage_id="delivery-and-remedies",
        title="The laptop arrives broken -- what now?",
        facts="The laptop arrives and won't power on at all.",
        question="What can the buyer do?",
        choices=[
            LifecycleChoice(
                label="Reject the goods (the whole shipment, since it's a single laptop) and pursue cover or damages",
                is_correct=True,
                outcome=f'{delivery["citation"]} lets a buyer reject the whole if the goods fail to conform to the contract; having rightfully rejected, {buyer_remedies["citation"]} then lets the buyer "cover" (buy a replacement) and recover damages, or recover damages for nondelivery.',
                section_id="8.2-711", citation=buyer_remedies["citation"],
            ),
            LifecycleChoice(
                label="The buyer must accept the laptop as-is and can only complain informally afterward",
                is_correct=False,
                outcome=f'{delivery["citation"]} gives the buyer a real right to reject nonconforming goods -- there is no rule requiring acceptance of defective goods with only an informal complaint as recourse.',
                section_id="8.2-601", citation=delivery["citation"],
            ),
        ],
        explanation=(
            f'{delivery["citation"]}: if the goods fail to conform to the contract, the buyer may reject '
            f'the whole. {buyer_remedies["citation"]}: on rightful rejection, the buyer may "cover" and '
            'recover damages, or recover damages for nondelivery.'
        ),
        section_id="8.2-711", citation=buyer_remedies["citation"],
        changed_fact_variants=[
            ChangedFactVariant(
                changed_fact=(
                    "What if the roles were reversed -- the laptop arrived in perfect working order, "
                    "but the buyer simply refused to pay and sent it back anyway?"
                ),
                effect=(
                    f'{seller_remedies["citation"]} governs a wrongfully rejecting buyer: the seller may '
                    'withhold delivery of any remaining goods, stop delivery by a carrier, resell and '
                    'recover damages, recover damages for nonacceptance (or the price in a proper case), '
                    'or cancel -- the mirror image of the buyer\'s remedies above.'
                ),
                section_id="8.2-703", citation=seller_remedies["citation"],
            ),
        ],
    )

    return TransactionLifecycle(
        lifecycle_id="consumer-goods-purchase-v1",
        title="Consumer goods purchase: a used laptop sale",
        stages=[stage_1, stage_2, stage_3, stage_4],
    )


def write_lifecycle_json(lifecycle: TransactionLifecycle, *, out_dir: Path = LIFECYCLES_DIR) -> Path:
    """Same Python-owns-ingestion / TypeScript-only-reads boundary this
    project already applies to StatuteSection data (see
    apps/web/src/lib/lawEngineData.ts's own docstring comment) -- the
    Next.js app never re-implements lifecycle-building logic, it only
    reads this real, Python-produced JSON."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{lifecycle.lifecycle_id}.json"
    out_path.write_text(json.dumps(lifecycle.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    written = write_lifecycle_json(build_consumer_goods_purchase_lifecycle())
    print(f"Wrote {written}")

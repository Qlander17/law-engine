"""Law Engine -- learning-primitive foundation (Live Run 1.37, Mission 18).

Reusable primitives meant to eventually support summaries, concept maps,
flashcards, MCQs, hypotheticals, adaptive quizzes, and progress tracking --
this run implements the two smallest real, useful ones (flashcard, MCQ)
against the real UCC Article 2 vertical slice, not a mocked example.

Every MCQ explains why the correct answer is correct AND why each
incorrect option is wrong, with a real citation back to source -- per this
run's own explicit requirement. No invented legal propositions: every
question and every explanation traces to one of the real, ingested
StatuteSection records.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import sys
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.retrieval import get_section


class LearningItemType(str, Enum):
    FLASHCARD = "FLASHCARD"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"


class LearningPathOrganization(str, Enum):
    """Live Run 1.38, Mission 13. Source organization and learner
    organization are different concepts -- a path can group items by
    AUTHORITY ("Article 2") or by OBJECTIVE ("how to buy goods"), and an
    OBJECTIVE path is free to pull items from whatever authority is
    actually relevant, crossing Article/source boundaries whenever that's
    more useful to the learner than staying inside one source's label."""

    AUTHORITY = "AUTHORITY"    # e.g. "Teach me Article 2."
    OBJECTIVE = "OBJECTIVE"    # e.g. "Teach me how to buy goods."


class LearningItemError(Exception):
    """Raised for real, unrecoverable learning-item construction errors."""


@dataclass
class Flashcard:
    item_id: str
    prompt: str
    answer: str
    citation: str
    section_id: str

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "type": LearningItemType.FLASHCARD.value,
            "prompt": self.prompt,
            "answer": self.answer,
            "citation": self.citation,
            "section_id": self.section_id,
        }


@dataclass
class MultipleChoiceQuestion:
    item_id: str
    prompt: str
    correct_choice: str
    why_correct: str
    incorrect_choices: dict[str, str]  # choice text -> why it's wrong
    citation: str
    section_id: str

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "type": LearningItemType.MULTIPLE_CHOICE.value,
            "prompt": self.prompt,
            "correct_choice": self.correct_choice,
            "why_correct": self.why_correct,
            "incorrect_choices": self.incorrect_choices,
            "citation": self.citation,
            "section_id": self.section_id,
        }

    def all_choices(self) -> list[str]:
        return [self.correct_choice] + list(self.incorrect_choices.keys())

    def explain(self, chosen: str) -> str:
        if chosen == self.correct_choice:
            return self.why_correct
        if chosen in self.incorrect_choices:
            return self.incorrect_choices[chosen]
        raise LearningItemError(f"{chosen!r} is not one of this question's real choices.")


@dataclass
class LearningPath:
    """A named, ordered sequence of real learning-item IDs, tagged with
    which organizing principle assembled it. Deliberately just an ordered
    list of item_ids rather than embedded item objects -- a path is a
    VIEW over existing items, not a copy of them, so an item's own source
    of truth (Flashcard/MultipleChoiceQuestion) never drifts from what a
    path presents."""

    path_id: str
    title: str
    organization: LearningPathOrganization
    item_ids: list[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "path_id": self.path_id,
            "title": self.title,
            "organization": self.organization.value,
            "item_ids": self.item_ids,
            "description": self.description,
        }


def build_authority_mode_path(path_id: str, title: str, item_ids: list[str], description: str = "") -> LearningPath:
    """Authority Mode: "teach me Article 2" -- organized by the source's
    own structure."""
    return LearningPath(
        path_id=path_id, title=title, organization=LearningPathOrganization.AUTHORITY,
        item_ids=item_ids, description=description,
    )


def build_objective_mode_path(path_id: str, title: str, item_ids: list[str], description: str = "") -> LearningPath:
    """Objective Mode: "teach me how to buy goods" -- organized by a real
    practical task. item_ids may span multiple authorities/sources; this
    function makes no assumption that they all come from one Article."""
    return LearningPath(
        path_id=path_id, title=title, organization=LearningPathOrganization.OBJECTIVE,
        item_ids=item_ids, description=description,
    )


# Real, concrete Objective Mode example built from the real Article 2 MCQ
# set (build_article_2_mcq_set() below) -- reframed around the practical
# task "buying goods" rather than "Article 2" as a label. Honest, disclosed
# limit: with only Article 2 content ingested so far, this path can't yet
# demonstrate crossing INTO another Article (e.g. pulling a UCC Article 9
# purchase-money-security-interest item into the same "buying goods on
# credit" objective) -- the architecture supports it (item_ids is just a
# flat list of IDs from wherever they come from), but there is no second
# Article's content ingested yet to draw from. See
# law-engine/docs/ucc-practical-curriculum.md for where that content gap
# sits in the overall curriculum plan.
def build_buying_goods_objective_path() -> LearningPath:
    return build_objective_mode_path(
        path_id="objective-buying-goods-v1",
        title="How to buy goods",
        item_ids=["a2-mcq-002", "a2-mcq-001", "a2-mcq-003"],
        description=(
            "Practical sequence for a goods purchase: does a binding contract "
            "exist even with open terms (§ 8.2-204), does the seller's "
            "merchant status matter (§ 8.2-104), and what warranty protection "
            "comes with the purchase automatically (§ 8.2-314) -- ordered by "
            "when a real buyer would actually encounter each question, not by "
            "the sections' numeric order within Article 2."
        ),
    )


def _require_section(section_id: str) -> dict:
    section = get_section(section_id)
    if section is None:
        raise LearningItemError(f"No ingested section {section_id!r} -- cannot build a learning item without a real source.")
    return section


def make_definition_flashcard(section_id: str, term: str, item_id: str) -> Flashcard:
    """Builds a flashcard for one real defined term, sourced directly from
    the ingested section's own real paragraph text (never invented)."""
    section = _require_section(section_id)
    if term not in section["defined_terms"]:
        raise LearningItemError(f"{term!r} is not a real defined term in section {section_id!r}.")
    matching = [p for p in section["paragraphs"] if term in p.lower() or f'"{term}"' in p]
    answer = matching[0] if matching else section["paragraphs"][0]
    return Flashcard(
        item_id=item_id,
        prompt=f'Under {section["citation"]}, how is "{term}" defined?',
        answer=answer,
        citation=section["citation"],
        section_id=section_id,
    )


# Real, hand-built MCQ set against the real ingested Article 2 slice --
# every citation and every explanation traces to the real statutory text
# ingested this run (law-engine/library/normalized/ucc/article-2-sections.json).
def build_article_2_mcq_set() -> list[MultipleChoiceQuestion]:
    questions = [
        MultipleChoiceQuestion(
            item_id="a2-mcq-001",
            prompt="Under Va. Code Ann. § 8.2-104, what makes someone a \"merchant\" for UCC Article 2 purposes?",
            correct_choice="Dealing in goods of the kind, or holding oneself out by occupation as having knowledge/skill peculiar to the goods or practices involved",
            why_correct='§ 8.2-104(1) defines "merchant" exactly this way -- occupation-based dealing in or knowledge of the relevant goods/practices, including knowledge attributed through an agent or broker.',
            incorrect_choices={
                "Having a business license in the state where the sale occurs": '§ 8.2-104 never mentions licensure -- "merchant" status turns on dealing in the goods or occupational knowledge/skill, not on any licensing requirement.',
                "Selling goods worth more than $500": "No dollar threshold appears anywhere in § 8.2-104's definition of merchant.",
                "Being a corporation rather than an individual": "Merchant status under § 8.2-104 is about occupational knowledge/dealing, not business entity type -- an individual can be a merchant and a corporation's mere existence doesn't make it one.",
            },
            citation="Va. Code Ann. § 8.2-104(1)",
            section_id="8.2-104",
        ),
        MultipleChoiceQuestion(
            item_id="a2-mcq-002",
            prompt="Under Va. Code Ann. § 8.2-204, can a contract for the sale of goods exist even if the parties never agree on every term?",
            correct_choice="Yes -- if the parties intended to make a contract and there is a reasonably certain basis for a remedy",
            why_correct="§ 8.2-204(3) says exactly this: a contract doesn't fail for indefiniteness merely because one or more terms are left open, as long as the parties intended a contract and a remedy can be reasonably determined.",
            incorrect_choices={
                "No -- every material term must be agreed to in writing": "§ 8.2-204(1) explicitly allows a contract to be shown \"in any manner sufficient to show agreement, including conduct,\" and § 8.2-204(3) tolerates open terms -- a signed writing with every term fixed is not required.",
                "No -- price must always be agreed to first": "§ 8.2-204 imposes no such sequencing requirement; the statute cares about intent to contract and a reasonably certain remedy basis, not a mandatory price-first order.",
                "Only if both parties are merchants": "§ 8.2-204's formation rule applies generally, not only between merchants -- merchant-specific rules appear elsewhere (e.g., § 8.2-207(2)), not in this section.",
            },
            citation="Va. Code Ann. § 8.2-204(3)",
            section_id="8.2-204",
        ),
        MultipleChoiceQuestion(
            item_id="a2-mcq-003",
            prompt="Under Va. Code Ann. § 8.2-314, when is an implied warranty of merchantability created?",
            correct_choice="Automatically, in a contract for sale, if the seller is a merchant with respect to goods of that kind -- unless excluded or modified under § 8.2-316",
            why_correct="§ 8.2-314(1) implies the warranty by operation of law for a merchant-seller unless excluded/modified under § 8.2-316 -- the buyer doesn't need to ask for it or negotiate it in.",
            incorrect_choices={
                "Only if the buyer specifically requests it in writing": "§ 8.2-314 implies the warranty automatically for a qualifying merchant-seller; nothing in the section conditions it on a buyer's written request.",
                "Only for used goods, not new goods": "§ 8.2-314 draws no such distinction between new and used goods -- the warranty turns on merchant-seller status, not the goods' condition-as-new-or-used.",
                "Never -- Virginia does not recognize implied warranties": "§ 8.2-314 is itself Virginia's own enacted implied-warranty-of-merchantability provision -- the premise of this choice is directly contradicted by the statute's own existence.",
            },
            citation="Va. Code Ann. § 8.2-314(1)",
            section_id="8.2-314",
        ),
    ]
    return questions


if __name__ == "__main__":
    for q in build_article_2_mcq_set():
        print(q.prompt)
        print(" ->", q.correct_choice)

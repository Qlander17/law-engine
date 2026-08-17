from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import ingestion, learning


class FlashcardTests(unittest.TestCase):
    # Live Run 1.45 -- see test_ingestion.py's RunIngestionTests for the
    # real, disclosed reason (law-engine-publication-readiness-1.44.md,
    # §8): snapshot/restore the real tracked manifest around the real
    # ingestion call this class needs, so a stranger running the
    # documented test command never sees a dirty git tree afterward.
    @classmethod
    def setUpClass(cls) -> None:
        manifest_path = _LAW_ENGINE_ROOT / "library" / "manifests" / "va-code-title-8.2-article-2.json"
        cls._manifest_before = manifest_path.read_bytes() if manifest_path.exists() else None
        cls._manifest_path = manifest_path
        ingestion.run_ingestion()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._manifest_before is not None:
            cls._manifest_path.write_bytes(cls._manifest_before)

    def test_definition_flashcard_uses_real_source_text(self) -> None:
        card = learning.make_definition_flashcard("8.2-104", "merchant", "fc-001")
        self.assertIn("Merchant", card.answer)
        self.assertEqual(card.citation, "Va. Code Ann. § 8.2-104")

    def test_unknown_section_raises(self) -> None:
        with self.assertRaises(learning.LearningItemError):
            learning.make_definition_flashcard("8.2-999", "merchant", "fc-002")

    def test_unknown_term_raises(self) -> None:
        with self.assertRaises(learning.LearningItemError):
            learning.make_definition_flashcard("8.2-104", "not-a-real-term", "fc-003")


class MultipleChoiceQuestionTests(unittest.TestCase):
    def test_real_question_set_has_three_questions(self) -> None:
        questions = learning.build_article_2_mcq_set()
        self.assertEqual(len(questions), 3)

    def test_every_question_explains_correct_and_incorrect_choices(self) -> None:
        for q in learning.build_article_2_mcq_set():
            self.assertTrue(q.why_correct.strip())
            self.assertEqual(len(q.incorrect_choices), 3)
            for wrong_choice, explanation in q.incorrect_choices.items():
                self.assertTrue(explanation.strip())

    def test_every_question_has_a_real_citation(self) -> None:
        for q in learning.build_article_2_mcq_set():
            self.assertTrue(q.citation.startswith("Va. Code Ann."))

    def test_explain_returns_why_correct_for_correct_choice(self) -> None:
        q = learning.build_article_2_mcq_set()[0]
        self.assertEqual(q.explain(q.correct_choice), q.why_correct)

    def test_explain_returns_why_wrong_for_incorrect_choice(self) -> None:
        q = learning.build_article_2_mcq_set()[0]
        wrong = next(iter(q.incorrect_choices))
        self.assertEqual(q.explain(wrong), q.incorrect_choices[wrong])

    def test_explain_raises_for_unknown_choice(self) -> None:
        q = learning.build_article_2_mcq_set()[0]
        with self.assertRaises(learning.LearningItemError):
            q.explain("not a real choice")

    def test_all_choices_includes_correct_and_incorrect(self) -> None:
        q = learning.build_article_2_mcq_set()[0]
        choices = q.all_choices()
        self.assertEqual(len(choices), 4)
        self.assertIn(q.correct_choice, choices)


class LearningPathTests(unittest.TestCase):
    def test_authority_mode_path_carries_organization_tag(self) -> None:
        path = learning.build_authority_mode_path(
            "authority-article-2-v1", "Article 2: Sales", ["a2-mcq-001", "a2-mcq-002"]
        )
        self.assertEqual(path.organization, learning.LearningPathOrganization.AUTHORITY)
        self.assertEqual(path.to_dict()["organization"], "AUTHORITY")

    def test_objective_mode_path_carries_organization_tag(self) -> None:
        path = learning.build_objective_mode_path(
            "objective-financing-a-vehicle-v1", "How to finance a vehicle", ["a2-mcq-002"]
        )
        self.assertEqual(path.organization, learning.LearningPathOrganization.OBJECTIVE)

    def test_buying_goods_objective_path_references_real_items_in_practical_order(self) -> None:
        path = learning.build_buying_goods_objective_path()
        self.assertEqual(path.organization, learning.LearningPathOrganization.OBJECTIVE)
        real_item_ids = {q.item_id for q in learning.build_article_2_mcq_set()}
        self.assertTrue(set(path.item_ids).issubset(real_item_ids))
        # Practical order: does a contract exist, before merchant status,
        # before the warranty that attaches to it -- not numeric § order.
        self.assertEqual(path.item_ids, ["a2-mcq-002", "a2-mcq-001", "a2-mcq-003"])


if __name__ == "__main__":
    unittest.main()

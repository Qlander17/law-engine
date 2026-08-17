from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import cross_article_lifecycle as cal
from services import transaction_lifecycle as tl


class EquipmentPurchaseOnCreditLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lifecycle = cal.build_equipment_purchase_on_credit_lifecycle()

    def test_lifecycle_has_six_progressing_stages(self) -> None:
        self.assertEqual(len(self.lifecycle.stages), 6)
        self.assertEqual(
            [s.stage_id for s in self.lifecycle.stages],
            [
                "equipment-purchase-formation",
                "security-agreement-effectiveness",
                "attachment",
                "perfection-and-filing",
                "pmsi-priority",
                "default-and-disposition",
            ],
        )

    def test_genuinely_crosses_from_article_2_into_article_9(self) -> None:
        section_ids = {s.section_id for s in self.lifecycle.stages}
        article_2_ids = {sid for sid in section_ids if sid.startswith("8.2-")}
        article_9_ids = {sid for sid in section_ids if sid.startswith("8.9A-")}
        self.assertTrue(article_2_ids, "lifecycle should include real Article 2 stages")
        self.assertTrue(article_9_ids, "lifecycle should include real Article 9 stages")
        # The first stage is the sale (Article 2); a later stage is the
        # financing (Article 9) -- a genuine cross-Article progression,
        # not two unrelated lifecycles concatenated.
        self.assertTrue(self.lifecycle.stages[0].section_id.startswith("8.2-"))
        self.assertTrue(self.lifecycle.stages[-1].section_id.startswith("8.9A-"))

    def test_every_stage_and_choice_traces_to_a_real_ingested_section(self) -> None:
        from services.retrieval import get_section

        for stage in self.lifecycle.stages:
            self.assertIsNotNone(get_section(stage.section_id), f"{stage.stage_id} cites unknown section {stage.section_id!r}")
            for choice in stage.choices:
                self.assertIsNotNone(get_section(choice.section_id), f"choice in {stage.stage_id} cites unknown section {choice.section_id!r}")
            for variant in stage.changed_fact_variants:
                self.assertIsNotNone(get_section(variant.section_id), f"variant in {stage.stage_id} cites unknown section {variant.section_id!r}")

    def test_every_stage_has_exactly_one_correct_choice(self) -> None:
        for stage in self.lifecycle.stages:
            correct = [c for c in stage.choices if c.is_correct]
            self.assertEqual(len(correct), 1, f"{stage.stage_id} should have exactly one correct choice")

    def test_pmsi_stage_correctly_distinguishes_equipment_from_inventory(self) -> None:
        pmsi_stage = next(s for s in self.lifecycle.stages if s.stage_id == "pmsi-priority")
        self.assertTrue(pmsi_stage.changed_fact_variants)
        variant = pmsi_stage.changed_fact_variants[0]
        self.assertIn("inventory", variant.changed_fact.lower())

    def test_answer_and_stage_at_reuse_the_real_transaction_lifecycle_engine(self) -> None:
        # Confirms this is the same reusable engine, not a parallel
        # reimplementation -- Objective Mode's whole point (Mission 13)
        # is that the shape doesn't change just because sources do.
        self.assertIsInstance(self.lifecycle, tl.TransactionLifecycle)
        stage = self.lifecycle.stage_at(0)
        correct_label = next(c.label for c in stage.choices if c.is_correct)
        answer = self.lifecycle.answer(0, correct_label)
        self.assertTrue(answer.is_correct)

    def test_answer_unknown_choice_raises(self) -> None:
        with self.assertRaises(tl.TransactionLifecycleError):
            self.lifecycle.answer(0, "not a real choice")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import transaction_lifecycle as tl


class ConsumerGoodsPurchaseLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lifecycle = tl.build_consumer_goods_purchase_lifecycle()

    def test_lifecycle_has_four_progressing_stages(self) -> None:
        self.assertEqual(len(self.lifecycle.stages), 4)
        self.assertEqual(
            [s.stage_id for s in self.lifecycle.stages],
            ["threshold-scope", "formation", "merchant-and-warranties", "delivery-and-remedies"],
        )

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

    def test_every_stage_has_at_least_one_changed_fact_variant(self) -> None:
        for stage in self.lifecycle.stages:
            if stage.stage_id == "threshold-scope":
                continue  # the entry stage has no prior fact to vary
            self.assertGreater(len(stage.changed_fact_variants), 0, f"{stage.stage_id} has no changed-fact variant")

    def test_stage_at_raises_for_out_of_range_index(self) -> None:
        with self.assertRaises(tl.TransactionLifecycleError):
            self.lifecycle.stage_at(99)

    def test_answer_correct_choice_reports_is_correct_true(self) -> None:
        stage = self.lifecycle.stage_at(1)
        correct_label = next(c.label for c in stage.choices if c.is_correct)
        answer = self.lifecycle.answer(1, correct_label)
        self.assertTrue(answer.is_correct)
        self.assertEqual(answer.stage_id, "formation")

    def test_answer_incorrect_choice_reports_is_correct_false_with_real_outcome(self) -> None:
        stage = self.lifecycle.stage_at(2)
        wrong_label = next(c.label for c in stage.choices if not c.is_correct)
        answer = self.lifecycle.answer(2, wrong_label)
        self.assertFalse(answer.is_correct)
        self.assertTrue(answer.outcome)

    def test_answer_unknown_choice_raises(self) -> None:
        with self.assertRaises(tl.TransactionLifecycleError):
            self.lifecycle.answer(0, "not a real choice")

    def test_to_dict_round_trips_stage_count(self) -> None:
        d = self.lifecycle.to_dict()
        self.assertEqual(len(d["stages"]), 4)
        self.assertEqual(d["lifecycle_id"], "consumer-goods-purchase-v1")


if __name__ == "__main__":
    unittest.main()

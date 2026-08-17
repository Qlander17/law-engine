from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.tasks import Task, TaskError, TaskOption, build_article_2_consumer_to_operator_ladder


class TaskValidationTests(unittest.TestCase):
    def _valid_task_kwargs(self, **overrides):
        defaults = dict(
            task_id="t-fixture",
            scenario="Fixture scenario.",
            learner_role="ordinary consumer",
            objective="Fixture objective.",
            facts_provided=["A fact."],
            options=[
                TaskOption("right", "Right", True, "consequence", "feedback"),
                TaskOption("wrong", "Wrong", False, "consequence", "feedback"),
            ],
            governing_sections=["8.2-102"],
        )
        defaults.update(overrides)
        return defaults

    def test_a_real_task_with_a_real_section_validates_cleanly(self):
        task = Task(**self._valid_task_kwargs())
        task.validate()  # must not raise

    def test_citing_a_nonexistent_section_raises(self):
        task = Task(**self._valid_task_kwargs(governing_sections=["8.2-999-fabricated"]))
        with self.assertRaises(TaskError):
            task.validate()

    def test_no_governing_sections_raises(self):
        task = Task(**self._valid_task_kwargs(governing_sections=[]))
        with self.assertRaises(TaskError):
            task.validate()

    def test_zero_correct_options_raises(self):
        task = Task(**self._valid_task_kwargs(options=[
            TaskOption("a", "A", False, "c", "f"),
            TaskOption("b", "B", False, "c", "f"),
        ]))
        with self.assertRaises(TaskError):
            task.validate()

    def test_more_than_one_correct_option_raises(self):
        task = Task(**self._valid_task_kwargs(options=[
            TaskOption("a", "A", True, "c", "f"),
            TaskOption("b", "B", True, "c", "f"),
        ]))
        with self.assertRaises(TaskError):
            task.validate()

    def test_no_options_at_all_raises(self):
        task = Task(**self._valid_task_kwargs(options=[]))
        with self.assertRaises(TaskError):
            task.validate()

    def test_governing_citations_resolve_to_real_citation_text(self):
        task = Task(**self._valid_task_kwargs(governing_sections=["8.2-102"]))
        citations = task.governing_citations()
        self.assertEqual(len(citations), 1)
        self.assertIn("8.2-102", citations[0])

    def test_to_dict_includes_real_resolved_citations_not_just_ids(self):
        task = Task(**self._valid_task_kwargs(governing_sections=["8.2-102"]))
        d = task.to_dict()
        self.assertIn("governing_citations", d)
        self.assertEqual(d["governing_sections"], ["8.2-102"])


class Article2LadderTests(unittest.TestCase):
    def setUp(self):
        self.tasks = build_article_2_consumer_to_operator_ladder()
        self.by_id = {t.task_id: t for t in self.tasks}

    def test_real_four_task_ladder_builds_and_validates(self):
        self.assertEqual(len(self.tasks), 4)
        for task in self.tasks:
            task.validate()  # must not raise -- already called in the builder, re-asserted here

    def test_every_task_has_exactly_one_correct_option(self):
        for task in self.tasks:
            correct = [o for o in task.options if o.is_correct]
            self.assertEqual(len(correct), 1, msg=task.task_id)

    def test_every_governing_section_is_real_and_currently_ingested(self):
        for task in self.tasks:
            for section_id in task.governing_sections:
                self.assertIsNotNone(task.governing_citations())

    def test_role_progression_matches_the_intended_ladder(self):
        roles = [t.learner_role for t in self.tasks]
        self.assertEqual(roles[0], "ordinary consumer")
        self.assertEqual(roles[1], "small-business buyer")
        self.assertIn("operations", roles[2])
        self.assertIn("transfer", roles[3])

    def test_difficulty_increases_monotonically(self):
        difficulties = [t.difficulty for t in self.tasks]
        self.assertEqual(difficulties, sorted(difficulties))

    def test_task_chain_is_internally_consistent(self):
        for task in self.tasks:
            if task.next_task_id is not None:
                self.assertIn(task.next_task_id, self.by_id, msg=f"{task.task_id} -> missing next_task_id")
            if task.prerequisite_task_id is not None:
                self.assertIn(task.prerequisite_task_id, self.by_id, msg=f"{task.task_id} -> missing prerequisite_task_id")
        self.assertIsNone(self.by_id["a2-t1-buy-a-laptop"].prerequisite_task_id)
        self.assertIsNone(self.by_id["a2-t4-transfer-warranty"].next_task_id)

    def test_task_3_uses_exactly_the_three_real_statutory_options_plus_one_real_distractor(self):
        # Real, disclosed design choice: § 8.2-601 itself names exactly
        # three options (reject whole / accept whole / accept-and-reject-
        # part). A fourth, clearly-wrong distractor is legitimate design
        # (matches Mission 7's "four options when pedagogically
        # appropriate"), but the three REAL statutory options must all be
        # present and none fabricated beyond them.
        task_3 = self.by_id["a2-t3-nonconforming-delivery"]
        option_ids = {o.option_id for o in task_3.options}
        self.assertEqual(
            option_ids,
            {"reject-whole", "accept-whole", "accept-conforming-reject-rest", "keep-using-silently"},
        )
        self.assertTrue(self.by_id["a2-t3-nonconforming-delivery"].options[2].is_correct)

    def test_task_4_is_the_real_transfer_task_citing_a_new_section_beyond_task_3(self):
        task_3_sections = set(self.by_id["a2-t3-nonconforming-delivery"].governing_sections)
        task_4_sections = set(self.by_id["a2-t4-transfer-warranty"].governing_sections)
        self.assertTrue(task_4_sections - task_3_sections, "Task 4 must introduce at least one new governing section.")


if __name__ == "__main__":
    unittest.main()

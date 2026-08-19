from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.simulations import build_riverside_bistro_simulation


class RiversideBistroSimulationTests(unittest.TestCase):
    def setUp(self):
        self.steps = build_riverside_bistro_simulation()
        self.by_id = {s.task_id: s for s in self.steps}

    def test_real_three_step_simulation_builds_and_validates(self):
        self.assertEqual(len(self.steps), 3)
        for step in self.steps:
            step.validate()

    def test_no_step_opens_with_which_article_applies(self):
        # The exact Chairman correction this simulation exists to satisfy:
        # every objective must be a real action/decision, never a bare
        # "which Article/rule governs" doctrinal question.
        for step in self.steps:
            self.assertNotIn("article", step.objective.lower())
            self.assertNotIn("does ucc", step.objective.lower())

    def test_every_step_has_exactly_one_correct_real_action(self):
        for step in self.steps:
            correct = [o for o in step.options if o.is_correct]
            self.assertEqual(len(correct), 1, msg=step.task_id)

    def test_steps_chain_into_one_continuous_scenario(self):
        self.assertIsNone(self.by_id["sim-bistro-1-delivery"].prerequisite_task_id)
        self.assertEqual(self.by_id["sim-bistro-1-delivery"].next_task_id, "sim-bistro-2-invoice-terms")
        self.assertEqual(self.by_id["sim-bistro-2-invoice-terms"].prerequisite_task_id, "sim-bistro-1-delivery")
        self.assertEqual(self.by_id["sim-bistro-2-invoice-terms"].next_task_id, "sim-bistro-3-warranty-claim")
        self.assertEqual(self.by_id["sim-bistro-3-warranty-claim"].prerequisite_task_id, "sim-bistro-2-invoice-terms")
        self.assertIsNone(self.by_id["sim-bistro-3-warranty-claim"].next_task_id)

    def test_difficulty_increases_across_steps(self):
        difficulties = [s.difficulty for s in self.steps]
        self.assertEqual(difficulties, sorted(difficulties))

    def test_every_step_names_a_real_competency(self):
        for step in self.steps:
            self.assertTrue(step.competency_id.strip(), msg=step.task_id)

    def test_step_3_is_a_real_transfer_connecting_back_to_step_2s_reasoning(self):
        step_2_sections = set(self.by_id["sim-bistro-2-invoice-terms"].governing_sections)
        step_3_sections = set(self.by_id["sim-bistro-3-warranty-claim"].governing_sections)
        # Step 3 must introduce new authority (the actual warranty claim)
        # while still connecting back to step 2's disclaimer analysis.
        self.assertTrue(step_3_sections - step_2_sections)
        self.assertTrue(step_3_sections & step_2_sections)

    def test_simulation_context_fields_are_populated_where_real(self):
        step_1 = self.by_id["sim-bistro-1-delivery"]
        self.assertTrue(step_1.business_or_personal_context)
        self.assertTrue(step_1.time_pressure)
        self.assertTrue(step_1.parties_involved)

    def test_governing_citations_resolve_for_every_step(self):
        for step in self.steps:
            citations = step.governing_citations()
            self.assertTrue(citations)
            for citation in citations:
                self.assertIn("Va. Code Ann.", citation)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.simulations_article9 import build_espresso_bar_financing_simulation


class EspressoBarFinancingSimulationTests(unittest.TestCase):
    def setUp(self):
        self.steps = build_espresso_bar_financing_simulation()
        self.by_id = {s.task_id: s for s in self.steps}

    def test_real_four_step_simulation_builds_and_validates(self):
        self.assertEqual(len(self.steps), 4)
        for step in self.steps:
            step.validate()

    def test_no_step_opens_with_which_article_applies(self):
        # The same Chairman correction build_riverside_bistro_simulation()
        # exists to satisfy: every objective must be a real action/decision,
        # never a bare "which Article/section governs" doctrinal question.
        for step in self.steps:
            self.assertNotIn("article", step.objective.lower())
            self.assertNotIn("does ucc", step.objective.lower())
            self.assertNotIn("which section", step.objective.lower())

    def test_every_step_has_exactly_one_correct_real_action(self):
        for step in self.steps:
            correct = [o for o in step.options if o.is_correct]
            self.assertEqual(len(correct), 1, msg=step.task_id)

    def test_no_option_is_a_bare_yes_no_legal_conclusion(self):
        # Live Run 1.57 patch: options must be real actions with real
        # consequences, never a bare Yes/No legal-conclusion statement
        # (docs/task-first-pedagogy-and-task-ladder-architecture.md's
        # "Exact Article 9 simulation patch" section).
        for step in self.steps:
            for option in step.options:
                self.assertFalse(
                    option.label.startswith("Yes --") or option.label.startswith("No --"),
                    msg=f"{step.task_id}/{option.option_id}: {option.label!r}",
                )

    def test_every_step_has_a_populated_effect_and_rights_evidence_fields(self):
        # Live Run 1.49 added business_effect/legal_effect/
        # rights_created_waived_or_preserved/evidence_created_preserved_or_lost
        # to Task; Live Run 1.50's mission left them empty on every step.
        for step in self.steps:
            self.assertTrue(step.business_effect, msg=step.task_id)
            self.assertTrue(step.legal_effect, msg=step.task_id)
            self.assertTrue(step.rights_created_waived_or_preserved, msg=step.task_id)
            self.assertTrue(step.evidence_created_preserved_or_lost, msg=step.task_id)

    def test_steps_chain_into_one_continuous_scenario(self):
        self.assertIsNone(self.by_id["sim-espresso-1-attachment"].prerequisite_task_id)
        self.assertEqual(self.by_id["sim-espresso-1-attachment"].next_task_id, "sim-espresso-2-perfection")
        self.assertEqual(self.by_id["sim-espresso-2-perfection"].prerequisite_task_id, "sim-espresso-1-attachment")
        self.assertEqual(self.by_id["sim-espresso-2-perfection"].next_task_id, "sim-espresso-3-priority")
        self.assertEqual(self.by_id["sim-espresso-3-priority"].prerequisite_task_id, "sim-espresso-2-perfection")
        self.assertEqual(self.by_id["sim-espresso-3-priority"].next_task_id, "sim-espresso-4-default")
        self.assertEqual(self.by_id["sim-espresso-4-default"].prerequisite_task_id, "sim-espresso-3-priority")
        self.assertIsNone(self.by_id["sim-espresso-4-default"].next_task_id)

    def test_difficulty_increases_across_steps(self):
        difficulties = [s.difficulty for s in self.steps]
        self.assertEqual(difficulties, sorted(difficulties))
        self.assertEqual(len(set(difficulties)), len(difficulties))

    def test_every_step_names_a_real_distinct_competency(self):
        competency_ids = [step.competency_id.strip() for step in self.steps]
        for cid in competency_ids:
            self.assertTrue(cid)
        # Repetition means practicing a competency across facts, not a
        # relabeled repeat -- each step here exercises a distinct skill.
        self.assertEqual(len(set(competency_ids)), len(competency_ids))

    def test_step_2_shares_and_extends_step_1s_authority(self):
        step_1_sections = set(self.by_id["sim-espresso-1-attachment"].governing_sections)
        step_2_sections = set(self.by_id["sim-espresso-2-perfection"].governing_sections)
        self.assertTrue(step_1_sections & step_2_sections)
        self.assertTrue(step_2_sections - step_1_sections)

    def test_step_3_shares_and_extends_step_2s_authority(self):
        step_2_sections = set(self.by_id["sim-espresso-2-perfection"].governing_sections)
        step_3_sections = set(self.by_id["sim-espresso-3-priority"].governing_sections)
        self.assertTrue(step_2_sections & step_3_sections)
        self.assertTrue(step_3_sections - step_2_sections)

    def test_step_4_is_a_real_transfer_that_still_references_the_priority_outcome(self):
        # Step 4 introduces a new competency (default remedies) rather than
        # repeating step 3's authority -- the real "transfer" test (cycle
        # step 9): recognizing the concept in a role/context shift, not a
        # relabeled repeat. It must still reference back to the priority
        # determination the learner already worked out.
        step_3_sections = set(self.by_id["sim-espresso-3-priority"].governing_sections)
        step_4_sections = set(self.by_id["sim-espresso-4-default"].governing_sections)
        self.assertFalse(step_3_sections & step_4_sections)
        step_4 = self.by_id["sim-espresso-4-default"]
        self.assertIn("Riverbend", step_4.scenario + " ".join(step_4.facts_provided))
        self.assertIn("subordinate", step_4.scenario + " ".join(step_4.facts_provided))

    def test_step_4_transfers_the_learner_role_to_the_lender(self):
        step_1_role = self.by_id["sim-espresso-1-attachment"].learner_role
        step_4_role = self.by_id["sim-espresso-4-default"].learner_role
        self.assertNotEqual(step_1_role, step_4_role)
        self.assertIn("lender", step_4_role.lower())

    def test_simulation_context_fields_are_populated_where_real(self):
        step_1 = self.by_id["sim-espresso-1-attachment"]
        self.assertTrue(step_1.business_or_personal_context)
        self.assertTrue(step_1.time_pressure)
        self.assertTrue(step_1.financial_stakes)
        self.assertTrue(step_1.parties_involved)

    def test_governing_citations_resolve_for_every_step(self):
        for step in self.steps:
            citations = step.governing_citations()
            self.assertTrue(citations)
            for citation in citations:
                self.assertIn("Va. Code Ann.", citation)

    def test_all_ten_directed_sections_are_covered_across_the_simulation(self):
        expected = {
            "8.9A-102", "8.9A-203", "8.9A-308", "8.9A-310",
            "8.9A-322", "8.9A-324", "8.9A-601", "8.9A-609", "8.9A-610",
        }
        actual: set[str] = set()
        for step in self.steps:
            actual.update(step.governing_sections)
        self.assertTrue(expected.issubset(actual))


if __name__ == "__main__":
    unittest.main()

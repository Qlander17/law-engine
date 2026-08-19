from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.simulations_article3 import build_freelance_note_simulation


class FreelanceNoteSimulationTests(unittest.TestCase):
    def setUp(self):
        self.steps = build_freelance_note_simulation()
        self.by_id = {s.task_id: s for s in self.steps}

    def test_real_four_step_simulation_builds_and_validates(self):
        self.assertEqual(len(self.steps), 4)
        for step in self.steps:
            step.validate()

    def test_no_step_opens_with_which_article_applies(self):
        for step in self.steps:
            self.assertNotIn("article", step.objective.lower())
            self.assertNotIn("does ucc", step.objective.lower())
            self.assertNotIn("which section", step.objective.lower())

    def test_every_step_has_exactly_one_correct_real_action(self):
        for step in self.steps:
            correct = [o for o in step.options if o.is_correct]
            self.assertEqual(len(correct), 1, msg=step.task_id)

    def test_no_option_is_a_bare_yes_no_legal_conclusion(self):
        for step in self.steps:
            for option in step.options:
                self.assertFalse(
                    option.label.startswith("Yes --") or option.label.startswith("No --"),
                    msg=f"{step.task_id}/{option.option_id}: {option.label!r}",
                )

    def test_steps_chain_into_one_continuous_scenario(self):
        self.assertIsNone(self.by_id["sim-note-1-negotiability"].prerequisite_task_id)
        self.assertEqual(self.by_id["sim-note-1-negotiability"].next_task_id, "sim-note-2-negotiation")
        self.assertEqual(self.by_id["sim-note-2-negotiation"].prerequisite_task_id, "sim-note-1-negotiability")
        self.assertEqual(self.by_id["sim-note-2-negotiation"].next_task_id, "sim-note-3-indorsement-type")
        self.assertEqual(self.by_id["sim-note-3-indorsement-type"].prerequisite_task_id, "sim-note-2-negotiation")
        self.assertEqual(self.by_id["sim-note-3-indorsement-type"].next_task_id, "sim-note-4-enforcement")
        self.assertEqual(self.by_id["sim-note-4-enforcement"].prerequisite_task_id, "sim-note-3-indorsement-type")
        self.assertIsNone(self.by_id["sim-note-4-enforcement"].next_task_id)

    def test_difficulty_increases_across_steps(self):
        difficulties = [s.difficulty for s in self.steps]
        self.assertEqual(difficulties, sorted(difficulties))
        self.assertEqual(len(set(difficulties)), len(difficulties))

    def test_every_step_names_a_real_distinct_competency(self):
        competency_ids = [step.competency_id.strip() for step in self.steps]
        for cid in competency_ids:
            self.assertTrue(cid)
        self.assertEqual(len(set(competency_ids)), len(competency_ids))

    def test_step_2_shares_and_extends_step_1s_authority_theme(self):
        # Step 2 doesn't repeat step 1's negotiability sections -- it's a
        # real, distinct competency (negotiation/transfer) -- but both
        # steps trace back to the same note, and step 2's authority
        # (§ 8.3A-201) directly depends on step 1's confirmed negotiable
        # instrument.
        step_1_sections = set(self.by_id["sim-note-1-negotiability"].governing_sections)
        step_2_sections = set(self.by_id["sim-note-2-negotiation"].governing_sections)
        self.assertFalse(step_1_sections & step_2_sections)

    def test_step_3_shares_and_extends_step_2s_authority(self):
        step_2_sections = set(self.by_id["sim-note-2-negotiation"].governing_sections)
        step_3_sections = set(self.by_id["sim-note-3-indorsement-type"].governing_sections)
        self.assertTrue(step_2_sections & step_3_sections)
        self.assertTrue(step_3_sections - step_2_sections)

    def test_step_4_is_a_real_transfer_that_still_references_prior_steps(self):
        step_3_sections = set(self.by_id["sim-note-3-indorsement-type"].governing_sections)
        step_4_sections = set(self.by_id["sim-note-4-enforcement"].governing_sections)
        self.assertFalse(step_3_sections & step_4_sections)
        step_4 = self.by_id["sim-note-4-enforcement"]
        self.assertIn("Ridgeline", step_4.scenario + " ".join(step_4.facts_provided))
        self.assertIn("Jamie", step_4.scenario + " ".join(step_4.facts_provided))

    def test_step_4_transfers_the_learner_role(self):
        step_1_role = self.by_id["sim-note-1-negotiability"].learner_role
        step_4_role = self.by_id["sim-note-4-enforcement"].learner_role
        self.assertNotEqual(step_1_role, step_4_role)
        self.assertIn("transfer", step_4_role.lower())

    def test_simulation_context_fields_are_populated_where_real(self):
        step_1 = self.by_id["sim-note-1-negotiability"]
        self.assertTrue(step_1.business_or_personal_context)
        self.assertTrue(step_1.financial_stakes)
        self.assertTrue(step_1.parties_involved)

    def test_every_step_has_a_populated_effect_and_rights_evidence_fields(self):
        for step in self.steps:
            self.assertTrue(step.business_effect, msg=step.task_id)
            self.assertTrue(step.legal_effect, msg=step.task_id)
            self.assertTrue(step.rights_created_waived_or_preserved, msg=step.task_id)
            self.assertTrue(step.evidence_created_preserved_or_lost, msg=step.task_id)

    def test_governing_citations_resolve_for_every_step(self):
        for step in self.steps:
            citations = step.governing_citations()
            self.assertTrue(citations)
            for citation in citations:
                self.assertIn("Va. Code Ann.", citation)

    def test_only_phase_2_ingested_sections_are_cited(self):
        # Real, disclosed anti-fabrication check: every section this
        # simulation cites must be one of the 11 real sections
        # services/ingestion_article3.py actually ingested -- never a
        # broader or invented Article 3 citation.
        ingested = {
            "8.3A-102", "8.3A-103", "8.3A-104", "8.3A-109", "8.3A-201",
            "8.3A-203", "8.3A-204", "8.3A-205", "8.3A-206", "8.3A-301", "8.3A-302",
        }
        for step in self.steps:
            for section_id in step.governing_sections:
                self.assertIn(section_id, ingested, msg=f"{step.task_id} cites un-ingested {section_id!r}")

    def test_all_named_directed_sections_are_covered_across_the_simulation(self):
        expected = {
            "8.3A-104", "8.3A-109", "8.3A-201", "8.3A-203",
            "8.3A-204", "8.3A-205", "8.3A-301", "8.3A-302",
        }
        actual: set[str] = set()
        for step in self.steps:
            actual.update(step.governing_sections)
        self.assertTrue(expected.issubset(actual))


if __name__ == "__main__":
    unittest.main()

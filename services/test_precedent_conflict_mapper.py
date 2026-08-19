from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import legal_proof_graph as lpg
from services import precedent_conflict_mapper as pcm


class ClassifyPrecedentConflictTests(unittest.TestCase):
    """Live Run 1.60, Mission 8, Phase 6 -- real tests exercising all four
    required output categories
    (docs/law-engine-precedent-conflict-thesis.md §3) against realistic
    input variations on the real flagship proof graph."""

    def setUp(self) -> None:
        self.graph = lpg.build_promissory_note_enforcement_proof_graph()

    def test_florida_matching_facts_is_high_confidence(self) -> None:
        fact_pattern = pcm.NewFactPattern(
            jurisdiction="Florida",
            proceeding_type=pcm.ProceedingType.JUDICIAL_FORECLOSURE_COMPLAINT,
            note_indorsed_in_blank=True,
            party_in_possession_at_relevant_time=True,
            suing_as_servicer_without_proven_authority=False,
        )
        result = pcm.classify_precedent_conflict(self.graph, fact_pattern)
        self.assertEqual(result.category, pcm.PrecedentConflictCategory.HIGH_CONFIDENCE_CONTROLLING_AUTHORITY)
        self.assertIn("178 So. 3d 62", result.controlling_or_persuasive_citations[0])
        self.assertIsNone(result.distinguishing_fact)

    def test_north_carolina_matching_facts_is_high_confidence(self) -> None:
        fact_pattern = pcm.NewFactPattern(
            jurisdiction="North Carolina",
            proceeding_type=pcm.ProceedingType.POWER_OF_SALE_HEARING,
            note_indorsed_in_blank=True,
            party_in_possession_at_relevant_time=True,
        )
        result = pcm.classify_precedent_conflict(self.graph, fact_pattern)
        self.assertEqual(result.category, pcm.PrecedentConflictCategory.HIGH_CONFIDENCE_CONTROLLING_AUTHORITY)
        self.assertIn("244 N.C. App. 583", result.controlling_or_persuasive_citations[0])

    def test_note_not_indorsed_in_blank_is_fact_sensitive(self) -> None:
        fact_pattern = pcm.NewFactPattern(
            jurisdiction="Florida",
            proceeding_type=pcm.ProceedingType.JUDICIAL_FORECLOSURE_COMPLAINT,
            note_indorsed_in_blank=False,
            party_in_possession_at_relevant_time=True,
        )
        result = pcm.classify_precedent_conflict(self.graph, fact_pattern)
        self.assertEqual(result.category, pcm.PrecedentConflictCategory.FACT_SENSITIVE_DISTINGUISHABLE)
        self.assertIsNotNone(result.distinguishing_fact)
        self.assertIn("not indorsed in blank", result.distinguishing_fact)

    def test_florida_unproven_servicer_authority_is_fact_sensitive(self) -> None:
        # The real, disclosed nuance Phase 3 found in Rodriguez's actual
        # holding (see services/ingestion_case_law.py's own notes).
        fact_pattern = pcm.NewFactPattern(
            jurisdiction="Florida",
            proceeding_type=pcm.ProceedingType.JUDICIAL_FORECLOSURE_COMPLAINT,
            note_indorsed_in_blank=True,
            party_in_possession_at_relevant_time=True,
            suing_as_servicer_without_proven_authority=True,
        )
        result = pcm.classify_precedent_conflict(self.graph, fact_pattern)
        self.assertEqual(result.category, pcm.PrecedentConflictCategory.FACT_SENSITIVE_DISTINGUISHABLE)
        self.assertIn("servicer", result.distinguishing_fact)

    def test_north_carolina_no_possession_at_hearing_is_fact_sensitive(self) -> None:
        fact_pattern = pcm.NewFactPattern(
            jurisdiction="North Carolina",
            proceeding_type=pcm.ProceedingType.POWER_OF_SALE_HEARING,
            note_indorsed_in_blank=True,
            party_in_possession_at_relevant_time=False,
        )
        result = pcm.classify_precedent_conflict(self.graph, fact_pattern)
        self.assertEqual(result.category, pcm.PrecedentConflictCategory.FACT_SENSITIVE_DISTINGUISHABLE)
        self.assertIn("possession", result.distinguishing_fact)

    def test_known_jurisdiction_mismatched_proceeding_type_is_fact_sensitive(self) -> None:
        fact_pattern = pcm.NewFactPattern(
            jurisdiction="Florida",
            proceeding_type=pcm.ProceedingType.POWER_OF_SALE_HEARING,
            note_indorsed_in_blank=True,
            party_in_possession_at_relevant_time=True,
        )
        result = pcm.classify_precedent_conflict(self.graph, fact_pattern)
        self.assertEqual(result.category, pcm.PrecedentConflictCategory.FACT_SENSITIVE_DISTINGUISHABLE)

    def test_third_jurisdiction_known_proceeding_type_is_persuasive_disagreement(self) -> None:
        fact_pattern = pcm.NewFactPattern(
            jurisdiction="Georgia",
            proceeding_type=pcm.ProceedingType.JUDICIAL_FORECLOSURE_COMPLAINT,
            note_indorsed_in_blank=True,
            party_in_possession_at_relevant_time=True,
        )
        result = pcm.classify_precedent_conflict(self.graph, fact_pattern)
        self.assertEqual(result.category, pcm.PrecedentConflictCategory.PERSUASIVE_DISAGREEMENT)
        self.assertEqual(len(result.controlling_or_persuasive_citations), 2)

    def test_third_jurisdiction_undetermined_proceeding_is_genuine_uncertainty(self) -> None:
        fact_pattern = pcm.NewFactPattern(
            jurisdiction="Georgia",
            proceeding_type=pcm.ProceedingType.UNDETERMINED_OR_HYBRID,
            note_indorsed_in_blank=True,
            party_in_possession_at_relevant_time=True,
        )
        result = pcm.classify_precedent_conflict(self.graph, fact_pattern)
        self.assertEqual(result.category, pcm.PrecedentConflictCategory.GENUINE_UNRESOLVED_UNCERTAINTY)
        self.assertEqual(len(result.controlling_or_persuasive_citations), 2)
        self.assertIn("unsettled", result.explanation)

    def test_every_assessment_carries_the_real_disclaimer(self) -> None:
        fact_pattern = pcm.NewFactPattern(
            jurisdiction="Georgia",
            proceeding_type=pcm.ProceedingType.UNDETERMINED_OR_HYBRID,
            note_indorsed_in_blank=True,
            party_in_possession_at_relevant_time=True,
        )
        result = pcm.classify_precedent_conflict(self.graph, fact_pattern)
        self.assertIn("not personalized legal advice", result.disclaimer)

    def test_to_dict_round_trips(self) -> None:
        fact_pattern = pcm.NewFactPattern(
            jurisdiction="Florida",
            proceeding_type=pcm.ProceedingType.JUDICIAL_FORECLOSURE_COMPLAINT,
            note_indorsed_in_blank=True,
            party_in_possession_at_relevant_time=True,
        )
        result = pcm.classify_precedent_conflict(self.graph, fact_pattern)
        d = result.to_dict()
        self.assertEqual(d["category"], "HIGH_CONFIDENCE_CONTROLLING_AUTHORITY")
        self.assertIn("disclaimer", d)


if __name__ == "__main__":
    unittest.main()

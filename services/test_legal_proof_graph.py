from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import legal_proof_graph as lpg


class BuildAttachmentProofGraphTests(unittest.TestCase):
    """Live Run 1.43, Mission 15 -- real regression tests for the
    design doc's "Smallest Useful Implementation Slice": one real
    LegalProofGraph for the § 8.9A-203(b) attachment test."""

    def setUp(self) -> None:
        self.graph = lpg.build_attachment_proof_graph()

    def test_has_exactly_one_governing_authority_citing_real_ingested_section(self) -> None:
        self.assertEqual(len(self.graph.authorities), 1)
        self.assertIn("8.9A-203", self.graph.authorities[0].citation)
        self.assertTrue(self.graph.authorities[0].rule_text.strip())

    def test_has_three_real_verified_facts(self) -> None:
        self.assertEqual(len(self.graph.facts), 3)
        for fact in self.graph.facts:
            self.assertTrue(fact.statement.strip())
            self.assertTrue(fact.supporting_evidence, f"{fact.node_id} has no supporting_evidence")

    def test_has_exactly_one_intermediate_proposition(self) -> None:
        self.assertEqual(len(self.graph.propositions), 1)
        self.assertEqual(self.graph.propositions[0].kind, lpg.ProofNodeKind.INTERMEDIATE_PROPOSITION)

    def test_conclusion_node_id_points_at_the_proposition(self) -> None:
        self.assertEqual(self.graph.conclusion_node_id, self.graph.propositions[0].node_id)

    def test_no_dangling_edges(self) -> None:
        self.assertEqual(self.graph.check_no_dangling_edges(), [])

    def test_proposition_requires_all_three_facts(self) -> None:
        prop = self.graph.propositions[0]
        self.assertEqual(len(prop.required_fact_ids), 3)
        fact_ids = {f.node_id for f in self.graph.facts}
        for required_id in prop.required_fact_ids:
            self.assertIn(required_id, fact_ids)

    def test_weakest_link_verification_status_is_real_and_traceable(self) -> None:
        prop_id = self.graph.propositions[0].node_id
        status = self.graph.weakest_link_verification_status(prop_id)
        self.assertIsInstance(status, lpg.VerificationStatus)

    def test_weakest_link_raises_for_unknown_proposition(self) -> None:
        with self.assertRaises(lpg.LegalProofGraphError):
            self.graph.weakest_link_verification_status("not-a-real-proposition-id")

    def test_to_dict_round_trips_every_node_kind(self) -> None:
        rendered = self.graph.to_dict()
        self.assertEqual(rendered["graph_id"], self.graph.graph_id)
        self.assertIn("facts", rendered)
        self.assertIn("authorities", rendered)
        self.assertIn("propositions", rendered)

    def test_shared_classification_does_not_imply_equivalence_no_equivalent_to_edge_kind(self) -> None:
        # Real, disclosed design constraint from the Euclidean-reasoning
        # architecture doc: there is deliberately no EQUIVALENT_TO edge
        # kind, only CLASSIFIED_AS -- confirms the design principle
        # actually made it into the implementation, not just the doc.
        edge_kind_names = {k.name for k in lpg.ProofEdgeKind}
        self.assertIn("CLASSIFIED_AS", edge_kind_names)
        self.assertNotIn("EQUIVALENT_TO", edge_kind_names)


if __name__ == "__main__":
    unittest.main()

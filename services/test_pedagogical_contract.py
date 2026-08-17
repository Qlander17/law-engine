from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import pedagogical_contract as pc
from services.models import (
    AuthorityType,
    ConfidenceLabel,
    PedagogicalSubjectKind,
    VerificationStatus,
)
from services.retrieval import get_section


class ImpliedWarrantyOfMerchantabilityContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = pc.build_implied_warranty_of_merchantability_contract()

    def test_citation_matches_real_ingested_section(self) -> None:
        section = get_section("8.2-314")
        self.assertIsNotNone(section)
        self.assertEqual(self.contract.authority_citation, section["citation"])
        self.assertEqual(self.contract.section_id, "8.2-314")
        self.assertEqual(self.contract.source_document_id, section["source_document_id"])

    def test_governing_text_excerpt_is_the_real_ingested_paragraph(self) -> None:
        section = get_section("8.2-314")
        self.assertEqual(self.contract.governing_text_excerpt, section["paragraphs"][0])
        self.assertIn("merchantable", self.contract.governing_text_excerpt)

    def test_is_grounded_as_source_verified_not_invented(self) -> None:
        self.assertEqual(self.contract.authority_type, AuthorityType.STATUTE)
        self.assertEqual(self.contract.verification_status, VerificationStatus.SOURCE_VERIFIED)
        self.assertEqual(self.contract.confidence_label, ConfidenceLabel.VERIFIED)
        self.assertEqual(self.contract.subject_kind, PedagogicalSubjectKind.RULE)
        self.assertEqual(self.contract.jurisdiction, "Commonwealth of Virginia")

    def test_every_fact_sensitivity_citation_traces_to_a_real_or_derived_section(self) -> None:
        for note in self.contract.fact_sensitivity:
            self.assertIsNotNone(note.citation, f"fact-sensitivity note {note.changed_fact!r} has no citation")
            # every note in this builder cites either the real ingested
            # 8.2-314 section or 8.2-316, which is derived from 8.2-314's
            # own ingested cross_references/paragraph text -- never an
            # invented section number.
            self.assertIn("8.2-31", note.citation)

    def test_metaphor_is_present_and_labeled_pedagogical_only(self) -> None:
        self.assertIsNotNone(self.contract.metaphor)
        self.assertTrue(self.contract.metaphor.is_pedagogical_only)
        self.assertIn("not a legal rule", self.contract.metaphor.disclaimer)

    def test_metaphor_never_overwrites_governing_text(self) -> None:
        self.assertNotEqual(self.contract.metaphor.illustration, self.contract.governing_text_excerpt)
        self.assertNotIn("sandwich", self.contract.governing_text_excerpt.lower())
        self.assertIn("merchantable", self.contract.governing_text_excerpt.lower())

    def test_to_dict_round_trips(self) -> None:
        d = self.contract.to_dict()
        self.assertEqual(d["contract_id"], "implied-warranty-of-merchantability-va-8.2-314")
        self.assertEqual(d["authority_citation"], "Va. Code Ann. § 8.2-314")
        self.assertEqual(d["subject_kind"], "RULE")
        self.assertEqual(d["verification_status"], "SOURCE_VERIFIED")
        self.assertEqual(d["confidence_label"], "VERIFIED")
        self.assertTrue(d["metaphor"]["is_pedagogical_only"])
        self.assertGreater(len(d["how_to_recognize"]), 0)
        self.assertGreater(len(d["what_can_go_wrong"]), 0)
        self.assertGreater(len(d["commonly_confused_with"]), 0)
        self.assertGreater(len(d["fact_sensitivity"]), 0)

    def test_require_section_raises_for_uningested_section(self) -> None:
        with self.assertRaises(pc.PedagogicalContractError):
            pc._require_section("not-a-real-section-id")


if __name__ == "__main__":
    unittest.main()

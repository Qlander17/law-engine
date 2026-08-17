from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import asset_intelligence as ai
from services.retrieval import get_section


class AssetProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profiles = ai.build_all_profiles()

    def test_at_least_five_profiles_across_distinct_asset_types(self) -> None:
        self.assertGreaterEqual(len(self.profiles), 5)
        asset_types = {p.asset_type for p in self.profiles}
        self.assertEqual(len(asset_types), len(self.profiles), "expected distinct AssetType values across profiles")

    def test_every_profile_with_a_citation_traces_to_a_real_ingested_section(self) -> None:
        for profile in self.profiles:
            if profile.citation is None:
                continue
            self.assertIsNotNone(
                profile.section_id,
                f"{profile.asset_type} has a citation but no section_id",
            )
            section = get_section(profile.section_id)
            self.assertIsNotNone(
                section, f"{profile.asset_type} cites unknown section {profile.section_id!r}"
            )
            self.assertEqual(
                section["citation"], profile.citation,
                f"{profile.asset_type}'s citation does not match the real ingested section's citation",
            )

    def test_every_ungrounded_profile_discloses_it_explicitly(self) -> None:
        for profile in self.profiles:
            if profile.citation is None:
                self.assertTrue(
                    profile.citation_grounding_note,
                    f"{profile.asset_type} has no citation and no grounding disclosure",
                )
                self.assertIn("not yet", profile.citation_grounding_note.lower())

    def test_real_property_profile_is_not_security_interest_eligible(self) -> None:
        real_property = next(p for p in self.profiles if p.asset_type == ai.AssetType.REAL_PROPERTY)
        self.assertFalse(real_property.security_interest_eligible)
        self.assertIsNotNone(real_property.perfection_method)
        self.assertIn("not applicable", real_property.perfection_method.lower())

    def test_real_property_profile_explicitly_notes_non_ucc_contrast(self) -> None:
        real_property = next(p for p in self.profiles if p.asset_type == ai.AssetType.REAL_PROPERTY)
        combined_text = " ".join(
            [
                real_property.legal_classification,
                real_property.perfection_method or "",
                real_property.priority_notes,
                " ".join(real_property.governing_bodies_of_law),
                " ".join(real_property.common_mistakes),
            ]
        ).lower()
        self.assertIn("not", combined_text)
        self.assertTrue(
            "article 9" in combined_text and "article 2" in combined_text,
            "expected the REAL_PROPERTY profile to explicitly name both UCC Article 2 and Article 9 as inapplicable",
        )
        self.assertNotIn("ucc article 9", " ".join(real_property.governing_bodies_of_law).lower())
        self.assertNotIn("ucc article 2", " ".join(real_property.governing_bodies_of_law).lower())

    def test_real_property_profile_grounded_in_real_goods_definition_for_contrast(self) -> None:
        real_property = next(p for p in self.profiles if p.asset_type == ai.AssetType.REAL_PROPERTY)
        section = get_section("8.2-105")
        self.assertIsNotNone(section)
        self.assertEqual(real_property.citation, section["citation"])

    def test_consumer_goods_profile_grounded_in_real_goods_definition(self) -> None:
        consumer_goods = next(p for p in self.profiles if p.asset_type == ai.AssetType.CONSUMER_GOODS)
        section = get_section("8.2-105")
        self.assertEqual(consumer_goods.citation, section["citation"])
        self.assertEqual(consumer_goods.section_id, "8.2-105")

    def test_accounts_receivable_profile_is_ungrounded_article_9(self) -> None:
        accounts = next(p for p in self.profiles if p.asset_type == ai.AssetType.ACCOUNTS_RECEIVABLE)
        self.assertIsNone(accounts.citation)
        self.assertIsNone(accounts.section_id)
        self.assertIn("article 9", accounts.citation_grounding_note.lower())

    def test_build_all_profiles_raises_on_missing_section(self) -> None:
        original = ai.get_section
        try:
            ai.get_section = lambda section_id: None
            with self.assertRaises(ai.AssetIntelligenceError):
                ai.build_consumer_goods_profile()
        finally:
            ai.get_section = original

    def test_to_dict_round_trips_consumer_goods_profile(self) -> None:
        consumer_goods = next(p for p in self.profiles if p.asset_type == ai.AssetType.CONSUMER_GOODS)
        d = consumer_goods.to_dict()
        self.assertEqual(d["asset_type"], "CONSUMER_GOODS")
        self.assertEqual(d["security_interest_eligible"], True)
        self.assertEqual(d["citation"], consumer_goods.citation)
        self.assertIsInstance(d["evidence_of_ownership"], list)
        self.assertIsInstance(d["governing_bodies_of_law"], list)

    def test_to_dict_round_trips_real_property_profile(self) -> None:
        real_property = next(p for p in self.profiles if p.asset_type == ai.AssetType.REAL_PROPERTY)
        d = real_property.to_dict()
        self.assertEqual(d["asset_type"], "REAL_PROPERTY")
        self.assertEqual(d["security_interest_eligible"], False)
        self.assertEqual(d["perfection_method"], real_property.perfection_method)
        self.assertEqual(d["common_mistakes"], real_property.common_mistakes)

    def test_all_profiles_have_non_empty_required_narrative_fields(self) -> None:
        for profile in self.profiles:
            self.assertTrue(profile.legal_classification)
            self.assertTrue(profile.title_concept)
            self.assertTrue(profile.possession_concept)
            self.assertTrue(profile.control_concept)
            self.assertTrue(profile.transferability)
            self.assertTrue(profile.assignability)
            self.assertTrue(profile.priority_notes)
            self.assertTrue(profile.record_retention_notes)
            self.assertTrue(profile.jurisdiction)
            self.assertGreater(len(profile.evidence_of_ownership), 0)
            self.assertGreater(len(profile.controlling_documents), 0)
            self.assertGreater(len(profile.governing_bodies_of_law), 0)
            self.assertGreater(len(profile.common_mistakes), 0)


if __name__ == "__main__":
    unittest.main()

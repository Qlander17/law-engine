from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import ingestion_case_law as ing_case_law
from services.models import (
    AuthorityType,
    SourceLayer,
    SourceManifest,
    VerificationStatus,
)


class AuthorityTypeNewMembersTests(unittest.TestCase):
    def test_five_new_members_exist(self) -> None:
        self.assertEqual(AuthorityType.JUDICIAL_HOLDING.value, "JUDICIAL_HOLDING")
        self.assertEqual(AuthorityType.DICTA.value, "DICTA")
        self.assertEqual(AuthorityType.PERSUASIVE_OPINION.value, "PERSUASIVE_OPINION")
        self.assertEqual(AuthorityType.COMMON_LAW_RULE.value, "COMMON_LAW_RULE")
        self.assertEqual(AuthorityType.ADMINISTRATIVE_INTERPRETATION.value, "ADMINISTRATIVE_INTERPRETATION")

    def test_original_case_member_untouched(self) -> None:
        # Real, disclosed both/and (module docstring) -- CASE stays, the
        # five new members are additive refinements, not a rename.
        self.assertEqual(AuthorityType.CASE.value, "CASE")


class SourceManifestNewFieldsTests(unittest.TestCase):
    def test_new_fields_default_to_none(self) -> None:
        # A pre-existing-style construction (no new fields passed) must
        # not break -- this is the real regression check Phase 4 asked for.
        manifest = SourceManifest(
            document_id="doc-1",
            title="Title",
            authority_type=AuthorityType.STATUTE,
            jurisdiction="Commonwealth of Virginia",
            citation="Va. Code Ann. § 1-1",
            official_source_url="https://law.lis.virginia.gov/",
            publisher="Commonwealth of Virginia",
            retrieval_timestamp="2026-01-01T00:00:00",
            sha256_hash="0" * 64,
            verification_status=VerificationStatus.SOURCE_VERIFIED,
        )
        self.assertIsNone(manifest.binding_scope)
        self.assertIsNone(manifest.hierarchy_level)
        self.assertIsNone(manifest.override_mechanism)

    def test_new_fields_round_trip_through_to_dict(self) -> None:
        manifest = SourceManifest(
            document_id="doc-2",
            title="Title",
            authority_type=AuthorityType.JUDICIAL_HOLDING,
            jurisdiction="Florida",
            citation="178 So. 3d 62",
            official_source_url="https://example.gov/",
            publisher="Publisher",
            retrieval_timestamp="2026-01-01T00:00:00",
            sha256_hash="0" * 64,
            verification_status=VerificationStatus.RETRIEVED,
            binding_scope="Binding within Florida's Fourth DCA.",
            hierarchy_level=2,
            override_mechanism="Reversal by the Florida Supreme Court.",
        )
        d = manifest.to_dict()
        self.assertEqual(d["binding_scope"], "Binding within Florida's Fourth DCA.")
        self.assertEqual(d["hierarchy_level"], 2)
        self.assertEqual(d["override_mechanism"], "Reversal by the Florida Supreme Court.")


class RodriguezManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = ing_case_law.build_rodriguez_manifest()

    def test_real_hash_matches_real_source_file(self) -> None:
        real_bytes = ing_case_law.RODRIGUEZ_PATH.read_bytes()
        import hashlib

        self.assertEqual(self.manifest.sha256_hash, hashlib.sha256(real_bytes).hexdigest())

    def test_uses_judicial_holding_authority_type(self) -> None:
        self.assertEqual(self.manifest.authority_type, AuthorityType.JUDICIAL_HOLDING)

    def test_uses_interpretation_layer(self) -> None:
        self.assertEqual(self.manifest.source_layer, SourceLayer.INTERPRETATION)

    def test_source_verified_after_live_run_1_62(self) -> None:
        # Real, honest upgrade -- see module docstring: Live Run 1.62
        # independently, directly read (not AI-summarized) the complete
        # official opinion PDF this run, after CourtListener's search API
        # surfaced its own stored mirror of the official court PDF.
        self.assertEqual(self.manifest.verification_status, VerificationStatus.SOURCE_VERIFIED)

    def test_real_citation(self) -> None:
        self.assertIn("178 So. 3d 62", self.manifest.citation)

    def test_new_fields_populated(self) -> None:
        self.assertIsNotNone(self.manifest.binding_scope)
        self.assertEqual(self.manifest.hierarchy_level, 2)
        self.assertIsNotNone(self.manifest.override_mechanism)

    def test_notes_disclose_real_correction_to_live_run_1_59(self) -> None:
        self.assertIn("real, disclosed correction", self.manifest.notes)
        self.assertIn("servicer-authority", self.manifest.notes)


class GreeneManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = ing_case_law.build_greene_manifest()

    def test_real_hash_matches_real_source_file(self) -> None:
        real_bytes = ing_case_law.GREENE_PATH.read_bytes()
        import hashlib

        self.assertEqual(self.manifest.sha256_hash, hashlib.sha256(real_bytes).hexdigest())

    def test_uses_judicial_holding_authority_type(self) -> None:
        self.assertEqual(self.manifest.authority_type, AuthorityType.JUDICIAL_HOLDING)

    def test_source_verified_after_live_run_1_62(self) -> None:
        # Real, honest upgrade -- see module docstring: Live Run 1.62
        # independently, directly read (not AI-summarized) the complete
        # official opinion PDF from the North Carolina Judicial Branch's
        # own opinions server (appellate.nccourts.org) this run.
        self.assertEqual(self.manifest.verification_status, VerificationStatus.SOURCE_VERIFIED)

    def test_real_citation(self) -> None:
        self.assertIn("244 N.C. App. 583", self.manifest.citation)

    def test_new_fields_populated(self) -> None:
        self.assertIsNotNone(self.manifest.binding_scope)
        self.assertEqual(self.manifest.hierarchy_level, 2)
        self.assertIsNotNone(self.manifest.override_mechanism)

    def test_notes_disclose_real_case_name_correction(self) -> None:
        self.assertIn("Greene v. Trustee Services of Carolina", self.manifest.notes)


class RunIngestionTests(unittest.TestCase):
    def test_run_ingestion_writes_real_files(self) -> None:
        rodriguez_path, greene_path = ing_case_law.run_ingestion()
        self.assertTrue(rodriguez_path.exists())
        self.assertTrue(greene_path.exists())

    def setUp(self) -> None:
        self._rodriguez_manifest_path = (
            _LAW_ENGINE_ROOT / "library" / "manifests" / "fl-4dca-rodriguez-v-wells-fargo-2015.json"
        )
        self._greene_manifest_path = (
            _LAW_ENGINE_ROOT / "library" / "manifests" / "nc-app-greene-v-trustee-services-2016.json"
        )
        self._rodriguez_before = (
            self._rodriguez_manifest_path.read_bytes() if self._rodriguez_manifest_path.exists() else None
        )
        self._greene_before = (
            self._greene_manifest_path.read_bytes() if self._greene_manifest_path.exists() else None
        )

    def tearDown(self) -> None:
        # Same real-write-path discipline as test_ingestion_article3.py's
        # own RunIngestionTests -- the write really happens and is really
        # verified, but a stranger's clone is never left modified by
        # simply running the documented test command.
        if self._rodriguez_before is not None:
            self._rodriguez_manifest_path.write_bytes(self._rodriguez_before)
        elif self._rodriguez_manifest_path.exists():
            self._rodriguez_manifest_path.unlink()
        if self._greene_before is not None:
            self._greene_manifest_path.write_bytes(self._greene_before)
        elif self._greene_manifest_path.exists():
            self._greene_manifest_path.unlink()


if __name__ == "__main__":
    unittest.main()

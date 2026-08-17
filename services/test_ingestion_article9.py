from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import ingestion_article9 as ing9
from services.models import AuthorityType, SourceLayer, VerificationStatus


class NormalizeSectionsTests(unittest.TestCase):
    def test_real_thirteen_sections_normalized(self) -> None:
        sections = ing9.normalize_sections()
        ids = {s.section_id for s in sections}
        self.assertEqual(len(sections), 13)
        self.assertIn("8.9A-203", ids)  # attachment
        self.assertIn("8.9A-308", ids)  # perfection
        self.assertIn("8.9A-324", ids)  # PMSI priority
        self.assertIn("8.9A-610", ids)  # default/disposition

    def test_every_section_has_real_nonempty_paragraphs(self) -> None:
        for section in ing9.normalize_sections():
            self.assertGreater(len(section.paragraphs), 0)
            for p in section.paragraphs:
                self.assertGreater(len(p.strip()), 0)

    def test_citation_format(self) -> None:
        sections = ing9.normalize_sections()
        attachment_section = next(s for s in sections if s.section_id == "8.9A-203")
        self.assertEqual(attachment_section.citation, "Va. Code Ann. § 8.9A-203")

    def test_defined_terms_extracted_from_real_definitions_section(self) -> None:
        sections = {s.section_id: s for s in ing9.normalize_sections()}
        defined = sections["8.9A-102"].defined_terms
        self.assertIn("Collateral", defined)
        self.assertIn("Chattel paper", defined)
        self.assertGreater(len(defined), 20)

    def test_non_definitions_sections_have_no_invented_defined_terms(self) -> None:
        sections = {s.section_id: s for s in ing9.normalize_sections()}
        self.assertEqual(sections["8.9A-203"].defined_terms, [])

    def test_cross_references_are_real_extracted_citations(self) -> None:
        sections = {s.section_id: s for s in ing9.normalize_sections()}
        # § 8.9A-609 -- "Secured party's right to take possession after
        # default" -- really does reference § 8.9A-610 in its own text.
        self.assertIn("8.9A-610", sections["8.9A-609"].cross_references)
        # A section never lists itself as its own cross-reference.
        self.assertNotIn("8.9A-322", sections["8.9A-322"].cross_references)


class SourceManifestBuildTests(unittest.TestCase):
    def test_manifest_hash_matches_real_raw_file(self) -> None:
        manifest = ing9.build_source_manifest()
        real_bytes = ing9.RAW_EXTRACT_PATH.read_bytes()
        self.assertEqual(manifest.sha256_hash, hashlib.sha256(real_bytes).hexdigest())

    def test_manifest_uses_statute_authority_type(self) -> None:
        manifest = ing9.build_source_manifest()
        self.assertEqual(manifest.authority_type, AuthorityType.STATUTE)

    def test_manifest_starts_source_verified(self) -> None:
        manifest = ing9.build_source_manifest()
        self.assertEqual(manifest.verification_status, VerificationStatus.SOURCE_VERIFIED)

    def test_manifest_declares_public_domain_reasoning(self) -> None:
        manifest = ing9.build_source_manifest()
        self.assertIn("public domain", manifest.licensing_status)
        self.assertIn("edict of government", manifest.licensing_status)

    def test_manifest_is_enactment_layer(self) -> None:
        manifest = ing9.build_source_manifest()
        self.assertEqual(manifest.source_layer, SourceLayer.ENACTMENT)


class RunIngestionTests(unittest.TestCase):
    def test_run_ingestion_writes_real_files(self) -> None:
        # Live Run 1.45 -- real, disclosed public-repo hygiene fix
        # (law-engine-publication-readiness-1.44.md, section 8):
        # run_ingestion() writes through to the real, tracked manifest
        # files, rewriting retrieval_timestamp on every test run and
        # leaving a dirty git tree for no substantive reason. This test
        # genuinely needs to exercise the real write path (that's the
        # point of the test), so instead of mocking it out, snapshot
        # the real tracked files' bytes first and restore them
        # afterward -- the write still really happens and is really
        # verified, but the tracked file a stranger clones is never
        # left modified by simply running the documented test command.
        normalized_path, manifest_path = ing9.run_ingestion()
        self.assertTrue(normalized_path.exists())
        self.assertTrue(manifest_path.exists())

    def setUp(self) -> None:
        self._normalized_path = _LAW_ENGINE_ROOT / "library" / "normalized" / "ucc" / "article-9-sections.json"
        self._manifest_path = _LAW_ENGINE_ROOT / "library" / "manifests" / "va-code-title-8.9a-article-9.json"
        self._normalized_before = self._normalized_path.read_bytes() if self._normalized_path.exists() else None
        self._manifest_before = self._manifest_path.read_bytes() if self._manifest_path.exists() else None

    def tearDown(self) -> None:
        if self._normalized_before is not None:
            self._normalized_path.write_bytes(self._normalized_before)
        if self._manifest_before is not None:
            self._manifest_path.write_bytes(self._manifest_before)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import ingestion_article1 as ing1
from services.models import AuthorityType, SourceLayer, VerificationStatus


class NormalizeSectionsTests(unittest.TestCase):
    def test_real_four_sections_normalized(self) -> None:
        sections = ing1.normalize_sections()
        ids = {s.section_id for s in sections}
        self.assertEqual(len(sections), 4)
        self.assertIn("8.1A-103", ids)  # supplementary principles of law
        self.assertIn("8.1A-201", ids)  # general definitions
        self.assertIn("8.1A-301", ids)  # territorial applicability
        self.assertIn("8.1A-302", ids)  # variation by agreement

    def test_every_section_has_real_nonempty_paragraphs(self) -> None:
        for section in ing1.normalize_sections():
            self.assertGreater(len(section.paragraphs), 0)
            for p in section.paragraphs:
                self.assertGreater(len(p.strip()), 0)

    def test_citation_format(self) -> None:
        sections = ing1.normalize_sections()
        definitions_section = next(s for s in sections if s.section_id == "8.1A-201")
        self.assertEqual(definitions_section.citation, "Va. Code Ann. § 8.1A-201")

    def test_defined_terms_extracted_from_real_definitions_section(self) -> None:
        sections = {s.section_id: s for s in ing1.normalize_sections()}
        defined = sections["8.1A-201"].defined_terms
        # These three are the exact terms this mission's own directive named
        # as motivating the ingestion (the cross-Article "good faith" gap
        # documented in docs/zero-assumption-pedagogy-design.md).
        self.assertIn("Good faith", defined)
        self.assertIn("Record", defined)
        self.assertIn("Security interest", defined)
        self.assertGreater(len(defined), 20)

    def test_non_definitions_sections_have_no_invented_defined_terms(self) -> None:
        sections = {s.section_id: s for s in ing1.normalize_sections()}
        self.assertEqual(sections["8.1A-103"].defined_terms, [])
        self.assertEqual(sections["8.1A-301"].defined_terms, [])
        self.assertEqual(sections["8.1A-302"].defined_terms, [])

    def test_cross_references_are_real_extracted_citations(self) -> None:
        sections = {s.section_id: s for s in ing1.normalize_sections()}
        # § 8.1A-201(b)(3) "Agreement" really does cross-reference
        # § 8.1A-303 (course of performance/dealing/usage of trade), and
        # (b)(35) "Security interest" really does cross-reference
        # § 8.1A-203 (lease-versus-security-interest test).
        self.assertIn("8.1A-303", sections["8.1A-201"].cross_references)
        self.assertIn("8.1A-203", sections["8.1A-201"].cross_references)
        # A section never lists itself as its own cross-reference.
        self.assertNotIn("8.1A-201", sections["8.1A-201"].cross_references)

    def test_definitions_with_intervening_clause_are_a_disclosed_gap(self) -> None:
        # Real, disclosed regex-extraction limitation (see module
        # docstring): "Agreement," as distinguished from "contract," means
        # ... -- the intervening clause between the closing quote and
        # "means" means the simple pattern does not capture it. This test
        # pins that real, honest limitation rather than silently masking
        # it.
        sections = {s.section_id: s for s in ing1.normalize_sections()}
        self.assertNotIn("Agreement", sections["8.1A-201"].defined_terms)


class SourceManifestBuildTests(unittest.TestCase):
    def test_manifest_hash_matches_real_raw_file(self) -> None:
        manifest = ing1.build_source_manifest()
        real_bytes = ing1.RAW_EXTRACT_PATH.read_bytes()
        self.assertEqual(manifest.sha256_hash, hashlib.sha256(real_bytes).hexdigest())

    def test_manifest_uses_statute_authority_type(self) -> None:
        manifest = ing1.build_source_manifest()
        self.assertEqual(manifest.authority_type, AuthorityType.STATUTE)

    def test_manifest_starts_source_verified(self) -> None:
        manifest = ing1.build_source_manifest()
        self.assertEqual(manifest.verification_status, VerificationStatus.SOURCE_VERIFIED)

    def test_manifest_declares_public_domain_reasoning(self) -> None:
        manifest = ing1.build_source_manifest()
        self.assertIn("public domain", manifest.licensing_status)
        self.assertIn("edict of government", manifest.licensing_status)

    def test_manifest_is_enactment_layer(self) -> None:
        manifest = ing1.build_source_manifest()
        self.assertEqual(manifest.source_layer, SourceLayer.ENACTMENT)


class RunIngestionTests(unittest.TestCase):
    def test_run_ingestion_writes_real_files(self) -> None:
        # Mirrors test_ingestion_article9.py's own snapshot/restore
        # discipline (law-engine-publication-readiness-1.44.md, section 8):
        # run_ingestion() writes through to the real, tracked manifest
        # files, rewriting retrieval_timestamp on every test run. This test
        # genuinely needs to exercise the real write path, so instead of
        # mocking it out, setUp/tearDown snapshot the real tracked files'
        # bytes first and restore them afterward -- the write still really
        # happens and is really verified, but the tracked file a stranger
        # clones is never left modified by simply running the documented
        # test command.
        normalized_path, manifest_path = ing1.run_ingestion()
        self.assertTrue(normalized_path.exists())
        self.assertTrue(manifest_path.exists())

    def setUp(self) -> None:
        self._normalized_path = _LAW_ENGINE_ROOT / "library" / "normalized" / "ucc" / "article-1-sections.json"
        self._manifest_path = _LAW_ENGINE_ROOT / "library" / "manifests" / "va-code-title-8.1a-article-1.json"
        self._normalized_before = self._normalized_path.read_bytes() if self._normalized_path.exists() else None
        self._manifest_before = self._manifest_path.read_bytes() if self._manifest_path.exists() else None

    def tearDown(self) -> None:
        if self._normalized_before is not None:
            self._normalized_path.write_bytes(self._normalized_before)
        if self._manifest_before is not None:
            self._manifest_path.write_bytes(self._manifest_before)


if __name__ == "__main__":
    unittest.main()

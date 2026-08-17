from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import ingestion
from services.models import AuthorityType, VerificationStatus


class NormalizeSectionsTests(unittest.TestCase):
    def test_real_eleven_sections_normalized(self) -> None:
        sections = ingestion.normalize_sections()
        ids = {s.section_id for s in sections}
        self.assertEqual(len(sections), 11)
        self.assertIn("8.2-314", ids)
        self.assertIn("8.2-104", ids)

    def test_every_section_has_real_nonempty_paragraphs(self) -> None:
        for section in ingestion.normalize_sections():
            self.assertGreater(len(section.paragraphs), 0)
            for p in section.paragraphs:
                self.assertGreater(len(p.strip()), 0)

    def test_citation_format(self) -> None:
        sections = ingestion.normalize_sections()
        merchant_section = next(s for s in sections if s.section_id == "8.2-104")
        self.assertEqual(merchant_section.citation, "Va. Code Ann. § 8.2-104")

    def test_defined_terms_are_real_and_curated(self) -> None:
        sections = {s.section_id: s for s in ingestion.normalize_sections()}
        self.assertIn("merchant", sections["8.2-104"].defined_terms)
        self.assertIn("goods", sections["8.2-105"].defined_terms)


class SourceManifestBuildTests(unittest.TestCase):
    def test_manifest_hash_matches_real_raw_file(self) -> None:
        manifest = ingestion.build_source_manifest()
        real_bytes = ingestion.RAW_EXTRACT_PATH.read_bytes()
        self.assertEqual(manifest.sha256_hash, hashlib.sha256(real_bytes).hexdigest())

    def test_manifest_uses_statute_authority_type(self) -> None:
        manifest = ingestion.build_source_manifest()
        self.assertEqual(manifest.authority_type, AuthorityType.STATUTE)

    def test_manifest_starts_source_verified(self) -> None:
        manifest = ingestion.build_source_manifest()
        self.assertEqual(manifest.verification_status, VerificationStatus.SOURCE_VERIFIED)

    def test_manifest_declares_public_domain_reasoning(self) -> None:
        manifest = ingestion.build_source_manifest()
        self.assertIn("public domain", manifest.licensing_status)
        self.assertIn("edict of government", manifest.licensing_status)


class RunIngestionTests(unittest.TestCase):
    # Live Run 1.45 -- see the matching fix/comment in
    # test_ingestion_article9.py's RunIngestionTests for the real,
    # disclosed reason (law-engine-publication-readiness-1.44.md, §8).
    def setUp(self) -> None:
        self._normalized_path = _LAW_ENGINE_ROOT / "library" / "normalized" / "ucc" / "article-2-sections.json"
        self._manifest_path = _LAW_ENGINE_ROOT / "library" / "manifests" / "va-code-title-8.2-article-2.json"
        self._normalized_before = self._normalized_path.read_bytes() if self._normalized_path.exists() else None
        self._manifest_before = self._manifest_path.read_bytes() if self._manifest_path.exists() else None

    def tearDown(self) -> None:
        if self._normalized_before is not None:
            self._normalized_path.write_bytes(self._normalized_before)
        if self._manifest_before is not None:
            self._manifest_path.write_bytes(self._manifest_before)

    def test_run_ingestion_writes_real_files(self) -> None:
        normalized_path, manifest_path = ingestion.run_ingestion()
        self.assertTrue(normalized_path.exists())
        self.assertTrue(manifest_path.exists())


if __name__ == "__main__":
    unittest.main()

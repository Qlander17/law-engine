from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import ingestion_article3 as ing3
from services.models import AuthorityType, SourceLayer, VerificationStatus


class NormalizeSectionsTests(unittest.TestCase):
    def test_real_twelve_sections_normalized(self) -> None:
        sections = ing3.normalize_sections()
        ids = {s.section_id for s in sections}
        self.assertEqual(len(sections), 12)
        self.assertIn("8.3A-104", ids)  # negotiable instrument
        self.assertIn("8.3A-204", ids)  # indorsement
        self.assertIn("8.3A-301", ids)  # person entitled to enforce
        self.assertIn("8.3A-302", ids)  # holder in due course
        self.assertIn("8.3A-308", ids)  # proof of signatures / holder-in-due-course status

    def test_every_section_has_real_nonempty_paragraphs(self) -> None:
        for section in ing3.normalize_sections():
            self.assertGreater(len(section.paragraphs), 0)
            for p in section.paragraphs:
                self.assertGreater(len(p.strip()), 0)

    def test_citation_format(self) -> None:
        sections = ing3.normalize_sections()
        negotiability_section = next(s for s in sections if s.section_id == "8.3A-104")
        self.assertEqual(negotiability_section.citation, "Va. Code Ann. § 8.3A-104")

    def test_negotiable_instrument_defined_in_real_ingested_text(self) -> None:
        sections = {s.section_id: s for s in ing3.normalize_sections()}
        # Real, disclosed case-insensitive-first-letter pattern (see module
        # docstring): § 8.3A-104(a) defines "negotiable instrument" in
        # lowercase, mid-sentence, unlike Article 9's own always-capitalized
        # defined terms.
        self.assertIn("negotiable instrument", sections["8.3A-104"].defined_terms)

    def test_holder_in_due_course_defined_in_real_ingested_text(self) -> None:
        sections = {s.section_id: s for s in ing3.normalize_sections()}
        self.assertIn("holder in due course", sections["8.3A-302"].defined_terms)

    def test_definitions_section_has_real_defined_terms(self) -> None:
        sections = {s.section_id: s for s in ing3.normalize_sections()}
        defined = sections["8.3A-103"].defined_terms
        self.assertIn("Drawer", defined)
        self.assertIn("Maker", defined)
        self.assertIn("Good faith", defined)

    def test_non_definitional_section_has_no_invented_defined_terms(self) -> None:
        sections = {s.section_id: s for s in ing3.normalize_sections()}
        self.assertEqual(sections["8.3A-203"].defined_terms, [])

    def test_cross_references_are_real_extracted_citations(self) -> None:
        sections = {s.section_id: s for s in ing3.normalize_sections()}
        # § 8.3A-109 -- "Payable to bearer or to order" -- really does
        # reference § 8.3A-205 in its own text.
        self.assertIn("8.3A-205", sections["8.3A-109"].cross_references)
        # A section never lists itself as its own cross-reference.
        self.assertNotIn("8.3A-302", sections["8.3A-302"].cross_references)

    def test_holder_is_not_duplicated_from_article_1(self) -> None:
        # "Holder" is already a real, ingested Article 1 general
        # definition (§ 8.1A-201) -- this module must not re-define it.
        sections = ing3.normalize_sections()
        for section in sections:
            self.assertNotIn("Holder", section.defined_terms)

    def test_proof_of_signatures_section_cross_references_person_entitled_to_enforce(self) -> None:
        # § 8.3A-308(b)'s real text ties "producing the instrument" to
        # proving entitlement under § 8.3A-301 -- the real statutory hook
        # for the flagship precedent pair's procedural-timing question
        # (see module docstring's Phase 1 gap-check disclosure).
        sections = {s.section_id: s for s in ing3.normalize_sections()}
        self.assertIn("8.3A-301", sections["8.3A-308"].cross_references)
        self.assertIn("burden-of-proof", sections["8.3A-308"].topics)


class SourceManifestBuildTests(unittest.TestCase):
    def test_manifest_hash_matches_real_raw_file(self) -> None:
        manifest = ing3.build_source_manifest()
        real_bytes = ing3.RAW_EXTRACT_PATH.read_bytes()
        self.assertEqual(manifest.sha256_hash, hashlib.sha256(real_bytes).hexdigest())

    def test_manifest_uses_statute_authority_type(self) -> None:
        manifest = ing3.build_source_manifest()
        self.assertEqual(manifest.authority_type, AuthorityType.STATUTE)

    def test_manifest_starts_source_verified(self) -> None:
        manifest = ing3.build_source_manifest()
        self.assertEqual(manifest.verification_status, VerificationStatus.SOURCE_VERIFIED)

    def test_manifest_declares_public_domain_reasoning(self) -> None:
        manifest = ing3.build_source_manifest()
        self.assertIn("public domain", manifest.licensing_status)
        self.assertIn("edict of government", manifest.licensing_status)

    def test_manifest_is_enactment_layer(self) -> None:
        manifest = ing3.build_source_manifest()
        self.assertEqual(manifest.source_layer, SourceLayer.ENACTMENT)


class RunIngestionTests(unittest.TestCase):
    def test_run_ingestion_writes_real_files(self) -> None:
        # Same real-write-path discipline as test_ingestion_article9.py's
        # own RunIngestionTests: the write really happens and is really
        # verified, but the tracked file a stranger clones is never left
        # modified by simply running the documented test command.
        normalized_path, manifest_path = ing3.run_ingestion()
        self.assertTrue(normalized_path.exists())
        self.assertTrue(manifest_path.exists())

    def setUp(self) -> None:
        self._normalized_path = _LAW_ENGINE_ROOT / "library" / "normalized" / "ucc" / "article-3-sections.json"
        self._manifest_path = _LAW_ENGINE_ROOT / "library" / "manifests" / "va-code-title-8.3a-article-3.json"
        self._normalized_before = self._normalized_path.read_bytes() if self._normalized_path.exists() else None
        self._manifest_before = self._manifest_path.read_bytes() if self._manifest_path.exists() else None

    def tearDown(self) -> None:
        if self._normalized_before is not None:
            self._normalized_path.write_bytes(self._normalized_before)
        if self._manifest_before is not None:
            self._manifest_path.write_bytes(self._manifest_before)


if __name__ == "__main__":
    unittest.main()

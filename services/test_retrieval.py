from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import ingestion, retrieval


class RetrievalTests(unittest.TestCase):
    # Live Run 1.45 -- see test_ingestion.py's RunIngestionTests for the
    # real, disclosed reason (law-engine-publication-readiness-1.44.md,
    # §8).
    @classmethod
    def setUpClass(cls) -> None:
        manifest_path = _LAW_ENGINE_ROOT / "library" / "manifests" / "va-code-title-8.2-article-2.json"
        cls._manifest_before = manifest_path.read_bytes() if manifest_path.exists() else None
        cls._manifest_path = manifest_path
        ingestion.run_ingestion()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._manifest_before is not None:
            cls._manifest_path.write_bytes(cls._manifest_before)

    def test_get_section_returns_real_section(self) -> None:
        section = retrieval.get_section("8.2-314")
        self.assertIsNotNone(section)
        self.assertIn("merchantable", " ".join(section["paragraphs"]).lower())

    def test_get_section_returns_none_for_unknown_id(self) -> None:
        self.assertIsNone(retrieval.get_section("8.2-999"))

    def test_search_finds_merchantability_section(self) -> None:
        results = retrieval.search("merchantability")
        ids = {r["section_id"] for r in results}
        self.assertIn("8.2-314", ids)

    def test_search_returns_real_citation_and_matched_text(self) -> None:
        results = retrieval.search("merchant")
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertTrue(r["citation"].startswith("Va. Code Ann."))
            self.assertGreater(len(r["matched_paragraphs"]), 0)

    def test_search_empty_query_returns_empty(self) -> None:
        self.assertEqual(retrieval.search("   "), [])

    def test_search_by_topic_offer_acceptance(self) -> None:
        results = retrieval.search_by_topic("offer-acceptance")
        ids = {r["section_id"] for r in results}
        self.assertIn("8.2-206", ids)
        self.assertIn("8.2-207", ids)


if __name__ == "__main__":
    unittest.main()

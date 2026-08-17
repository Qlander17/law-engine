from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import syntax_analysis_export as sae
from services.retrieval import load_sections


class BuildAnalysisTests(unittest.TestCase):
    def test_covers_every_real_ingested_section(self) -> None:
        analysis = sae.build_analysis()
        sections = load_sections()
        self.assertEqual(set(analysis.keys()), set(sections.keys()))

    def test_every_paragraph_gets_one_analysis_record(self) -> None:
        analysis = sae.build_analysis()
        sections = load_sections()
        for section_id, section in sections.items():
            real_paragraphs = [p for p in section["paragraphs"] if p.strip()]
            self.assertEqual(len(analysis[section_id]), len(real_paragraphs))

    def test_merchant_definition_flags_definitional_sentence(self) -> None:
        analysis = sae.build_analysis()
        merchant_records = analysis["8.2-104"]
        self.assertTrue(any(r["is_definitional_sentence"] or r["operative_terms_found"] for r in merchant_records))


if __name__ == "__main__":
    unittest.main()

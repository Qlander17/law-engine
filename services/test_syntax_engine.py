from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.syntax_engine import AnalysisMode, SyntaxEngineError, analyze_sentence


class AnalyzeSentenceTests(unittest.TestCase):
    def test_detects_mandatory_modal(self) -> None:
        result = analyze_sentence("The buyer shall pay within 30 days.")
        self.assertIn("shall", result.modal_verbs_found)
        self.assertTrue(result.is_mandatory)
        self.assertFalse(result.is_permissive)

    def test_detects_permissive_modal(self) -> None:
        result = analyze_sentence("The seller may withhold delivery.")
        self.assertIn("may", result.modal_verbs_found)
        self.assertTrue(result.is_permissive)
        self.assertFalse(result.is_mandatory)

    def test_detects_conjunction_and_disjunction(self) -> None:
        result = analyze_sentence("The buyer and the seller may agree, or a court may decide.")
        self.assertTrue(result.has_conjunction)
        self.assertTrue(result.has_disjunction)

    def test_detects_negation(self) -> None:
        result = analyze_sentence("Goods which are not both existing and identified are future goods.")
        self.assertTrue(result.has_negation)

    def test_finds_known_defined_terms(self) -> None:
        result = analyze_sentence("The goods must be merchantable.", known_defined_terms=["goods", "merchant"])
        self.assertIn("goods", result.defined_terms_used)
        self.assertNotIn("merchant", result.defined_terms_used)

    def test_rejects_empty_text(self) -> None:
        with self.assertRaises(SyntaxEngineError):
            analyze_sentence("   ")

    def test_reserved_modes_raise_not_silently_succeed(self) -> None:
        for mode in (
            AnalysisMode.HISTORICAL_GRAMMAR,
            AnalysisMode.MILLER_STYLE_ANALYSIS,
            AnalysisMode.COURT_CONSTRUCTION_COMPARISON,
        ):
            with self.assertRaises(SyntaxEngineError):
                analyze_sentence("test sentence", mode=mode)

    def test_standard_and_statutory_modes_work(self) -> None:
        for mode in (AnalysisMode.STANDARD_LANGUAGE_PARSE, AnalysisMode.STATUTORY_LEGAL_PARSE):
            result = analyze_sentence("A contract may be made.", mode=mode)
            self.assertEqual(result.mode, mode)

    def test_detects_operative_terms(self) -> None:
        result = analyze_sentence('"Goods" means all things which are movable and includes fixtures.')
        self.assertIn("means", result.operative_terms_found)
        self.assertIn("includes", result.operative_terms_found)
        self.assertIn("and", result.operative_terms_found)

    def test_detects_conditional(self) -> None:
        result = analyze_sentence("If the buyer rejects the goods, the seller may cure.")
        self.assertTrue(result.has_conditional)
        self.assertIn("if", result.conditional_markers_found)

    def test_detects_exception(self) -> None:
        result = analyze_sentence("Notwithstanding subsection (a), the seller may withhold delivery.")
        self.assertTrue(result.has_exception)
        self.assertIn("notwithstanding", result.exception_markers_found)

    def test_detects_cross_references(self) -> None:
        result = analyze_sentence("Subject to Section 8.2-206 and this article, an offer invites acceptance.")
        self.assertTrue(any("8.2-206" in ref for ref in result.cross_references))
        self.assertTrue(any("this article" in ref.lower() for ref in result.cross_references))

    def test_detects_incorporated_definition(self) -> None:
        result = analyze_sentence("The term has the meaning set forth in § 8.2-104.")
        self.assertEqual(len(result.incorporated_definitions), 1)
        self.assertIn("has the meaning set forth in", result.incorporated_definitions[0])

    def test_detects_definitional_sentence(self) -> None:
        result = analyze_sentence('"Merchant" means a person who deals in goods of the kind.')
        self.assertTrue(result.is_definitional_sentence)

    def test_non_definitional_sentence_is_not_flagged(self) -> None:
        result = analyze_sentence("The buyer shall pay within 30 days.")
        self.assertFalse(result.is_definitional_sentence)

    def test_flags_quoted_term_not_in_known_defined_terms(self) -> None:
        result = analyze_sentence('A "cover" purchase must be made in good faith.', known_defined_terms=["good faith"])
        self.assertIn("cover", result.potentially_undefined_terms)

    def test_does_not_flag_quoted_term_that_is_known(self) -> None:
        result = analyze_sentence('The "merchant" standard applies.', known_defined_terms=["merchant"])
        self.assertNotIn("merchant", result.potentially_undefined_terms)


if __name__ == "__main__":
    unittest.main()

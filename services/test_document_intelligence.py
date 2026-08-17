from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import document_intelligence as di
from services.retrieval import get_section


class DocumentFamilyEnumTests(unittest.TestCase):
    def test_covers_required_families(self) -> None:
        required = {
            "CONTRACT", "PURCHASE_ORDER", "INVOICE", "SECURITY_AGREEMENT",
            "FINANCING_STATEMENT", "PROMISSORY_NOTE", "NEGOTIABLE_INSTRUMENT",
            "CHECK_DRAFT", "GUARANTY", "LEASE", "BILL_OF_LADING",
            "WAREHOUSE_RECEIPT", "TITLE_CERTIFICATE", "ASSIGNMENT", "OTHER",
        }
        actual = {member.value for member in di.DocumentFamily}
        self.assertTrue(required.issubset(actual))


class GroundedProfileCitationTests(unittest.TestCase):
    """Every profile that claims grounding must trace to a real ingested
    section -- never an invented citation."""

    def test_purchase_order_profile_traces_to_real_ingested_sections(self) -> None:
        profile = di.build_purchase_order_profile()
        self.assertTrue(profile.grounded_in_ingested_text)
        section_206 = get_section("8.2-206")
        section_204 = get_section("8.2-204")
        self.assertIsNotNone(section_206)
        self.assertIsNotNone(section_204)
        self.assertIn(section_206["citation"], profile.related_authorities)
        self.assertIn(section_204["citation"], profile.related_authorities)

    def test_invoice_profile_traces_to_real_ingested_section(self) -> None:
        profile = di.build_invoice_profile()
        self.assertTrue(profile.grounded_in_ingested_text)
        section = get_section("8.2-207")
        self.assertIsNotNone(section)
        self.assertIn(section["citation"], profile.related_authorities)
        # the ingested text never uses the word "invoice" -- the grounding
        # note must disclose that this is a functional mapping, not a
        # literal word match.
        self.assertIn("invoice", profile.grounding_note.lower())
        self.assertIn("function", profile.grounding_note.lower())

    def test_sales_contract_profile_traces_to_real_ingested_sections(self) -> None:
        profile = di.build_sales_contract_profile()
        self.assertTrue(profile.grounded_in_ingested_text)
        section_204 = get_section("8.2-204")
        section_105 = get_section("8.2-105")
        self.assertIsNotNone(section_204)
        self.assertIsNotNone(section_105)
        self.assertIn(section_204["citation"], profile.related_authorities)
        self.assertIn(section_105["citation"], profile.related_authorities)

    def test_all_grounded_profiles_only_cite_real_sections(self) -> None:
        """Belt-and-suspenders: for every profile that self-reports as
        grounded, every citation string in related_authorities must equal
        the citation of some real, currently-ingested section."""
        real_citations = set()
        for section_id in ["8.2-102", "8.2-104", "8.2-105", "8.2-204", "8.2-206",
                            "8.2-207", "8.2-313", "8.2-314", "8.2-601", "8.2-703", "8.2-711"]:
            section = get_section(section_id)
            self.assertIsNotNone(section, f"expected {section_id!r} to be a real ingested section")
            real_citations.add(section["citation"])

        for profile in di.build_all_profiles():
            if not profile.grounded_in_ingested_text:
                continue
            for citation in profile.related_authorities:
                self.assertIn(
                    citation, real_citations,
                    f"{profile.family.value} claims grounding but cites {citation!r}, "
                    "which is not a real ingested section's citation",
                )


class UngroundedProfileHonestyTests(unittest.TestCase):
    """Profiles for document types not covered by ingested Article 2 text
    must say so explicitly and must not carry a citation."""

    def test_security_agreement_profile_is_explicitly_ungrounded(self) -> None:
        profile = di.build_security_agreement_profile()
        self.assertFalse(profile.grounded_in_ingested_text)
        self.assertEqual(profile.related_authorities, [])
        self.assertIn("NOT grounded", profile.grounding_note)

    def test_financing_statement_profile_is_explicitly_ungrounded(self) -> None:
        profile = di.build_financing_statement_profile()
        self.assertFalse(profile.grounded_in_ingested_text)
        self.assertEqual(profile.related_authorities, [])
        self.assertIn("NOT grounded", profile.grounding_note)

    def test_promissory_note_profile_is_explicitly_ungrounded(self) -> None:
        profile = di.build_promissory_note_profile()
        self.assertFalse(profile.grounded_in_ingested_text)
        self.assertEqual(profile.related_authorities, [])
        self.assertIn("NOT grounded", profile.grounding_note)

    def test_no_ungrounded_profile_invents_a_section_number(self) -> None:
        """No ungrounded profile's text fields should reference a
        Va. Code Ann. section number that isn't a real ingested section
        (guards against accidentally smuggling an invented citation into
        a prose field instead of related_authorities)."""
        import re

        real_section_ids = {
            "8.2-102", "8.2-104", "8.2-105", "8.2-204", "8.2-206",
            "8.2-207", "8.2-313", "8.2-314", "8.2-601", "8.2-703", "8.2-711",
        }
        for builder in [
            di.build_security_agreement_profile,
            di.build_financing_statement_profile,
            di.build_promissory_note_profile,
        ]:
            profile = builder()
            haystack = " ".join(
                [
                    profile.legal_function,
                    profile.signature_authentication_rules,
                    profile.transfer_indorsement_rules,
                    profile.filing_possession_control_consequences,
                    profile.grounding_note,
                    profile.title_vs_substance_note,
                    *profile.common_confusions,
                    *profile.identifying_features,
                ]
            )
            found_section_numbers = set(re.findall(r"8\.2-\d+", haystack))
            self.assertTrue(
                found_section_numbers.issubset(real_section_ids),
                f"{profile.family.value} references a section number not in the real ingested set: "
                f"{found_section_numbers - real_section_ids}",
            )


class DocumentProfileShapeTests(unittest.TestCase):
    def test_title_vs_substance_note_present_on_every_profile(self) -> None:
        for profile in di.build_all_profiles():
            self.assertTrue(profile.title_vs_substance_note.strip())

    def test_to_dict_round_trips_for_every_profile(self) -> None:
        for profile in di.build_all_profiles():
            d = profile.to_dict()
            self.assertEqual(d["family"], profile.family.value)
            self.assertIn("title_vs_substance_note", d)
            self.assertIn("grounded_in_ingested_text", d)

    def test_every_profile_has_populated_core_fields(self) -> None:
        for profile in di.build_all_profiles():
            self.assertGreater(len(profile.identifying_features), 0, profile.family.value)
            self.assertGreater(len(profile.required_elements), 0, profile.family.value)
            self.assertGreater(len(profile.common_confusions), 0, profile.family.value)
            self.assertTrue(profile.legal_function.strip(), profile.family.value)


class DocumentIdentificationExerciseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.exercise = di.build_purchase_order_identification_exercise()

    def test_exactly_one_correct_answer(self) -> None:
        correct = self.exercise.correct_choice()
        self.assertEqual(correct.family, di.DocumentFamily.PURCHASE_ORDER)
        self.assertEqual(sum(1 for c in self.exercise.choices if c.is_correct), 1)

    def test_at_least_two_plausible_wrong_alternatives(self) -> None:
        wrong = [c for c in self.exercise.choices if not c.is_correct]
        self.assertGreaterEqual(len(wrong), 2)

    def test_every_choice_has_a_real_nonempty_explanation(self) -> None:
        for choice in self.exercise.choices:
            self.assertTrue(choice.explanation.strip(), choice.label)
            self.assertGreater(len(choice.explanation), 20, choice.label)

    def test_correct_choice_explanation_cites_real_ingested_section(self) -> None:
        section = get_section("8.2-206")
        self.assertIsNotNone(section)
        correct = self.exercise.correct_choice()
        self.assertIn(section["citation"], correct.explanation)

    def test_wrong_choice_explanations_each_cite_real_ingested_sections(self) -> None:
        contract_section = get_section("8.2-204")
        confirmation_section = get_section("8.2-207")
        wrong_by_family = {c.family: c for c in self.exercise.choices if not c.is_correct}
        self.assertIn(contract_section["citation"], wrong_by_family[di.DocumentFamily.CONTRACT].explanation)
        self.assertIn(
            confirmation_section["citation"],
            wrong_by_family[di.DocumentFamily.INVOICE].explanation,
        )

    def test_answer_returns_matching_choice(self) -> None:
        result = self.exercise.answer(di.DocumentFamily.PURCHASE_ORDER)
        self.assertTrue(result.is_correct)

    def test_answer_raises_for_unlisted_family(self) -> None:
        with self.assertRaises(di.DocumentIntelligenceError):
            self.exercise.answer(di.DocumentFamily.GUARANTY)

    def test_metaphor_is_labeled_pedagogical_only_and_distinct_from_hypothetical(self) -> None:
        self.assertIsNotNone(self.exercise.metaphor)
        self.assertTrue(self.exercise.metaphor.is_pedagogical_only)
        self.assertIn("not a legal rule", self.exercise.metaphor.disclaimer)
        self.assertNotEqual(self.exercise.metaphor.illustration, self.exercise.hypothetical)

    def test_to_dict_round_trips(self) -> None:
        d = self.exercise.to_dict()
        self.assertEqual(d["exercise_id"], "what-kind-of-document-po-vs-invoice-vs-contract")
        self.assertEqual(len(d["choices"]), 3)
        self.assertTrue(d["metaphor"]["is_pedagogical_only"])


class RequireSectionErrorTests(unittest.TestCase):
    def test_require_section_raises_for_uningested_section(self) -> None:
        with self.assertRaises(di.DocumentIntelligenceError):
            di._require_section("not-a-real-section-id")


if __name__ == "__main__":
    unittest.main()

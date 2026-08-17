from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.models import (
    AuthorityType,
    CisgApplicabilityAssessment,
    ConfidenceLabel,
    FactSensitivityNote,
    PedagogicalContract,
    PedagogicalMetaphor,
    PedagogicalSubjectKind,
    ProvisionComparison,
    SourceLayer,
    SourceManifest,
    StatuteSection,
    TransactionScope,
    VerificationStatus,
    now_iso,
)


class VerificationStatusTests(unittest.TestCase):
    def test_all_required_states_present(self) -> None:
        required = {
            "DISCOVERED", "RETRIEVED", "SOURCE_VERIFIED", "AUTHORITY_CLASSIFIED",
            "CURRENTNESS_CHECKED", "CROSS_VERIFIED", "TRUSTED_FOR_ANALYSIS", "CONFLICT", "UNKNOWN",
        }
        self.assertEqual({v.value for v in VerificationStatus}, required)


class SourceManifestTests(unittest.TestCase):
    def test_to_dict_round_trips_real_fields(self) -> None:
        manifest = SourceManifest(
            document_id="test-doc",
            title="Test Statute",
            authority_type=AuthorityType.STATUTE,
            jurisdiction="Commonwealth of Virginia",
            citation="Va. Code Ann. § 1-1",
            official_source_url="https://law.lis.virginia.gov/vacode/1-1/",
            publisher="Commonwealth of Virginia",
            retrieval_timestamp=now_iso(),
            sha256_hash="deadbeef",
            verification_status=VerificationStatus.SOURCE_VERIFIED,
        )
        d = manifest.to_dict()
        self.assertEqual(d["document_id"], "test-doc")
        self.assertEqual(d["authority_type"], "STATUTE")
        self.assertEqual(d["verification_status"], "SOURCE_VERIFIED")
        self.assertEqual(d["licensing_status"], "public domain -- state statute (edict of government)")

    def test_source_layer_defaults_to_enactment(self) -> None:
        manifest = SourceManifest(
            document_id="test-doc-2",
            title="Test Statute 2",
            authority_type=AuthorityType.STATUTE,
            jurisdiction="Commonwealth of Virginia",
            citation="Va. Code Ann. § 1-2",
            official_source_url="https://law.lis.virginia.gov/vacode/1-2/",
            publisher="Commonwealth of Virginia",
            retrieval_timestamp=now_iso(),
            sha256_hash="deadbeef",
            verification_status=VerificationStatus.SOURCE_VERIFIED,
        )
        self.assertEqual(manifest.source_layer, SourceLayer.ENACTMENT)
        self.assertEqual(manifest.to_dict()["source_layer"], "ENACTMENT")

    def test_source_layer_can_be_set_to_model_or_interpretation(self) -> None:
        model_manifest = SourceManifest(
            document_id="ulc-model-2-314",
            title="Model UCC § 2-314",
            authority_type=AuthorityType.STATUTE,
            jurisdiction="ULC/ALI (Model, not enacted anywhere by itself)",
            citation="U.C.C. § 2-314 (Am. L. Inst. & Unif. Law Comm'n)",
            official_source_url="https://www.uniformlaws.org/",
            publisher="Uniform Law Commission",
            retrieval_timestamp=now_iso(),
            sha256_hash="deadbeef",
            verification_status=VerificationStatus.SOURCE_VERIFIED,
            source_layer=SourceLayer.MODEL,
        )
        self.assertEqual(model_manifest.source_layer, SourceLayer.MODEL)


class ProvisionComparisonTests(unittest.TestCase):
    def test_to_dict_represents_ungapped_model_layer(self) -> None:
        comparison = ProvisionComparison(
            provision_key="ucc-2-314-merchantability",
            enactment_section_ids={"Commonwealth of Virginia": "8.2-314"},
        )
        d = comparison.to_dict()
        self.assertIsNone(d["model_section_id"])
        self.assertEqual(d["enactment_section_ids"]["Commonwealth of Virginia"], "8.2-314")


class CisgApplicabilityAssessmentTests(unittest.TestCase):
    def test_defaults_to_undetermined_scope(self) -> None:
        assessment = CisgApplicabilityAssessment(
            transaction_id="test-txn-1",
            seller_place_of_business_country="United States",
            buyer_place_of_business_country="Germany",
        )
        self.assertEqual(assessment.scope, TransactionScope.UNDETERMINED)
        self.assertFalse(assessment.parties_opted_out_under_article_6)

    def test_forum_dependent_article_95_fields_are_separate_from_party_countries(self) -> None:
        assessment = CisgApplicabilityAssessment(
            transaction_id="test-txn-3",
            seller_place_of_business_country="United States",
            buyer_place_of_business_country="Germany",
            both_in_contracting_states=True,
            forum_country="United States",
            forum_is_article_95_declarant=True,
        )
        d = assessment.to_dict()
        self.assertEqual(d["forum_country"], "United States")
        self.assertTrue(d["forum_is_article_95_declarant"])
        # forum_country is tracked independently of the parties' own
        # countries -- exactly why it's a separate field rather than
        # folded into both_in_contracting_states.
        self.assertIn("forum_country", d)
        self.assertIn("seller_place_of_business_country", d)

    def test_consumer_goods_exclusion_is_representable(self) -> None:
        assessment = CisgApplicabilityAssessment(
            transaction_id="test-txn-2",
            seller_place_of_business_country="United States",
            buyer_place_of_business_country="France",
            is_consumer_goods_purchase=True,
            scope=TransactionScope.INTERNATIONAL_NON_CISG,
            reasoning_notes=["Excluded under CISG Article 2(a): goods bought for personal, family, or household use."],
        )
        d = assessment.to_dict()
        self.assertTrue(d["is_consumer_goods_purchase"])
        self.assertEqual(d["scope"], "INTERNATIONAL_NON_CISG")


class StatuteSectionTests(unittest.TestCase):
    def test_to_dict_round_trips(self) -> None:
        section = StatuteSection(
            section_id="8.2-104",
            title="Definitions",
            paragraphs=["(1) Merchant means..."],
            citation="Va. Code Ann. § 8.2-104",
            source_document_id="va-code-title-8.2-article-2",
            topics=["merchant-status"],
            defined_terms=["merchant"],
        )
        d = section.to_dict()
        self.assertEqual(d["section_id"], "8.2-104")
        self.assertIn("merchant", d["defined_terms"])


class PedagogicalMetaphorTests(unittest.TestCase):
    def test_to_dict_always_marks_pedagogical_only(self) -> None:
        metaphor = PedagogicalMetaphor(illustration="A warranty is like a handshake nobody had to make out loud.")
        d = metaphor.to_dict()
        self.assertTrue(d["is_pedagogical_only"])
        self.assertIn("not a legal rule", d["disclaimer"])


class FactSensitivityNoteTests(unittest.TestCase):
    def test_to_dict_round_trips_optional_citation(self) -> None:
        note = FactSensitivityNote(changed_fact="Seller is not a merchant.", effect="Warranty does not attach.")
        d = note.to_dict()
        self.assertIsNone(d["citation"])
        self.assertEqual(d["changed_fact"], "Seller is not a merchant.")


class PedagogicalContractTests(unittest.TestCase):
    def test_to_dict_round_trips_required_and_optional_fields(self) -> None:
        contract = PedagogicalContract(
            contract_id="test-contract-1",
            subject_name="Test Rule",
            subject_kind=PedagogicalSubjectKind.RULE,
            authority_citation="Va. Code Ann. § 1-1",
            authority_type=AuthorityType.STATUTE,
            jurisdiction="Commonwealth of Virginia",
            verification_status=VerificationStatus.SOURCE_VERIFIED,
            confidence_label=ConfidenceLabel.VERIFIED,
            governing_text_excerpt="The real statutory text.",
            how_to_recognize=["Fact one.", "Fact two."],
            fact_sensitivity=[FactSensitivityNote(changed_fact="X changes.", effect="Y follows.", citation="Va. Code Ann. § 1-1")],
            metaphor=PedagogicalMetaphor(illustration="It's like a library card."),
        )
        d = contract.to_dict()
        self.assertEqual(d["contract_id"], "test-contract-1")
        self.assertEqual(d["subject_kind"], "RULE")
        self.assertEqual(d["authority_type"], "STATUTE")
        self.assertEqual(d["verification_status"], "SOURCE_VERIFIED")
        self.assertEqual(d["confidence_label"], "VERIFIED")
        self.assertEqual(d["source_layer"], "ENACTMENT")
        self.assertEqual(len(d["fact_sensitivity"]), 1)
        self.assertEqual(d["metaphor"]["illustration"], "It's like a library card.")

    def test_optional_fields_default_to_none_or_empty(self) -> None:
        contract = PedagogicalContract(
            contract_id="test-contract-2",
            subject_name="Test Rule 2",
            subject_kind=PedagogicalSubjectKind.CONCEPT,
            authority_citation="Va. Code Ann. § 1-2",
            authority_type=AuthorityType.STATUTE,
            jurisdiction="Commonwealth of Virginia",
            verification_status=VerificationStatus.UNKNOWN,
            confidence_label=ConfidenceLabel.UNVERIFIED,
        )
        d = contract.to_dict()
        self.assertIsNone(d["metaphor"])
        self.assertIsNone(d["governing_text_excerpt"])
        self.assertIsNone(d["signing_authentication_process"])
        self.assertEqual(d["how_to_recognize"], [])
        self.assertEqual(d["fact_sensitivity"], [])

    def test_metaphor_field_is_structurally_distinct_from_governing_text(self) -> None:
        """The metaphor must live in its own field/type and must never be
        what a caller reads when they ask for the governing text -- this is
        the mechanism, not just a convention, that keeps a simplified
        illustration from silently replacing the actual rule."""
        contract = PedagogicalContract(
            contract_id="test-contract-3",
            subject_name="Test Rule 3",
            subject_kind=PedagogicalSubjectKind.RULE,
            authority_citation="Va. Code Ann. § 1-3",
            authority_type=AuthorityType.STATUTE,
            jurisdiction="Commonwealth of Virginia",
            verification_status=VerificationStatus.SOURCE_VERIFIED,
            confidence_label=ConfidenceLabel.VERIFIED,
            governing_text_excerpt="Actual statutory language.",
            metaphor=PedagogicalMetaphor(illustration="A simplified teaching story."),
        )
        d = contract.to_dict()
        self.assertNotEqual(d["governing_text_excerpt"], d["metaphor"]["illustration"])
        self.assertIn("Actual statutory language.", d["governing_text_excerpt"])
        self.assertNotIn("simplified teaching story", d["governing_text_excerpt"])
        self.assertTrue(d["metaphor"]["is_pedagogical_only"])


if __name__ == "__main__":
    unittest.main()

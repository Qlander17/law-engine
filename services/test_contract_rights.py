from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import contract_rights as cr
from services.retrieval import get_section


class ContractAnatomyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.anatomy = cr.build_laptop_sale_contract_anatomy()

    def test_agreement_description_traces_to_a_real_ingested_section(self) -> None:
        section = get_section(self.anatomy.section_id)
        self.assertIsNotNone(section, f"cites unknown section {self.anatomy.section_id!r}")
        self.assertEqual(section["citation"], self.anatomy.citation)
        self.assertIn(section["citation"], self.anatomy.the_agreement_description)

    def test_document_agreement_and_rights_are_distinct_fields(self) -> None:
        self.assertNotEqual(self.anatomy.physical_document_description, self.anatomy.the_agreement_description)
        self.assertGreater(len(self.anatomy.rights_and_obligations), 0)
        self.assertTrue(self.anatomy.payment_rights_description)

    def test_ucc_classifications_cover_all_four_categories(self) -> None:
        categories = {c.category for c in self.anatomy.ucc_payment_right_classifications}
        self.assertEqual(categories, {"account", "chattel paper", "instrument", "payment intangible"})

    def test_ucc_classifications_disclose_ungrounded_article_9_status(self) -> None:
        self.assertIn("not yet ingested", self.anatomy.ucc_classification_grounding_note.lower())

    def test_build_raises_on_missing_section(self) -> None:
        original = cr.get_section
        try:
            cr.get_section = lambda section_id: None
            with self.assertRaises(cr.ContractRightsError):
                cr.build_laptop_sale_contract_anatomy()
        finally:
            cr.get_section = original

    def test_to_dict_round_trips(self) -> None:
        d = self.anatomy.to_dict()
        self.assertEqual(d["contract_id"], "laptop-sale-contract-anatomy-v1")
        self.assertEqual(len(d["ucc_payment_right_classifications"]), 4)
        self.assertEqual(d["citation"], self.anatomy.citation)
        self.assertIsInstance(d["rights_and_obligations"], list)


if __name__ == "__main__":
    unittest.main()

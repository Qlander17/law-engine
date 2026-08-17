from __future__ import annotations

import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import obligation_perspective as op
from services.retrieval import get_section

# Loose or legally-incorrect asset/liability language this module must
# never produce -- an obligation is a liability to the obligor and a
# right/asset to the obligee at the same time, never both to the same
# party in the same breath.
BANNED_PHRASES = [
    "equity in a liability",
    "asset in a liability",
    "liability that is also an asset to the same party",
]


class ObligationPerspectiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.perspectives = op.build_all_perspectives()

    def test_at_least_four_perspectives_across_distinct_instruments(self) -> None:
        self.assertGreaterEqual(len(self.perspectives), 4)
        instrument_ids = {p.instrument_id for p in self.perspectives}
        self.assertEqual(
            len(instrument_ids), len(self.perspectives),
            "expected distinct instrument_id values across perspectives",
        )

    def test_every_grounded_perspective_traces_to_a_real_ingested_section(self) -> None:
        for perspective in self.perspectives:
            if not perspective.grounded_in_ingested_text:
                continue
            self.assertIsNotNone(
                perspective.citation,
                f"{perspective.instrument_id} claims grounding but has no citation",
            )
            self.assertIsNotNone(
                perspective.section_id,
                f"{perspective.instrument_id} claims grounding but has no section_id",
            )
            section = get_section(perspective.section_id)
            self.assertIsNotNone(
                section, f"{perspective.instrument_id} cites unknown section {perspective.section_id!r}"
            )
            self.assertEqual(
                section["citation"], perspective.citation,
                f"{perspective.instrument_id}'s citation does not match the real ingested section's citation",
            )

    def test_every_ungrounded_perspective_discloses_it_explicitly(self) -> None:
        for perspective in self.perspectives:
            if perspective.grounded_in_ingested_text:
                continue
            self.assertIsNone(perspective.citation)
            self.assertIsNone(perspective.section_id)
            self.assertTrue(
                perspective.grounding_note,
                f"{perspective.instrument_id} is ungrounded but has no grounding_note",
            )
            self.assertTrue(
                "not" in perspective.grounding_note.lower(),
                f"{perspective.instrument_id}'s grounding_note should explicitly say what is not grounded",
            )

    def test_promissory_note_is_ungrounded_article_3(self) -> None:
        note = next(p for p in self.perspectives if p.instrument_id == "promissory-note-unsecured-v1")
        self.assertFalse(note.grounded_in_ingested_text)
        self.assertIsNone(note.citation)
        self.assertIn("article 3", note.grounding_note.lower())
        self.assertEqual(note.role(op.PerspectiveRole.OBLIGOR).description[:8], "Borrower")
        self.assertEqual(note.role(op.PerspectiveRole.OBLIGEE).description[:6], "Lender")

    def test_lease_is_ungrounded_article_2a(self) -> None:
        lease = next(p for p in self.perspectives if p.instrument_id == "equipment-lease-obligation-v1")
        self.assertFalse(lease.grounded_in_ingested_text)
        self.assertIsNone(lease.citation)
        self.assertIn("2a", lease.grounding_note.lower())
        self.assertIn("no ingested content", lease.grounding_note.lower())

    def test_security_interest_grounded_in_real_article_9_attachment_section(self) -> None:
        interest = next(
            p for p in self.perspectives if p.instrument_id == "security-interest-equipment-pmsi-v1"
        )
        self.assertTrue(interest.grounded_in_ingested_text)
        section = get_section("8.9A-203")
        self.assertIsNotNone(section)
        self.assertEqual(interest.citation, section["citation"])
        self.assertEqual(interest.section_id, "8.9A-203")
        # The PMSI-priority claim (a second real citation, embedded in
        # priority_notes rather than the single citation field) must also
        # trace to a real ingested section, not merely be asserted.
        pmsi_section = get_section("8.9A-324")
        self.assertIsNotNone(pmsi_section)
        self.assertIn(pmsi_section["citation"], interest.priority_notes)

    def test_security_interest_correctly_identifies_debtor_and_secured_party(self) -> None:
        interest = next(
            p for p in self.perspectives if p.instrument_id == "security-interest-equipment-pmsi-v1"
        )
        debtor = interest.role(op.PerspectiveRole.DEBTOR)
        secured_party = interest.role(op.PerspectiveRole.SECURED_PARTY)
        self.assertIn("business", debtor.description.lower())
        self.assertIn("granted the security interest", debtor.description.lower())
        self.assertIn("dealer", secured_party.description.lower())
        self.assertIn("security interest", secured_party.description.lower())
        # DEBTOR/SECURED_PARTY must be distinct roles from the generic
        # OBLIGOR/OBLIGEE pair also present on this same instrument --
        # the whole point being the more specific UCC vocabulary is used,
        # not silently collapsed into the generic pair.
        roles_present = {r.role for r in interest.role_assignments}
        self.assertIn(op.PerspectiveRole.DEBTOR, roles_present)
        self.assertIn(op.PerspectiveRole.SECURED_PARTY, roles_present)
        self.assertIn(op.PerspectiveRole.OBLIGOR, roles_present)
        self.assertIn(op.PerspectiveRole.OBLIGEE, roles_present)

    def test_security_interest_is_secured_with_collateral(self) -> None:
        interest = next(
            p for p in self.perspectives if p.instrument_id == "security-interest-equipment-pmsi-v1"
        )
        self.assertTrue(interest.is_secured)
        self.assertIsNotNone(interest.collateral_description)
        self.assertIn("equipment", interest.collateral_description.lower())

    def test_lease_is_not_secured(self) -> None:
        lease = next(p for p in self.perspectives if p.instrument_id == "equipment-lease-obligation-v1")
        self.assertFalse(lease.is_secured)
        self.assertIsNone(lease.collateral_description)

    def test_account_receivable_account_definition_traces_to_real_paragraph_text(self) -> None:
        """Verifies -- rather than assumes -- that "Account" is really
        defined in 8.9A-102's ingested paragraph text, since the
        section's defined_terms convenience index does NOT separately
        list "Account" as its own entry (it lists "Account debtor" but
        not "Account")."""
        section = get_section("8.9A-102")
        self.assertIsNotNone(section)
        self.assertNotIn(
            "Account", section["defined_terms"],
            "this test's premise (defined_terms omits bare 'Account') no longer holds -- "
            "re-examine whether obligation_perspective.py's grounding_note explanation is still accurate",
        )
        self.assertIn("Account debtor", section["defined_terms"])
        account_paragraph = next(
            (p for p in section["paragraphs"] if p.startswith('(2) "Account,"')), None
        )
        self.assertIsNotNone(
            account_paragraph, "8.9A-102's ingested paragraphs no longer contain the 'Account' definition"
        )
        self.assertIn("right to payment of a monetary obligation", account_paragraph)
        account_debtor_paragraph = next(
            (p for p in section["paragraphs"] if p.startswith('(3) "Account debtor"')), None
        )
        self.assertIsNotNone(account_debtor_paragraph)
        self.assertIn("obligated on an account", account_debtor_paragraph)

    def test_account_receivable_grounded_in_real_8_9a_102(self) -> None:
        receivable = next(
            p for p in self.perspectives if p.instrument_id == "account-receivable-account-debtor-v1"
        )
        self.assertTrue(receivable.grounded_in_ingested_text)
        section = get_section("8.9A-102")
        self.assertEqual(receivable.citation, section["citation"])
        self.assertEqual(receivable.section_id, "8.9A-102")

    def test_account_receivable_carries_assignor_assignee_and_account_debtor_roles(self) -> None:
        receivable = next(
            p for p in self.perspectives if p.instrument_id == "account-receivable-account-debtor-v1"
        )
        roles_present = {r.role for r in receivable.role_assignments}
        self.assertIn(op.PerspectiveRole.ACCOUNT_DEBTOR, roles_present)
        self.assertIn(op.PerspectiveRole.ASSIGNOR, roles_present)
        self.assertIn(op.PerspectiveRole.ASSIGNEE, roles_present)

    def test_all_seven_perspective_roles_appear_somewhere_across_examples(self) -> None:
        all_roles = set()
        for perspective in self.perspectives:
            all_roles.update(r.role for r in perspective.role_assignments)
        self.assertEqual(all_roles, set(op.PerspectiveRole))

    def test_role_raises_for_role_not_assigned_on_instrument(self) -> None:
        note = next(p for p in self.perspectives if p.instrument_id == "promissory-note-unsecured-v1")
        with self.assertRaises(op.ObligationPerspectiveError):
            note.role(op.PerspectiveRole.SECURED_PARTY)

    def test_build_all_perspectives_raises_on_missing_section(self) -> None:
        original = op.get_section
        try:
            op.get_section = lambda section_id: None
            with self.assertRaises(op.ObligationPerspectiveError):
                op.build_security_interest_perspective()
            with self.assertRaises(op.ObligationPerspectiveError):
                op.build_account_receivable_perspective()
        finally:
            op.get_section = original

    def test_to_dict_round_trips_promissory_note(self) -> None:
        note = next(p for p in self.perspectives if p.instrument_id == "promissory-note-unsecured-v1")
        d = note.to_dict()
        self.assertEqual(d["instrument_id"], "promissory-note-unsecured-v1")
        self.assertEqual(d["is_secured"], False)
        self.assertEqual(d["grounded_in_ingested_text"], False)
        self.assertIsInstance(d["role_assignments"], list)
        self.assertEqual(d["role_assignments"][0]["role"], "OBLIGOR")
        self.assertIsInstance(d["applicable_ucc_articles"], list)

    def test_to_dict_round_trips_security_interest(self) -> None:
        interest = next(
            p for p in self.perspectives if p.instrument_id == "security-interest-equipment-pmsi-v1"
        )
        d = interest.to_dict()
        self.assertEqual(d["instrument_id"], "security-interest-equipment-pmsi-v1")
        self.assertEqual(d["is_secured"], True)
        self.assertEqual(d["citation"], interest.citation)
        role_values = {r["role"] for r in d["role_assignments"]}
        self.assertIn("DEBTOR", role_values)
        self.assertIn("SECURED_PARTY", role_values)

    def test_no_perspective_uses_banned_asset_liability_conflation_phrases(self) -> None:
        for perspective in self.perspectives:
            combined_text = " ".join(
                [
                    perspective.what_the_obligor_owns_or_owes,
                    perspective.what_the_obligee_is_owed_or_owns,
                    perspective.the_right_the_obligee_has_against_the_obligor,
                    perspective.the_right_if_any_the_obligor_has_against_the_obligee,
                    perspective.transfer_notes,
                    perspective.priority_notes,
                    perspective.what_changes_on_assignment_or_transfer,
                    perspective.what_happens_on_default,
                    perspective.grounding_note,
                    " ".join(a.description for a in perspective.role_assignments),
                ]
            ).lower()
            for banned in BANNED_PHRASES:
                self.assertNotIn(
                    banned, combined_text,
                    f"{perspective.instrument_id} uses banned asset/liability-conflating phrase {banned!r}",
                )

    def test_all_perspectives_have_non_empty_required_narrative_fields(self) -> None:
        for perspective in self.perspectives:
            self.assertTrue(perspective.instrument_name)
            self.assertTrue(perspective.what_the_obligor_owns_or_owes)
            self.assertTrue(perspective.what_the_obligee_is_owed_or_owns)
            self.assertTrue(perspective.the_right_the_obligee_has_against_the_obligor)
            self.assertTrue(perspective.the_right_if_any_the_obligor_has_against_the_obligee)
            self.assertTrue(perspective.evidencing_document)
            self.assertTrue(perspective.transfer_notes)
            self.assertTrue(perspective.priority_notes)
            self.assertTrue(perspective.what_changes_on_assignment_or_transfer)
            self.assertTrue(perspective.what_happens_on_default)
            self.assertGreater(len(perspective.applicable_ucc_articles), 0)
            self.assertGreater(len(perspective.role_assignments), 0)
            self.assertTrue(perspective.grounding_note)


if __name__ == "__main__":
    unittest.main()

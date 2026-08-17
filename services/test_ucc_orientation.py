from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import ucc_orientation as uo
from services.asset_intelligence import AssetType
from services.document_intelligence import DocumentFamily

# A real Model UCC Article designation looks like "UCC Article <number>[letter]"
# -- optionally followed by explanatory text (e.g. Article 6's withdrawal note).
# It must NOT look like a fabricated specific section citation (e.g. "8.2-999"
# or "Section 9-999"), which this module must never invent.
_REAL_ARTICLE_DESIGNATION = re.compile(r"^UCC Article \d+A?\b")
_INVENTED_SECTION_PATTERN = re.compile(r"\bSection\s+\d|§\s*\d")


class UccOrientationArticleOverviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.articles = uo.build_all_article_overviews()

    def test_exactly_eleven_articles(self) -> None:
        self.assertEqual(len(self.articles), 11)

    def test_articles_are_distinct_and_match_enum(self) -> None:
        seen = {a.article for a in self.articles}
        self.assertEqual(len(seen), 11)
        self.assertEqual(seen, set(uo.UccArticle))

    def test_only_article_2_and_article_9_have_ingested_coverage(self) -> None:
        covered = {a.article for a in self.articles if a.has_ingested_coverage}
        self.assertEqual(covered, {uo.UccArticle.ARTICLE_2, uo.UccArticle.ARTICLE_9})

    def test_every_article_has_a_non_empty_real_world_example(self) -> None:
        for overview in self.articles:
            self.assertTrue(
                overview.real_world_example and overview.real_world_example.strip(),
                f"{overview.article} has no real_world_example",
            )

    def test_every_article_has_non_empty_core_narrative_fields(self) -> None:
        for overview in self.articles:
            self.assertTrue(overview.subject_matter.strip(), overview.article)
            self.assertTrue(overview.why_separate_article.strip(), overview.article)
            self.assertTrue(overview.practical_problem_solved.strip(), overview.article)
            self.assertTrue(overview.cross_article_connection_note.strip(), overview.article)
            self.assertTrue(overview.virginia_enactment_note.strip(), overview.article)
            self.assertTrue(overview.ingested_coverage_note.strip(), overview.article)
            self.assertTrue(overview.asset_document_mapping_note.strip(), overview.article)

    def test_model_uc_citations_look_real_not_invented(self) -> None:
        for overview in self.articles:
            self.assertRegex(
                overview.model_uc_citation,
                _REAL_ARTICLE_DESIGNATION,
                f"{overview.article}'s model_uc_citation does not look like a real Article designation",
            )
            self.assertNotRegex(
                overview.model_uc_citation,
                _INVENTED_SECTION_PATTERN,
                f"{overview.article}'s model_uc_citation looks like a fabricated section citation",
            )

    def test_connects_to_article_is_a_different_real_article(self) -> None:
        for overview in self.articles:
            self.assertIsInstance(overview.connects_to_article, uo.UccArticle)
            self.assertNotEqual(overview.connects_to_article, overview.article)

    def test_virginia_enactment_titles_follow_title_8_pattern_except_repealed_article_6(self) -> None:
        for overview in self.articles:
            if overview.article == uo.UccArticle.ARTICLE_6:
                self.assertIsNone(overview.virginia_enactment_title)
                self.assertIn("no current title 8.6", overview.virginia_enactment_note.lower())
                continue
            self.assertIsNotNone(overview.virginia_enactment_title)
            self.assertTrue(overview.virginia_enactment_title.startswith("Title 8."))

    def test_article_1_uses_title_8_1a_not_bare_8_1(self) -> None:
        article_1 = next(a for a in self.articles if a.article == uo.UccArticle.ARTICLE_1)
        self.assertEqual(article_1.virginia_enactment_title, "Title 8.1A (Uniform Commercial Code -- General Provisions)")

    def test_article_2_and_9_enactment_titles_match_real_ingestion_modules(self) -> None:
        article_2 = next(a for a in self.articles if a.article == uo.UccArticle.ARTICLE_2)
        article_9 = next(a for a in self.articles if a.article == uo.UccArticle.ARTICLE_9)
        self.assertIn("Title 8.2 ", article_2.virginia_enactment_title)
        self.assertIn("Title 8.9A", article_9.virginia_enactment_title)

    def test_ingested_coverage_note_counts_are_live_not_hardcoded_stale(self) -> None:
        article_2 = next(a for a in self.articles if a.article == uo.UccArticle.ARTICLE_2)
        article_9 = next(a for a in self.articles if a.article == uo.UccArticle.ARTICLE_9)
        real_article_2_count = uo._count_ingested_sections("8.2-")
        real_article_9_count = uo._count_ingested_sections("8.9A-")
        self.assertGreater(real_article_2_count, 0)
        self.assertGreater(real_article_9_count, 0)
        self.assertIn(str(real_article_2_count), article_2.ingested_coverage_note)
        self.assertIn(str(real_article_9_count), article_9.ingested_coverage_note)

    def test_related_asset_types_are_real_existing_enum_members(self) -> None:
        for overview in self.articles:
            for asset_type in overview.related_asset_types:
                self.assertIsInstance(asset_type, AssetType)
                self.assertIn(asset_type, AssetType)

    def test_related_document_families_are_real_existing_enum_members(self) -> None:
        for overview in self.articles:
            for family in overview.related_document_families:
                self.assertIsInstance(family, DocumentFamily)
                self.assertIn(family, DocumentFamily)

    def test_empty_asset_or_document_mapping_is_explicitly_disclosed(self) -> None:
        for overview in self.articles:
            if not overview.related_asset_types and not overview.related_document_families:
                self.assertTrue(
                    overview.asset_document_mapping_note,
                    f"{overview.article} has no asset/document mapping and no disclosure note",
                )

    def test_article_9_related_assets_cover_core_collateral_types(self) -> None:
        article_9 = next(a for a in self.articles if a.article == uo.UccArticle.ARTICLE_9)
        self.assertIn(AssetType.EQUIPMENT, article_9.related_asset_types)
        self.assertIn(AssetType.INVENTORY, article_9.related_asset_types)
        self.assertIn(DocumentFamily.SECURITY_AGREEMENT, article_9.related_document_families)
        self.assertIn(DocumentFamily.FINANCING_STATEMENT, article_9.related_document_families)

    def test_article_2_connects_to_article_9_and_vice_versa(self) -> None:
        article_2 = next(a for a in self.articles if a.article == uo.UccArticle.ARTICLE_2)
        article_9 = next(a for a in self.articles if a.article == uo.UccArticle.ARTICLE_9)
        self.assertEqual(article_2.connects_to_article, uo.UccArticle.ARTICLE_9)
        self.assertEqual(article_9.connects_to_article, uo.UccArticle.ARTICLE_2)

    def test_article_6_discloses_repeal_and_is_not_presented_as_still_standard(self) -> None:
        article_6 = next(a for a in self.articles if a.article == uo.UccArticle.ARTICLE_6)
        self.assertFalse(article_6.has_ingested_coverage)
        self.assertIsNone(article_6.virginia_enactment_title)
        combined = (article_6.model_uc_citation + " " + article_6.virginia_enactment_note).lower()
        self.assertTrue("repeal" in combined or "withdrawn" in combined)

    def test_to_dict_round_trips_article_overview(self) -> None:
        article_9 = next(a for a in self.articles if a.article == uo.UccArticle.ARTICLE_9)
        d = article_9.to_dict()
        self.assertEqual(d["article"], "9")
        self.assertEqual(d["has_ingested_coverage"], True)
        self.assertIsInstance(d["related_asset_types"], list)
        self.assertIn("EQUIPMENT", d["related_asset_types"])
        self.assertIsInstance(d["related_document_families"], list)
        self.assertIn("SECURITY_AGREEMENT", d["related_document_families"])


class UccOrientationTopLevelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.orientation = uo.build_ucc_orientation()

    def test_top_level_narrative_fields_are_non_empty(self) -> None:
        self.assertTrue(self.orientation.why_uniform_commercial_law_exists.strip())
        self.assertTrue(self.orientation.what_uniform_means_in_practice.strip())
        self.assertTrue(self.orientation.is_the_ucc_itself_binding_law.strip())
        self.assertTrue(self.orientation.why_split_into_articles.strip())
        self.assertTrue(self.orientation.article_12_note.strip())

    def test_orientation_contains_all_eleven_articles(self) -> None:
        self.assertEqual(len(self.orientation.articles), 11)

    def test_article_12_note_mentions_article_12_and_virginia_title_8_12(self) -> None:
        note = self.orientation.article_12_note.lower()
        self.assertIn("article 12", note)
        self.assertIn("8.12", note)
        self.assertIn("not", note)

    def test_article_12_is_not_among_the_eleven_full_overviews(self) -> None:
        self.assertNotIn("12", [a.article.value for a in self.orientation.articles])

    def test_is_ucc_binding_law_narrative_cites_georgia_v_pro(self) -> None:
        self.assertIn("Public.Resource.Org", self.orientation.is_the_ucc_itself_binding_law)

    def test_what_uniform_means_narrative_distinguishes_model_from_enactment(self) -> None:
        text = self.orientation.what_uniform_means_in_practice.lower()
        self.assertIn("model", text)
        self.assertIn("enact", text)

    def test_sources_are_non_empty_and_reference_real_authoritative_domains(self) -> None:
        self.assertGreaterEqual(len(self.orientation.sources), 5)
        joined = " ".join(self.orientation.sources)
        self.assertIn("uniformlaws.org", joined)
        self.assertIn("law.cornell.edu", joined)
        self.assertIn("law.lis.virginia.gov", joined)

    def test_get_article_returns_the_right_overview(self) -> None:
        article_9 = self.orientation.get_article(uo.UccArticle.ARTICLE_9)
        self.assertEqual(article_9.article, uo.UccArticle.ARTICLE_9)
        self.assertTrue(article_9.has_ingested_coverage)

    def test_get_article_raises_for_article_12(self) -> None:
        with self.assertRaises(uo.UccOrientationError):
            self.orientation.get_article("12")  # type: ignore[arg-type]

    def test_to_dict_round_trips_top_level_orientation(self) -> None:
        d = self.orientation.to_dict()
        self.assertEqual(len(d["articles"]), 11)
        self.assertIsInstance(d["sources"], list)
        self.assertIn("article_12_note", d)
        self.assertTrue(d["why_uniform_commercial_law_exists"])


if __name__ == "__main__":
    unittest.main()

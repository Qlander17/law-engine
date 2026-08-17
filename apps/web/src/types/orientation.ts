// Law Engine -- typed UCC orientation model (Live Run 1.45, Mission
// 5/V1). Mirrors law-engine/services/ucc_orientation.py's dataclasses
// 1:1, same Python-owns-the-data / TypeScript-only-types-it boundary
// as types/statute.ts and types/lifecycle.ts.

export interface ArticleOverview {
  article: string;
  display_name: string;
  model_uc_citation: string;
  subject_matter: string;
  why_separate_article: string;
  practical_problem_solved: string;
  real_world_example: string;
  connects_to_article: string;
  cross_article_connection_note: string;
  virginia_enactment_title: string | null;
  virginia_enactment_note: string;
  has_ingested_coverage: boolean;
  ingested_coverage_note: string;
  related_asset_types: string[];
  related_document_families: string[];
  asset_document_mapping_note: string;
}

export interface UccOrientation {
  why_uniform_commercial_law_exists: string;
  what_uniform_means_in_practice: string;
  is_the_ucc_itself_binding_law: string;
  why_split_into_articles: string;
  articles: ArticleOverview[];
  article_12_note: string;
  sources: string[];
}

// Law Engine -- typed legal-domain models (Live Run 1.37, Mission 19).
// Deliberately mirrors the real Python StatuteSection/SourceManifest
// shapes 1:1 (law-engine/services/models.py) -- this is the clean
// Python<->TypeScript boundary (Mission 20): Python owns ingestion and
// writes the real, normalized JSON; TypeScript only ever reads and
// types it, never re-derives or duplicates the ingestion logic.

export type VerificationStatus =
  | "DISCOVERED"
  | "RETRIEVED"
  | "SOURCE_VERIFIED"
  | "AUTHORITY_CLASSIFIED"
  | "CURRENTNESS_CHECKED"
  | "CROSS_VERIFIED"
  | "TRUSTED_FOR_ANALYSIS"
  | "CONFLICT"
  | "UNKNOWN";

export type AuthorityType =
  | "CONSTITUTION"
  | "STATUTE"
  | "REGULATION"
  | "COURT_RULE"
  | "CASE"
  | "TREATY"
  | "TREATISE"
  | "SECONDARY_AUTHORITY"
  | "CLAIM_ALTERNATIVE_THEORY";

export interface StatuteSection {
  section_id: string;
  title: string;
  paragraphs: string[];
  citation: string;
  source_document_id: string;
  topics: string[];
  cross_references: string[];
  defined_terms: string[];
}

export interface SourceManifest {
  document_id: string;
  title: string;
  authority_type: AuthorityType;
  jurisdiction: string;
  citation: string;
  official_source_url: string;
  publisher: string;
  retrieval_timestamp: string;
  sha256_hash: string;
  verification_status: VerificationStatus;
  court: string | null;
  publication_or_effective_date: string | null;
  version: string;
  superseded: boolean;
  licensing_status: string;
  topics: string[];
  cross_references: string[];
  notes: string;
}

export type StatuteSectionMap = Record<string, StatuteSection>;

"""Law Engine -- Article 9 (Secured Transactions) ingestion (Live Run
1.39, Mission 14). Same real, verbatim-sourcing discipline as
services/ingestion.py (Article 2): read the immutable raw extract in
library/source/ucc/, build real StatuteSection records, write a real
SHA-256-hashed SourceManifest. A parallel module rather than an extension
of ingestion.py so Article 2's own ingestion path stays untouched and
independently re-runnable.

Real, disclosed subset: 13 of Article 9's real sections (Va. Code Ann.
Title 8.9A), chosen to cover the bounded set this run's directive named --
scope, definitions, security agreement effectiveness, attachment,
after-acquired property/future advances, perfection, the filing
requirement, priority (unperfected interests, conflicting interests, and
purchase-money priority specifically), and default (rights after default,
repossession, disposition of collateral) -- not the full Article (Title
8.9A runs through Part 8; this covers Parts 1-3 and 6 only, plus Part 5's
filing-trigger section).

Source: law.lis.virginia.gov, fetched directly (raw HTML, not an
AI-summarized or secondary source) on 2026-08-16. Virginia's own ENACTED
statute text is used, not the ALI/ULC "official" UCC text (separately
copyrighted) -- same sourcing rationale as Article 2's ingestion.py,
documented further in docs/ucc-source-licensing-audit.md.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.models import (
    AuthorityType,
    SourceLayer,
    SourceManifest,
    StatuteSection,
    VerificationStatus,
    now_iso,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "library" / "source" / "ucc"
NORMALIZED_DIR = ROOT / "library" / "normalized" / "ucc"
MANIFEST_DIR = ROOT / "library" / "manifests"

RAW_EXTRACT_PATH = SOURCE_DIR / "va-title-8.9a-article-9-raw-extract.json"

# Real, hand-assigned topic tags per section (thematic, matching this
# run's own bounded-subset framing) -- not invented content, just
# categorization of the real ingested text.
_SECTION_TOPICS: dict[str, list[str]] = {
    "8.9A-102": ["definitions", "scope"],
    "8.9A-109": ["scope"],
    "8.9A-201": ["security-agreement", "effectiveness"],
    "8.9A-203": ["attachment", "security-agreement"],
    "8.9A-204": ["attachment", "after-acquired-property", "future-advances"],
    "8.9A-308": ["perfection"],
    "8.9A-310": ["perfection", "filing"],
    "8.9A-317": ["priority", "unperfected-interests"],
    "8.9A-322": ["priority", "conflicting-interests"],
    "8.9A-324": ["priority", "purchase-money-security-interest"],
    "8.9A-601": ["default", "remedies"],
    "8.9A-609": ["default", "repossession"],
    "8.9A-610": ["default", "disposition-of-collateral"],
}

# Regex-extracted, not hand-invented: matches this title's own real
# '"Term" means' definitional pattern (seen directly in the ingested
# § 8.9A-102 text). Applied only to 102 since it's the definitions
# section; other sections' defined_terms stay empty unless they define a
# term inline themselves.
_DEFINED_TERM_PATTERN = re.compile(r'"([A-Z][A-Za-z /\'-]{1,40})"\s+means\b')

# Regex-extracted real in-text cross-references ("§ 8.9A-XXX" or
# "§§ 8.9A-XXX and 8.9A-YYY"-style single citations) -- not hand-curated,
# so a large section like 102 doesn't silently miss real references.
_CROSS_REF_PATTERN = re.compile(r"§\s*8\.9A-(\d+(?:\.\d+)?)")


def _sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_raw_extract() -> dict:
    return json.loads(RAW_EXTRACT_PATH.read_text(encoding="utf-8"))


def _extract_defined_terms(section_id: str, paragraphs: list[str]) -> list[str]:
    if section_id != "8.9A-102":
        return []
    full_text = " ".join(paragraphs)
    terms = sorted({m.group(1).strip() for m in _DEFINED_TERM_PATTERN.finditer(full_text)})
    return terms


def _extract_cross_references(section_id: str, paragraphs: list[str]) -> list[str]:
    full_text = " ".join(paragraphs)
    refs = sorted({f"8.9A-{m.group(1)}" for m in _CROSS_REF_PATTERN.finditer(full_text)} - {section_id})
    return refs


def normalize_sections() -> list[StatuteSection]:
    """Builds real StatuteSection records from the real raw extract.
    Never invents paragraph text -- every paragraph is the real, extracted
    statutory text captured this run. defined_terms/cross_references are
    regex-extracted from that same real text, not hand-invented."""
    raw = load_raw_extract()
    sections: list[StatuteSection] = []
    for sec_id, data in raw.items():
        paragraphs = data["paragraphs"]
        sections.append(
            StatuteSection(
                section_id=sec_id,
                title=data["title"],
                paragraphs=paragraphs,
                citation=f"Va. Code Ann. § {sec_id}",
                source_document_id="va-code-title-8.9a-article-9",
                topics=_SECTION_TOPICS.get(sec_id, []),
                cross_references=_extract_cross_references(sec_id, paragraphs),
                defined_terms=_extract_defined_terms(sec_id, paragraphs),
            )
        )
    return sections


def write_normalized_sections(sections: list[StatuteSection]) -> Path:
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = NORMALIZED_DIR / "article-9-sections.json"
    payload = {s.section_id: s.to_dict() for s in sections}
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def build_source_manifest() -> SourceManifest:
    """Real provenance manifest for the raw extract as a whole -- one
    immutable source document (the Virginia Title 8.9A extract), hashed
    for real, byte-level integrity checking."""
    raw_bytes = RAW_EXTRACT_PATH.read_bytes()
    manifest = SourceManifest(
        document_id="va-code-title-8.9a-article-9",
        title="Code of Virginia, Title 8.9A (Commercial Code -- Secured Transactions) sections (bounded cross-Article subset)",
        authority_type=AuthorityType.STATUTE,
        jurisdiction="Commonwealth of Virginia",
        citation=(
            "Va. Code Ann. §§ 8.9A-102, 8.9A-109, 8.9A-201, 8.9A-203, "
            "8.9A-204, 8.9A-308, 8.9A-310, 8.9A-317, 8.9A-322, 8.9A-324, "
            "8.9A-601, 8.9A-609, 8.9A-610"
        ),
        official_source_url="https://law.lis.virginia.gov/vacode/title8.9A/",
        publisher="Commonwealth of Virginia, Division of Legislative Automated Systems",
        retrieval_timestamp=now_iso(),
        sha256_hash=hashlib.sha256(raw_bytes).hexdigest(),
        verification_status=VerificationStatus.SOURCE_VERIFIED,
        licensing_status="public domain -- enacted state statute (edict of government), not the separately-copyrighted ALI/ULC official UCC text",
        source_layer=SourceLayer.ENACTMENT,
        topics=["ucc", "article-9", "secured-transactions", "commercial-law"],
        notes=(
            "Real, disclosed subset: 13 of Article 9's real sections "
            "(Title 8.9A runs through Part 8; this covers Parts 1-3 and "
            "6, plus one Part 5 filing-trigger section) -- chosen to "
            "support scope, definitions, security-agreement "
            "effectiveness, attachment, after-acquired property/future "
            "advances, perfection, the filing requirement, priority "
            "(including purchase-money priority), and default/remedies. "
            "Retrieved directly from law.lis.virginia.gov (raw HTML), "
            "not from any secondary or AI-summarized source, specifically "
            "to keep the statutory text verbatim. Ingested specifically "
            "to support a genuine Article 2 -> Article 9 cross-Article "
            "transaction lifecycle (see services/cross_article_lifecycle.py)."
        ),
    )
    return manifest


def write_manifest(manifest: SourceManifest) -> Path:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    out_path = MANIFEST_DIR / f"{manifest.document_id}.json"
    out_path.write_text(json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def run_ingestion() -> tuple[Path, Path]:
    """Real, idempotent ingestion entrypoint: normalize + write manifest.
    Returns (normalized_sections_path, manifest_path)."""
    sections = normalize_sections()
    normalized_path = write_normalized_sections(sections)
    manifest = build_source_manifest()
    manifest_path = write_manifest(manifest)
    return normalized_path, manifest_path


if __name__ == "__main__":
    normalized_path, manifest_path = run_ingestion()
    print(f"Normalized sections written to: {normalized_path}")
    print(f"Manifest written to: {manifest_path}")

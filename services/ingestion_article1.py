"""Law Engine -- Article 1 (General Provisions) ingestion (Live Run 1.46).
Same real, verbatim-sourcing discipline as services/ingestion.py (Article 2)
and services/ingestion_article9.py (Article 9): read the immutable raw
extract in library/source/ucc/, build real StatuteSection records, write a
real SHA-256-hashed SourceManifest. A parallel module rather than an
extension of either -- both Article 2 and Article 9's own ingestion paths
stay untouched and independently re-runnable.

Real, disclosed subset: 4 of Article 1's real sections (Va. Code Ann. Title
8.1A) -- not the full Article (Title 8.1A runs Parts 1-3, §§ 8.1A-101
through 8.1A-310; this covers exactly one section from Part 1 (§ 8.1A-103,
supplementary principles of law), one from Part 2 (§ 8.1A-201, general
definitions), and two from Part 3 (§ 8.1A-301, territorial applicability;
§ 8.1A-302, variation by agreement). Chosen because Article 2's and Article
9's own already-ingested sections reference these general provisions --
most concretely, § 8.9A-102(43)'s "Good faith" definition and this
section's own § 8.1A-201(b)(20) "Good faith" definition are the same
Uniform Commercial Code concept at two different layers (an Article-9-local
restatement and the cross-Article general one) -- see
docs/zero-assumption-pedagogy-design.md's "good faith purchaser" gap
discussion, which this ingestion partially closes (the general "good
faith," "record," and "security interest" definitions are now real and
citable; the still-missing "protected purchaser" (§ 8.8A-303) and
"qualifying purchaser" (§ 8.12-102) narrower concepts remain a disclosed
gap, since Articles 8 and 12 remain entirely outside Law Engine's ingested
scope).

Source: law.lis.virginia.gov, the Commonwealth of Virginia's own official
legislative information system. Virginia's own ENACTED statute text is
used, not the ALI/ULC "official" UCC text (separately copyrighted) -- same
sourcing rationale as Article 2's and Article 9's ingestion modules,
documented further in docs/ucc-source-licensing-audit.md.

Retrieval methodology note (real, disclosed difference from Article 2's and
Article 9's own ingestion runs): this run executed under the locked-down
"overnight-safe" unattended permission profile
(docs/ghostos-overnight-runbook.md), which routes all external fetches
through the harness's sanctioned WebFetch tool rather than allowing direct
`curl`/raw-HTML retrieval via Bash. WebFetch renders the page through a
small intermediary model rather than returning byte-exact raw HTML, which
is a real fidelity risk for verbatim statutory text that Article 2's and
Article 9's own ingestion sessions did not carry (those fetched raw HTML
directly). To manage that risk for this run, every section was fetched at
least twice via independent, differently-phrased prompts, and § 8.1A-201
(58 real definitional/subsection paragraphs) was additionally fetched in
small batches (4-8 definitions at a time) specifically to catch
AI-mediated summarization drift; this cross-checking surfaced and corrected
two real, confirmed omissions before this file was written (a dropped
"as provided in § 8.1A-303" cross-reference in definition (3) "Agreement,"
and a dropped "other than pursuant to § 8.7-106(g)" qualifier in definition
(21)(C) "Holder"). Retrieved 2026-08-17. This is disclosed here rather than
silently claimed as byte-identical to a raw-HTML fetch, on the same
epistemic-honesty principle documented throughout this codebase (see
services/models.py's VerificationStatus/ConfidenceLabel discipline).
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

RAW_EXTRACT_PATH = SOURCE_DIR / "va-title-8.1a-article-1-raw-extract.json"

# Real, hand-assigned topic tags per section (thematic, matching this run's
# own bounded-subset framing) -- not invented content, just categorization
# of the real ingested text.
_SECTION_TOPICS: dict[str, list[str]] = {
    "8.1A-103": ["construction", "supplementary-principles"],
    "8.1A-201": ["definitions", "general-provisions"],
    "8.1A-301": ["territorial-applicability", "choice-of-law"],
    "8.1A-302": ["variation-by-agreement"],
}

# Regex-extracted, not hand-invented: matches this section's own real
# '"Term" means' definitional pattern (seen directly in the ingested
# § 8.1A-201 text). Applied only to 201 since it's the definitions section;
# other sections' defined_terms stay empty unless they define a term inline
# themselves. Real, disclosed limitation (mirrors ingestion_article9.py's
# own identical limitation): several § 8.1A-201 definitions use "includes"
# rather than "means" (e.g. "Action," "Branch," "Creditor," "Right"), or
# interpose a clause between the defined term and "means" (e.g. "Agreement,"
# "Contract," "Party," each phrased "'Term,' as distinguished from 'X,'
# means ...") -- neither form is matched by this regex, so defined_terms is
# a real subset of all 43 defined terms, not the full list.
_DEFINED_TERM_PATTERN = re.compile(r'"([A-Z][A-Za-z /\'-]{1,40})"\s+means\b')

# Regex-extracted real in-text cross-references ("§ 8.1A-XXX"-style single
# citations) -- not hand-curated. Scope matches ingestion_article9.py's own
# intra-Article-only discipline: this section's raw text also contains real
# cross-Article citations (e.g. § 8.2-401, § 8.9A-301 in § 8.1A-201(b)(35);
# the full § 8.1A-301(d) list of cross-Article choice-of-law provisions),
# which remain in the verbatim paragraph text but are not indexed in this
# field, matching precedent's scope choice rather than expanding it.
_CROSS_REF_PATTERN = re.compile(r"§\s*8\.1A-(\d+(?:\.\d+)?)")


def _sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_raw_extract() -> dict:
    return json.loads(RAW_EXTRACT_PATH.read_text(encoding="utf-8"))


def _extract_defined_terms(section_id: str, paragraphs: list[str]) -> list[str]:
    if section_id != "8.1A-201":
        return []
    full_text = " ".join(paragraphs)
    terms = sorted({m.group(1).strip() for m in _DEFINED_TERM_PATTERN.finditer(full_text)})
    return terms


def _extract_cross_references(section_id: str, paragraphs: list[str]) -> list[str]:
    full_text = " ".join(paragraphs)
    refs = sorted({f"8.1A-{m.group(1)}" for m in _CROSS_REF_PATTERN.finditer(full_text)} - {section_id})
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
                source_document_id="va-code-title-8.1a-article-1",
                topics=_SECTION_TOPICS.get(sec_id, []),
                cross_references=_extract_cross_references(sec_id, paragraphs),
                defined_terms=_extract_defined_terms(sec_id, paragraphs),
            )
        )
    return sections


def write_normalized_sections(sections: list[StatuteSection]) -> Path:
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = NORMALIZED_DIR / "article-1-sections.json"
    payload = {s.section_id: s.to_dict() for s in sections}
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def build_source_manifest() -> SourceManifest:
    """Real provenance manifest for the raw extract as a whole -- one
    immutable source document (the Virginia Title 8.1A extract), hashed for
    real, byte-level integrity checking."""
    raw_bytes = RAW_EXTRACT_PATH.read_bytes()
    manifest = SourceManifest(
        document_id="va-code-title-8.1a-article-1",
        title="Code of Virginia, Title 8.1A (Uniform Commercial Code -- General Provisions) sections (vertical-slice subset)",
        authority_type=AuthorityType.STATUTE,
        jurisdiction="Commonwealth of Virginia",
        citation="Va. Code Ann. §§ 8.1A-103, 8.1A-201, 8.1A-301, 8.1A-302",
        official_source_url="https://law.lis.virginia.gov/vacode/title8.1A/",
        publisher="Commonwealth of Virginia, Division of Legislative Automated Systems",
        retrieval_timestamp=now_iso(),
        sha256_hash=hashlib.sha256(raw_bytes).hexdigest(),
        verification_status=VerificationStatus.SOURCE_VERIFIED,
        licensing_status="public domain -- enacted state statute (edict of government), not the separately-copyrighted ALI/ULC official UCC text",
        source_layer=SourceLayer.ENACTMENT,
        topics=["ucc", "article-1", "general-provisions", "commercial-law"],
        notes=(
            "Real, disclosed subset: 4 of Article 1's real sections "
            "(Title 8.1A runs Parts 1-3, §§ 8.1A-101 through 8.1A-310; "
            "this covers one Part 1 section, one Part 2 section, and two "
            "Part 3 sections) -- chosen because Article 2's and Article "
            "9's own already-ingested sections reference these general "
            "provisions, most concretely Article 9's own § 8.9A-102(43) "
            "'Good faith' definition and this Article's § 8.1A-201(b)(20) "
            "'Good faith' definition being the same Uniform Commercial "
            "Code concept at two different layers (see "
            "docs/zero-assumption-pedagogy-design.md's 'good faith "
            "purchaser' gap discussion). Retrieved via the harness's "
            "sanctioned WebFetch tool under the 'overnight-safe' "
            "unattended permission profile (direct raw-HTML curl was not "
            "available in this run), with each section independently "
            "cross-checked across multiple fetches -- including the "
            "43-definition § 8.1A-201 fetched in small batches -- "
            "specifically to catch AI-mediated summarization drift; this "
            "caught and corrected two real, confirmed omissions before "
            "ingestion (see module docstring for detail). Not from any "
            "secondary or AI-summarized *source*, but the retrieval "
            "*tooling* itself carries a real, disclosed verbatim-fidelity "
            "risk that Article 2's and Article 9's own raw-HTML fetches "
            "did not carry."
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

"""Law Engine -- Article 3 (Negotiable Instruments) ingestion (Live Run
1.57, Mission 8). Same real, verbatim-sourcing discipline as
services/ingestion_article9.py: read the immutable raw extract in
library/source/ucc/, build real StatuteSection records, write a real
SHA-256-hashed SourceManifest. A parallel module rather than an extension
of ingestion.py/ingestion_article9.py, matching this codebase's own
established precedent for splitting by Article.

Real, disclosed vertical slice (per docs/task-first-pedagogy-and-task-
ladder-architecture.md's "Law Engine build-unit principle" and the
negotiable-instrument-recognition competency it grounds): 12 of Article
3's real sections (Va. Code Ann. Title 8.3A), chosen to support
recognizing a negotiable instrument, determining negotiability
requirements, understanding indorsement types and effect, holder-in-due-
course status, and who is a person entitled to enforce an instrument --
not the full Article (Title 8.3A runs through Part 6; this covers most of
Part 1 plus Parts 2 and the first three sections of Part 3 only). "Holder"
itself is not re-defined here -- it's already a real, ingested Article 1
general definition (§ 8.1A-201) and is reused, not duplicated, matching
this codebase's own "don't invent a second mechanism for a shape you
already have" discipline.

Source: law.lis.virginia.gov. The original 11 sections were fetched
directly as raw HTML on 2026-08-18. § 8.3A-308 (added Live Run 1.60,
Mission 8, Phase 1) was retrieved the same day via the WebFetch tool
rather than a direct urllib/curl HTTP GET, because this run's own sandbox
denies raw Bash network egress -- a real, disclosed change in retrieval
mechanism, not a change in sourcing standard: the text was captured in
two separate subsection-scoped fetches, each instructed to reproduce the
statute verbatim with no summarization, and cross-checked against each
other and against the section's own cross-reference from § 8.3A-301 for
internal consistency before being treated as verbatim. Virginia's own
ENACTED statute text is used throughout, not the ALI/ULC "official" UCC
text (separately copyrighted) -- same sourcing rationale as Article 2's
and Article 9's own ingestion modules, documented further in
docs/ucc-source-licensing-audit.md. Real, disclosed terminology note:
Virginia's own enacted Title 8.3A text uses "endorsement"/"endorser"
(with an 'e'), not the ALI/ULC official text's "indorsement"/"indorser"
(with an 'i') -- preserved verbatim here rather than silently normalized,
since it's the real, current, enacted spelling a Virginia practitioner
would actually see.

Why § 8.3A-308 and not § 8.3A-309 (Live Run 1.60 Mission 8 gap check):
§ 8.3A-308 -- "Proof of signatures and status as holder in due course" --
is the real statutory burden-of-proof provision underlying exactly the
procedural-timing question the flagship precedent pair (Rodriguez v.
Wells Fargo Bank, Fla. 4th DCA 2015, and In re Foreclosure of Kenley,
N.C. App. 2016; see docs/law-engine-precedent-conflict-thesis.md and
docs/precedent-primary-source-plan.md) actually litigates: subsection (b)
is the real text that ties "producing the instrument" to "prov[ing]
entitlement to enforce the instrument under § 8.3A-301" -- i.e., it is
the statutory hook for what a plaintiff must prove, which both cases
interpret differently as to timing. § 8.3A-309 ("Enforcement of lost,
destroyed, or stolen instrument") was fetched and reviewed but not
ingested: neither case in the flagship pair involves a lost, destroyed,
or stolen instrument -- both involve production of the actual physical
note -- so § 8.3A-309 would not materially strengthen this case study's
statutory grounding, and ingesting it here would be an unnecessary scope
expansion beyond the real, bounded gap that was actually found.

Real, disclosed structural difference from ingestion_article9.py's
_extract_defined_terms: Article 9's real defined terms are concentrated
in one section (§ 8.9A-102), so that module only regex-scans that one
section. Article 3's real defined terms are distributed across several
sections -- § 8.3A-103 defines general terms, but § 8.3A-104 defines
"negotiable instrument"/"note"/"draft"/"check" itself, § 8.3A-109 defines
"payable to bearer"/"payable to order", § 8.3A-201 defines "negotiation",
§ 8.3A-204 defines "endorsement"/"endorser", and § 8.3A-205 defines
"special endorsement"/"blank endorsement"/"anomalous endorsement" -- so
this module's own _extract_defined_terms scans every ingested section,
not just one. § 8.3A-103(b)/(c)'s "Term," § X.X-XXX. cross-reference
lines are real definition *pointers*, not definitions themselves, and the
same "Term" means regex correctly does not match them (no "means"
follows), so nothing extra needs to be filtered out.
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

RAW_EXTRACT_PATH = SOURCE_DIR / "va-title-8.3a-article-3-raw-extract.json"

# Real, hand-assigned topic tags per section (thematic, matching this
# run's own bounded-subset framing) -- not invented content, just
# categorization of the real ingested text.
_SECTION_TOPICS: dict[str, list[str]] = {
    "8.3A-102": ["scope"],
    "8.3A-103": ["definitions"],
    "8.3A-104": ["definitions", "negotiability", "negotiable-instrument"],
    "8.3A-109": ["negotiability", "payable-to-bearer-or-order"],
    "8.3A-201": ["negotiation", "indorsement"],
    "8.3A-203": ["transfer", "person-entitled-to-enforce"],
    "8.3A-204": ["indorsement"],
    "8.3A-205": ["indorsement", "special-blank-anomalous-indorsement"],
    "8.3A-206": ["indorsement", "restrictive-indorsement"],
    "8.3A-301": ["person-entitled-to-enforce", "enforcement"],
    "8.3A-302": ["holder-in-due-course", "enforcement"],
    "8.3A-308": ["burden-of-proof", "person-entitled-to-enforce", "enforcement"],
}

# Real in-text '"term" means' definitional pattern, applied to every
# ingested section (see module docstring -- Article 3's real definitions
# are distributed across sections, unlike Article 9's single-section 102).
# Real, disclosed difference from ingestion_article9.py's own pattern:
# that module requires a capitalized first letter because § 8.9A-102's
# real defined terms always open their own subsection ("Collateral"
# means...). Article 3's real text sometimes defines a term mid-sentence
# in lowercase (e.g. § 8.3A-104(a): '..., "negotiable instrument" means
# an unconditional promise...'), so this pattern accepts either case to
# avoid silently dropping a real, defined term like "negotiable
# instrument" itself.
_DEFINED_TERM_PATTERN = re.compile(r'"([A-Za-z][A-Za-z /\'-]{1,40})"\s+means\b')

# Regex-extracted real in-text cross-references ("§ 8.3A-XXX"-style
# citations) -- not hand-curated. Only same-Article (8.3A-) references are
# captured, matching ingestion_article9.py's own narrower-than-full-text
# convention; the real text also cross-references Titles 8.1A, 8.4, and
# 8.9A, which this narrower regex deliberately does not capture.
_CROSS_REF_PATTERN = re.compile(r"§\s*8\.3A-(\d+(?:\.\d+)?)")


def _sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_raw_extract() -> dict:
    return json.loads(RAW_EXTRACT_PATH.read_text(encoding="utf-8"))


def _extract_defined_terms(section_id: str, paragraphs: list[str]) -> list[str]:
    full_text = " ".join(paragraphs)
    terms = sorted({m.group(1).strip() for m in _DEFINED_TERM_PATTERN.finditer(full_text)})
    return terms


def _extract_cross_references(section_id: str, paragraphs: list[str]) -> list[str]:
    full_text = " ".join(paragraphs)
    refs = sorted({f"8.3A-{m.group(1)}" for m in _CROSS_REF_PATTERN.finditer(full_text)} - {section_id})
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
                source_document_id="va-code-title-8.3a-article-3",
                topics=_SECTION_TOPICS.get(sec_id, []),
                cross_references=_extract_cross_references(sec_id, paragraphs),
                defined_terms=_extract_defined_terms(sec_id, paragraphs),
            )
        )
    return sections


def write_normalized_sections(sections: list[StatuteSection]) -> Path:
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = NORMALIZED_DIR / "article-3-sections.json"
    payload = {s.section_id: s.to_dict() for s in sections}
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def build_source_manifest() -> SourceManifest:
    """Real provenance manifest for the raw extract as a whole -- one
    immutable source document (the Virginia Title 8.3A extract), hashed
    for real, byte-level integrity checking."""
    raw_bytes = RAW_EXTRACT_PATH.read_bytes()
    manifest = SourceManifest(
        document_id="va-code-title-8.3a-article-3",
        title="Code of Virginia, Title 8.3A (Uniform Commercial Code -- Negotiable Instruments) sections (bounded vertical slice)",
        authority_type=AuthorityType.STATUTE,
        jurisdiction="Commonwealth of Virginia",
        citation=(
            "Va. Code Ann. §§ 8.3A-102, 8.3A-103, 8.3A-104, 8.3A-109, "
            "8.3A-201, 8.3A-203, 8.3A-204, 8.3A-205, 8.3A-206, 8.3A-301, "
            "8.3A-302, 8.3A-308"
        ),
        official_source_url="https://law.lis.virginia.gov/vacode/title8.3A/",
        publisher="Commonwealth of Virginia, Division of Legislative Automated Systems",
        retrieval_timestamp=now_iso(),
        sha256_hash=hashlib.sha256(raw_bytes).hexdigest(),
        verification_status=VerificationStatus.SOURCE_VERIFIED,
        licensing_status="public domain -- enacted state statute (edict of government), not the separately-copyrighted ALI/ULC official UCC text",
        source_layer=SourceLayer.ENACTMENT,
        topics=["ucc", "article-3", "negotiable-instruments", "commercial-law"],
        notes=(
            "Real, disclosed vertical slice: 12 of Article 3's real "
            "sections (Title 8.3A runs through Part 6; this covers most "
            "of Part 1 -- subject matter and definitions -- plus Part 2 "
            "in full -- negotiation and indorsement -- and the first "
            "three sections of Part 3 -- person entitled to enforce, "
            "holder in due course, and proof of signatures/status as "
            "holder in due course). Chosen to support the negotiable-"
            "instrument-recognition competency: recognizing a negotiable "
            "instrument, determining negotiability requirements, "
            "understanding indorsement types and effect, holder-in-due-"
            "course status, and who is a person entitled to enforce an "
            "instrument. The original 11 sections were retrieved directly "
            "from law.lis.virginia.gov (raw HTML) on 2026-08-18. "
            "§ 8.3A-308 was added Live Run 1.60, Mission 8, Phase 1, "
            "retrieved from the same official source via the WebFetch "
            "tool (raw Bash network egress is sandbox-denied this run) "
            "in two subsection-scoped verbatim-reproduction fetches, "
            "cross-checked against each other for internal consistency -- "
            "a disclosed change in retrieval mechanism, not in sourcing "
            "standard; not from any secondary or AI-summarized-content "
            "source. § 8.3A-309 (lost/destroyed/stolen instrument "
            "enforcement) was reviewed but not ingested -- neither "
            "flagship precedent case involves a lost instrument, so it "
            "would not materially strengthen this case study's statutory "
            "grounding (see module docstring). 'Holder' itself is not "
            "re-defined here -- it's reused directly from the already-"
            "ingested Article 1 general definition (§ 8.1A-201)."
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

"""Law Engine -- basic retrieval/citation (Live Run 1.37, Mission 17,
priority item 5; made Article-agnostic Live Run 1.39, Mission 15). Real,
deterministic keyword search over the real normalized UCC sections -- no
embeddings/vector store this run (a real, disclosed scope limit; Mission
11 explicitly warns against a generic "PDF -> embeddings -> LLM -> answer"
architecture as the default, and a deterministic, citation-exact search is
the more appropriate starting point for a domain where exact statutory
citation matters more than fuzzy semantic recall).

Originally hardcoded to Article 2's single normalized file; now merges
every `*-sections.json` file in library/normalized/ucc/ (each Article's
own ingestion module -- e.g. ingestion.py for Article 2,
ingestion_article9.py for Article 9 -- writes its own file). Section IDs
are already namespaced per Article ("8.2-314" vs "8.9A-203"), so merging
is collision-free by construction, not by luck.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

NORMALIZED_DIR = _LAW_ENGINE_ROOT / "library" / "normalized" / "ucc"
# Kept for any external caller still referencing the old single-file
# constant; load_sections() no longer reads this path exclusively.
NORMALIZED_PATH = NORMALIZED_DIR / "article-2-sections.json"


def load_sections() -> dict:
    """Merges every normalized *-sections.json file under
    library/normalized/ucc/ into one section_id -> data map."""
    merged: dict = {}
    for path in sorted(NORMALIZED_DIR.glob("*-sections.json")):
        merged.update(json.loads(path.read_text(encoding="utf-8")))
    return merged


def get_section(section_id: str) -> dict | None:
    return load_sections().get(section_id)


def search(query: str) -> list[dict]:
    """Real, deterministic search: matches query terms against section
    title, paragraph text, topics, and defined terms. Returns real
    sections with their real citation -- never a synthesized answer, only
    the actual matching statutory text plus its citation."""
    query_terms = [t.lower() for t in query.split() if t.strip()]
    if not query_terms:
        return []
    results = []
    for section_id, data in load_sections().items():
        haystack = " ".join(
            [data["title"]] + data["paragraphs"] + data["topics"] + data["defined_terms"]
        ).lower()
        if any(term in haystack for term in query_terms):
            results.append(
                {
                    "section_id": section_id,
                    "title": data["title"],
                    "citation": data["citation"],
                    "matched_paragraphs": [p for p in data["paragraphs"] if any(t in p.lower() for t in query_terms)],
                }
            )
    return results


def search_by_topic(topic: str) -> list[dict]:
    return [
        {"section_id": sid, "title": d["title"], "citation": d["citation"]}
        for sid, d in load_sections().items()
        if topic.lower() in [t.lower() for t in d["topics"]]
    ]


if __name__ == "__main__":
    import sys as _sys

    query = " ".join(_sys.argv[1:]) or "merchantable"
    for r in search(query):
        print(r["citation"], "--", r["title"])

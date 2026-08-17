"""Law Engine -- syntax-analysis export (Live Run 1.38, Mission 20).

Pre-computes a real analyze_sentence() result for every paragraph of
every ingested section, and writes it to normalized JSON -- same
Python-owns-the-analysis / TypeScript-only-reads boundary already applied
to statute sections and the transaction lifecycle (see
apps/web/src/lib/lawEngineData.ts). Chosen over having the Next.js API
route shell out to Python per-request: the analysis is fully deterministic
and small, so precomputing it once is simpler and more robust than
process-spawning from a Node route.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.retrieval import load_sections
from services.syntax_engine import analyze_sentence

OUT_PATH = _LAW_ENGINE_ROOT / "library" / "normalized" / "syntax-analysis" / "article-2-sections-analysis.json"


def build_analysis() -> dict:
    sections = load_sections()
    out: dict = {}
    for section_id, section in sections.items():
        known_terms = section.get("defined_terms", [])
        out[section_id] = [
            analyze_sentence(paragraph, known_defined_terms=known_terms).to_dict()
            for paragraph in section["paragraphs"]
            if paragraph.strip()
        ]
    return out


def write_analysis(out_path: Path = OUT_PATH) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(build_analysis(), indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    written = write_analysis()
    print(f"Wrote {written}")

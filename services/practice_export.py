"""Law Engine -- practice-items export (Live Run 1.45, Mission 5/V1).

Writes the real, already-built Article 2 MCQ set (learning.py) and the
real Document Identification exercise (document_intelligence.py) to
normalized JSON -- the same Python-owns-the-content boundary already
applied elsewhere. Closes the second-highest-value gap the Live Run
1.44 UCC completion map found: both were real, tested, and grounded,
but had zero UI surface since Live Run 1.37.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.document_intelligence import build_purchase_order_identification_exercise
from services.learning import build_article_2_mcq_set

OUT_PATH = _LAW_ENGINE_ROOT / "library" / "normalized" / "practice" / "article-2-practice.json"


def build_practice_set() -> dict:
    return {
        "mcqs": [q.to_dict() for q in build_article_2_mcq_set()],
        "document_identification_exercise": build_purchase_order_identification_exercise().to_dict(),
    }


def write_practice_set(out_path: Path = OUT_PATH) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(build_practice_set(), indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    written = write_practice_set()
    print(f"Wrote {written}")

"""Law Engine -- Task Ladder export (Live Run 1.48).

Same Python-owns-the-content boundary as practice_export.py /
ucc_orientation_export.py: writes the real, validated Task Ladder to
normalized JSON for the Next.js app to read directly, never re-deriving
or duplicating the content client-side.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.tasks import build_article_2_consumer_to_operator_ladder

OUT_PATH = _LAW_ENGINE_ROOT / "library" / "normalized" / "tasks" / "article-2-consumer-to-operator-ladder.json"


def build_task_ladder_export() -> dict:
    tasks = build_article_2_consumer_to_operator_ladder()
    return {
        "ladder_id": "article-2-consumer-to-operator-v1",
        "title": "Article 2: From Consumer to Operator",
        "tasks": [t.to_dict() for t in tasks],
    }


def write_task_ladder(out_path: Path = OUT_PATH) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(build_task_ladder_export(), indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    written = write_task_ladder()
    print(f"Wrote {written}")

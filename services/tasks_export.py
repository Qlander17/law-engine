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
from services.simulations import build_riverside_bistro_simulation
from services.simulations_article9 import build_espresso_bar_financing_simulation
from services.simulations_article3 import build_freelance_note_simulation

TASKS_DIR = _LAW_ENGINE_ROOT / "library" / "normalized" / "tasks"
OUT_PATH = TASKS_DIR / "article-2-consumer-to-operator-ladder.json"
SIMULATION_OUT_PATH = TASKS_DIR / "riverside-bistro-simulation.json"
ESPRESSO_SIMULATION_OUT_PATH = TASKS_DIR / "espresso-bar-financing-simulation.json"
NOTE_SIMULATION_OUT_PATH = TASKS_DIR / "freelance-note-simulation.json"


def build_task_ladder_export() -> dict:
    tasks = build_article_2_consumer_to_operator_ladder()
    return {
        "ladder_id": "article-2-consumer-to-operator-v1",
        "title": "Article 2: From Consumer to Operator",
        "tasks": [t.to_dict() for t in tasks],
    }


def build_simulation_export() -> dict:
    steps = build_riverside_bistro_simulation()
    return {
        "ladder_id": "riverside-bistro-simulation-v1",
        "title": "Riverside Bistro: A Real-World Simulation",
        "tasks": [s.to_dict() for s in steps],
    }


def write_task_ladder(out_path: Path = OUT_PATH) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(build_task_ladder_export(), indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def write_simulation(out_path: Path = SIMULATION_OUT_PATH) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(build_simulation_export(), indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def build_espresso_simulation_export() -> dict:
    steps = build_espresso_bar_financing_simulation()
    return {
        "ladder_id": "espresso-bar-financing-simulation-v1",
        "title": "Anna's Espresso Bar: A Secured Transactions Simulation",
        "tasks": [s.to_dict() for s in steps],
    }


def write_espresso_simulation(out_path: Path = ESPRESSO_SIMULATION_OUT_PATH) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(build_espresso_simulation_export(), indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def build_note_simulation_export() -> dict:
    steps = build_freelance_note_simulation()
    return {
        "ladder_id": "freelance-note-simulation-v1",
        "title": "Jamie's Freelance Note: A Negotiable Instruments Simulation",
        "tasks": [s.to_dict() for s in steps],
    }


def write_note_simulation(out_path: Path = NOTE_SIMULATION_OUT_PATH) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(build_note_simulation_export(), indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    written = write_task_ladder()
    print(f"Wrote {written}")
    written_sim = write_simulation()
    print(f"Wrote {written_sim}")
    written_espresso_sim = write_espresso_simulation()
    print(f"Wrote {written_espresso_sim}")
    written_note_sim = write_note_simulation()
    print(f"Wrote {written_note_sim}")

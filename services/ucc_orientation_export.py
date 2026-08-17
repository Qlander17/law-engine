"""Law Engine -- UCC orientation export (Live Run 1.45, Mission 5/V1).

Writes the real, already-built ucc_orientation.build_ucc_orientation()
result to normalized JSON, matching the same Python-owns-the-content /
TypeScript-only-reads boundary already applied to statute sections,
lifecycles, and syntax analysis (see apps/web/src/lib/lawEngineData.ts).
This closes the single highest-value gap the Live Run 1.44 UCC
completion map found: real, well-sourced orientation content that
existed only as a Python object, invisible to any real user.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.ucc_orientation import build_ucc_orientation

OUT_PATH = _LAW_ENGINE_ROOT / "library" / "normalized" / "orientation" / "ucc-orientation.json"


def write_orientation(out_path: Path = OUT_PATH) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    orientation = build_ucc_orientation()
    out_path.write_text(json.dumps(orientation.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    written = write_orientation()
    print(f"Wrote {written}")

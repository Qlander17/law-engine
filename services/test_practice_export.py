from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services import practice_export as export_mod


class WritePracticeSetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp_dir, True)

    def test_writes_real_mcqs_and_exercise(self) -> None:
        out_path = self.tmp_dir / "practice.json"
        written = export_mod.write_practice_set(out_path)
        data = json.loads(written.read_text())
        self.assertGreater(len(data["mcqs"]), 0)
        self.assertIn("choices", data["document_identification_exercise"])

    def test_every_mcq_has_exactly_one_correct_choice_and_real_citation(self) -> None:
        data = export_mod.build_practice_set()
        for mcq in data["mcqs"]:
            self.assertTrue(mcq["correct_choice"])
            self.assertTrue(mcq["citation"])
            self.assertGreaterEqual(len(mcq["incorrect_choices"]), 1)

    def test_exercise_has_exactly_one_correct_choice(self) -> None:
        data = export_mod.build_practice_set()
        correct = [c for c in data["document_identification_exercise"]["choices"] if c["is_correct"]]
        self.assertEqual(len(correct), 1)


if __name__ == "__main__":
    unittest.main()

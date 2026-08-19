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

from services import tasks_export as export_mod


class WriteTaskLadderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp_dir, True)

    def test_writes_real_four_task_ladder(self) -> None:
        out_path = self.tmp_dir / "tasks.json"
        written = export_mod.write_task_ladder(out_path)
        data = json.loads(written.read_text())
        self.assertEqual(len(data["tasks"]), 4)

    def test_every_exported_task_has_real_resolved_governing_citations(self) -> None:
        data = export_mod.build_task_ladder_export()
        for task in data["tasks"]:
            self.assertTrue(task["governing_citations"])
            for citation in task["governing_citations"]:
                self.assertIn("Va. Code Ann.", citation)

    def test_task_options_are_present_and_exactly_one_correct_per_task(self) -> None:
        data = export_mod.build_task_ladder_export()
        for task in data["tasks"]:
            correct = [o for o in task["options"] if o["is_correct"]]
            self.assertEqual(len(correct), 1, msg=task["task_id"])


class WriteSimulationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp_dir, True)

    def test_writes_real_three_step_simulation(self) -> None:
        out_path = self.tmp_dir / "sim.json"
        written = export_mod.write_simulation(out_path)
        data = json.loads(written.read_text())
        self.assertEqual(len(data["tasks"]), 3)

    def test_every_exported_step_has_real_resolved_governing_citations(self) -> None:
        data = export_mod.build_simulation_export()
        for step in data["tasks"]:
            self.assertTrue(step["governing_citations"])
            for citation in step["governing_citations"]:
                self.assertIn("Va. Code Ann.", citation)


class WriteEspressoSimulationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp_dir, True)

    def test_writes_real_four_step_simulation(self) -> None:
        out_path = self.tmp_dir / "espresso-sim.json"
        written = export_mod.write_espresso_simulation(out_path)
        data = json.loads(written.read_text())
        self.assertEqual(len(data["tasks"]), 4)

    def test_every_exported_step_has_real_resolved_governing_citations(self) -> None:
        data = export_mod.build_espresso_simulation_export()
        for step in data["tasks"]:
            self.assertTrue(step["governing_citations"])
            for citation in step["governing_citations"]:
                self.assertIn("Va. Code Ann.", citation)

    def test_task_options_are_present_and_exactly_one_correct_per_step(self) -> None:
        data = export_mod.build_espresso_simulation_export()
        for step in data["tasks"]:
            correct = [o for o in step["options"] if o["is_correct"]]
            self.assertEqual(len(correct), 1, msg=step["task_id"])


class WriteNoteSimulationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp_dir, True)

    def test_writes_real_four_step_simulation(self) -> None:
        out_path = self.tmp_dir / "note-sim.json"
        written = export_mod.write_note_simulation(out_path)
        data = json.loads(written.read_text())
        self.assertEqual(len(data["tasks"]), 4)

    def test_every_exported_step_has_real_resolved_governing_citations(self) -> None:
        data = export_mod.build_note_simulation_export()
        for step in data["tasks"]:
            self.assertTrue(step["governing_citations"])
            for citation in step["governing_citations"]:
                self.assertIn("Va. Code Ann.", citation)

    def test_task_options_are_present_and_exactly_one_correct_per_step(self) -> None:
        data = export_mod.build_note_simulation_export()
        for step in data["tasks"]:
            correct = [o for o in step["options"] if o["is_correct"]]
            self.assertEqual(len(correct), 1, msg=step["task_id"])


if __name__ == "__main__":
    unittest.main()

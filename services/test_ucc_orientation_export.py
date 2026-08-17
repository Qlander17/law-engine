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

from services import ucc_orientation_export as export_mod


class WriteOrientationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp_dir, True)

    def test_writes_real_file_with_all_eleven_articles(self) -> None:
        out_path = self.tmp_dir / "orientation.json"
        written = export_mod.write_orientation(out_path)
        self.assertTrue(written.exists())
        data = json.loads(written.read_text())
        self.assertEqual(len(data["articles"]), 11)

    def test_real_default_output_path_is_under_normalized_orientation(self) -> None:
        self.assertIn("normalized", str(export_mod.OUT_PATH.parts))
        self.assertIn("orientation", str(export_mod.OUT_PATH.parts))

    def test_article_overview_has_no_invented_fields(self) -> None:
        out_path = self.tmp_dir / "orientation.json"
        export_mod.write_orientation(out_path)
        data = json.loads(out_path.read_text())
        article_2 = next(a for a in data["articles"] if a["article"] == "2")
        self.assertTrue(article_2["has_ingested_coverage"])
        self.assertIn("8.2", article_2["virginia_enactment_title"] or "")


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path
from scripts.build_dashboard import ROOT, compile_dashboard


class DashboardCompilerTests(unittest.TestCase):
    def test_real_fixture(self):
        result = compile_dashboard(ROOT / "dashboard.yaml", ROOT / "data/sales.csv")
        self.assertEqual(result["row_count"], 40)
        self.assertEqual(len(result["config"]["charts"]), 3)

    def test_invalid_numeric_data_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "invalid.csv"
            file.write_text("date,region,category,revenue,orders,units\n2026-01-01,North,Software,not-a-number,2,3\n")
            with self.assertRaisesRegex(ValueError, "line 2"):
                compile_dashboard(ROOT / "dashboard.yaml", file)

    def test_missing_columns_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "missing.csv"
            file.write_text("date,revenue\n2026-01-01,12\n")
            with self.assertRaisesRegex(ValueError, "Missing CSV columns"):
                compile_dashboard(ROOT / "dashboard.yaml", file)


if __name__ == "__main__":
    unittest.main()

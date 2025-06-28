import os
import sys
import unittest
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calibrate_model import run_calibration


class TestCalibration(unittest.TestCase):
    def test_run_calibration_mae(self):
        log_path = Path("calibration_logs") / "last_run.json"
        if log_path.exists():
            log_path.unlink()

        results = run_calibration()

        self.assertIn("liver_glucose", results["errors"])
        self.assertLess(results["errors"]["liver_glucose"], 1.0)
        self.assertTrue(log_path.exists())


if __name__ == "__main__":
    unittest.main()
    
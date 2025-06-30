import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hdt.unit_operations.sleep_regulation_center import SleepRegulationCenter


class TestSleepRegulationCenter(unittest.TestCase):
    def setUp(self):
        self.sleep = SleepRegulationCenter({})

    def test_step_outputs(self):
        result = self.sleep.step({"circadian_phase": 0.75, "sleep_quality": 0.8, "cortisol": 0.1})
        self.assertIn("melatonin", result)
        self.assertIn("recovery_score", result)

    def test_state_bounds(self):
        result = self.sleep.step({"circadian_phase": 0.0, "sleep_quality": 1.0, "cortisol": 0.0})
        self.assertGreaterEqual(result["melatonin"], 0.0)
        self.assertLessEqual(result["melatonin"], 1.0)
        self.assertGreaterEqual(result["recovery_score"], 0.0)
        self.assertLessEqual(result["recovery_score"], 1.0)

    def test_override(self):
        self.sleep.set_sleep_drive_override(0.2)
        result = self.sleep.step({"circadian_phase": 0.5})
        self.assertEqual(result["recovery_score"], round(1.0 - 0.2, 3))
        self.sleep.clear_override()


if __name__ == "__main__":
    unittest.main()
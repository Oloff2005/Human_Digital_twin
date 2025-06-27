import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hdt.unit_operations.muscle_effector import MuscleEffector


class TestMuscleEffector(unittest.TestCase):
    def setUp(self):
        self.muscle = MuscleEffector({})

    def test_step_outputs(self):
        inputs = {"glucose": 40, "fat": 20, "ketones": 5}
        result = self.muscle.step(inputs, activity_level="moderate")
        self.assertIn("substrate_used", result)
        self.assertIn("exhaust", result)

    def test_conservation_of_mass(self):
        inputs = {"glucose": 30, "fat": 10, "ketones": 2}
        result = self.muscle.step(inputs)
        used = result["substrate_used"]
        self.assertLessEqual(used["glucose"], inputs["glucose"]) 
        self.assertLessEqual(used["fat"], inputs["fat"])
        self.assertLessEqual(used["ketones"], inputs["ketones"])

    def test_zero_glucose(self):
        inputs = {"glucose": 0, "fat": 15, "ketones": 0}
        result = self.muscle.step(inputs)
        used = result["substrate_used"]
        self.assertEqual(used["glucose"], 0)


if __name__ == "__main__":
    unittest.main()
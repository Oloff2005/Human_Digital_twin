import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hdt.unit_operations.gut_reactor import GutReactor


class TestGutReactor(unittest.TestCase):
    def setUp(self):
        self.gut = GutReactor({})

    def test_step_outputs(self):
        meal = {"carbs": 50, "fat": 20, "protein": 15, "fiber": 5, "water": 200}
        result = self.gut.step({"meal_input": meal})
        self.assertIn("absorbed", result)
        self.assertIn("residue", result)

    def test_conservation_of_mass(self):
        meal = {"carbs": 60, "fat": 25, "protein": 10, "fiber": 5, "water": 100}
        result = self.gut.step({"meal_input": meal})
        absorbed = result["absorbed"]
        residue = result["residue"]

        self.assertAlmostEqual(absorbed["glucose"] + residue["carbs"], meal["carbs"], places=2)
        self.assertAlmostEqual(absorbed["fatty_acids"] + residue["fat"], meal["fat"], places=2)
        self.assertAlmostEqual(absorbed["amino_acids"] + residue["protein"], meal["protein"], places=2)
        self.assertAlmostEqual(absorbed["water"] + residue["water"], meal["water"], places=2)

    def test_zero_glucose(self):
        meal = {"carbs": 0, "fat": 10, "protein": 5, "fiber": 0, "water": 50}
        result = self.gut.step({"meal_input": meal})
        absorbed = result["absorbed"]
        residue = result["residue"]
        self.assertEqual(absorbed["glucose"], 0)
        self.assertEqual(residue["carbs"], 0)


if __name__ == "__main__":
    unittest.main()
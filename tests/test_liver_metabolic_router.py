import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hdt.unit_operations.liver_metabolic_router import LiverMetabolicRouter


class TestLiverMetabolicRouter(unittest.TestCase):
    def setUp(self):
        self.liver = LiverMetabolicRouter({})

    def test_step_outputs(self):
        portal = {"glucose": 50, "fatty_acids": 20, "amino_acids": 5}
        result = self.liver.step({"portal_input": portal})
        self.assertIn("to_storage", result)
        self.assertIn("to_muscle_aerobic", result)
        self.assertIn("to_muscle_anaerobic", result)

    def test_conservation_of_mass(self):
        portal = {"glucose": 40, "fatty_acids": 15, "amino_acids": 2}
        result = self.liver.step({"portal_input": portal})
        stored = result["to_storage"]
        aerobic = result["to_muscle_aerobic"]
        mass_in = portal["glucose"] + min(self.liver.gluconeogenesis_rate, portal["amino_acids"])
        mass_out = stored["glycogen_stored"] + aerobic["glucose"]
        self.assertAlmostEqual(mass_out, mass_in, places=2)

    def test_zero_glucose(self):
        portal = {"glucose": 0, "fatty_acids": 0, "amino_acids": 0}
        result = self.liver.step({"portal_input": portal})
        stored = result["to_storage"]
        aerobic = result["to_muscle_aerobic"]
        anaerobic = result["to_muscle_anaerobic"]
        self.assertEqual(stored["glycogen_stored"], 0)
        self.assertEqual(aerobic["glucose"], 0)
        self.assertEqual(anaerobic["glucose"], 0)


if __name__ == "__main__":
    unittest.main()
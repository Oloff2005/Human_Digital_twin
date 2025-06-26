import unittest
from hdt.inputs.signal_normalizer import SignalNormalizer

class TestSignalNormalizer(unittest.TestCase):
    def setUp(self):
        self.normalizer = SignalNormalizer()

    def test_normalizes_known_signals(self):
        sample_input = {
            "BrainController": {
                "heart_rate": 80,
                "hrv": 0.72,
                "sleep_score": 90,
                "training_readiness": 86,
                "oxygen_saturation": 97,
                "stress_score": 10
            }
        }

        result = self.normalizer.normalize(sample_input)

        self.assertAlmostEqual(result["BrainController"]["heart_rate"], 0.8)
        self.assertAlmostEqual(result["BrainController"]["sleep_score"], 0.9)
        self.assertAlmostEqual(result["BrainController"]["training_readiness"], 0.86)
        self.assertAlmostEqual(result["BrainController"]["oxygen_saturation"], 0.97)
        self.assertAlmostEqual(result["BrainController"]["stress_score"], 0.1)
        self.assertEqual(result["BrainController"]["hrv"], 0.72)  # unchanged

    def test_passes_through_unknown_signals(self):
        sample_input = {
            "MuscleEffector": {
                "fatigue_signal": 3.0,
                "lactate": 1.2
            }
        }

        result = self.normalizer.normalize(sample_input)
        self.assertEqual(result["MuscleEffector"]["fatigue_signal"], 3.0)
        self.assertEqual(result["MuscleEffector"]["lactate"], 1.2)

if __name__ == "__main__":
    unittest.main()

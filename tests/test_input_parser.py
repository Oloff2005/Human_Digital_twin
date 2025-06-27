import unittest
from hdt.inputs.input_parser import InputParser

class TestInputParser(unittest.TestCase):
    def setUp(self):
        # Simulate wearable_mapping.json structure
        self.mock_mapping = {
            "heart_rate": ["BrainController", "HeartCirculation"],
            "hrv": ["BrainController"],
            "sleep_score": ["BrainController", "SleepRegulationCenter"],
            "steps": ["BrainController", "MuscleReactor"]
        }

        # Simulate Apple Health data input
        self.mock_input = {
            "heart_rate": 70,
            "hrv": 85,
            "sleep_score": 90,
            "steps": 11000
        }

        # Override parser with mock mapping instead of file loading
        class TestableParser(InputParser):
            def __init__(self, mapping):
                self.mapping = mapping

        self.parser = TestableParser(self.mock_mapping)

    def test_parse_returns_correct_structure(self):
        parsed = self.parser.parse(self.mock_input)

        self.assertIn("BrainController", parsed)
        self.assertIn("SleepRegulationCenter", parsed)
        self.assertIn("MuscleReactor", parsed)
        self.assertIn("HeartCirculation", parsed)

        self.assertEqual(parsed["BrainController"]["heart_rate"], 70)
        self.assertEqual(parsed["BrainController"]["hrv"], 85)
        self.assertEqual(parsed["BrainController"]["sleep_score"], 90)
        self.assertEqual(parsed["MuscleReactor"]["steps"], 11000)
        self.assertEqual(parsed["HeartCirculation"]["heart_rate"], 70)


    def test_handles_missing_data(self):
        incomplete_input = {
            "heart_rate": 62
        }
        parsed = self.parser.parse(incomplete_input)
        self.assertIn("BrainController", parsed)
        self.assertEqual(parsed["BrainController"]["heart_rate"], 62)
        self.assertNotIn("hrv", parsed.get("BrainController", {}))
    
    def test_logs_and_skips_invalid_values(self):
        bad_input = {"heart_rate": None, "hrv": float('nan')}
        with self.assertLogs('hdt.inputs.input_parser', level='WARNING') as cm:
            parsed = self.parser.parse(bad_input)
        self.assertEqual(parsed, {})
        self.assertTrue(any('heart_rate' in msg for msg in cm.output))
        self.assertTrue(any('hrv' in msg for msg in cm.output))

if __name__ == "__main__":
    unittest.main()




import unittest
import os
import json
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hdt.inputs.input_parser import InputParser
from hdt.inputs.signal_normalizer import SignalNormalizer

class TestInputProcessing(unittest.TestCase):
    def setUp(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.mapping_path = os.path.join(project_root, "hdt", "config", "wearable_mapping.json")
        self.sample_input_path = os.path.join(project_root, "data", "sample_inputs.json")

    def test_parser_output_structure(self):
        parser = InputParser(self.mapping_path)
        parsed = parser.parse(self.sample_input_path)
        self.assertIsInstance(parsed, dict)
        self.assertIn("BrainController", parsed)
        self.assertIn("heart_rate", parsed["BrainController"])

    def test_signal_normalization(self):
        parser = InputParser(self.mapping_path)
        parsed = parser.parse(self.sample_input_path)
        normalizer = SignalNormalizer()
        normalized = normalizer.normalize(parsed)
        self.assertGreaterEqual(normalized["BrainController"]["heart_rate"], 0.0)
        self.assertLessEqual(normalized["BrainController"]["heart_rate"], 1.0)
        self.assertGreaterEqual(normalized["BrainController"]["sleep_score"], 0.0)
        self.assertLessEqual(normalized["BrainController"]["sleep_score"], 1.0)

if __name__ == '__main__':
    unittest.main()
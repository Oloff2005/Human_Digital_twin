import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hdt.recommender.rule_engine import RuleEngine


class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.rules_path = os.path.join(
            os.path.dirname(__file__), "..", "hdt", "recommender", "rules.yaml"
        )

    def test_rule_based_mode(self):
        engine = RuleEngine(mode="rule_based", rules_path=self.rules_path, rule_version="version_A")
        out = engine.get_recommendations({"Liver": {"glucose": 160}})
        self.assertIn("Consider reducing sugar intake", out)

    def test_ml_based_mode(self):
        engine = RuleEngine(mode="ml_based")
        out = engine.get_recommendations({"Liver": {"glucose": 120}})
        self.assertIsInstance(out, list)
        for item in out:
            self.assertIsInstance(item, str)

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            RuleEngine(mode="unknown")


if __name__ == "__main__":
    unittest.main()
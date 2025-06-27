import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hdt.recommender.recommender import Recommender, threshold_rule_match


class TestRecommender(unittest.TestCase):
    def setUp(self):
        rules_path = os.path.join(os.path.dirname(__file__), "..", "hdt", "recommender", "rules.yaml")
        self.rec = Recommender(rules_path)

    def test_recommend_structure(self):
        state = {"Liver": {"glucose": 160}}
        output = self.rec.recommend(state)
        self.assertIsInstance(output, list)
        for item in output:
            self.assertIsInstance(item, str)
        self.assertIn("Consider reducing sugar intake", output)
        
    def test_threshold_rule_match(self):
        path = os.path.join(
            os.path.dirname(__file__), "..", "hdt", "config", "rules.yaml"
        )
        values = {
            "glucose": 9.0,
            "cortisol": 0.8,
            "sleep_quality": 50,
            "heart_rate": 110,
        }
        out = threshold_rule_match(values, path)
        self.assertIn(
            "Reduce carbohydrate intake; blood sugar elevated.",
            out,
        )
        self.assertIn(
            "High stress detected. Prioritize rest and reduce workload.",
            out,
        )
        self.assertIn(
            "Low sleep quality. Aim for consistent bedtime and avoid screens.",
            out,
        )
        self.assertIn(
            "Elevated heart rate. Consider breathing exercises or hydration.",
            out,
        )


if __name__ == "__main__":
    unittest.main()
import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hdt.recommender.recommender import Recommender, threshold_rule_match
from hdt.recommender.rule_engine import RuleEngine


class TestRecommender(unittest.TestCase):
    def setUp(self):
        rules_path = os.path.join(
            os.path.dirname(__file__), "..", "hdt", "recommender", "rules.yaml"
        )
        self.rec = Recommender(rules_path, rule_version="version_A")

    def test_recommend_structure(self):
        state = {"Liver": {"glucose": 160}}
        output = self.rec.recommend(state)
        self.assertIsInstance(output, list)
        for item in output:
            self.assertIsInstance(item, str)
        self.assertIn("Consider reducing sugar intake", output)
    
    def test_version_b(self):
        rules_path = os.path.join(
            os.path.dirname(__file__), "..", "hdt", "recommender", "rules.yaml"
        )
        rec_b = Recommender(rules_path, rule_version="version_B")
        out = rec_b.recommend({"Liver": {"glucose": 160}})
        self.assertIn("Limit sugar intake", out)
        self.assertEqual(rec_b.get_version(), "version_B")
    
    def test_rule_versions_different(self):
        rec_a_out = self.rec.recommend({"Liver": {"glucose": 160}})
        rules_path = os.path.join(
            os.path.dirname(__file__), "..", "hdt", "recommender", "rules.yaml"
        )
        rec_b = Recommender(rules_path, rule_version="version_B")
        rec_b_out = rec_b.recommend({"Liver": {"glucose": 160}})
        self.assertNotEqual(rec_a_out, rec_b_out)

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
        
    def test_rule_engine_mode_switch(self):
        engine = RuleEngine(
            mode="rule_based",
            rules_path=os.path.join(os.path.dirname(__file__), "..", "hdt", "recommender", "rules.yaml"),
            rule_version="version_A",
        )
        state = {"Liver": {"glucose": 160}}
        rule_out = engine.get_recommendations(state)
        engine.mode = "ml_based"
        ml_out = engine.get_recommendations(state)
        self.assertNotEqual(rule_out, ml_out)

if __name__ == "__main__":
    unittest.main()
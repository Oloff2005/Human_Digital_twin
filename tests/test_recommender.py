import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hdt.recommender.recommender import Recommender


class TestRecommender(unittest.TestCase):
    def setUp(self):
        rules_path = os.path.join(os.path.dirname(__file__), "..", "hdt", "recommender", "rules.yaml")
        self.rec = Recommender(rules_path)

    def test_recommend_structure(self):
        state = {"Liver": {"glucose": 160}}
        output = self.rec.recommend(state)
        self.assertIsInstance(output, dict)
        self.assertIn("suggestions", output)
        self.assertIsInstance(output["suggestions"], list)
        for item in output["suggestions"]:
            self.assertIsInstance(item, str)
        self.assertIn("Consider reducing sugar intake", output["suggestions"])


if __name__ == "__main__":
    unittest.main()
import unittest
from hdt.validation.input_schema import AppleHealthInput
from pydantic import ValidationError

class TestAppleHealthInput(unittest.TestCase):
    def test_valid_input(self):
        data = {
            "heart_rate": 75,
            "sleep_score": 88,
            "steps": 12000
        }
        model = AppleHealthInput(**data)
        self.assertEqual(model.heart_rate, 75)
        self.assertEqual(model.steps, 12000)

    def test_partial_input(self):
        data = {"sleep_score": 92}
        model = AppleHealthInput(**data)
        self.assertEqual(model.sleep_score, 92)

    def test_invalid_data_type(self):
        with self.assertRaises(ValidationError):
            AppleHealthInput(heart_rate="fast", steps="lots")

if __name__ == "__main__":
    unittest.main()

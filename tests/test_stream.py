import unittest
from hdt.streams import Stream


class TestStream(unittest.TestCase):
    def test_delayed_transfer(self):
        s = Stream("A", "B", delay=2)
        s.push({"x": 1}, timestamp=0)
        # nothing should be ready at t=1
        self.assertEqual(s.step(1), [])
        # payload available at t=2
        self.assertEqual(s.step(2), [{"x": 1}])
        # buffer is empty afterwards
        self.assertEqual(s.step(3), [])


if __name__ == "__main__":
    unittest.main()
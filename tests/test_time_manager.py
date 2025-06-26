import unittest
from hdt.core.time_manager import TimeManager

class TestTimeManager(unittest.TestCase):
    def test_time_progression(self):
        time = TimeManager()
        self.assertEqual(time.get_time_state(), {'minute': 0, 'hour': 0, 'day': 0})

        time.tick(60)
        self.assertEqual(time.get_time_state(), {'minute': 60, 'hour': 1, 'day': 0})

        time.tick(60 * 24)  # 1 more day
        self.assertEqual(time.get_time_state(), {'minute': 1500, 'hour': 1, 'day': 1})

if __name__ == '__main__':
    unittest.main()

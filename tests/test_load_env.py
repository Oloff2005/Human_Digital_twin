import os
import tempfile
import unittest

from utils.env_utils import load_env

class TestLoadEnv(unittest.TestCase):
    def test_load_env_parses_file(self):
        content = """API_TOKEN=abc123
LOG_PATH=/tmp/app.log
# Comment line
QUOTED="quoted value"""""
        with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
            tf.write(content)
            tf.flush()
            path = tf.name
        try:
            env = load_env(path)
            self.assertEqual(env["API_TOKEN"], "abc123")
            self.assertEqual(env["LOG_PATH"], "/tmp/app.log")
            self.assertEqual(env["QUOTED"], "quoted value")
            # Check os.environ was populated
            self.assertEqual(os.environ.get("API_TOKEN"), "abc123")
        finally:
            os.remove(path)

if __name__ == "__main__":
    unittest.main()
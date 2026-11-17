import unittest


class TestExample(unittest.TestCase):
    def test_adds(self):
        total = 1 + 1
        expected = 2
        self.assertEqual(total, expected)

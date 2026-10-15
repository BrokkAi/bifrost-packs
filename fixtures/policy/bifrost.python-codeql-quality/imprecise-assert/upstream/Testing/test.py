# Source: github/codeql/python/ql/test/query-tests/Testing/test.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
from unittest import TestCase

class MyTest(TestCase):

    def test1(self):
        self.assertTrue(1 == 1) # $ Alert
        self.assertFalse(1 > 2) # $ Alert
        self.assertTrue(1 in [1]) # $ Alert
        self.assertFalse(0 is "") # $ Alert

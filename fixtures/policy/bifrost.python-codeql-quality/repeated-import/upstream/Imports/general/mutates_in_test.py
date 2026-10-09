# Source: github/codeql/python/ql/test/query-tests/Imports/general/mutates_in_test.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
import mutable_attr
import unittest

class T(unittest.TestCase):

    def test_foo(self):
        mutable_attr.y = 3

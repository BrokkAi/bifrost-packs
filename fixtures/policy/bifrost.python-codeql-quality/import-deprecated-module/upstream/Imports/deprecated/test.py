# Source: github/codeql/python/ql/test/query-tests/Imports/deprecated/test.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
# Some deprecated modules
import rfc822 # $ Alert
import posixfile # $ Alert

# We should only report a bad import once
class Foo(object):
    def foo(self):
        import md5 # $ Alert

# Backwards compatible code, should not report
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

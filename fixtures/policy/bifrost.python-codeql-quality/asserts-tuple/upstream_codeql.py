# Upstream source: github/codeql/python/ql/test/query-tests/Statements/asserts/assert.py
# CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

# Excerpt from upstream lines 4-17
def _f():
    assert (yield 3) # $ Alert[py/side-effect-in-assert]
    x = [ 1 ]
    assert len(x)   #Call without side-effects
    assert sys.exit(1) # $ Alert[py/side-effect-in-assert] #Call with side-effects
    expected_types = (Response, six.text_type, six.binary_type)
    assert isinstance(obj, expected_types), \
        "obj must be %s, not %s" % (
            " or ".join(t.__name__ for t in expected_types),
            type(obj).__name__)

def assert_tuple(x, y):
    assert () # $ Alert[py/asserts-tuple]
    assert (x, y) # $ Alert[py/asserts-tuple]

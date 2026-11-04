# Source: github/codeql/python/ql/test/query-tests/Expressions/super/test_except.py at ae741615
# MIT License, Copyright GitHub, Inc.

try:

    @decorator
    class S(object):

        def __init__(self, *args, **kwargs):
            super(S, self).__init__(*args, **kwargs)

except Exception:

    class S(object):
        pass

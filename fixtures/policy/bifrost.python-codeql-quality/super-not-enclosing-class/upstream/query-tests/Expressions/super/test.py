# Source: github/codeql/python/ql/test/query-tests/Expressions/super/test.py at ae741615
# MIT License, Copyright GitHub, Inc.
import sys

#Container inheriting from builtin
class MyDict(dict):
    pass

class NotMyDict(object):

    def f(self):
        super(MyDict, self).f() # $ Alert

#Splitting
PY2 = sys.version_info[0] == 2

if PY2:
    pass


class InSplit(MyDict):

    def __init__(self):
        super(InSplit, self).f()

if PY2:
    pass

# Source: github/codeql/python/ql/test/query-tests/Variables/undefined/odasa3987.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

from somwhere import may_raise, value, SomeException

def f(cond1, cond2):
    try:
        may_raise()
        var = value()
    except Exception:
        if cond2:
            var = 7
    if var == 1:
        var = var + 1
    elif var == 2:
        var +- 3
    if cond2:
        pass
    var = var + 4 # var must be defined to have passed line 11

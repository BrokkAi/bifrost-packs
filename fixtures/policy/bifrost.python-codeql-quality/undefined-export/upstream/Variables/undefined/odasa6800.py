# Source: github/codeql/python/ql/test/query-tests/Variables/undefined/odasa6800.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
#We don't (yet) follow this import
fail = __import__("odasa%s" % 6418).fail

def foo(x):
    if x:
        var = 0
    else:
        fail('Current version is not numeric')
    return var

# Source: github/codeql/python/ql/test/query-tests/Imports/general/imports_mutable.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
from mutable_attr import x, y

def f():
    print(x)
    print(y)

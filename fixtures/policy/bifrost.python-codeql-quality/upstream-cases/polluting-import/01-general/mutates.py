# Source: github/codeql/python/ql/test/query-tests/Imports/general/mutates.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
import mutable_attr

def f():
    mutable_attr.x = 2

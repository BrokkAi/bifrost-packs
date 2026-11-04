# Source: github/codeql/python/ql/test/query-tests/Functions/general/use_mox.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
import mox

#Use mox
mox

def f():
    pass

#This may be OK as it might be mocked

f().AndReturns("Something")

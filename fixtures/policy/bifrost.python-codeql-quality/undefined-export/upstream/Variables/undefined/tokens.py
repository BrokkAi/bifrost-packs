# Source: github/codeql/python/ql/test/query-tests/Variables/undefined/tokens.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
TOKEN_0 = 0
TOKEN_1 = 1
TOKEN_2 = 2
TOKEN_3 = 3
TOKEN_4 = 4
TOKEN_5 = 5

__all__ = [ "TOKEN_0" ]

for i in range(1,6):
    __all__.append("TOKEN_%d" % i)

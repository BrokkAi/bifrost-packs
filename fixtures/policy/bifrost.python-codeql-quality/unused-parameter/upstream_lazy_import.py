# Source: github/codeql/python/ql/test/query-tests/Variables/unused/lazy_import.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

from clever_lazy_module_thing import range

#OK iteration over range
def OK4(n):
    for i in range(n):
        print("x")

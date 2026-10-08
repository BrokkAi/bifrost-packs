# Source: github/codeql/python/ql/test/query-tests/Imports/cyclic-module/module2.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
import module1

# direct use
a2 = module1.a1

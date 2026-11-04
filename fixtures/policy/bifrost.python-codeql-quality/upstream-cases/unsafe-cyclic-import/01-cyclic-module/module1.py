# Source: github/codeql/python/ql/test/query-tests/Imports/cyclic-module/module1.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
# potentially crashing cycles
import module2
import module3

a1 = module2.a2
b1 = 2

# bad style cycles
import module4
def foo():
    import module5

# okay, because some of the cycle is not top level
import module6

# OK because this import occurs after relevant definition (a1)
import module8

#OK because cycle is guarded by `if False:`
from module10 import x

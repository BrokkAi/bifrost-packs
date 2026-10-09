# Source: github/codeql/python/ql/test/query-tests/Imports/PyCheckerTests/imports_test.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

#Import and import from

import test_module2 # $ Alert[py/import-and-import-from]
from test_module2 import func

#Module imports itself
import imports_test

import pkg_ok
import pkg_notok

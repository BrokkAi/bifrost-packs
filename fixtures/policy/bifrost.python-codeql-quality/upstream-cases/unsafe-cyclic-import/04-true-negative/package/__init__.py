# Source: github/codeql/python/ql/test/query-tests/Imports/cyclic-module-package-fp/true-negative/package/__init__.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
p = 1
from bar.foo import foo
from package import baz

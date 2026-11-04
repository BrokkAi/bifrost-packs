# Source: github/codeql/python/ql/test/query-tests/Imports/cyclic-module-package-fp/false-negative/package/__init__.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
from bar.foo import foo
from package import baz
p = 1

# Source: github/codeql/python/ql/test/query-tests/Imports/PyCheckerTests/pkg_ok/__init__.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
import pkg_ok.foo1 as foo1

from pkg_ok import foo2
from pkg_ok.foo3 import Foo3

from . import foo4
from .foo5 import Foo5

# Source: github/codeql/python/ql/test/query-tests/Imports/PyCheckerTests/pkg_notok/__init__.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
class Foo(object):
    pass

import pkg_notok # $ Alert[py/import-and-import-from]

# This import is a bit tricky. It will make `bar` available in as `pkg_notok.bar` as a
# side effect (see https://docs.python.org/3/reference/import.html#submodules), but the
# *import* will add a binding to `pkg_notok` to the current scope -- so technically the
# module imports itself.
import pkg_notok.bar

from pkg_notok import Foo
from pkg_notok import Foo as NotOkFoo
from pkg_notok import *

# Source: github/codeql/python/ql/test/query-tests/Imports/cyclic-module-annotations-fp/module2.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
from __future__ import annotations

import dataclasses
import typing

import module1

@dataclasses.dataclass()
class Bar:
    def is_in_foo(self, foo: module1.Foo):
        return self in foo.bars

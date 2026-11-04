# Source: github/codeql/python/ql/test/query-tests/Imports/cyclic-module-annotations-fp/module4.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
import dataclasses
import typing

import module3

@dataclasses.dataclass()
class Bar:
    def is_in_foo(self, foo: module3.Foo):
        return self in foo.bars

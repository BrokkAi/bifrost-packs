# Source: github/codeql/python/ql/test/query-tests/Imports/cyclic-module-annotations-fp/module3.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
import dataclasses
import typing

import module4

@dataclasses.dataclass()
class Foo:
    bars: typing.List[module4.Bar]

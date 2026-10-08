# Source: github/codeql/python/ql/test/query-tests/Imports/cyclic-module-annotations-fp/module1.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
from __future__ import annotations

import dataclasses
import typing

import module2

@dataclasses.dataclass()
class Foo:
    bars: typing.List[module2.Bar]

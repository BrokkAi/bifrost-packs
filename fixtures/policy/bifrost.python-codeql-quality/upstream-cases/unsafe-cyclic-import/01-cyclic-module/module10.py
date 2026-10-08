# Source: github/codeql/python/ql/test/query-tests/Imports/cyclic-module/module10.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
from typing import TYPE_CHECKING

if False:
    import module1

if TYPE_CHECKING:
    import module1

x = 1

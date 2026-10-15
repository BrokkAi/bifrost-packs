# Source: github/codeql/python/ql/test/query-tests/Variables/undefined/import_star.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

#ODASA-4596
from tokens import *

#TOKEN_1 is defined in tokens, but we cannot determine that statically.
TOKEN_1

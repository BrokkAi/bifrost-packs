# Python percent-format-wrong-arguments fixture

Mirrors CodeQL query python/ql/src/Expressions/WrongNumberArgumentsForFormat.ql at pinned CodeQL commit ae741615f3e178ce61289a651790dc67fcc18e19.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic model is required.

Expected findings: pkg/formatting.py:1. The policy run completed completely with no diagnostics.

Near misses: Two percent conversions supplied with exactly two tuple values.

## Upstream CodeQL test evidence

Added upstream excerpt from `github/codeql/python/ql/test/query-tests/Expressions/general/str_fmt_test.py` at `ae741615f3e178ce61289a651790dc67fcc18e19` in `upstream_codeql.py`, with the source license header. Original decisive source lines: 10-14, 17-19, 25-34.


### Required upstream-test gate result

Upstream case `Expressions/general/WrongNumberArgumentsForFormat.expected`: 2 CodeQL rows, 2 Bifrost rows, FP=0, FN=0, abstentions=0; completion `inconclusive`.

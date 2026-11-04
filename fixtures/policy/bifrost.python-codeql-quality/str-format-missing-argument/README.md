# Python str-format-missing-argument fixture

Mirrors CodeQL query python/ql/src/Expressions/Formatting/WrongNumberArgumentsFor3101Format.ql at pinned CodeQL commit ae741615f3e178ce61289a651790dc67fcc18e19.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic model is required.

Expected findings: pkg/formatting.py:4. The policy run completed completely with no diagnostics.

Near misses: A two-field format supplied with two values and a one-field format supplied with one value.

## Upstream CodeQL test evidence

Added upstream excerpt from `github/codeql/python/ql/test/query-tests/Expressions/Formatting/test.py` at `ae741615f3e178ce61289a651790dc67fcc18e19` in `upstream_codeql.py`, with the source license header. Original decisive source lines: 5-5, 23-23, 29-29.


### Required upstream-test gate result

Upstream case `Expressions/Formatting/WrongNumberArgumentsFor3101Format.expected`: 6 CodeQL rows, 3 Bifrost rows, FP=0, FN=0, abstentions=3; completion `inconclusive`. 3 missing expected rows are typed abstentions on this Inconclusive run.

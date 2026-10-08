# Python str-format-missing-named-argument fixture

Mirrors CodeQL query python/ql/src/Expressions/Formatting/WrongNameInArgumentsFor3101Format.ql at pinned CodeQL commit ae741615f3e178ce61289a651790dc67fcc18e19.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic model is required.

Expected findings: pkg/formatting.py:2. The policy run completed completely with no diagnostics.

Near misses: A matching keyword for the named field and a positional-only numeric field.

## Upstream CodeQL test evidence

Added upstream excerpt from `github/codeql/python/ql/test/query-tests/Expressions/Formatting/test.py` at `ae741615f3e178ce61289a651790dc67fcc18e19` in `upstream_codeql.py`, with the source license header. Original decisive source lines: 4-4, 17-17, 20-20.


### Required upstream-test gate result

Upstream case `Expressions/Formatting/WrongNameInArgumentsFor3101Format.expected`: 2 CodeQL rows, 1 Bifrost rows, FP=0, FN=0, abstentions=1; completion `inconclusive`. 1 missing expected rows are typed abstentions on this Inconclusive run.

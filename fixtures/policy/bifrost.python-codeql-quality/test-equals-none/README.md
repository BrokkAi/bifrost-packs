# Python test-equals-none fixture

Mirrors CodeQL query python/ql/src/Expressions/EqualsNone.ql at pinned CodeQL commit ae741615f3e178ce61289a651790dc67fcc18e19.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic model is required.

Expected findings: src/check.py:4. The policy run completed completely with no diagnostics.

Near misses: The equivalent singleton check using is None.

## Upstream CodeQL test evidence

Added upstream excerpt from `github/codeql/python/ql/test/query-tests/Expressions/general/expressions_test.py` at `ae741615f3e178ce61289a651790dc67fcc18e19` in `upstream_codeql.py`, with the source license header. Original decisive source lines: 63-67, 112-115.


### Required upstream-test gate result

Upstream case `Expressions/general/EqualsNone.expected`: 1 CodeQL rows, 1 Bifrost rows, FP=0, FN=0, abstentions=0; completion `complete`.

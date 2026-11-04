# Python comparison-using-is fixture

Mirrors CodeQL query python/ql/src/Expressions/IncorrectComparisonUsingIs.ql at pinned CodeQL commit ae741615f3e178ce61289a651790dc67fcc18e19.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic model is required.

Expected findings: lib.py:11, lib.py:12. The campaign-only fixture completed completely before the upstream excerpt was added; the combined gate fixture completion is recorded below.

Near misses: Identity-only classes, mixed value-equality and identity-only operands, and None singleton identity.

## Upstream CodeQL test evidence

Added upstream excerpt from `github/codeql/python/ql/test/query-tests/Expressions/eq/expressions_test.py` at `ae741615f3e178ce61289a651790dc67fcc18e19` in `upstream_codeql.py`, with the source license header. Original decisive source lines: 44-47, 49-52, 69-72.


### Required upstream-test gate result

Upstream case `Expressions/eq/IncorrectComparisonUsingIs.expected`: 1 CodeQL rows, 1 Bifrost rows, FP=0, FN=0, abstentions=0; completion `inconclusive`. The interned-string, empty-tuple, and small-integer near misses at upstream lines 51, 71, and 72 are excluded; the expected positive at line 46 remains.

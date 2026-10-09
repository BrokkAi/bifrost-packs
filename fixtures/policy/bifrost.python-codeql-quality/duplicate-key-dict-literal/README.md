# Python duplicate-key-dict-literal fixture

Mirrors CodeQL query python/ql/src/Expressions/DuplicateKeyInDictionaryLiteral.ql at pinned CodeQL commit ae741615f3e178ce61289a651790dc67fcc18e19.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic model is required.

Expected findings: lib.py:2, lib.py:10. The campaign-only fixture completed completely before the upstream excerpt was added; the combined gate fixture completion is recorded below.

Near misses: Distinct string keys; the second positive also checks equality after Python escape decoding.

## Upstream CodeQL test evidence

Added upstream excerpt from `github/codeql/python/ql/test/query-tests/Expressions/general/expressions_test.py` at `ae741615f3e178ce61289a651790dc67fcc18e19` in `upstream_codeql.py`, with the source license header. Original positive source lines: 3-6; added upstream unique-key near miss lines 212-217.


### Required upstream-test gate result

Upstream case `Expressions/general/DuplicateKeyInDictionaryLiteral.expected`: 2 CodeQL rows, 2 Bifrost rows, FP=0, FN=0, abstentions=0; completion `inconclusive`. The two dictionary pairs are found at later-key anchors; the upstream byte/string-key control leaves the run inconclusive.

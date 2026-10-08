# Python comparison-of-constants fixture

Mirrors CodeQL query python/ql/src/Expressions/CompareConstants.ql at pinned CodeQL commit ae741615f3e178ce61289a651790dc67fcc18e19.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic model is required.

Expected findings: lib.py:2, lib.py:3. The policy run completed completely with no diagnostics.

Near misses: A comparison with only one constant and a direct assert comparison. General arithmetic constant folding remains outside this bounded constant-expression contract.

## Upstream CodeQL test evidence

Added upstream excerpt from `github/codeql/python/ql/test/query-tests/Expressions/general/compare.py` at `ae741615f3e178ce61289a651790dc67fcc18e19` in `upstream_codeql.py`, with the source license header. Original positive source lines: 12-13; added upstream near misses include lines 3-5 and 26.


### Required upstream-test gate result

Upstream case `Expressions/general/CompareConstants.expected`: 2 CodeQL rows, 2 Bifrost rows, FP=0, FN=0, abstentions=0; completion `complete`.

# Python old-style-octal-literal fixture

Mirrors CodeQL query python/ql/src/Lexical/OldOctalLiteral.ql at pinned CodeQL commit ae741615f3e178ce61289a651790dc67fcc18e19.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic model is required.

Expected findings: main.py:1. The policy run completed completely with no diagnostics.

Near misses: A 0o-prefixed octal literal, a common permission-mask spelling, and a modern helper literal.

## Upstream CodeQL test evidence

CodeQL query-tests contains no OldOctalLiteral.expected. Added the upstream query help sample from `python/ql/src/Lexical/OldOctalLiteral.py` as an extra positive and spelling near-misses; it is not counted as a query-test case.


### Required upstream-test gate result

No upstream query-test expected file exists for this query, so the replay ran 0 query-test cases. The QL help sample is included as an attributed positive/control fixture.

# py-asserts-tuple

Pinned CodeQL source: `python/ql/src/Statements/AssertOnTuple.ql` at `ae741615f3e178ce61289a651790dc67fcc18e19`.
The policy contract is limited to: flag Python assert statements whose test expression is a tuple literal.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

Expected positive: helper.py:2. Expected clean controls: helper.py:3.
The policy is copied to `.bifrost/policies/asserts-tuple.rqlp` for the pinned run.
Pinned validation command:

`bifrost --root . --policy-file .bifrost/policies/asserts-tuple.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08`

Observed: `Complete`, finding at `helper.py:2`; campaign near-miss controls stayed clean.

## Upstream CodeQL test evidence

Added upstream excerpt from `github/codeql/python/ql/test/query-tests/Statements/asserts/assert.py` at `ae741615f3e178ce61289a651790dc67fcc18e19` in `upstream_codeql.py`, with the source license header. Original positive source lines: 16-17; added upstream near-miss lines include 7 and 10-13.


### Required upstream-test gate result

Upstream case `Statements/asserts/AssertOnTuple.expected`: 2 CodeQL rows, 2 Bifrost rows, FP=0, FN=0, abstentions=0; completion `complete`.

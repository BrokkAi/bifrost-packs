# py-str-format-surplus-argument

Pinned CodeQL source: `python/ql/src/Expressions/Formatting/UnusedArgumentIn3101Format.ql` at `ae741615f3e178ce61289a651790dc67fcc18e19`.
The policy contract is limited to: flag supported str.format calls with proven surplus positional arguments.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

Expected positive: cases.py:2. Expected clean controls: cases.py:6.
The policy is copied to `.bifrost/policies/str-format-surplus-argument.rqlp` for the pinned run.
Pinned validation command:

`bifrost --root . --policy-file .bifrost/policies/str-format-surplus-argument.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08`

Observed: `Complete`, finding at `cases.py:2`; campaign near-miss controls stayed clean.

## Upstream CodeQL test evidence

Added upstream excerpt from `github/codeql/python/ql/test/query-tests/Expressions/Formatting/test.py` at `ae741615f3e178ce61289a651790dc67fcc18e19` in `upstream_codeql.py`, with the source license header. Original decisive source lines: 5-5, 23-23, 29-29.


### Required upstream-test gate result

Upstream case `Expressions/Formatting/UnusedArgumentIn3101Format.expected`: 4 CodeQL rows, 2 Bifrost rows, FP=0, FN=0, abstentions=2; completion `inconclusive`. 2 missing expected rows are typed abstentions on this Inconclusive run.

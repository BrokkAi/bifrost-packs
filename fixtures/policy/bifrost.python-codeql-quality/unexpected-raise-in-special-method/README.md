# Python unexpected raise in special method fixture

Expected findings: `helper.py:2`, the `def __getitem__` line whose body raises `ValueError`, and six findings in `upstream/test.py` for the decisive upstream cases. `KeyError` at line 8 is allowed by the lookup protocol, and the `ValueError()` at line 13 is only constructed, not raised.

Validated with Bifrost 0.13.1, build identity `9ace1176a28f5b1d790a76872c6fd038dbd4e2f8`, evaluation date `2026-10-17`. The fixture's policy hash is unchanged: `a7d0582e7e63b2df7c6bee5bbec1ac28e1dfb4e31f2c37c4557e1f5826675240`.

From this directory, the reproducible command is:

```sh
BIFROST_OPEN_PACKS_DISABLE=1 bifrost --root . --policy-file .bifrost/policies/unexpected-raise-in-special-method.rqlp --no-builtin-policies --no-incremental --format json --fail-on never --evaluation-date 2026-10-17
```

## Upstream CodeQL case

The upstream Python 3 test is `github/codeql/python/ql/test/query-tests/Functions/IncorrectRaiseInSpecialMethod/test.py` at `ae741615f3e178ce61289a651790dc67fcc18e19` (MIT License, Copyright GitHub, Inc.); expected rows are in `Functions/IncorrectRaiseInSpecialMethod/IncorrectRaiseInSpecialMethod.expected`. On the same engine build, Bifrost reports all six expected cases at the same method-definition lines as CodeQL, with 0 false positives and 0 missed expected cases. Both this upstream run and the combined fixture run are Inconclusive due to partial discovery.

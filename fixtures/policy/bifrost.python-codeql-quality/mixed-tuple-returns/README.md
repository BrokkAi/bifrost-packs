# Python mixed-tuple-returns fixture

Expected findings: `helper.py:1` and `helper.py:6`. The second is the one-local-alias positive from the engine test. `uniform` and annotated `annotated` are clean near misses.


Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

From this directory, the reproducible command is:

```sh
bifrost --root . --policy-file .bifrost/policies/mixed-tuple-returns.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

## Upstream CodeQL case

The upstream Python 3 test is `github/codeql/python/ql/test/query-tests/Functions/return_values/functions_test.py` at `ae741615f3e178ce61289a651790dc67fcc18e19` (MIT License, Copyright GitHub, Inc.); expected row: `Functions/return_values/ReturnConsistentTupleSizes.expected`. The positive function anchor is `upstream/functions_test.py:308` after the required provenance header. The combined fixture run is Inconclusive, keeps both campaign findings (`helper.py:1,6`), and abstains on this upstream positive because tuple-return analysis is partial. Upstream: 0 FPs, 0 complete-run FNs, 1 abstention.

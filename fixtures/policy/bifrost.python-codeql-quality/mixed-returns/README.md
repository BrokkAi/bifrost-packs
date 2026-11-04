# Python mixed-returns fixture

Expected finding: `helper.py:1`, whose reachable branch returns a value and whose fallthrough returns implicit `None`. `uniform` returns values on both paths; `explicit_none` explicitly returns `None` and is a near miss.


Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

From this directory, the reproducible command is:

```sh
bifrost --root . --policy-file .bifrost/policies/mixed-returns.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

## Upstream CodeQL case

The upstream Python 3 test is `github/codeql/python/ql/test/query-tests/Functions/return_values/functions_test.py` at `ae741615f3e178ce61289a651790dc67fcc18e19` (MIT License, Copyright GitHub, Inc.); expected rows: `Functions/return_values/ConsistentReturns.expected`. Its expected function anchors are `upstream/functions_test.py:20,24,338,346` after the required provenance header. The combined fixture run is Inconclusive and reports `upstream/functions_test.py:20` plus `helper.py:1`; the other three expected upstream cases abstain because return-profile analysis is partial. Upstream: 0 FPs, 0 complete-run FNs, 3 abstentions.

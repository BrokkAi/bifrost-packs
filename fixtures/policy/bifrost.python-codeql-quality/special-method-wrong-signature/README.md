# Python `special-method-wrong-signature` fixture

Mirrors CodeQL `python/ql/src/Functions/SignatureSpecialMethods.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `dbdbf306fc9d1998b01792dd43702f27e3f879a2c73c6fae11f47626d10e718e` and is `complete` with 6 findings.

## Upstream CodeQL test gate

The fixture includes 9 Python source file(s) from `github/codeql/python/ql/test/query-tests/Functions/general` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 6; actual 6; false positives 0; misses 0; completion `complete`. The comparison uses the pinned query-test expected locations.

Positive fixture locations after the attribution headers:

- `upstream/Functions/general/om_test.py:70-71`
- `upstream/Functions/general/om_test.py:73-74`
- `upstream/Functions/general/om_test.py:85-91`
- `upstream/Functions/general/om_test.py:64-65`
- `upstream/Functions/general/om_test.py:67-68`
- `upstream/Functions/general/om_test.py:61-62`

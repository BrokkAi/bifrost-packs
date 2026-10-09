# Python `unnecessary-lambda` fixture

Mirrors CodeQL `python/ql/src/Expressions/UnnecessaryLambda.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `0aa83ee8b76fb36672f1a0b35076004632fc6155512a71ac1f9e8486d4292961` and is `complete` with 6 findings.

## Upstream CodeQL test gate

The fixture includes 4 Python source file(s) from `github/codeql/python/ql/test/query-tests/Expressions/general` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 6; actual 6; false positives 0; misses 0; completion `complete`. The comparison uses exact primary locations.

Positive fixture locations after the attribution headers:

- `upstream/Expressions/general/expressions_test.py:151`
- `upstream/Expressions/general/expressions_test.py:15`
- `upstream/Expressions/general/expressions_test.py:14`
- `upstream/Expressions/general/expressions_test.py:143`
- `upstream/Expressions/general/expressions_test.py:13`
- `upstream/Expressions/general/expressions_test.py:144`

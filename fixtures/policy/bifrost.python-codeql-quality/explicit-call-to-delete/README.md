# Python `explicit-call-to-delete` fixture

Mirrors CodeQL `python/ql/src/Expressions/ExplicitCallToDel.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `fed9fd62cba96099f5461f4d3e7a6e7b9c313b72c8e7724259f7e5eb0dbff4d9` and is `complete` with 2 findings.

## Upstream CodeQL test gate

The fixture includes 4 Python source file(s) from `github/codeql/python/ql/test/query-tests/Expressions/general` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 2; actual 2; false positives 0; misses 0; completion `complete`. The comparison uses exact primary locations.

Positive fixture locations after the attribution headers:

- `upstream/Expressions/general/expressions_test.py:135`
- `upstream/Expressions/general/expressions_test.py:39`

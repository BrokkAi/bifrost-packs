# Python `raise-not-implemented` fixture

Mirrors CodeQL `python/ql/src/Exceptions/NotImplementedIsNotAnException.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `529339297c2d195e269725be55f5659d3030a977fdd840fc9fd865bfc57d11db` and is `complete` with 2 findings.

## Upstream CodeQL test gate

The fixture includes 2 Python source file(s) from `github/codeql/python/ql/test/query-tests/Exceptions/general` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 2; actual 2; false positives 0; misses 0; completion `complete`. The comparison uses exact primary locations.

Positive fixture locations after the attribution headers:

- `upstream/Exceptions/general/exceptions_test.py:201`
- `upstream/Exceptions/general/exceptions_test.py:198`

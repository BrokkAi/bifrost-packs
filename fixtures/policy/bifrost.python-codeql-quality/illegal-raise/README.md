# Python `illegal-raise` fixture

Mirrors CodeQL `python/ql/src/Exceptions/IllegalRaise.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `cf0fb7d7dbb3eb7b1b9ec34391598cf3f6da0ecdb57eabfe2fa0d13f7a15b1ac` and is `inconclusive` with 3 findings.

## Upstream CodeQL test gate

The fixture includes 2 Python source file(s) from `github/codeql/python/ql/test/query-tests/Exceptions/general` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 3; actual 3; false positives 0; misses 0; completion `inconclusive (partial_discovery)`. The comparison uses exact primary locations.

Positive fixture locations after the attribution headers:

- `upstream/Exceptions/general/exceptions_test.py:42`
- `upstream/Exceptions/general/exceptions_test.py:48`
- `upstream/Exceptions/general/exceptions_test.py:45`

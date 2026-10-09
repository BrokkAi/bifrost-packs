# Python `iter-returns-non-iterator` fixture

Mirrors CodeQL `python/ql/src/Functions/IterReturnsNonIterator.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `5e6e05da711a7c8308a61582fadeb45952a4d397db780824d39c57f0130757ac` and is `complete` with 2 findings.

## Upstream CodeQL test gate

The fixture includes 9 Python source file(s) from `github/codeql/python/ql/test/query-tests/Functions/general` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 3; actual 3; false positives 0; misses 0; completion `complete`. The comparison uses the pinned query-test expected locations.

Positive fixture locations after the attribution headers:

- `upstream/Functions/general/protocols.py:22-25`
- `upstream/Functions/general/protocols.py:22-25`

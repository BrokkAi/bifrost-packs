# Python `iter-returns-non-self` fixture

Mirrors CodeQL `python/ql/src/Functions/IterReturnsNonSelf.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `8c0c9a3fd43e6217865a0766ea547d8215cfd2b1eaa802c9a9792c59c63ad8fd` and is `complete` with 2 findings.

## Upstream CodeQL test gate

The fixture includes 1 Python source file(s) from `github/codeql/python/ql/test/query-tests/Functions/iterators` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 2; actual 2; false positives 0; misses 0; completion `complete`. The comparison uses the pinned query-test expected locations.

Positive fixture locations after the attribution headers:

- `upstream/Functions/iterators/test.py:7-8`
- `upstream/Functions/iterators/test.py:53-55`

# Python `repeated-import` fixture

Mirrors CodeQL `python/ql/src/Imports/MultipleImports.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `103ffb744c4cb039e14e6548c1d229ab46c29c66a609954fd57a7ca5afdca8c5` and is `complete` with 2 findings.

## Upstream CodeQL test gate

The fixture includes 10 Python source file(s) from `github/codeql/python/ql/test/query-tests/Imports/general` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 2; actual 2; false positives 0; misses 0; completion `complete`. The comparison uses unique primary file/line locations.

Positive fixture locations after the attribution headers:

- `upstream/Imports/general/imports_test.py:36`
- `upstream/Imports/general/imports_test.py:35`

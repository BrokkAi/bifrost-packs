# Python `import-deprecated-module` fixture

Mirrors CodeQL `python/ql/src/Imports/DeprecatedModule.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `751f43b99dd7551eb82db0fadfa2383bdf7d34f3ef6bd534114a5e7d4b3ebbcb` and is `complete` with 3 findings.

## Upstream CodeQL test gate

The fixture includes 1 Python source file(s) from `github/codeql/python/ql/test/query-tests/Imports/deprecated` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 3; actual 3; false positives 0; misses 0; completion `complete`. The comparison uses unique primary file/line locations.

Positive fixture locations after the attribution headers:

- `upstream/Imports/deprecated/test.py:4`
- `upstream/Imports/deprecated/test.py:5`
- `upstream/Imports/deprecated/test.py:10`

# Python `undefined-export` fixture

Mirrors CodeQL `python/ql/src/Variables/UndefinedExport.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `53b8d11bf51e99df77af2ba5cbe62bcff33001d04daf2bdc3e5d1c06c0a18c7b` and is `inconclusive` with 2 findings.

## Upstream CodeQL test gate

The fixture includes 16 Python source file(s) from `github/codeql/python/ql/test/query-tests/Variables/undefined` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 2; actual 2; false positives 0; misses 0; completion `inconclusive`. The comparison uses unique primary file/line locations.

Positive fixture locations after the attribution headers:

- `upstream/Variables/undefined/exports.py:3`
- `upstream/Variables/undefined/decorated_exports.py:5`

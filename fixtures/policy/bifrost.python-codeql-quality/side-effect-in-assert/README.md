# Python `side-effect-in-assert` fixture

Mirrors CodeQL `python/ql/src/Statements/SideEffectInAssert.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `ef4e18f59041533f5c314926ef24cff5c99d1df71d045cc88153d8dbb0912856` and is `complete` with 3 findings.

## Upstream CodeQL test gate

The fixture includes 2 Python source file(s) from `github/codeql/python/ql/test/query-tests/Statements/asserts` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 3; actual 3; false positives 0; misses 0; completion `complete`. The comparison uses exact primary locations.

Positive fixture locations after the attribution headers:

- `upstream/Statements/asserts/side_effect.py:7`
- `upstream/Statements/asserts/assert.py:7`
- `upstream/Statements/asserts/assert.py:10`

# Python `missing-docstring` fixture

Mirrors CodeQL `python/ql/src/Statements/DocStrings.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `e13622d44dc11ef712e3072a1b3f118504e9247b6f9cc7588ca6820b1bbdb558` and is `complete` with 4 findings.

## Upstream CodeQL test gate

The fixture includes 1 Python source file(s) from `github/codeql/python/ql/test/query-tests/Statements/DocStrings` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 4; actual 4; false positives 0; misses 0; completion `complete`. The comparison uses the pinned query-test expected locations.

Positive fixture locations after the attribution headers:

- `upstream/Statements/DocStrings/DocStrings.py:50-53`
- `upstream/Statements/DocStrings/DocStrings.py:55-58`
- `upstream/Statements/DocStrings/DocStrings.py:1-62`
- `upstream/Statements/DocStrings/DocStrings.py:42-53`

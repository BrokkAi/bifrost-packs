# Python `constant-conditional-expression` fixture

Mirrors CodeQL `python/ql/src/Statements/ConstantInConditional.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `b6eb55dc474d5f84818aa7f28780035bdd890d68bb0a1f16b0f139bf7a321908` and is `complete` with 2 findings.

## Upstream CodeQL test gate

The fixture includes 4 Python source file(s) from `github/codeql/python/ql/test/query-tests/Statements/general` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 2; actual 2; false positives 0; misses 0; completion `complete`. The comparison uses exact primary locations.

Positive fixture locations after the attribution headers:

- `upstream/Statements/general/statements_test.py:11`
- `upstream/Statements/general/statements_test.py:7`

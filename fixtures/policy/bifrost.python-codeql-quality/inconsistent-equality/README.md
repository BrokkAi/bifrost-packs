# Python `inconsistent-equality` fixture

Mirrors CodeQL `python/ql/src/Classes/Comparisons/EqualsOrNotEquals.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `56927fc10741fa7ff82305ce1173deddf4e4cbad3e15d056634103f718ebc423` and is `complete` with 2 findings.

## Upstream CodeQL test gate

The fixture includes 1 Python source file(s) from `github/codeql/python/ql/test/query-tests/Classes/equals-not-equals` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 2; actual 2; false positives 0; misses 0; completion `complete`. The comparison uses the pinned query-test expected locations.

Positive fixture locations after the attribution headers:

- `upstream/Classes/equals-not-equals/EqualsOrNotEquals.py:16-22`
- `upstream/Classes/equals-not-equals/EqualsOrNotEquals.py:39-46`

# Python `incomplete-ordering` fixture

Mirrors CodeQL `python/ql/src/Classes/Comparisons/IncompleteOrdering.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `6ad706c8b444d8fd73d8a23ffbc3d961f0e54b3efd9e59fc3dfa205c73c3852d` and is `complete` with 2 findings.

## Upstream CodeQL test gate

The fixture includes 1 Python source file(s) from `github/codeql/python/ql/test/query-tests/Classes/incomplete-ordering` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 2; actual 2; false positives 0; misses 0; completion `complete`. The comparison uses the pinned query-test expected locations.

Positive fixture locations after the attribution headers:

- `upstream/Classes/incomplete-ordering/incomplete_ordering.py:30-35`
- `upstream/Classes/incomplete-ordering/incomplete_ordering.py:5-16`

# Python `implicit-string-concatenation-in-list` fixture

Mirrors CodeQL `python/ql/src/Expressions/UnintentionalImplicitStringConcatenation.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `5b7098c98e63ada6f22c0e89834e3558b86abeefa78a58ffe81384d1cd5b65bf` and is `complete` with 8 findings.

## Upstream CodeQL test gate

The fixture includes 1 Python source file(s) from `github/codeql/python/ql/test/query-tests/Expressions/strings` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 4; actual 4 expected concatenation spans; 8 literal anchors (at least two within each expected span); false positives 0; misses 0; completion `complete`. The comparison uses at least two literal anchors inside each upstream concatenation span.

Positive fixture locations after the attribution headers:

- `upstream/Expressions/strings/test.py:38`
- `upstream/Expressions/strings/test.py:26`
- `upstream/Expressions/strings/test.py:25`
- `upstream/Expressions/strings/test.py:36`
- `upstream/Expressions/strings/test.py:19`
- `upstream/Expressions/strings/test.py:37`
- `upstream/Expressions/strings/test.py:35`
- `upstream/Expressions/strings/test.py:20`

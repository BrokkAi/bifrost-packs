# Python `multiple-calls-to-delete` fixture

Mirrors CodeQL `python/ql/src/Classes/CallsToInitDel/SuperclassDelCalledMultipleTimes.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `a0bc0f508699b09f9be1964bccd505f3023670dc030355f51c0bb06a6c10918e` and is `complete` with 2 findings.

## Upstream CodeQL test gate

The fixture includes 1 Python source file(s) from `github/codeql/python/ql/test/query-tests/Classes/multiple/multiple-del` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 2; actual 2; false positives 0; misses 0; completion `complete`. The comparison uses the pinned query-test expected locations.

Positive fixture locations after the attribution headers:

- `upstream/Classes/multiple/multiple-del/multiple_del.py:23-26`
- `upstream/Classes/multiple/multiple-del/multiple_del.py:45-48`

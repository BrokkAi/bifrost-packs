# Python `multiple-calls-to-init` fixture

Mirrors CodeQL `python/ql/src/Classes/CallsToInitDel/SuperclassInitCalledMultipleTimes.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `edd838ca9b06a18d5d8b68f86da21fd34c7c9b90ea080a07d53ed4d2c9cad90b` and is `complete` with 4 findings.

## Upstream CodeQL test gate

The fixture includes 1 Python source file(s) from `github/codeql/python/ql/test/query-tests/Classes/multiple/multiple-init` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 4; actual 4; false positives 0; misses 0; completion `complete`. The comparison uses the pinned query-test expected locations.

Positive fixture locations after the attribution headers:

- `upstream/Classes/multiple/multiple-init/multiple_init.py:44-47`
- `upstream/Classes/multiple/multiple-init/multiple_init.py:86-89`
- `upstream/Classes/multiple/multiple-init/multiple_init.py:23-26`
- `upstream/Classes/multiple/multiple-init/multiple_init.py:113-117`

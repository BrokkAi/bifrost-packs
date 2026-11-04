# Python `missing-call-to-init` fixture

Mirrors CodeQL `python/ql/src/Classes/CallsToInitDel/MissingCallToInit.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `0d1d0bef189f5819e2c1389dc74e77bf77b99928c1ee7e8219ae31325edfeff6` and is `inconclusive` with 6 findings.

## Upstream CodeQL test gate

The fixture includes 1 Python source file(s) from `github/codeql/python/ql/test/query-tests/Classes/missing-init` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 6; actual 6; false positives 0; misses 0; completion `inconclusive`. The comparison uses the pinned query-test expected locations.

Positive fixture locations after the attribution headers:

- `upstream/Classes/missing-init/missing_init.py:124-129`
- `upstream/Classes/missing-init/missing_init.py:134-139`
- `upstream/Classes/missing-init/missing_init.py:44-45`
- `upstream/Classes/missing-init/missing_init.py:69-73`
- `upstream/Classes/missing-init/missing_init.py:15-18`
- `upstream/Classes/missing-init/missing_init.py:202-205`

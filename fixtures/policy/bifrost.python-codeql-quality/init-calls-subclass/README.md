# Python `init-calls-subclass` fixture

Mirrors CodeQL `python/ql/src/Classes/InitCallsSubclass/InitCallsSubclassMethod.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `ef60680a7162ae93aeb4698ede91934d086eddbb9a967f513a2f65a8707e2f8f` and is `inconclusive` with 2 findings.

## Upstream CodeQL test gate

The fixture includes 1 Python source file(s) from `github/codeql/python/ql/test/query-tests/Classes/init-calls-subclass-method` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 2; actual 2; false positives 0; misses 0; completion `inconclusive`. The comparison uses the pinned query-test expected locations.

Positive fixture locations after the attribution headers:

- `upstream/Classes/init-calls-subclass-method/init_calls_subclass.py:34`
- `upstream/Classes/init-calls-subclass-method/init_calls_subclass.py:10`

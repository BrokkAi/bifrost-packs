# Python `missing-docstring` fixture

Mirrors CodeQL `python/ql/src/Statements/DocStrings.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.15.2 from bifrost-dev 11358-python-docstring-test-scope (BrokkAi/bifrost-dev#11705), evaluation date `2026-11-11`. The fixture run reports policy hash `5b2e47dc476874ba2e643db1f2e61c69af7a637d627c8a9765084755802d2acc` and is `complete` with 4 findings. None of the upstream declarations is test code or a script entry point, so the test-scope and entry-point exclusions leave the CodeQL comparison unchanged.

## Upstream CodeQL test gate

The fixture includes 1 Python source file(s) from `github/codeql/python/ql/test/query-tests/Statements/DocStrings` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 4; actual 4; false positives 0; misses 0; completion `complete`. The comparison uses the pinned query-test expected locations.

Positive fixture locations after the attribution headers:

- `upstream/Statements/DocStrings/DocStrings.py:50-53`
- `upstream/Statements/DocStrings/DocStrings.py:55-58`
- `upstream/Statements/DocStrings/DocStrings.py:1-62`
- `upstream/Statements/DocStrings/DocStrings.py:42-53`

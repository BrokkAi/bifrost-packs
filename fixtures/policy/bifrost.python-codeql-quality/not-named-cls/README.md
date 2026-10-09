# Python `not-named-cls` fixture

Mirrors CodeQL `python/ql/src/Functions/NonCls.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `1f76c34cd57036c400424d4795f6a97009edb923a85b4fc48bee14a6a9ef9652` and is `complete` with 4 findings.

## Upstream CodeQL test gate

The fixture includes 1 Python source file(s) from `github/codeql/python/ql/test/query-tests/Functions/methodArgNames` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 4; actual 4; false positives 0; misses 0; completion `complete`. The comparison uses unique source lines; expected markers checked within method declaration ranges.

Positive fixture locations after the attribution headers:

- `upstream/Functions/methodArgNames/parameter_names.py:23-25`
- `upstream/Functions/methodArgNames/parameter_names.py:27-30`
- `upstream/Functions/methodArgNames/parameter_names.py:39-40`
- `upstream/Functions/methodArgNames/parameter_names.py:18-20`

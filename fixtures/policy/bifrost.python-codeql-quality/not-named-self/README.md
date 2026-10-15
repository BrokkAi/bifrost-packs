# Python `not-named-self` fixture

Mirrors CodeQL `python/ql/src/Functions/NonSelf.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The fixture run reports policy hash `37fe92ff0de36dfbd10a9052bf455f7b55e0b55f5f13b5b814bc33dd5c967a45` and is `complete` with 3 findings.

## Upstream CodeQL test gate

The fixture includes 1 Python source file(s) from `github/codeql/python/ql/test/query-tests/Functions/methodArgNames` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each source file retains its full test content and starts with the pinned GitHub CodeQL path and MIT attribution. The unmarked examples in those same sources are the near misses.

Upstream comparison: expected 3; actual 3; false positives 0; misses 0; completion `complete`. The comparison uses unique source lines; expected markers checked within method declaration ranges.

Positive fixture locations after the attribution headers:

- `upstream/Functions/methodArgNames/parameter_names.py:59-60`
- `upstream/Functions/methodArgNames/parameter_names.py:56-57`
- `upstream/Functions/methodArgNames/parameter_names.py:53-54`

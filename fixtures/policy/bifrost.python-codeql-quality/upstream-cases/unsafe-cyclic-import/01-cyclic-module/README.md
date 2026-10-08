# Upstream CodeQL fixture: `unsafe-cyclic-import`

Upstream query test: `github/codeql/python/ql/test/query-tests/Imports/cyclic-module/ModuleLevelCyclicImport.expected`
CodeQL commit: `ae741615f3e178ce61289a651790dc67fcc18e19`.
Expected result rows: 3.
Python sources: 12. Each source begins with the required provenance and MIT attribution comments.

Run from this fixture directory:

```sh
bifrost --root . --policy-file .bifrost/policies/unsafe-cyclic-import.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

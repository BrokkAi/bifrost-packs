# Upstream CodeQL fixture: `polluting-import`

Upstream query test: `github/codeql/python/ql/test/query-tests/Imports/general/UnintentionalImport.expected`
CodeQL commit: `ae741615f3e178ce61289a651790dc67fcc18e19`.
Expected result rows: 1.
Python sources: 10. Each source begins with the required provenance and MIT attribution comments.

Run from this fixture directory:

```sh
bifrost --root . --policy-file .bifrost/policies/polluting-import.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

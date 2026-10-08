# syntax-error

Reports source-backed Python parser syntax-error nodes.

Expected finding: `bad.py:1`. `good.py:1-2` parses successfully.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic models were activated.

Command, run from this fixture directory:

```sh
bifrost --root . --policy-file .bifrost/policies/syntax-error.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

The policy run completed with `Complete`.

## Upstream CodeQL cases

No matching upstream query-test directory or `.expected` case exists for this pinned query under `github/codeql/python/ql/test/query-tests` at `ae741615f3e178ce61289a651790dc67fcc18e19`; the fixture therefore covers the available engine-supported behavior.

# import-and-import-from

Reports the plain `import` statement when one locally resolved module is imported with both Python forms in one scope.

Expected finding: `main.py:1` (`import helper`). `main.py:2` is the `from` form and is not selected; `other` is a different module.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic models were activated.

Command, run from this fixture directory:

```sh
bifrost --root . --policy-file .bifrost/policies/import-and-import-from.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

The policy run completed with `Complete`.

## Upstream CodeQL cases

Pinned query-test sources, including positive cases and near misses, are preserved under [`../upstream-cases/import-and-import-from/`](../upstream-cases/import-and-import-from/). Each case has its own fixture root and `.bifrost` policy copy so its original import/module layout stays intact.

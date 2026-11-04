# import-own-module

Reports a complete import whose module identity matches its enclosing Python module.

Expected finding: `main.py:1`. `main.py:2` imports `helper`, and `helper.py:1` imports `main` from a different module.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic models were activated.

Command, run from this fixture directory:

```sh
bifrost --root . --policy-file .bifrost/policies/import-own-module.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

The policy run completed with `Complete`.

## Upstream CodeQL cases

Pinned query-test sources, including positive cases and near misses, are preserved under [`../upstream-cases/import-own-module/`](../upstream-cases/import-own-module/). Each case has its own fixture root and `.bifrost` policy copy so its original import/module layout stays intact.

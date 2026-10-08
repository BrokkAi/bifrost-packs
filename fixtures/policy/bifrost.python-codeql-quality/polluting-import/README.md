# polluting-import

Reports a complete wildcard import from a resolved local module without `__all__`.

Expected finding: `main.py:1`. The wildcard import at line 2 comes from `safe_exporter`, which declares `__all__`; line 3 is a regular import.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic models were activated.

Command, run from this fixture directory:

```sh
bifrost --root . --policy-file .bifrost/policies/polluting-import.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

The policy run completed with `Complete`.

## Upstream CodeQL cases

Pinned query-test sources, including positive cases and near misses, are preserved under [`../upstream-cases/polluting-import/`](../upstream-cases/polluting-import/). Each case has its own fixture root and `.bifrost` policy copy so its original import/module layout stays intact.

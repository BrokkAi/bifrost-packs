# overly-complex-delete

Reports a destructor with reachable cyclomatic complexity above three.

Expected finding: `helper.py:2` (`Complex.__del__`). `Simple.__del__` at `helper.py:12` is the simple near miss.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic models were activated.

Command, run from this fixture directory:

```sh
bifrost --root . --policy-file .bifrost/policies/overly-complex-delete.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

The policy run completed with `Complete`.

## Upstream CodeQL cases

Pinned query-test sources, including positive cases and near misses, are preserved under [`../upstream-cases/overly-complex-delete/`](../upstream-cases/overly-complex-delete/). Each case has its own fixture root and `.bifrost` policy copy so its original import/module layout stays intact.

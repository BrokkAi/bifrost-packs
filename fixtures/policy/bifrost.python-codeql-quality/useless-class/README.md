# useless-class

Reports a public top-level class with at most one public method when the engine proves the CodeQL exclusions.

Expected finding: `bases.py:1` (`Useless`). `Useful` has two methods; `Stateful` writes instance state. The calls in `main.py` exercise all three classes.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic models were activated.

Command, run from this fixture directory:

```sh
bifrost --root . --policy-file .bifrost/policies/useless-class.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

The policy run completed with `Complete`.

## Upstream CodeQL cases

Pinned query-test sources, including positive cases and near misses, are preserved under [`../upstream-cases/useless-class/`](../upstream-cases/useless-class/). Each case has its own fixture root and `.bifrost` policy copy so its original import/module layout stays intact.

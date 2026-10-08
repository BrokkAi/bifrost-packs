# unsafe-cyclic-import

Reports proven module-level member reads and from-imports that occur before a cyclic target defines the member.

Expected findings: `a.py:2` (`b.late`) and `from_a.py:1` (`from from_b import late`). The `safe_a.py`/`safe_b.py` cycle defines `ready` before closing the cycle and is clean.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic models were activated.

Command, run from this fixture directory:

```sh
bifrost --root . --policy-file .bifrost/policies/unsafe-cyclic-import.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

The policy run completed with `Complete`.

## Upstream CodeQL cases

Pinned query-test sources, including positive cases and near misses, are preserved under [`../upstream-cases/unsafe-cyclic-import/`](../upstream-cases/unsafe-cyclic-import/). Each case has its own fixture root and `.bifrost` policy copy so its original import/module layout stays intact.

# undefined-placeholder-variable

Reports local reads that complete procedure-flow facts prove may occur before initialization.

Expected finding: `helper.py:4` (`missing_placeholder`). `initialized_in_every_arm` and `initialized_before_use` are clean local-flow controls.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic models were activated.

Command, run from this fixture directory:

```sh
bifrost --root . --policy-file .bifrost/policies/undefined-placeholder-variable.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

The policy run completed with `Complete`.

## Upstream CodeQL cases

No matching upstream query-test directory or `.expected` case exists for this pinned query under `github/codeql/python/ql/test/query-tests` at `ae741615f3e178ce61289a651790dc67fcc18e19`; the fixture therefore covers the available engine-supported behavior.

# Python `super()` class argument mismatch

Expected finding: `pkg/classes.py:8`, where `Target.bad` passes `Other` to
`super()`. The calls at lines 11 and 15 pass their owning class and are near
misses. Run completion is `Complete`.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic models are required.
The reported policy hash is
`180df8a10b8e3b8c7a5fc8535a997b59aedbc12a99cd8ae31a689c40ca67d95b`.

Reproduce from this directory:

```sh
bifrost --root . --policy-file .bifrost/policies/super-not-enclosing-class.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

## Upstream-test gate

Ran CodeQL Expressions/super/CallToSuperWrongClass.expected with both test.py and test_except.py. The expected mismatch at original test.py:10 is reported at test.py:12 after the two provenance comments; test_except.py's valid super(S, self) is clean. The suite run is Inconclusive (capability_incomplete), but its only expected row is found (FP 0, FN 0, abstentions 0).

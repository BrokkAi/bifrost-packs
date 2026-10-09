# Python hash without equality

Expected findings: `positive.py:1` (`HashOnly`) and `positive.py:19`
(`DerivedHash`). `HashAndEq` and `near_miss.py:1` (`EqOnly`) are clean.
Inherited equality does not satisfy the direct-declaration check. Run
completion is `Complete`.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic models are required.
The reported policy hash is
`a68fe71c1a543dd180f5e79481397686541109ef2fae44b426cd9172544ad290`.

Reproduce from this directory:

```sh
bifrost --root . --policy-file .bifrost/policies/equals-hash-mismatch.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

## Upstream-test gate

Ran CodeQL Classes/equals-hash/EqualsOrHash.expected (one suite, source equalsHash.py). Its expected findings are classes C and D at original lines 13 and 17; this fixture adds two provenance comment lines, so Bifrost reports equalsHash.py:15 and :19. The result is Complete and matches both rows. Classes A and B are clean near misses (FP 0, FN 0, abstentions 0).

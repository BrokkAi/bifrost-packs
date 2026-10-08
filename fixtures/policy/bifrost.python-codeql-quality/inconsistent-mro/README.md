# Python inconsistent MRO

Expected finding: `bases.py:9` (`Broken(X, Y)`). `Good(Y, X)` at line 12 is a
near miss. Run completion is `Complete`.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. No semantic models are required.
The reported policy hash is
`a6f8a0ff608da2cf47586d1970caf05f143abca3e49aee8a7984520728e43651`.

Reproduce from this directory:

```sh
bifrost --root . --policy-file .bifrost/policies/inconsistent-mro.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

## Upstream-test gate

The pinned CodeQL InconsistentMRO.ql has no query-test .expected suite or test/2/test/3 variant. I added and ran its upstream example at upstream/query-example/InconsistentMRO.py; the Y(object, X) case produces no finding in an Inconclusive run, so it is one abstention (FP 0, FN 0). The campaign Broken(X, Y) case remains Complete. The fixture .bifrostignore keeps the separately run upstream example out of the campaign result.

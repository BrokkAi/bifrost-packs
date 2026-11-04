# Python Polynomial ReDoS

Expected findings: `main.py:7, 10`; `upstream/PolynomialReDoS.py:9, 10`.

Near miss: Safe anchored whitespace regex at `main.py:8`.

The upstream test's Flask request source is outside this public lane. Its stdlib regex and sink cases are preserved with the public `sys.argv[1]` source in `upstream/PolynomialReDoS.py`.

Semantic models: `bifrost.python-security-sink-declarations.json`, `bifrost.python-security-sink-summaries.json`, `bifrost.python-stdlib-api-declarations.json`.

Validation: **ProvenBySummary**, policy hash `f5389a0ed9e2b4f2dfb5c5de203bdd859b5c5dae06c9d17e4720b624b5f5cbb2`. Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/polynomial-redos.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

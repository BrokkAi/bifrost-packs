# Python Hardcoded Credentials

Expected findings: `main.py:7, 13, 16, 17`.

Near misses: Short HMAC key at line 8 and short SMTP password at line 14.

The CodeQL upstream case sends module-level constants to a caller-defined `client.connect(username=..., password=...)`; this public rule's exact endpoints are standard-library HMAC, SMTP, and FTP credential APIs, so that generic client sink is outside its contract.

Semantic models: `bifrost.python-security-sink-declarations.json`, `bifrost.python-security-sink-summaries.json`, `bifrost.python-stdlib-api-declarations.json`.

Validation: **ProvenBySummary**, policy hash `e4c2fc9ccf60715a98a1065be5b265aeb27621e334c274cd8fe58a24526ae026`. Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/hardcoded-credentials.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

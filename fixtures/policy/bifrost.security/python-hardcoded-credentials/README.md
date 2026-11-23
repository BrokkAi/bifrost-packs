# Python Hardcoded Credentials

Expected findings on Bifrost 0.15.3 and 0.15.4: `main.py:7, 13, 16` and `hmac_overloads.py:11, 15, 19, 25, 29, 33`.

Near misses: the short HMAC keys, long messages and digest names, spread arguments, a caller-defined `new`, `hashlib.new`, and a third-party `requests` call.

Expected completion: `inconclusive` with `partial_discovery`, scoped to the files that call `hmac.new`. The active models leave these overloaded calls without complete binding, so a clean result in such a file is not proof that no flow exists. A Python file with no `hmac.new` call completes.

Known gap: `main.py:17`, the `ftplib.FTP(passwd=...)` constructor, is in the rule's stated contract but reports no finding on 0.15.3 or 0.15.4, because the engine does not expose that call as an exact external callee.

The CodeQL upstream case sends module-level constants to a caller-defined `client.connect(username=..., password=...)`; this public rule's exact endpoints are standard-library HMAC, SMTP, and FTP credential APIs, so that generic client sink is outside its contract.

Semantic models: `bifrost.python-security-sink-declarations.json`, `bifrost.python-security-sink-summaries.json`, `bifrost.python-stdlib-api-declarations.json`.

Validation: policy hash `5978477045f69db19271fafc29632b68227297a23cdc23d8af980b2fa54f1a7c` on released Bifrost 0.15.4 (`bifrost --build-identity` prints ea8da845e8d702206a9acc0c6f28d8bd18fa71c0) with `packs/v0.16.0`, evaluation date 2026-11-23.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/hardcoded-credentials.rqlp --no-builtin-policies --format json --fail-on never --evaluation-date 2026-11-23
```

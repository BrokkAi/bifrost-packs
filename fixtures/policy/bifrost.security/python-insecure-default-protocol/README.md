# Python Insecure Default Protocol

Expected findings: `main.py:5`, `upstream/InsecureProtocol.py:8`.

Near misses: Explicit `ssl.PROTOCOL_TLSv1_2` at `main.py:9` and `upstream/InsecureProtocol.py:12`.

The original CodeQL test calls `ssl.wrap_socket()` without its required `sock` argument. The fixture adds the required argument while preserving the default-protocol case.

Semantic models: `bifrost.python-stdlib-api-declarations.json` and
`bifrost.python-ssl-protocol-declarations.json` (the complete SSL artifact
declares the `ssl.wrap_socket` signature).

Validation: **Complete**, policy hash `7f75179bc93797e45910ca813fc7a2e578798b05bddbf65a4dddb7ef8dac2ca8`. Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/insecure-default-protocol.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

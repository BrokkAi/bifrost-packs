# Python Insecure SSL/TLS Protocol

Expected findings: `main.py:5-12`; `upstream/InsecureProtocol.py:7-12`.

Near misses: Modern or compatibility protocols at `main.py:13-22` and `upstream/InsecureProtocol.py:13-14`; local lookalike at `main.py:23`.

Semantic model: `bifrost.python-ssl-protocol-declarations.json`, complete for the nine declared `ssl.PROTOCOL_*` constants and the `ssl.wrap_socket(ssl_version)` / `ssl.SSLContext.__init__(protocol)` signatures.

Validation: **Complete**, policy hash `79a24169888d2b3e54bf5c44f0154c94eecc519b196916b68bbf8f7f9b094559`. Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/insecure-protocol.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

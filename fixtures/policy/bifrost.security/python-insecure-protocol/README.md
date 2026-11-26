# Python Insecure SSL/TLS Protocol

Expected findings: `main.py:5-12`; `upstream/InsecureProtocol.py:7-12`.

Near misses: Modern or compatibility protocols at `main.py:13-22` and `upstream/InsecureProtocol.py:13-14`; local lookalike at `main.py:23`.

Semantic model: `bifrost.python-ssl-protocol-declarations.json`, which declares the nine `ssl.PROTOCOL_*` constants and the `ssl.wrap_socket(ssl_version)` / `ssl.SSLContext.__init__(protocol)` signatures. The pack is marked `partial` from 1.0.1 (#463), because it is not a complete Python declaration surface. On the released Bifrost 0.15.4 with the native `packs/v0.16.0` bundle the run is still **Inconclusive** (`partial_discovery`) with no findings, under either marking.

The policy binds only calls whose callee is spelled `wrap_socket` or `SSLContext` (#410). An API imported under another name is outside its selection.

Validation: **Inconclusive** (`partial_discovery`) with no findings, policy hash `b6e46fd4d814eb4fdac9cec0b726762b474572c776b5453257eed4ef290f7c3b`, on the released Bifrost 0.15.3 (`bifrost --build-identity` prints cc7ebd1676e002b657e10304cfd977bc289e25ed) with the native `packs/v0.15.0` bundle, evaluation date 2026-10-08. The `ssl.SSLContext` calls have no complete actual-to-formal binding and `resolved-value` cannot prove one unshadowed constant identity (bifrost-dev#5240), so the expected findings above are not reproduced on this engine. With `BIFROST_OPEN_PACKS_DISABLE=1` and no installed bundle the run is `not_run` (`qualified-call-locator-zero` for `ssl.SSLContext.__init__`). The previous selector, which bound every call, gave the same completion, diagnostics and findings on the same engine and bundle. The last complete validation, with all 14 expected findings, is the Bifrost 0.15.0 record in `docs/qualification/v0150-precise-capabilities.md`.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/insecure-protocol.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

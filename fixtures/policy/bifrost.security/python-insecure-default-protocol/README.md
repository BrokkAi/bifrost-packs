# Python Insecure Default Protocol

Expected findings: `main.py:5`, `imports.py:9`, `imports.py:13`, `upstream/InsecureProtocol.py:8`.

Near misses: Explicit `ssl.PROTOCOL_TLSv1_2` at `main.py:9` and `upstream/InsecureProtocol.py:12`.

Not examined: `imports.py:17` calls `ssl.wrap_socket` through a function imported under another name (`from ssl import wrap_socket as renamed_wrap_socket`). The policy binds only calls whose callee is spelled `wrap_socket` (#410), so this call is outside its selection: it is not reported and does not make the run incomplete. `imports.py:9` (`from ssl import wrap_socket`) and `imports.py:13` (`import ssl as tls`) keep the spelling and are reported. Before #410 the policy bound every call in the file and reported `imports.py:17` too.

The original CodeQL test calls `ssl.wrap_socket()` without its required `sock` argument. The fixture adds the required argument while preserving the default-protocol case.

Semantic models: `bifrost.python-stdlib-api-declarations.json` and
`bifrost.python-ssl-protocol-declarations.json` (the bounded SSL artifact
declares the `ssl.wrap_socket` signature). The SSL artifact is marked `partial`
from 1.0.1 (#463). On the released Bifrost 0.15.4 with the native
`packs/v0.16.0` bundle the run is **Complete** with the four expected findings
under either marking.

Validation: **Complete**, policy hash `0199b6d1d86a0e6b8b00ba26da1742a5bd16698fb1e2cf8fa3b400057e962eac`. Validated with the released Bifrost 0.15.3 (`bifrost --build-identity` prints cc7ebd1676e002b657e10304cfd977bc289e25ed) and the native `packs/v0.15.0` bundle, evaluation date 2026-10-08. On that engine the fixture's own `.bifrost/semantic-models` do not resolve `ssl.wrap_socket` by themselves: with `BIFROST_OPEN_PACKS_DISABLE=1` and no installed bundle the run is `not_run` (`qualified-call-locator-zero`).

Run from this fixture directory, with the released packs bundle available (the default, or `BIFROST_SEMANTIC_PACK_CACHE_ROOT` naming an installed bundle):

```console
bifrost --root . --policy-file .bifrost/policies/insecure-default-protocol.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

# Python Insecure Temporary File

Expected findings: `main.py:7, 8`; `upstream/InsecureTemporaryFile.py:7`.

Near misses:
- Secure `tempfile.NamedTemporaryFile()` at `main.py:11`.
- A local `mktemp` helper that creates the file with `tempfile.mkstemp` at `local_shadow.py:5-13`. Its call does not resolve to `tempfile.mktemp`.
- `os.tempnam()` and `os.tmpnam()` at `main.py:9, 10` and `upstream/InsecureTemporaryFile.py:8, 9`. CodeQL's query names them, but they are Python 2 APIs that were removed in Python 3.0, so no supported CPython declares them and the policy does not select them (#96). Before #96 the policy also required exact `os.tempnam` and `os.tmpnam` identities, and on a real project such as pip, where nothing declared them, the whole run was `not_run`. `bifrost.python-stdlib-api-declarations` 0.8.0 removes the two made-up declarations.

Semantic models: `bifrost.python-stdlib-api-declarations.json` (0.5.0 snapshot, without the two Python 2 declarations). `tempfile.mktemp` is also declared by the typeshed stdlib pack.

Validation:
- Released Bifrost 0.15.4 (build `ea8da845e8d702206a9acc0c6f28d8bd18fa71c0`) with the native `packs/v0.16.0` bundle, evaluation date 2026-11-25: **not run**, `qualified-call-locator-ambiguous`. `tempfile.mktemp` resolves to both the typeshed identity and `member.python.tempfile.mktemp`. This is BrokkAi/bifrost-dev#14548. Its fix ("the single semantic pack that certifies a callable family" answers) is listed for Bifrost 0.15.5.
- Unreleased bifrost-dev build `4a837c2daf758ac6836e5e551f905b98aaff82ff` (contains that fix; supplementary evidence only), same bundle and date: **Complete**, exactly the three expected findings above, policy hash `08c73737ad195d1dec4e4a62d6dcf6f5451c34ae9db5dd371ee612bc1ff1f5eb`. A pip-shaped control (`NamedTemporaryFile(delete=False, dir=..., prefix=..., suffix=".tmp")`, `requires-python >=3.10`, no workspace models) is complete with no findings.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/insecure-temporary-file.rqlp --no-builtin-policies --format json --evaluation-date 2026-11-25
```

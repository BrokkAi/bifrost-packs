# Python Insecure Temporary File

Expected findings: `main.py:7, 8, 9, 10`; `upstream/InsecureTemporaryFile.py:7, 8, 9`.

Near miss: Secure `tempfile.NamedTemporaryFile()` at `main.py:11`.

Semantic models: `bifrost.python-stdlib-api-declarations.json`.

Validation: **Complete**, policy hash `354e457ef8ed2dbb32e0123851f5937c1ee95b497ee4f41a75f8bc87bd181c5c`. Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/insecure-temporary-file.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

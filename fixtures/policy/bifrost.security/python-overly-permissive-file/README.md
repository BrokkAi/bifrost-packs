# Python Overly Permissive File

Expected findings: `main.py:7, 9`; `upstream/WeakFilePermissions.py:6, 7, 8, 10, 11, 12`.

Near misses: Owner-only modes at `main.py:8, 10, 11` and `upstream/WeakFilePermissions.py:9`.

Semantic models: `bifrost.python-stdlib-api-declarations.json`.

Validation: **Complete**, policy hash `7a020c360d47cdaf64b53f0984fc4bf6e71b6ba1e27427ef699752ba59c1ad70`. Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/overly-permissive-file.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

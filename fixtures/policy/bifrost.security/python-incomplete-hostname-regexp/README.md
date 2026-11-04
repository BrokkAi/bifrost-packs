# Python Incomplete Hostname Regexp

Expected findings: `app.py:3`, `upstream/hosttest.py:4`.

Near misses: Escaped hostname dots at `app.py:4` and `upstream/hosttest.py:5`; unrelated escaped URL at `upstream/hosttest.py:6`.

Semantic models: none.

Validation: **Complete**, policy hash `aa61c11d6c8a4872ae2d49fc84f0e8c341e4fb59dc7430972c62daf99488567d`. Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/incomplete-hostname-regexp.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

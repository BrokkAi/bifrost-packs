# Python Incomplete URL Substring Sanitization

Expected findings: `helpers.py:5, 9, 17`; `upstream/urltest.py:8, 10`.

Near misses: Boundary-aware suffix at `helpers.py:13` and `upstream/urltest.py:16`; scheme-anchored prefix at `helpers.py:21` and `upstream/urltest.py:19`; parsed hostname equality at `helpers.py:25`; allowlist membership at `upstream/urltest.py:13`; reversed membership at `helpers.py:29`.

The upstream Flask request/redirect wrappers were omitted. This public structural rule models no framework source or sink.

Semantic models: none.

Validation: **Complete**, policy hash `1684f3722e5cb61e7bb4221bc5da37fc4b03f69f9098ffcc526552cc8d1e509b`. Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/incomplete-url-substring-sanitization.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

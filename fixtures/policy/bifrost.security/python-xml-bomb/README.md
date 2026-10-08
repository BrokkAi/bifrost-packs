# Python XML Bomb

Expected findings: `main.py:13, 14, 15`.

Near miss: Constant XML string at `main.py:16`; public source is `sys.argv[1]` at line 12.

The CodeQL upstream case uses Flask request input and `lxml.etree`; those third-party APIs are outside this standard-library fixture and are not included here.

Semantic models: `bifrost.python-security-sink-declarations.json`, `bifrost.python-security-sink-summaries.json`, `bifrost.python-stdlib-api-declarations.json`.

Validation: **ProvenBySummary**, policy hash `bd31c05263190d0308de01ecccf69528957895038aaa5ec08f37c10035b86e85`. Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/xml-bomb.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

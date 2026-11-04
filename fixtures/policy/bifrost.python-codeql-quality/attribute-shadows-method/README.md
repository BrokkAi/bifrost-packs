# `py/attribute-shadows-method`

Reports a descendant method hidden by an ancestor initializer's proven attribute write. The policy uses complete Python C3 ancestry and local flow; it excludes same-class methods, setters, and writable properties. A read-only property is retained because the ancestor write may fail at runtime.

## Validation

- Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.
- Command, run from this directory: `bifrost --root . --policy-file .bifrost/policies/attribute-shadows-method.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08`.
- Completion: `Complete`; policy hash `92c60463ce2ce407c26af5c44d6b9d5bdf94ef236a74335e0b118f52db5ad90e`.
- Expected findings: `positive.py:7`, `engine_cases.py:7`, `engine_cases.py:18`, and the read-only property at `engine_cases.py:54`.
- Clean near misses: the base-owned same-name method, the writable property, the setter, and the campaign's same-class and writable-property cases.
- No semantic model is required.

The policy covers transitive ancestry and property exclusions; unknown ancestry and dynamic initializer writes remain incomplete. Source query: `python/ql/src/Classes/SubclassShadowing/SubclassShadowing.ql`, CodeQL commit `ae741615f3e178ce61289a651790dc67fcc18e19`.


## Upstream-test gate

Ran CodeQL Classes/subclass-shadowing/SubclassShadowing.expected (one suite, source subclass_shadowing.py). Both expected rows, original lines 11 and 41, are reported at fixture lines 13 and 43 after the two provenance comments. The superclass-own-method and writable-property/setter cases are clean. Run completion is Complete (FP 0, FN 0, abstentions 0).

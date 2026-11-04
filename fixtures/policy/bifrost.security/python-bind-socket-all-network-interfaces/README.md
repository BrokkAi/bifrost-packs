# Python Bind Socket All Network Interfaces

Campaign fixture findings: `main.py:7, 13, 18`.

Upstream cases: `upstream/BindToAllInterfaces_test.py:7, 8, 11` are the direct IPv4, empty-host, and IPv6 positives; lines 9 and 12 are the dedicated-interface and Unix-socket near misses. The upstream-only run has candidate findings but is Inconclusive because the pinned engine reports unknown procedure semantics for the copied test function. The accepted campaign validation therefore selects `main.py` only.

Semantic models: `bifrost.python-security-sink-declarations.json`, `bifrost.python-security-sink-summaries.json`, `bifrost.python-stdlib-api-declarations.json`.

Campaign validation: **ProvenBySummary**, policy hash `763c209d50e7e3ce8b06b7f3aa30a4e258d36f90adc23ebbee2b731ba99554a1`. Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

```console
bifrost --root . --policy-file .bifrost/policies/bind-socket-all-network-interfaces.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08 --sources main.py
```

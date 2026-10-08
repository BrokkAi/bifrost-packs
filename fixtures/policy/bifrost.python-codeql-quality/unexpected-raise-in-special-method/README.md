# Python unexpected-raise-in-special-method fixture

Expected finding: `helper.py:3`, where `__getitem__` raises `ValueError`. `KeyError` at line 8 is allowed by the lookup protocol, and the `ValueError()` at line 13 is only constructed, not raised.


Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

From this directory, the reproducible command is:

```sh
bifrost --root . --policy-file .bifrost/policies/unexpected-raise-in-special-method.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

## Upstream CodeQL case

The upstream Python 3 test is `github/codeql/python/ql/test/query-tests/Functions/IncorrectRaiseInSpecialMethod/test.py` at `ae741615f3e178ce61289a651790dc67fcc18e19` (MIT License, Copyright GitHub, Inc.); expected rows: `Functions/IncorrectRaiseInSpecialMethod/IncorrectRaiseInSpecialMethod.expected`. All six CodeQL method anchors have corresponding Bifrost findings at their raise expressions; the combined fixture also retains `helper.py:3`. Upstream: 0 FPs, 0 missing expected cases, 0 expected-case abstentions; the run is Inconclusive, and all six anchors differ from CodeQL's method anchors.

The RQL fact is anchored to a `throw` and does not expose the owning procedure ID. Anchor probes are recorded in the lane report: `procedure-of` and `enclosing-decl` reject a `python_rule_fact` input, while `python-special-method-raise` rejects declaration input. RQL can select methods separately, but cannot correlate that method row to the filtered raise fact or transfer the finding anchor. I therefore kept the finding at the proven raise site rather than emit a method-level approximation.

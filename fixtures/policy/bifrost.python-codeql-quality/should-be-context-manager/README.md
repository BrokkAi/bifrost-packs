# Python resource context-manager fixture

Expected finding: `bases.py:1` (`Resource` has `__del__` and neither context-manager method). `SafeResource` implements both methods; `PartialResource` implements `__enter__`, so both are clean controls.


Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.

From this directory, the reproducible command is:

```sh
bifrost --root . --policy-file .bifrost/policies/should-be-context-manager.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08
```

## Upstream CodeQL case

The upstream Python 3 test is `github/codeql/python/ql/test/query-tests/Classes/should-be-context-manager/should_be_context_manager.py` at `ae741615f3e178ce61289a651790dc67fcc18e19` (MIT License, Copyright GitHub, Inc.); expected rows: `Classes/should-be-context-manager/ShouldBeContextManager.expected`. Its two positives are `upstream/should_be_context_manager.py:5,18` after the required provenance header. The combined fixture run is Complete and reports both upstream classes plus `bases.py:1`: 0 upstream FPs, 0 FNs, 0 abstentions.

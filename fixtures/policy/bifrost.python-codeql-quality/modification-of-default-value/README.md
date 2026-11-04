# Python `modification-of-default-value` fixture

Mirrors CodeQL `python/ql/src/Functions/ModificationOfParameterWithDefault.ql` from commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. The policy fixture uses Python 3.12.0 and requires no semantic models. The original campaign-only fixture run is Complete. With upstream tests included, the combined fixture run is Inconclusive (`partial_discovery`) with 29 findings total: the 11 campaign cases and 18 of 29 upstream rows. The 11 upstream rows not returned are abstentions, not complete-run misses.

Expected findings: `test.py:2,6,9,12,15,18,21,24,27,33,37` (the 11 proven mutating operations). Near misses in this fixture stay clean: rebinding, immutable defaults, empty guards, non-default values, copied values, and other locals.

## CodeQL upstream test gate

Includes all 1 Python source files from `github/codeql/python/ql/test/query-tests/Functions/ModificationOfParameterWithDefault` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each copied file starts with its upstream path and `MIT License, Copyright GitHub, Inc.` attribution. Compare `ModificationOfParameterWithDefault.expected` (CodeQL upstream subpath selections): 29 expected rows; pinned Bifrost produced 18; FP 0, FN 0, abstentions 11; completion inconclusive: partial_discovery. Raw command, JSON, and comparison are in the parent handback report artifacts.

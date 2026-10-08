# Python `unused-global-variable` fixture

Mirrors CodeQL `python/ql/src/Variables/UnusedModuleVariable.ql` from commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. The policy fixture uses Python 3.12.0 and requires no semantic models. The original campaign-only fixture run is Complete. With upstream tests included, the combined fixture run is Inconclusive (`capability_incomplete`): the campaign positive remains, while all six upstream expected rows abstain with no false positives.

Expected findings: `helper.py:1` (`unused_global`). Near misses in this fixture stay clean: `helper.py:2` (`used_global`), which is read in `exported()`.

A separate `locals()` control is Inconclusive with no finding because dynamic namespace reads make the binding-use set incomplete. Its log is in the parent report directory.

## CodeQL upstream test gate

Includes all 4 Python source files from `github/codeql/python/ql/test/query-tests/Variables/unused` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each copied file starts with its upstream path and `MIT License, Copyright GitHub, Inc.` attribution. Compare `UnusedModuleVariable.expected` (CodeQL upstream expected alerts): 6 expected rows; pinned Bifrost produced 0; FP 0, FN 0, abstentions 6; completion inconclusive: capability_incomplete. Raw command, JSON, and comparison are in the parent handback report artifacts.

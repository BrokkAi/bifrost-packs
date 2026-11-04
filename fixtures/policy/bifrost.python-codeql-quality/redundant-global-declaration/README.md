# Python `redundant-global-declaration` fixture

Mirrors CodeQL `python/ql/src/Variables/GlobalAtModuleLevel.ql` from commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08. The policy fixture uses Python 3.12.0 and requires no semantic models. The combined fixture run is Complete with two findings: the campaign positive and the one upstream positive. The upstream case has no false positives, false negatives, or abstentions.

Expected findings: `helper.py:1` (`global configured` at module scope). Near misses in this fixture stay clean: `helper.py:7` function-local `global configured` directive.

## CodeQL upstream test gate

Includes all 3 Python source files from `github/codeql/python/ql/test/query-tests/Variables/general` at `ae741615f3e178ce61289a651790dc67fcc18e19`. Each copied file starts with its upstream path and `MIT License, Copyright GitHub, Inc.` attribution. Compare `GlobalAtModuleLevel.expected` (CodeQL upstream expected alerts): 1 expected rows; pinned Bifrost produced 1; FP 0, FN 0, abstentions 0; completion complete. Raw command, JSON, and comparison are in the parent handback report artifacts.

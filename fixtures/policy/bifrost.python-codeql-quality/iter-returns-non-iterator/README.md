# Python `iter-returns-non-iterator` fixture

Mirrors CodeQL `python/ql/src/Functions/IterReturnsNonIterator.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

The fixture declares Python 3.12 in `.python-version` and `pyproject.toml`. It contains the complete upstream `protocols.py` query test and the other six Python source files from `github/codeql/python/ql/test/query-tests/Functions/general` as clean controls. Each source file retains its contents and starts with the pinned GitHub CodeQL path and MIT attribution. The object declaration model from this branch is active for validation.

## Expected findings

The upstream expected file contains four rows. Bifrost 0.13.0, build identity `a48861ce8e3f82ed3aa3f6c3aa63ecc8b7b4f7d9`, reports four findings at `protocols.py:16`, `protocols.py:20` (two), and `protocols.py:30`; the `__iter__` method lines are 16, 22, 27, and 40. The row for location-less builtin `object` maps to the returning method at upstream line 16. In the copied fixture, the two-line attribution header and blank line shift these locations to `upstream/Functions/general/protocols.py:18`, `:22` (two findings), and `:32`. The six other source files produce no findings.

The protocol run is inconclusive because of one unrelated `UnresolvedCall` diagnostic in `protocols.py:62-63`. With a leading comment line, findings shift by one line and the diagnostic is at lines 63-64. Both variants have zero false positives and zero misses.

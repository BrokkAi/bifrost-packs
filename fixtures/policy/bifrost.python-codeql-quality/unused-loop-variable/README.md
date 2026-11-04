# `py/unused-loop-variable`

Reports lexical variable cases covered by the pinned CodeQL query `Variables/SuspiciousUnusedLoopIterationVariable.ql`. The fixture contains the decisive upstream positives and local near-miss controls. Despite its legacy filename, `positive.py` is an implicit-repeat control: its single `consume(1)` statement is excluded by the upstream query's `implicit_repeat` predicate and is expected to remain clean. `near_miss.py` reads the loop target and is also expected to remain clean.

## Validation

- Engine: Bifrost 0.13.1, build identity `9ace1176a28f5b1d790a76872c6fd038dbd4e2f8`.
- Evaluation date: `2026-10-17`; run completion: `complete`; policy hash: `858f54f5edc4e25ebf5cb7d606e71f209d2ea40ed2e266d4d134c9ac6d81de11`.
- Command from this directory: `BIFROST_OPEN_PACKS_DISABLE=1 bifrost --root . --policy-file .bifrost/policies/unused-loop-variable.rqlp --no-builtin-policies --no-incremental --format json --fail-on never --evaluation-date 2026-10-17`.
- Expected findings:
- `upstream_test.py:6`
- `upstream_test.py:68`
- `upstream_test.py:74`
- `upstream_test.py:80`
- `upstream_test.py:108`
- `upstream_variables_test.py:135`
- `near_miss.py` is clean.

The upstream source is from `github/codeql` at `ae741615f3e178ce61289a651790dc67fcc18e19`; its MIT attribution is retained in each source file and covered by `NOTICE.md` / `licenses/CodeQL-MIT.txt`.

# `py/nested-loops-with-same-variable`

Reports lexical variable cases covered by the pinned CodeQL query `Statements/NestedLoopsSameVariable.ql`. The fixture contains an explicit positive and realistic near miss, plus the decisive CodeQL upstream test source(s).

## Validation

- Engine: Bifrost 0.13.1, build identity `9ace1176a28f5b1d790a76872c6fd038dbd4e2f8`.
- Evaluation date: `2026-10-17`; run completion: `complete`; policy hash: `7ef74c4ad8411fea483b447ddd879569a7a4bbeb19dada92578822afa3dc70f1`.
- Command from this directory: `BIFROST_OPEN_PACKS_DISABLE=1 bifrost --root . --policy-file .bifrost/policies/nested-loops-with-same-variable.rqlp --no-builtin-policies --no-incremental --format json --fail-on never --evaluation-date 2026-10-17`.
- Expected findings:
- `positive.py:4`
- `upstream_nested.py:5`
- `upstream_nested.py:21`
- `upstream_nested.py:29`
- `upstream_nested.py:37`
- `upstream_nested.py:44`
- `upstream_nested.py:52`
- `near_miss.py` is clean.

The upstream source is from `github/codeql` at `ae741615f3e178ce61289a651790dc67fcc18e19`; its MIT attribution is retained in each source file and covered by `NOTICE.md` / `licenses/CodeQL-MIT.txt`.

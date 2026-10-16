# `py/unused-parameter`

Reports lexical variable cases covered by the pinned CodeQL query `Variables/UnusedParameter.ql`. The fixture contains an explicit positive and realistic near miss, plus the decisive CodeQL upstream test source(s).

## Validation

- Engine: Bifrost 0.13.1, build identity `9ace1176a28f5b1d790a76872c6fd038dbd4e2f8`.
- Evaluation date: `2026-10-17`; run completion: `complete`; policy hash: `ed8bfb97b65ff134952f8e41fcc4496aa3c82db48b3b9df8631cfbfa1401559c`.
- Command from this directory: `BIFROST_OPEN_PACKS_DISABLE=1 bifrost --root . --policy-file .bifrost/policies/unused-parameter.rqlp --no-builtin-policies --no-incremental --format json --fail-on never --evaluation-date 2026-10-17`.
- Expected findings:
- `positive.py:1`
- `upstream_variables_test.py:27`
- `near_miss.py` is clean.

The upstream source is from `github/codeql` at `ae741615f3e178ce61289a651790dc67fcc18e19`; its MIT attribution is retained in each source file and covered by `NOTICE.md` / `licenses/CodeQL-MIT.txt`.

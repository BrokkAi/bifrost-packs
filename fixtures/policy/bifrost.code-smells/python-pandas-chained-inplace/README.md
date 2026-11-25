# `python-pandas-chained-inplace` fixture

Exercises `bifrost.correctness.python-pandas-chained-inplace` (BrokkAi/bifrost-packs#451, arm 1).

Validated with the Bifrost 0.15.4 `aarch64-apple-darwin` release (archive SHA-256 verified, build `ea8da845e8d7`, the same build identity as the Linux CLI pinned in `policy-authoring.json`) on 2026-11-25. No semantic models are needed. The run is `complete`, with no diagnostics and these definite findings:

- `positive.py:5`: `stats["Time"].fillna("-", inplace=True)` (the pingouin pre-image shape).
- `positive.py:10`: `df.loc[mask, "x"].clip(lower=0, inplace=True)`.
- `positive.py:11`: `df.iloc[:, 0].replace(0, 1, inplace=True)`.

The near misses produce no findings:

- `near_miss.py`: assigning the result back, whole-frame `inplace=True` calls, `frames[i].dropna(inplace=True)`
  on a list element, and selections without `inplace`.

## Real code

On the pre-fix parent of raphaelvallat/pingouin@790ae3f (`3a468ac5`) the rule reports
`src/pingouin/pairwise.py:593`, the line the fix changed. At current heads of pingouin, PyPortfolioOpt, backtesting.py, networkx and bifrost-service the rule is `complete` with no findings.

## Known edges

- The rule is not gated on the pandas version. Under Copy-on-Write (pandas 3.0, or `mode.copy_on_write`) the call
  never changes the frame; before that it changes it only when the selection is a view, and pandas 2.2 warns.
  The finding is a correctness prompt either way.
- A dict of DataFrames indexed by a string literal, such as `frames["train"].dropna(inplace=True)`, is reported:
  the receiver type is not resolved.
- Attribute column access (`df.col.fillna(..., inplace=True)`) and chained subscripts with non-literal keys are
  not selected, because they cannot be told apart from ordinary objects without pandas types.

## Reproduce

```bash
cd fixtures/policy/bifrost.code-smells/python-pandas-chained-inplace
bifrost --root . --policy-file .bifrost/policies/python-pandas-chained-inplace.rqlp --format json --fail-on never --output report.json
```

The fixture copy of the policy must match `rules/bifrost.code-smells/policies/python-pandas-chained-inplace.rqlp`.

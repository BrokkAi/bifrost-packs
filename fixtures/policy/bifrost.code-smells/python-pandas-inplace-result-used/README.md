# `python-pandas-inplace-result-used` fixture

Exercises `bifrost.correctness.python-pandas-inplace-result-used` (BrokkAi/bifrost-packs#451, arm 2).

Validated with the Bifrost 0.15.4 `aarch64-apple-darwin` release (archive SHA-256 verified, build `ea8da845e8d7`, the same build identity as the Linux CLI pinned in `policy-authoring.json`) on 2026-11-25. No semantic models are needed. The run is `complete`, with no diagnostics and these definite findings:

- `positive.py:5`: `out = df.dropna(inplace=True)`.
- `positive.py:10`: `return df.sort_values("a", inplace=True)`.
- `positive.py:14`: `df.reset_index(drop=True, inplace=True).rename(...)` (receiver of another call).
- `positive.py:19`: `index = index.set_names(names, inplace=True)`.

The near misses produce no findings:

- `near_miss.py`: whole-frame `inplace=True` calls used as statements, `dropna()` and `dropna(inplace=False)`
  results, and `torch.nn.ReLU(inplace=True)`, `nn.Dropout(..., inplace=True)` and `F.relu(x, inplace=True)`,
  whose names are not pandas inplace methods.

## Real code

At current heads of pingouin, PyPortfolioOpt, backtesting.py, networkx and bifrost-service the rule is `complete` with no findings.

## Known edges

- The receiver type is not resolved. A non-pandas method with one of the listed names (`dropna`, `fillna`,
  `replace`, `rename`, `reset_index`, `set_index`, `sort_values`, `sort_index`, `drop`, `drop_duplicates`,
  `interpolate`, `clip`, `where`, `mask`, `query`, `eval`, `ffill`, `bfill`, `pad`, `backfill`, `set_names`,
  `set_levels`, `set_codes`, `set_axis`) that takes `inplace=True` and returns a value would be reported.
- Only a literal `inplace=True` is selected; `inplace=flag` is not.
- A result passed as an argument, such as `print(df.dropna(inplace=True))`, is not selected.

## Reproduce

```bash
cd fixtures/policy/bifrost.code-smells/python-pandas-inplace-result-used
bifrost --root . --policy-file .bifrost/policies/python-pandas-inplace-result-used.rqlp --format json --fail-on never --output report.json
```

The fixture copy of the policy must match `rules/bifrost.code-smells/policies/python-pandas-inplace-result-used.rqlp`.

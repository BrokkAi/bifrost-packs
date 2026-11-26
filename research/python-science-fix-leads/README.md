# Python science and quant fix-commit leads

These rule leads come from public bug-fix history (2023 to 2026, plus the fixes linked from GHSA advisories) in numpy, scipy, pandas, statsmodels, scikit-learn, networkx, mpmath, pingouin, PyPortfolioOpt and backtesting.py. Each lead is a queued research candidate, not an implemented rule or a vulnerability report. The issues hold the pre-fix commits, files and lines, and the qualification cases.

Kinds: (a) a general Python pattern; (b) a misuse of a numpy, pandas or scikit-learn API that needs a semantic model. A "gap" lead names an existing rule that would plausibly miss the fix's pre-image.

| Issue | Package (evidence) | Fix commit(s) | Kind | Existing rule | Contract |
| --- | --- | --- | --- | --- | --- |
| [#446](https://github.com/BrokkAi/bifrost-packs/issues/446) | numpy, pandas, scikit-learn (joblib) | `numpy/numpy@89b6887` | (b) library API misuse; gap | bifrost.correctness.unsafe-deserialization (pickle.load/loads by receiver name only) | Model numpy, pandas and joblib pickle-backed loaders on untrusted paths |
| [#447](https://github.com/BrokkAi/bifrost-packs/issues/447) | scikit-learn | `scikit-learn/scikit-learn@70ca21f` | (b) library API misuse, version-gated | none | Model persisted scikit-learn text vectorizers that retain pruned training tokens |
| [#448](https://github.com/BrokkAi/bifrost-packs/issues/448) | scipy, statsmodels, scikit-learn, pandas, backtesting.py | `scipy/scipy@971be31`, `scipy/scipy@e368cd4`, `statsmodels/statsmodels@6f2bda5`, `scikit-learn/scikit-learn@85302bb`, `pandas-dev/pandas@ddceb8e` | (b) semantic numpy model | none (modification-of-default-value covers defaults only) | Flag in-place writes to caller-owned array arguments |
| [#449](https://github.com/BrokkAi/bifrost-packs/issues/449) | scipy | `scipy/scipy@ac5ae74`, `scipy/scipy@0005d0f`, `scipy/scipy@b92b297` | (a) general Python | none (modification-of-default-value covers literal defaults only) | Flag options and kwargs dicts mutated after `x = x or {}` |
| [#450](https://github.com/BrokkAi/bifrost-packs/issues/450) | numpy | `numpy/numpy@f76c61e` | (a) general Python | none | Flag class-level mutable attributes mutated through an instance alias |
| [#451](https://github.com/BrokkAi/bifrost-packs/issues/451) | pandas (callers: pingouin, statsmodels) | `raphaelvallat/pingouin@790ae3f`, `statsmodels/statsmodels@350256c` | (b) semantic pandas model | none | Flag `inplace=True` on a column selection or caller-owned pandas object |
| [#452](https://github.com/BrokkAi/bifrost-packs/issues/452) | pandas (caller: PyPortfolioOpt) | `PyPortfolio/PyPortfolioOpt@a4e2ee5` | (b) semantic pandas model | none | Flag `pct_change()` with the default padding over NaN gaps in price series |
| [#453](https://github.com/BrokkAi/bifrost-packs/issues/453) | scipy, PyPortfolioOpt, backtesting.py | `scipy/scipy@2aa5509`, `PyPortfolio/PyPortfolioOpt@d508869`, `kernc/backtesting.py@3a83e71` | (b) semantic numpy/pandas model | none | Flag integer-dtype buffers that later receive float values |
| [#454](https://github.com/BrokkAi/bifrost-packs/issues/454) | backtesting.py | `kernc/backtesting.py@14f111a` | (b) semantic numpy/pandas model | none | Flag `astype(int)` on datetime and nanosecond values (platform-width integer) |
| [#455](https://github.com/BrokkAi/bifrost-packs/issues/455) | pingouin | `raphaelvallat/pingouin@1ffb923` | (a) general Python | none (side-effect-in-assert and assert-literal-constant are different contracts) | Flag `assert` used to validate public-API arguments |
| [#456](https://github.com/BrokkAi/bifrost-packs/issues/456) | networkx | `networkx/networkx@35a5574` | (a) general Python; gap | bifrost.python-codeql-quality.comparison-using-is (needs resolved value-equality operand types) | Flag `is`/`is not` comparing values of unresolved or generic type |
| [#457](https://github.com/BrokkAi/bifrost-packs/issues/457) | scikit-learn, statsmodels | `scikit-learn/scikit-learn@5f91dca`, `statsmodels/statsmodels@cce9093` | (b) semantic numpy model | none | Flag global numpy RNG calls where a seeded generator is in scope |
| [#458](https://github.com/BrokkAi/bifrost-packs/issues/458) | PyPortfolioOpt | `PyPortfolio/PyPortfolioOpt@e12417a` | (a) general Python | none | Flag file extension taken by `split('.')[1]` |
| [#459](https://github.com/BrokkAi/bifrost-packs/issues/459) | pandas | `pandas-dev/pandas@54f0938` | (a) general Python; gap | bifrost.correctness.resource-lifecycle (list escape stays inconclusive) | Model file handles accumulated in a list that leak when a later step raises |

## Considered and not filed

- No fix commit for a backtest lookahead (`shift(-1)` used as a feature) or for train/test data leakage turned up in these repositories' Python history, so neither has an issue here. They need evidence from another source.
- mpmath CVE-2021-29063 (ReDoS in `mpmathify`, fix c811b37c): this is in scope for the existing `polynomial-redos` rule. It needs an analyzer check of the pre-image, not a new lead.
- numpy CVE-2014-1858/1859 and scipy CVE-2013-4251 (predictable temporary files): the existing `insecure-temporary-file` rule already selects `mktemp`.
- Most numpy and pandas fixes are in C, or concern internal numerical-algorithm or dtype-dispatch details that no caller-side static rule could express.

## Outcomes on Bifrost 0.15.4 (2026-11-25)

Qualified with the released Bifrost 0.15.4 CLI (build `ea8da845e8d7`, the `policy-authoring.json` pin). Seven
rules ship in `bifrost.code-smells` 4.1.0; each fixture README records its run, near misses, real-code evidence
and known edges.

| Issue | Outcome | Rule or blocker |
| --- | --- | --- |
| #446 | Not built | Needs numpy, pandas and joblib loader declarations and sink summaries, plus an untrusted-path source; new third-party packs need a native recipe change. Widening the name-matched `unsafe-deserialization` rule to `joblib.load` and `pd.read_pickle` without provenance would be noisy in ML code. The numpy < 1.16.3 arm also needs Python dependency evidence. |
| #447 | Not built | Version-gated on scikit-learn < 1.5.0, and Python static dependency evidence is unavailable on 0.15.4. Also needs typestate for fitted estimators through `Pipeline`. |
| #448 | Not built | Needs ndarray, sparse and pandas receiver typing and numpy alias summaries (`np.asarray` may alias). An augmented assignment on a parameter cannot be told apart from a harmless scalar rebinding (`x += 1`). |
| #449 | Built | `bifrost.correctness.python-or-default-argument-mutation` |
| #450 | Built | `bifrost.correctness.python-shared-class-attribute-mutation` |
| #451 | Built (arms 1 and 2) | `bifrost.correctness.python-pandas-chained-inplace`, `bifrost.correctness.python-pandas-inplace-result-used`. Arm 3 (`inplace=True` on a caller's frame) needs pandas receiver typing. |
| #452 | Not built | The pandas < 3.0 default is the whole hazard, and Python static dependency evidence is unavailable on 0.15.4. Unversioned, it would fire on every `pct_change()` in pandas 3 code. |
| #453 | Not built | Needs numpy and pandas dtype inference for constructors and stored values. |
| #454 | Not built | Needs datetime dtype inference for the `astype` receiver, and NumPy < 2 version evidence. |
| #455 | Built (opt-in) | `bifrost.correctness.python-assert-argument-validation` |
| #456 | Not built | The container-relation arm needs element provenance, and RQL capture correlation does not backtrack under `has`. |
| #457 | Built (arm 1) | `bifrost.correctness.python-numpy-global-rng-with-local-generator`. Arm 2 (`np.random.seed` in library code) is not built: `set_seed` helpers do it on purpose. |
| #458 | Built | `bifrost.correctness.python-split-file-extension` |
| #459 | Not built | Needs file and compression acquisition families for `resource-lifecycle` and container ownership tracking (#439). |

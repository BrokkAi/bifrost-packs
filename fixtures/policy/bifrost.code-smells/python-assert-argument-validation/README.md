# `python-assert-argument-validation` fixture

Exercises `bifrost.correctness.python-assert-argument-validation` (BrokkAi/bifrost-packs#455).

Validated with the Bifrost 0.15.4 `aarch64-apple-darwin` release (archive SHA-256 verified, build `ea8da845e8d7`, the same build identity as the Linux CLI pinned in `policy-authoring.json`) on 2026-11-25. No semantic models are needed. The run is `complete`, with no diagnostics and these definite findings:

- `positive.py:1`: parameters `k`, `n` and `p` of `bayesfactor_binom` (`assert 0 < p < 1, ...` and
  `assert k <= n, ...`).
- `positive.py:7`: parameters `x`, `y` and `method` of `correlation` (`assert method in [...]` and
  `assert len(x) == len(y)`).
- `positive.py:14`: parameter `alpha` of `__init__`.

The near misses produce no findings:

- `near_miss.py`: an explicit `raise ValueError`; an assert in a `_private` helper, in a nested `_recurse`
  helper and in an `assert_graphs_equal` helper; asserts about a local, about `self` attributes, `is not None`
  and `isinstance` narrowing; a parameter rebound before the assert, and a parameter used only in the assert message.
- `tests/test_api.py`: test modules are excluded.

## Real code

On the pre-fix parent of raphaelvallat/pingouin@1ffb923 (`be7a55b5`) the rule reports 60 parameters, including
`bayesfactor_binom` in `src/pingouin/bayesian.py:137`, which the fix converted. At backtesting.py head it reports 9
(for example `Backtest.__init__` `cash` and `margin`, and `close(portion)`), and at networkx head 6
(`uniform_int_from_avg` and `change_color`); each is a public-API argument check by assert. pingouin, PyPortfolioOpt and
bifrost-service heads report none. The policy is opt-in because projects that use asserts for development checks
on purpose would see many findings.

## Known edges

- The finding is on the parameter, not the assert: `binding-uses`, which would map back to the assert, marks any
  scope that references a builtin as incomplete on Bifrost 0.15.4. One finding per parameter, however many asserts
  read it.
- Public means a name without a leading underscore, plus `__init__`, `__call__` and `__new__`; `__all__` is not
  consulted.
- Comparisons anywhere in the assert, including inside `and`/`or`, are selected; a bare `assert flag` or
  `assert callable(f)` is not.

## Reproduce

```bash
cd fixtures/policy/bifrost.code-smells/python-assert-argument-validation
bifrost --root . --policy-file .bifrost/policies/python-assert-argument-validation.rqlp --format json --fail-on never --output report.json
```

The fixture copy of the policy must match `rules/bifrost.code-smells/policies/python-assert-argument-validation.rqlp`.

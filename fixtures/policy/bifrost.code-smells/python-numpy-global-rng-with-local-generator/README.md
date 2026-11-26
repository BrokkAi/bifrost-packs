# `python-numpy-global-rng-with-local-generator` fixture

Exercises `bifrost.correctness.python-numpy-global-rng-with-local-generator` (BrokkAi/bifrost-packs#457, arm 1).

Validated with the Bifrost 0.15.4 `aarch64-apple-darwin` release (archive SHA-256 verified, build `ea8da845e8d7`, the same build identity as the Linux CLI pinned in `policy-authoring.json`) on 2026-11-25. No semantic models are needed. The run is `complete`, with no diagnostics and these definite findings:

- `positive.py:7`: `np.random.rand` next to `rng = np.random.RandomState(seed=3)`.
- `positive.py:12`: `np.random.choice` in a function with a `random_state` parameter.
- `positive.py:18`: `np.random.shuffle` next to `np.random.default_rng(rng)`.
- `positive.py:24`: `np.random.permutation` in a method with a `random_state` parameter.
- `plot_example.py:6`: module-level `np.random.rand` in a script that creates a `RandomState` (the
  scikit-learn `plot_mds.py` pre-image shape).

The near misses produce no findings:

- `near_miss.py`: all draws from the local generator; global draws in a function with no generator or seed
  parameter; a function that calls `np.random.seed` itself; stdlib `random.shuffle`; a method of a class whose
  `__init__` takes `random_state`.
- `other_np.py`: `np` bound to another module.
- `seeded_script.py`: a script that seeds the global stream with `np.random.seed`.
- `unrelated_module.py`: a module-level draw in a module whose only generator is created inside a function.
- `tests/test_sample.py`: test modules are excluded.

## Real code

On the pre-fix parent of scikit-learn/scikit-learn@5f91dca (`692289e4`), scoped to `examples/`, the rule reports
`examples/manifold/plot_mds.py:35` (the line the fix changed) and two examples with the same shape:
`covariance/plot_robust_vs_empirical_covariance.py:95` and `neighbors/plot_regression.py:31`. At current heads of pingouin, PyPortfolioOpt, backtesting.py, networkx and bifrost-service the rule is `complete` with no findings.

## Known edges

- The `np.random` receiver must be spelled `np` or `numpy`, in a module with `import numpy` (any alias).
  `from numpy import random`, `import numpy.random as npr` and `from numpy.random import rand` are not selected.
- A generator or seed parameter in an enclosing function also covers a nested function.
- Module-level draws are reported only when the module creates a generator at module level and no function in it
  creates one, so a script that also defines a generator factory is not reported.
- Arm 2 of the lead (`np.random.seed` inside library functions) is not built: `set_seed` helpers seed the global
  stream on purpose, so the arm would be noisy.

## Reproduce

```bash
cd fixtures/policy/bifrost.code-smells/python-numpy-global-rng-with-local-generator
bifrost --root . --policy-file .bifrost/policies/python-numpy-global-rng-with-local-generator.rqlp --format json --fail-on never --output report.json
```

The fixture copy of the policy must match `rules/bifrost.code-smells/policies/python-numpy-global-rng-with-local-generator.rqlp`.

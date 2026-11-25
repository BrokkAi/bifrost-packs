# `python-or-default-argument-mutation` fixture

Exercises `bifrost.correctness.python-or-default-argument-mutation` (BrokkAi/bifrost-packs#449).

Validated with the Bifrost 0.15.4 `aarch64-apple-darwin` release (archive SHA-256 verified, build `ea8da845e8d7`, the same build identity as the Linux CLI pinned in `policy-authoring.json`) on 2026-11-25. No semantic models are needed. The run is `complete`, with no diagnostics and these definite findings:

- `positive.py:2`: `options = options or {}`, then `options.pop(...)` and `options.setdefault(...)` (scipy `milp`
  shape).
- `positive.py:9`: `minimizer_kwargs = minimizer_kwargs or {}`, then a subscript store (scipy `shgo` shape).
- `positive.py:15`: `headers = headers or dict()`, then `headers.update(...)`.
- `positive.py:21`: `solver_options = solver_options if solver_options is not None else {}`, then a store.

The near misses produce no findings:

- `near_miss.py`: `dict(options or {})`, `{**(defaults or {}), **(options or {})}`, read-only use, `visited =
  visited or set()` and `memo = memo or {}` accumulators, a rebinding to `options.copy()` before the mutation,
  a store into another dict whose value reads `options`, `settings["x"] = options["x"]`, an `or` inside a
  comparison chain, `options.copy() if options is not None else {}`, and `kwargs = kwargs or {}` on a `**kwargs`
  parameter.

## Real code

At current heads of pingouin, PyPortfolioOpt, backtesting.py, networkx and bifrost-service the rule is `complete` with no findings.

## Known edges

- The variable name must look like a configuration mapping: `options`, `opts`, `kwargs`, `kws`, `config`, `cfg`,
  `conf`, `params`, `parameters`, `settings`, `attrs`, `attributes`, `headers`, `metadata`, `meta`, `extra`,
  `extras`, `defaults`, `context`, `ctx`, `props` or `properties`, with optional prefixes, or a prefixed `*_kwargs` /
  `*_kws`. Bare `kwargs` and `kws` are left out because a `**kwargs` dict is always fresh. Other names are not
  reported.
- A subscript store whose value mentions any configuration-like name is skipped, since the occurrence may be the
  read on the right-hand side; `options["a"] = other_options` is therefore not reported.
- Mutations are `pop`, `popitem`, `update`, `setdefault`, `clear` and subscript stores. `del x[k]` has no
  normalized kind on Bifrost 0.15.4 and is not selected; neither is `if x is None: x = {}`.
- The finding is on the normalising assignment's binder. Each mutation is joined to it through its exact lexical
  binding (`binding-of`, then `binding-occurrence`), which on Bifrost 0.15.4 is flow-sensitive.
- `binding-uses`, which would put the finding on the mutation, marks any scope that references a builtin as
  incomplete on Bifrost 0.15.4, so it is not used.
- RQL repeated capture labels under `has` bind the first matching descendant and do not backtrack, so the
  `x = x or {}` shape is matched within one assignment only.

## Reproduce

```bash
cd fixtures/policy/bifrost.code-smells/python-or-default-argument-mutation
bifrost --root . --policy-file .bifrost/policies/python-or-default-argument-mutation.rqlp --format json --fail-on never --output report.json
```

The fixture copy of the policy must match `rules/bifrost.code-smells/policies/python-or-default-argument-mutation.rqlp`.

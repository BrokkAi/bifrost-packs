# `python-shared-class-attribute-mutation` fixture

Exercises `bifrost.correctness.python-shared-class-attribute-mutation` (BrokkAi/bifrost-packs#450).

Validated with the Bifrost 0.15.4 `aarch64-apple-darwin` release (archive SHA-256 verified, build `ea8da845e8d7`, the same build identity as the Linux CLI pinned in `policy-authoring.json`) on 2026-11-25. No semantic models are needed. The run is `complete`, with no diagnostics and these definite findings:

- `positive.py:2` and `:3`: `NameValidator.defaultexcludelist` (list) and `defaultdeletechars` (set), extended
  and updated through `self` (the numpy pre-image shape).
- `positive.py:13`: `Router.routes = {}` with `self.routes.setdefault(...)`.

The near misses produce no findings:

- `near_miss.py`: an attribute copied onto the instance first (`self.excludes = list(self.excludes)`); tuple and
  frozenset attributes; mutation through `cls` in a classmethod; an attribute created in `__init__`; an annotated
  class attribute (`tags: list = []`); and an `_instances` registry.

## Real code

At current heads of pingouin, PyPortfolioOpt, backtesting.py, networkx and bifrost-service the rule is `complete` with no findings.

## Known edges

- The finding is the class attribute declaration. The mutation's `self.<name>` member is resolved with
  `occurrence-target`; a member the analyzer does not bind to the class body is not reported.
- Any assignment through `self` to the attribute, anywhere in the class, removes it, including `self.x += [...]`,
  which also mutates the shared list.
- Subscript stores (`self.x[k] = v`) and aliases (`d = self.x; d.add(...)`) are not selected.
- Names that contain `cache`, `registry`, `instances`, `handlers`, `hooks`, `plugins`, `subscribers`, `listeners`,
  `callbacks`, `observers` or `memo` are treated as deliberate shared state.

## Reproduce

```bash
cd fixtures/policy/bifrost.code-smells/python-shared-class-attribute-mutation
bifrost --root . --policy-file .bifrost/policies/python-shared-class-attribute-mutation.rqlp --format json --fail-on never --output report.json
```

The fixture copy of the policy must match `rules/bifrost.code-smells/policies/python-shared-class-attribute-mutation.rqlp`.

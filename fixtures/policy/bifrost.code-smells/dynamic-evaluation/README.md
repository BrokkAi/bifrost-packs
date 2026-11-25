# `dynamic-evaluation` fixture

Exercises `bifrost.correctness.dynamic-evaluation` after BrokkAi/bifrost-packs#376.
Before that change the rule matched any callee named `eval`, `exec` or
`Function`, so member calls such as `model.eval()` were reported as definite.

Validated with the Bifrost 0.15.1 `aarch64-apple-darwin` release (SHA-256
verified), on 2026-11-10. No semantic models are needed. The run is
`complete`, with no diagnostics and nine definite findings:

- `positive.py:8`, `:12`, `:16`: `eval(...)` and `exec(...)`, both proven
  `builtins.eval`/`builtins.exec`, and `builtins.eval(...)`.
- `positive.js` and `positive.ts`, lines 2, 6 and 10: `eval(...)`,
  `Function(...)` and `new Function(...)`.

The near misses produce no findings. On the same fixture the previous rule
reported 20 of them:

- `near_miss.py`: `model.eval()`, `df.eval(...)`, `session.exec(...)`,
  `PIL.ImageMath.eval(...)`, and builtin `eval` passed as an argument to a
  member call.
- `near_miss.js` and `near_miss.ts`: member calls with plain, nested, call,
  subscript and `Function` receivers. Also `obj.eval(Function, data)` and a
  locally bound `Function`. The JavaScript file also has a locally bound
  `eval`, which TypeScript rejects in strict mode.

`PIL.ImageMath.eval` does call `builtins.eval` internally. The rule doesn't
report it, because it can't tell such a call apart from an unrelated method
named `eval`.

## Python shadowed control

`../dynamic-evaluation-python-shadowed` holds a module function named `eval`
and a call to it. Builtin identity reports that call as `shadowed`, so the run
is typed `inconclusive` (`partial_discovery`) with no finding. An unresolved
or shadowed name is not evidence of a clean program.

## Known edges

- The Python `builtins.eval(...)` arm matches a receiver *named* `builtins`.
  It doesn't prove that the name binds the `builtins` module.
- `occurrences-in` also returns argument identifiers. An unqualified call that
  passes `eval` or `Function` as an argument, such as `eval(Function)`, adds a
  second finding at that argument.
- A JavaScript or TypeScript callee with no lexical binding counts as the
  global. A global reassigned at run time, such as `globalThis.eval = f`, is
  still reported.

## Reproduce

```bash
cd fixtures/policy/bifrost.code-smells/dynamic-evaluation
bifrost --root . --policy-file .bifrost/policies/dynamic-evaluation.rqlp --format json --fail-on never --output report.json
```

The fixture copy of the policy must match
`rules/bifrost.code-smells/policies/dynamic-evaluation.rqlp`.

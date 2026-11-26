# `empty-failure-handler` fixture

Exercises `bifrost.correctness.empty-failure-handler` after the intent
exclusions from
[`research/default-rule-precision-2026-11`](../../../../research/default-rule-precision-2026-11/README.md).
Catch clauses that state an intent to ignore the failure are no longer
reported:

- a comment inside the clause;
- a caught-exception binding spelled `_`, `ignore`, `ignored`, `expected` or
  `tolerated`;
- a Python clause that names `ImportError` or `ModuleNotFoundError`, unless
  it also names `Exception` or `BaseException`.

A `TODO`, `FIXME` or `XXX` comment in the clause marks the handling as
unfinished and keeps it reported, whatever the binding or caught type says.

The exclusions are pattern negations on each `catch` seed, such as
`(catch (not (has (identifier …))))`. They are not written as an `except` set
difference. A set difference is withheld as a whole when parser recovery
leaves any selected catch without a structural fact. An earlier draft written
that way passed this fixture but reported nothing on guava, which has one
recovered region.

Validated with the Bifrost 0.15.4 `aarch64-apple-darwin` release (SHA-256
verified against the GitHub release digest) on 2026-11-26. No semantic models
are needed. The run is `complete`, with no diagnostics and 17 definite
findings, all in the positive files:

- `positive.py:4`, `:11`, `:19`, `:26`, `:34`, `:43`, `:49`, `:56`: a bare
  `except`, `ValueError`, `KeyboardInterrupt`, an `OSError` clause whose only
  comment is a `TODO`, a `StopIteration` clause holding `...`, `except
  Exception` after a non-empty `ImportError` clause, an `ImportError`
  clause with a `TODO` comment, and `except (ImportError, Exception)`.
- `positive.js:4`, `:10`, `:16`, `:24`: `catch (e) {}`, `catch {}`, a `TODO`
  comment, and a comment that sits after the closing brace.
- `positive.ts:4`, `:10`: `catch (e) {}` and `catch {}`.
- `Positive.java:5`, `:12`, `:20`: an empty clause, a clause whose only
  comment is a `FIXME`, and a clause whose binding is named `ignored` but
  whose comment is a `TODO`.

The near-miss files produce no findings. On the same fixture the previous
policy reported all 15 of them, plus the same 17 positives:

- `near_miss.py`: `ImportError`, `ModuleNotFoundError` and
  `(ImportError, AttributeError)` fallbacks, a comment inside the clause, a
  trailing comment on the `except` line, and `except OSError as ignored`.
- `near_miss.js`: a line comment, a block comment, `catch (ignored)` and
  `catch (_)`.
- `near_miss.ts`: a comment and `catch (expected)`.
- `NearMiss.java`: a comment, and bindings named `ignored`, `tolerated` and
  `expected`.

## Known edges

- The comment must be inside the clause. A comment after the closing brace
  (`} catch {} // do nothing`) or above the `except` line is still reported,
  because it belongs to the enclosing statement.
- Any comment counts except `TODO`, `FIXME` and `XXX`, including lint
  directives such as `# noqa: PERF203`.
- The binding-name and `ImportError` checks match identifiers anywhere in the
  clause, because `catch` exposes no binding or caught-type role. The body is
  empty by then, so in practice that means the caught type and the binding.
  It also covers a C# exception filter variable (`catch (Exception ex) when
  (expected) {}`) and a perverse alias (`except Exception as ImportError:`).
  Neither appeared in the sample, and both are accepted as rare false
  negatives.
- Rust `Result::Err` and Go error/recover branches are seeded from callables,
  not clauses, so these exclusions don't apply to them. A Go branch whose only
  content is a comment is still reported.
- `KeyboardInterrupt` and `StopIteration` stay reported. Neither appeared as a
  deliberate empty handler in the labelled sample often enough to justify an
  exclusion.

## Reproduce

```bash
cd fixtures/policy/bifrost.code-smells/empty-failure-handler
bifrost --root . --no-builtin-policies --policy-file .bifrost/policies/empty-failure-handler.rqlp --format json --fail-on never
```

The fixture copy of the policy must match
`rules/bifrost.code-smells/policies/empty-failure-handler.rqlp`.

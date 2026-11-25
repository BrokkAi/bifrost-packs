# Python performance loops over stdlib json, re and pickle

Policies: `bifrost.performance.parsing-in-loop`,
`bifrost.performance.serialization-in-loop` and
`bifrost.performance.regex-compile-in-loop` (#168).

Expected findings:
- parsing: `positive.py:9` (`json.loads`), `:10` (`json.loads` with a keyword), `:14` (`pickle.loads` with a keyword).
- serialization: `positive.py:11` (`json.dumps` with two keywords), `:15` (`pickle.dumps` with a protocol).
- regex compile: `positive.py:12` (`re.compile`), `:13` (`re.compile` with flags).

Near misses (`near_miss.py`):
- A local `loads` helper called in a for loop and a comprehension. It resolves to the workspace function, which declares no parsing effect.
- `json.loads` and `re.compile` called once, before the loop.
- `re.compile` over a three-element string literal; the policies exclude small literal iterables.

Semantic model: `bifrost.python-performance-summaries.json` 1.2.0, the model this directory's `.bifrost/semantic-models` copies.

Validation, on the released Bifrost 0.15.4 (build `ea8da845e8d702206a9acc0c6f28d8bd18fa71c0`) with the native `packs/v0.16.0` bundle:
- With the 1.2.0 model: all three runs **Complete** with exactly the findings above, for `requires-python >=3.11` and for `>=3.13.5, <3.13.6`, where the security-sink summaries also activate.
- With only the bundle's 1.1.0 model (the `.bifrost` directory removed): all three runs **Inconclusive** (`capability_incomplete`) with no findings.
- pallets/flask `41cb747c` and psf/requests `dae7ef63` give the same completions with either model. flask's `parsing-in-loop` stays inconclusive: `config.py:162` calls a `loads` parameter whose default is `json.loads`, and `tests/test_json.py:102, 130` call `flask.json.loads` through the package attribute, which Bifrost leaves dispatch-unproven.

Taint pass-through (`taint/`): these summaries are also read by taint rules, so each one that returns data from its input declares that transfer. `json`, `pickle` and `re.compile` move every parameter to the return value. `sorted` moves its iterable, `subprocess.run` its `args`, and buffered `read` and `Cursor.execute` their receiver. With `requires-python = ">=3.13.5, <3.13.6"`, `bifrost.security.python.process-input-to-urlopen` reports `taint/main.py:8` (`json.loads`), `:12` (`json.loads` with a keyword) and `:16` (`pickle.loads`), `proven_by_summary`. Without transfers the same run was `proven_by_summary` with no findings, a false clean, and it already was for `pickle.loads` under 1.1.0. With the bundle's 1.1.0 model it is inconclusive for the two `json.loads` calls.

Run from this fixture directory:

```console
bifrost --root . --policy-id bifrost.performance.parsing-in-loop --policy-id bifrost.performance.serialization-in-loop --policy-id bifrost.performance.regex-compile-in-loop --format json
```

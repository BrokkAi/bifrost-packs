# Flask request value checked only by assert

These fixtures are for `bifrost.security.python.flask-request-in-assert`
(CWE-617), lead BrokkAi/bifrost-packs#433 (aiohttp CVE-2025-69227). Python
drops `assert` statements under `-O` and `PYTHONOPTIMIZE`, so a request check
written as an assert is gone in optimized deployments.

Sources are the exact Werkzeug `Request` accessor reads of
`flask-request-to-urlopen` (`request.args`, `form`, `cookies`, `headers`).
The sink is a value read inside an `assert` statement: an identifier, or the
result of a call. The rule needs only the Flask and Werkzeug request packs, so
it runs by default like the Flask `urlopen` rule.

Each case directory is its own workspace with the policy, the Flask and
Werkzeug request packs, and a `pyproject.toml` and `requirements.txt` that pin
`flask==3.1.0` and `werkzeug==3.1.0`.

## Validation

Released Bifrost 0.15.4 (`bifrost-v0.15.4-aarch64-apple-darwin`, build identity
`ea8da845e8d702206a9acc0c6f28d8bd18fa71c0`), evaluation date `2026-11-25`,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`BIFROST_OPEN_SEMANTIC_PACK_BUNDLE` set to the extracted `bifrost-semantic-packs`
directory of `packs/v0.16.0`, and a fresh home and `BIFROST_CACHE_DIR` for each
run. Each case was run twice with the same result. Both runs are
`inconclusive` (`partial_discovery`) because the view functions' procedure
semantics stay unknown; the findings are still reported.

| Case | Result |
| --- | --- |
| `positive` | 6 definite, complete findings on 4 asserts. Line 12: a query value tested against an allowlist. Line 19: two findings, one per read of the header local (`size is not None` and `size.isdigit()`). Line 25: two findings, the `request.cookies` read and the `.get(...)` result inside the assert. Line 32: a `getlist` result through `len(...)` |
| `near-miss` | 0 findings: the allowlist check written as `if ...: abort(400)` (line 12), an assert on a local constant beside an unused request read (line 21), and an internal `isinstance` assert on a parameter (line 27) |

## Known limits

- One finding is reported per tainted read inside the assert, so an assert that
  reads the same request value twice is reported twice.
- The rule does not look for another check of the same value. An assert that
  repeats an earlier `if ...: raise` is still reported.
- Asserts in test code are reported like any other when a Flask request value
  reaches them.
- The lead's original source, data read from `asyncio.StreamReader` or a socket,
  has no exact source model in the open packs; only Flask request values are
  sources here.

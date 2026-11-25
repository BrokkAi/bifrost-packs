# Flask request value parsed by parse_qs without max_num_fields

These fixtures are for the opt-in policy
`bifrost.security.python.flask-request-to-parse-qs` (CWE-770), lead
BrokkAi/bifrost-packs#436 (aiohttp CVE-2026-128126; CPython bpo-34155).
`urllib.parse.parse_qs` and `parse_qsl` build one entry per field. Their
`max_num_fields` argument caps that work; without it, one request with very
many fields can stall a worker.

Sources are the exact Werkzeug `Request` accessor reads of
`flask-request-to-urlopen` (`request.args`, `form`, `cookies`,
`headers`). The sink is formal 0 of `member.python.urllib.parse.parse_qs` or
`parse_qsl`, from the source-only packs in
`semantic-packs/python/untrusted-parsing/`. A call that passes a non-None
`max_num_fields` keyword, or six or more positional arguments, is excluded.

Each case directory is its own workspace with the policy, the Flask and
Werkzeug request packs, both untrusted-parsing packs, and a `pyproject.toml`
and `requirements.txt` that pin `flask==3.1.0` and `werkzeug==3.1.0`.

## Validation

Released Bifrost 0.15.4 (`bifrost-v0.15.4-aarch64-apple-darwin`, archive SHA-256
`515dd6e05ece2073f39b52cef2554e22707103453af36e701033b4f60a3f6d26`, build identity
`ea8da845e8d702206a9acc0c6f28d8bd18fa71c0`), evaluation date `2026-11-25`,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`BIFROST_OPEN_SEMANTIC_PACK_BUNDLE` set to the extracted `bifrost-semantic-packs`
directory of `packs/v0.16.0` (native archive SHA-256
`12ea4b37bfa3530b7473bd27aeabcbd401188bc1a369191fae44c3ba56bd6958`), and a fresh
home and `BIFROST_CACHE_DIR` for each run. Each case was run twice with the same
result.

Both runs are `inconclusive` (`partial_discovery`), because the enclosing
view functions' procedure semantics stay unknown, as in the Flask `urlopen`
fixtures. The findings are still reported.

| Case | Result |
| --- | --- |
| `positive` | 4 definite, complete findings: line 12 (`parse_qs(request.args.get(...))`), line 18 (`urllib.parse.parse_qsl` on a cookie with `keep_blank_values=True`), line 25 (a header through a local, with an explicit `max_num_fields=None`), line 30 (`parse_qsl` on a form value with four positional arguments) |
| `near-miss` | 0 findings: `max_num_fields=20` (line 13), `max_num_fields` as the sixth positional argument (line 19), a constant query string beside an unused request read (line 25), and a local class method named `parse_qs` (line 39) |

## Known limits

- An aliased import (`from urllib.parse import parse_qs as pq`) is not
  examined, because the selector also checks the callee spelling.
- The value of an explicit cap is not checked: `max_num_fields=10**9` counts
  as a cap.
- A raw body (`request.get_data()`, `request.stream`) is not a source: the
  Werkzeug pack does not declare those members.
- Django request values are not sources: view-function `request` parameters do
  not bind to `HttpRequest` yet (bifrost-dev#14566).
- aiohttp's own `await request.post()` (the affected-version caller variant of
  the lead) needs an aiohttp server model and the `pkg:pypi/aiohttp` version
  gate; it is not modeled.

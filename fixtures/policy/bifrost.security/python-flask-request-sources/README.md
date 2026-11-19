# Flask request value to os.system and urlopen

These fixtures are for the opt-in policies
`bifrost.security.python.flask-request-to-os-system` (CWE-78) and
`bifrost.security.python.flask-request-to-urlopen` (CWE-918) (bifrost-dev#14549).
Each source is an exact read of a Werkzeug `Request` accessor:
`request.args`, `form`, `cookies` or `headers`. The reviewed `get` and
`getlist` summaries carry the taint to their results. The sinks are the
reviewed `os.system` and `urllib.request.urlopen` members.

Each case directory is its own workspace. It contains the two policies, the
Flask and Werkzeug packs from `semantic-packs/python/web-request/`, the
reviewed `os.system` and stdlib packs, and a `pyproject.toml` and
`requirements.txt` that pin `flask==3.1.0` and `werkzeug==3.1.0`.

## Validation

Bifrost 0.15.3 development build 709884428bfc548ceaf4e2f2ebaed1f0539bdb91,
evaluation date `2026-11-19`, `BIFROST_WORKSPACE_SEMANTIC_MODELS=on`,
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off` and a fresh `BIFROST_CACHE_DIR` for each
run. Each case was run twice.

- **As committed:** every case and policy is `failed` (`endpoint_role_unresolved`)
  with no findings. The request packs report
  `incompatible: no activation evidence names package pkg:pypi/...`, so each
  source reports `qualified-value-locator-zero`. bifrost-dev#14580 closes this gap.
- **Simulated activation:** a scratch copy of each case with the request packs'
  shard activation replaced by `{"targets": [], "configurations": []}` stands in
  for lockfile evidence. The results are below.

| Case | Policy | Simulated result |
| --- | --- | --- |
| `positive` | `flask-request-to-urlopen` | 2 definite findings: line 30 (`request.cookies.get`) and line 37 (`query = request.args`, then `query.get`). The run is `inconclusive` (`partial_discovery`), because the route functions' procedure semantics stay unknown |
| `near-miss` | `flask-request-to-urlopen` | 0 findings, `inconclusive`. Line 36 opens a value from an `ImmutableMultiDict` the application built, and that is not a source |
| `positive`, `near-miss` | `flask-request-to-os-system` | `failed`: the `os.system` sink does not bind on this build, even for `sys.argv` input. The expected positives are lines 12 (`args.get`), 18 (`form.getlist`) and 24 (`headers.get`). The near misses are lines 24 (request value unused) and 30 (workspace `Settings.get`) |

## Known limits

- Subscript reads (`request.args["q"]`) are not sources (bifrost-dev#4651).
- `request.get_json()` is declared but is not a source: the call through the
  `LocalProxy` gives `CallBindingDispatchPartial`.
- `request.values`, `request.data` and the other excluded members are listed
  in `semantic-packs/python/web-request/README.md`.

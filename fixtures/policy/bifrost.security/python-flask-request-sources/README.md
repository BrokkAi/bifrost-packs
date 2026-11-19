# Flask request value to urlopen

These fixtures are for the opt-in policy
`bifrost.security.python.flask-request-to-urlopen` (CWE-918, bifrost-dev#14549).
Each source is an exact read of a Werkzeug `Request` accessor:
`request.args`, `form`, `cookies` or `headers`. The reviewed `get` and
`getlist` summaries carry the taint to their results. The sink is formal 0 of
the reviewed `urllib.request.urlopen` member.

Each case directory is its own workspace. It contains the policy, the Flask and
Werkzeug packs from `semantic-packs/python/web-request/`, the reviewed stdlib
packs, and a `pyproject.toml` and `requirements.txt` that pin `flask==3.1.0`
and `werkzeug==3.1.0`. `requires-python` matches the stdlib sink packs.

## Validation

Bifrost 0.15.3 development build 709884428bfc548ceaf4e2f2ebaed1f0539bdb91,
evaluation date `2026-11-19`, `BIFROST_WORKSPACE_SEMANTIC_MODELS=on`,
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off` and a fresh `BIFROST_CACHE_DIR` for each
run. Each case was run twice.

- **As committed:** both cases are `failed` (`endpoint_role_unresolved`) with no
  findings. The request packs report
  `incompatible: no activation evidence names package pkg:pypi/...`, so each
  source reports `qualified-value-locator-zero`. bifrost-dev#14580 closes this gap.
- **Simulated activation:** a scratch copy of each case with the request packs'
  shard activation replaced by `{"targets": [], "configurations": []}` stands in
  for lockfile evidence. The results are below. Every run is `inconclusive`
  (`partial_discovery`), because the enclosing functions' procedure semantics
  stay unknown. The findings are still reported.

| Case | Simulated result |
| --- | --- |
| `positive` | 5 definite findings: line 10 (`request.args.get`), line 17 (`query = request.args`, then `query.get`), line 23 (`request.form.getlist(...)[0]`), line 28 (`request.cookies.get`), and line 33 (`request.headers.get`) |
| `near-miss` | 0 findings. Line 15 reads a request value that never reaches the URL. Line 21 opens a value from an `ImmutableMultiDict` the application built, which is not a source |

## Known limits

- Subscript reads (`request.args["q"]`) are not traced (bifrost-dev#4651).
- `request.get_json()` is declared but is not a source: the call through the
  `LocalProxy` gives `CallBindingDispatchPartial`.
- `request.values`, `request.data` and the other excluded members are listed
  in `semantic-packs/python/web-request/README.md`.
- No command-injection rule yet: the reviewed `os.system` sink does not bind on
  bifrost-dev 709884428bf, even for `sys.argv` input.

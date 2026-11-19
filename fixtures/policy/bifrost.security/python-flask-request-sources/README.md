# Flask request value to os.system and urlopen

These fixtures are for the opt-in policies
`bifrost.security.python.flask-request-to-os-system` (CWE-78) and
`bifrost.security.python.flask-request-to-urlopen` (CWE-918) (bifrost-dev#14549).
The sources are exact calls on the classes the reviewed Werkzeug model pins:
`request.args`, `form` and `cookies` (`ImmutableMultiDict.get` and `getlist`),
`request.headers` (`EnvironHeaders.get` and `getlist`), and
`request.get_json()`. The sinks are the reviewed `os.system` and
`urllib.request.urlopen` members.

Each case directory is its own workspace. It contains the two policies, the
Flask and Werkzeug packs from `semantic-packs/python/web-request/`, the
reviewed `os.system` and stdlib packs, and a `pyproject.toml` and
`requirements.txt` that pin `flask==3.1.0` and `werkzeug==3.1.0`.

## Expected once bifrost-dev#14580 ships

| Case | Policy | Expected |
| --- | --- | --- |
| `positive` | `flask-request-to-os-system` | 3 findings: line 12 (`args.get`), line 18 (`form.getlist`), line 24 (`headers.get`) |
| `positive` | `flask-request-to-urlopen` | 2 findings: line 30 (`cookies.get`), line 37 (`get_json`) |
| `near-miss` | both | 0 findings. The cases are a request read that never reaches the command (line 21), a workspace `Settings.get` (line 27), and a request value that only selects between constant URLs (lines 34-35) |

The `os.system` sink does not bind on bifrost-dev master 709884428bf even
for `sys.argv` input, so the command-injection rows also need that fixed.
The `urlopen` sink binds on that build (`python-process-input-to-urlopen` is
`proven_by_summary`).

## Current result

Bifrost 0.15.3 development build 709884428bfc548ceaf4e2f2ebaed1f0539bdb91,
evaluation date `2026-11-19`, `BIFROST_WORKSPACE_SEMANTIC_MODELS=on`,
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off` and a fresh `BIFROST_CACHE_DIR` for each
run. Every case and policy is `failed` (`endpoint_role_unresolved`) with no
findings. The Flask and Werkzeug packs report
`incompatible: no activation evidence names package pkg:pypi/...`, so each
source reports `qualified-call-locator-zero`. This is the gap #14580 closes.
It is not a model defect.

## Known limits

- Subscript reads (`request.args["q"]`) are not sources (bifrost-dev#4651).
- `request.values`, `request.data` and the other excluded members are listed
  in `semantic-packs/python/web-request/README.md`.
- Imported summaries never carry `covers_overrides`, so runs that reach these
  calls may stay inconclusive (bifrost-dev#14547).

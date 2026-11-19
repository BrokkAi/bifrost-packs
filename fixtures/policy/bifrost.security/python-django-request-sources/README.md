# Django request value to os.system and urlopen

These fixtures are for the opt-in policies
`bifrost.security.python.django-request-to-os-system` (CWE-78) and
`bifrost.security.python.django-request-to-urlopen` (CWE-918) (bifrost-dev#14549).
Each source is an exact read of `HttpRequest.GET` or `HttpRequest.POST`, which
the reviewed Django model declares as exactly `django.http.QueryDict`. The
reviewed `QueryDict.get` and `getlist` summaries carry the taint to their
results. The sinks are the reviewed `os.system` and `urllib.request.urlopen`
members.

Each case directory is its own workspace. It contains the two policies, the
Django packs from `semantic-packs/python/web-request/`, the reviewed
`os.system` and stdlib packs, and a `pyproject.toml` and `requirements.txt`
that pin `django==5.2.0`.

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
| `positive` | `django-request-to-urlopen` | 1 definite finding: line 22 (`GET.get` on a constructed `HttpRequest()`), in an `inconclusive` (`partial_discovery`) run |
| `near-miss` | `django-request-to-urlopen` | 0 findings, `inconclusive`. Line 24 opens a value from a `QueryDict` the application built, and that is not a source |
| `positive`, `near-miss` | `django-request-to-os-system` | `failed`: the `os.system` sink does not bind on this build. The expected positive is line 16 (`POST.getlist` on a constructed request). Line 10, in the `ping` view, also needs bifrost-dev#14566, because view parameters do not bind to `HttpRequest` yet. The near misses are lines 13 (request value unused) and 18 (plain `dict.get`) |

## Known limits

- `request.COOKIES`, `request.META` and `request.body` are not sources (see
  `semantic-packs/python/web-request/README.md`).
- Subscript reads (`request.GET["q"]`) are not sources (bifrost-dev#4651).

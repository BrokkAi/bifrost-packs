# Django request value to urlopen

These fixtures are for the opt-in policy
`bifrost.security.python.django-request-to-urlopen` (CWE-918, bifrost-dev#14549).
Each source is an exact read of `HttpRequest.GET` or `HttpRequest.POST`, which
the reviewed Django model declares as exactly `django.http.QueryDict`. The
reviewed `QueryDict.get` and `getlist` summaries carry the taint to their
results. The sink is formal 0 of the reviewed `urllib.request.urlopen` member.

Each case directory is its own workspace. It contains the policy, the Django
packs from `semantic-packs/python/web-request/`, the reviewed stdlib packs, and
a `pyproject.toml` and `requirements.txt` that pin `django==5.2.0`.
`requires-python` matches the stdlib sink packs.

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
| `positive` | 2 definite findings and 1 possible finding. Line 14 (`GET.get`) and line 20 (`POST.getlist(...)[0]`) read constructed `HttpRequest()` objects and are definite. Line 8, in the `feed` view, is possible, because view parameters do not bind to `HttpRequest` yet (bifrost-dev#14566) |
| `near-miss` | 0 findings. Line 10 reads a request value that never reaches the URL. Line 16 opens a value from a `QueryDict` the application built, which is not a source |

## Known limits

- `request.COOKIES`, `request.META` and `request.body` are not sources (see
  `semantic-packs/python/web-request/README.md`).
- Subscript reads (`request.GET["q"]`) are not traced (bifrost-dev#4651).
- No command-injection rule yet: the reviewed `os.system` sink does not bind on
  bifrost-dev 709884428bf.

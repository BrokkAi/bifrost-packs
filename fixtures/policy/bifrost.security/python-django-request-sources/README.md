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

Released Bifrost 0.15.4 (`bifrost-v0.15.4-aarch64-apple-darwin`, build identity
`ea8da845e8d702206a9acc0c6f28d8bd18fa71c0`), evaluation date `2026-11-21`,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`BIFROST_OPEN_SEMANTIC_PACK_BUNDLE` set to the extracted `bifrost-semantic-packs`
directory of `packs/v0.15.0` (native archive SHA-256
`7421ad60d21d322aca49a027407f5f256b9151d51f2026aec9c5c1bccee79b3f`), and a fresh
home and `BIFROST_CACHE_DIR` for each run. Each case was run twice with the same
result, as committed and with no simulated activation.

The request packs activate from the pins in `requirements.txt`
(bifrost-dev#14581). The reviewed stdlib `urlopen` sink activates only when the
open packs are available: without them, the run is `failed`
(`endpoint_role_unresolved`) with `no activation evidence names toolchain
cpython`. Every run below is `inconclusive` (`partial_discovery`), because the
enclosing functions' procedure semantics stay unknown. The findings are still
reported.

| Case | Result |
| --- | --- |
| `positive` | 2 definite findings and 1 possible finding. Line 14 (`GET.get`) and line 20 (`POST.getlist(...)[0]`) read constructed `HttpRequest()` objects and are definite. Line 8, in the `feed` view, is possible, because view parameters do not bind to `HttpRequest` yet (bifrost-dev#14566) |
| `near-miss` | 0 findings. Line 10 reads a request value that never reaches the URL. Line 16 opens a value from a `QueryDict` the application built, which is not a source |

## Known limits

- `request.COOKIES`, `request.META` and `request.body` are not sources (see
  `semantic-packs/python/web-request/README.md`).
- Subscript reads (`request.GET["q"]`) are not traced (bifrost-dev#4651).
- No command-injection rule yet: the reviewed `os.system` sink does not bind on
  bifrost-dev 709884428bf.

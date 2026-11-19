# Django request value to os.system and urlopen

These fixtures are for the opt-in policies
`bifrost.security.python.django-request-to-os-system` (CWE-78) and
`bifrost.security.python.django-request-to-urlopen` (CWE-918) (bifrost-dev#14549).
The sources are exact `django.http.QueryDict.get` and `getlist` calls, the class
the reviewed Django model pins for `HttpRequest.GET` and `HttpRequest.POST`.
The sinks are the reviewed `os.system` and `urllib.request.urlopen` members.

Each case directory is its own workspace. It contains the two policies, the
Django packs from `semantic-packs/python/web-request/`, the reviewed
`os.system` and stdlib packs, and a `pyproject.toml` and `requirements.txt`
that pin `django==5.2.0`.

## Expected once bifrost-dev#14580 ships

| Case | Policy | Expected |
| --- | --- | --- |
| `positive` | `django-request-to-os-system` | 1 finding: line 16 (`POST.getlist` on a constructed `HttpRequest()`). Line 10, in the `ping` view, also needs bifrost-dev#14566, because view parameters do not bind to `HttpRequest` yet |
| `positive` | `django-request-to-urlopen` | 1 finding: line 22 (`GET.get` on a constructed `HttpRequest()`) |
| `near-miss` | both | 0 findings. The cases are a request read that never reaches the command (line 13), `get` on a plain dict (line 18), and a request value that only selects between constant URLs (lines 25-26) |

The `os.system` sink does not bind on bifrost-dev master 709884428bf even
for `sys.argv` input, so the command-injection rows also need that fixed.
The `urlopen` sink binds on that build.

## Current result

Bifrost 0.15.3 development build 709884428bfc548ceaf4e2f2ebaed1f0539bdb91,
evaluation date `2026-11-19`, `BIFROST_WORKSPACE_SEMANTIC_MODELS=on`,
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off` and a fresh `BIFROST_CACHE_DIR` for each
run. Every case and policy is `failed` (`endpoint_role_unresolved`) with no
findings. Both Django packs report
`incompatible: no activation evidence names package pkg:pypi/django`, so each
source reports `qualified-call-locator-zero` (bifrost-dev#14580).

## Known limits

- `request.COOKIES`, `request.META` and `request.body` are not sources (see
  `semantic-packs/python/web-request/README.md`).
- Subscript reads (`request.GET["q"]`) are not sources (bifrost-dev#4651).

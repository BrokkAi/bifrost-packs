# Python HTTP client with TLS verification disabled

These fixtures qualify the version-independent part of BrokkAi/bifrost-packs#427
(CWE-295) as four opt-in policies, one for each client library:

- `bifrost.security.python.requests-tls-verification-disabled`: `verify=False`
  on the requests module helpers and `requests.Session` request methods.
- `bifrost.security.python.httpx-tls-verification-disabled`: `verify=False` on
  the httpx top-level functions and the `Client` and `AsyncClient` constructors.
- `bifrost.security.python.aiohttp-tls-verification-disabled`: `ssl=False` or
  `verify_ssl=False` on `aiohttp.request`, the `ClientSession` request methods
  and `ws_connect`, and the `TCPConnector` constructor.
- `bifrost.security.python.urllib3-tls-verification-disabled`:
  `cert_reqs="CERT_NONE"` or `"NONE"`, or `assert_hostname=False`, on
  `PoolManager`, `ProxyManager`, `HTTPSConnectionPool`, `connection_from_url`
  and `proxy_from_url`.

Each entry is a relational assertion over call sites that bind with
`:proof exact` to a member of the reviewed declarations in
`semantic-packs/python/http-client/`. The literal must be the call's own keyword
argument. The rules are split by library because a rule whose locators don't
resolve is not run: one combined rule would lose every finding in a workspace
that doesn't pin all four libraries.

Each case directory is its own workspace. It holds the policy, the library's
declaration pack, and a `pyproject.toml` and `requirements.txt` that pin
`requests==2.34.2`, `httpx==0.28.1`, `aiohttp==3.14.5` or `urllib3==2.8.0`.
The `unpinned` cases pin nothing.

## Validation

Released Bifrost 0.15.4 (`bifrost-v0.15.4-aarch64-apple-darwin.tar.gz`, archive
SHA-256 verified against its `.sha256` asset, build identity
`ea8da845e8d702206a9acc0c6f28d8bd18fa71c0`, the same build that
`policy-authoring.json` pins for Linux), evaluation date 2026-11-25,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`BIFROST_OPEN_SEMANTIC_PACK_BUNDLE` set to the extracted
`bifrost-semantic-packs` directory of `packs/v0.16.0` (native archive SHA-256
verified against its `.sha256` asset), and a fresh home and
`BIFROST_CACHE_DIR` for each run. The bundle supplies none of the HTTP-client
models: each case carries its own copy. Every case was run twice with the same
result.

Run from a case directory:

```console
bifrost --root . --policy-file .bifrost/policies/<library>-tls-verification-disabled.rqlp
```

| Case | Result |
| --- | --- |
| `requests/positive` | complete; 5 definite findings: lines 6 (`requests.post`), 10 (`requests.get`), 14 (`requests.request`), 19 (`requests.Session()` then `s.put`) and 23 (`Session().get` after `from requests import Session`) |
| `requests/near-miss` | complete; 0 findings. `verify=True`, a CA-bundle path, no `verify`, `verify=settings.VERIFY`, other `False` keywords, a session with a CA bundle, and an application class whose `get` takes `verify=False` |
| `requests/incomplete-with-target` | inconclusive (`partial_discovery`); 1 definite finding at line 8. The `with requests.Session() as s` target leaves the receiver lookup open |
| `requests/incomplete-session-factory` | inconclusive (`partial_discovery`); 0 findings. `requests.session()` binds, but its declared result doesn't give `s.request` an exact receiver |
| `requests/unpinned` | `not_run` (`qualified-call-locator-zero`): no `pkg:pypi/requests` evidence, so the pack doesn't activate |
| `httpx/positive` | complete; 6 definite findings: lines 5 (`httpx.get`), 9 (`httpx.post`), 13 (`httpx.stream`), 18 (`httpx.Client(...)`), 23 (`httpx.AsyncClient(...)`) and 29 (`httpx.Client(verify=False, mounts={})`: no mount matches, so the default transport is used) |
| `httpx/near-miss` | complete; 0 findings. No `verify`, `verify=True`, a CA-bundle path, an `ssl.create_default_context()` context, `verify=settings.VERIFY`, `follow_redirects=False`, and a client given its own verifying `transport` |
| `httpx/unpinned` | `not_run` (`qualified-call-locator-zero`) |
| `aiohttp/positive` | complete; 5 definite findings: lines 6 (`session.post(..., verify_ssl=False)`), 11 (`TCPConnector(ssl=False)`), 15 (`aiohttp.request`), 21 (`session.get`) and 26 (`session.ws_connect(..., verify_ssl=False)`) |
| `aiohttp/near-miss` | complete; 0 findings. No `ssl`, an `ssl.create_default_context()` context, `TCPConnector(ssl=True)`, `allow_redirects=False`, and `aiohttp.request(..., ssl=False, connector=...)` with a connector that pins a `Fingerprint` |
| `aiohttp/incomplete-with-target` | inconclusive (`partial_discovery`); 2 definite findings at lines 8 and 14. The `async with aiohttp.ClientSession() as session` target leaves the receiver lookup open |
| `aiohttp/unpinned` | `not_run` (`qualified-call-locator-zero`) |
| `urllib3/positive` | complete; 7 definite findings: lines 6 (`PoolManager(cert_reqs="CERT_NONE")`), 11 (`PoolManager(..., cert_reqs="NONE")`), 15 (`assert_hostname=False`), 19 (`ProxyManager`), 23 (`HTTPSConnectionPool`), 27 (`connection_from_url`) and 32 (`assert_fingerprint=""`, which urllib3 skips) |
| `urllib3/near-miss` | complete; 0 findings. `cert_reqs="CERT_REQUIRED"`, no settings, a pinned `assert_hostname` string, `ca_certs`, `cert_reqs=settings.CERT_REQS`, and `cert_reqs="CERT_NONE"` with `assert_fingerprint` |
| `urllib3/unpinned` | `not_run` (`qualified-call-locator-zero`) |

The `unpinned` runs also report `workspace-model-load-failed` for the
workspace copy of the pack, which exits 2. A pack delivered in a bundle would
simply stay inactive.

## Known limits

- A value that reaches the keyword through a variable, settings object or
  `**options` spread is not reported. A clean run doesn't prove verification
  stays on.
- `session.verify = False`, `cert_reqs=ssl.CERT_NONE` (the constant, not the
  string), an `ssl.SSLContext` with verification turned off, transports and
  adapters are not covered.
- `with` and `async with` targets keep the run inconclusive (above).
- A call that also passes a configuration that can still authenticate the peer
  is not reported: httpx `transport=`, a non-empty urllib3 `assert_fingerprint=`,
  and `aiohttp.request(..., connector=...)`. A `ClientSession` method can't see
  its session's connector, so a session whose connector pins a `Fingerprint`
  is still reported when a request passes `ssl=False`.
- Version ranges are those reviewed in `semantic-packs/python/http-client/README.md`.

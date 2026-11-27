# Python HTTP-client declaration packs

These four packs declare the request surface of requests, httpx, aiohttp and
urllib3 that the TLS-verification rules for BrokkAi/bifrost-packs#427 use:

- `bifrost.security.python.requests-tls-verification-disabled`
- `bifrost.security.python.httpx-tls-verification-disabled`
- `bifrost.security.python.aiohttp-tls-verification-disabled`
- `bifrost.security.python.urllib3-tls-verification-disabled`

| Pack | Version | Activates on | Reviewed at |
| --- | --- | --- | --- |
| `bifrost.python-requests-declarations` | 0.1.0 | `pkg:pypi/requests` `>=2.32.0, <2.35.0` | v2.32.0, v2.32.5, v2.33.0, v2.33.1, v2.34.0, v2.34.2 |
| `bifrost.python-httpx-declarations` | 0.1.0 | `pkg:pypi/httpx` `>=0.28.0, <0.29.0` | 0.28.0, 0.28.1 |
| `bifrost.python-aiohttp-declarations` | 0.1.0 | `pkg:pypi/aiohttp` `>=3.14.0, <3.15.0` | v3.14.0, v3.14.5 |
| `bifrost.python-urllib3-declarations` | 0.1.0 | `pkg:pypi/urllib3` `>=2.0.0, <2.9.0` | 2.0.0, 2.2.0, 2.5.0, 2.7.0, 2.8.0 |

Each signature is copied from the runtime definition (the `else` branch of the
`TYPE_CHECKING` split where a library has one) at the tags above. Every tag in
a range gave the same signatures for the declared members. A range ends where a
signature changed or where nothing later was reviewed:

- requests 2.34.0 added an explicit `params` formal to `Session.get`. The pack
  has one shard for the shared surface (2.32.0 up to 2.35.0) and one
  `Session.get` shard for each signature.
- aiohttp 3.13 patch releases added `max_headers` to `ClientSession` and
  `dns_cache_max_size` to `TCPConnector`, so 3.13 is not claimed.
- httpx 1.0 is still in development and changes the client API.

## Activation

The packs need `pkg:pypi/<name>` activation evidence. Bifrost 0.15.4 derives
it from `uv.lock`, `poetry.lock`, pinned requirements, or a declared Python
environment (bifrost-dev#14581). Without that evidence no member resolves and
each rule reports `not_run`, which is not a clean result.

`native-generation.json` builds the httpx, aiohttp and urllib3 packs, and
`packs/v0.18.0` is the first packs release that delivers them. The requests pack
is not a job. The pinned 0.15.3 producer requires every shard of an authored
model to repeat the spec's activation exactly, and this pack's two `Session.get`
shards activate on narrower ranges than its shared shard. Until the pack is
restructured, a workspace supplies it in `.bifrost/semantic-models`, as the
fixtures in `fixtures/policy/bifrost.security/python-http-client-tls-verification`
do. All four rules stay opt-in.

## Reviewed claims

- `requests.get`, `options`, `head`, `post`, `put`, `patch`, `delete` and
  `request` are defined in `requests/api.py` and re-exported by
  `requests/__init__.py`. They forward `**kwargs`, including `verify`, to
  `Session.request`. `requests.Session` is `requests.sessions.Session`;
  `__enter__` returns the session. `requests.session()` returns a new `Session`.
- `httpx.get` and the other top-level functions in `httpx/_api.py` take
  keyword-only `verify`. `httpx.Client` and `httpx.AsyncClient`
  (`httpx/_client.py`) take keyword-only `verify` in `__init__`; their request
  methods take no `verify` in 0.28.
- `aiohttp.request` and the `ClientSession` request methods forward `**kwargs`
  to `ClientSession._request`, which takes `ssl` and the deprecated
  `verify_ssl`. `ClientSession.ws_connect` and `TCPConnector.__init__` take both
  keywords directly. `ClientSession.__aenter__` returns the session.
- `urllib3.PoolManager`, `ProxyManager`, `connection_from_url` and
  `proxy_from_url` forward `**kw` to the connection pool.
  `HTTPSConnectionPool.__init__` declares `cert_reqs` and `assert_hostname`.
  `resolve_cert_reqs` accepts `"CERT_NONE"` and `"NONE"` for `ssl.CERT_NONE`.

Declared parameter types are `builtins.object`: the rules select on identity
and keywords, not types. Return types are declared only where a rule needs a
receiver (`Session.__enter__`, `requests.session`, `ClientSession.__aenter__`).

## Not declared

- Response objects, adapters, transports (`httpx.HTTPTransport`), cookie jars,
  auth classes and `requests.adapters.HTTPAdapter`.
- Attribute writes such as `session.verify = False`.
- urllib3 1.x, requests before 2.32, httpx before 0.28 and aiohttp before
  3.14.

The packs carry the repository's `Apache-2.0` model license. They describe API
identity, not library code, and set `safety.review_required: false` as
first-party content.

# Flask request value decompressed without an output bound

These fixtures are for the opt-in policy
`bifrost.security.python.flask-request-to-decompress` (CWE-409), lead
BrokkAi/bifrost-packs#435 (urllib3 CVE-2025-66471, aiohttp CVE-2025-69223).
`zlib.decompress`, `gzip.decompress` and `bz2.decompress` inflate their whole
input with no output limit, so a small compressed request value can exhaust
memory.

Sources are the exact Werkzeug `Request` accessor reads of
`flask-request-to-urlopen` (`request.args`, `form`, `cookies`,
`headers`). Complete summaries for `base64.b64decode`,
`standard_b64decode` and `urlsafe_b64decode` carry the taint through base64
decoding. The sinks are formal 0 of the exact typeshed functions
`zlib.decompress`, `gzip.decompress` and `bz2.decompress`, closed by the
summaries in `semantic-packs/python/untrusted-parsing/`.

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
view functions' procedure semantics stay unknown. The findings are still
reported.

| Case | Result |
| --- | --- |
| `positive` | 4 definite, complete findings: line 16 (cookie, `urlsafe_b64decode`, `zlib.decompress`), line 22 (form value, `b64decode`, `gzip.decompress`), line 29 (query value, `standard_b64decode`, `bz2.decompress`), line 35 (a header straight into `zlib.decompress` with `wbits=31`) |
| `near-miss` | 0 findings: a bundled constant decompressed beside an unused request read (line 16), a decoded request value that is never decompressed (line 22), and a local class method named `decompress` (line 37) |

## Known limits

- Streaming decompressors are not covered. On Bifrost 0.15.4 the receiver of
  `zlib.decompressobj().decompress(...)` does not dispatch exactly, even with a
  declared exact return class, so the bounded form
  `decompress(data, max_length)` cannot be told apart from the unbounded one.
- `lzma.decompress` and third-party decompressors (`brotli`, `zstandard`) are
  not modeled. The typeshed pack does not cover `lzma`.
- `str.encode()` on a header value does not dispatch exactly on 0.15.4, so a
  value encoded before decompression is not traced.
- A raw body (`request.get_data()`, `request.files`) is not a source: the
  Werkzeug pack does not declare those members.
- An output-size check after decompression is not a sanitizer: the memory is
  spent by then.

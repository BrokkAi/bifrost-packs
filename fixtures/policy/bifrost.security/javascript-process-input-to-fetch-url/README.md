# JavaScript process argument to fetch URL fixture

Qualifies `bifrost.security.javascript.process-input-to-fetch-url` for the
global `fetch` part of BrokkAi/bifrost-packs#478 (CVE-2025-27152). The source
is a `process.argv` keyed read. The sinks are the input (URL) operands of the
global `fetch(input)` and `fetch(input, init)`. They bind through the reviewed
models copied into `.bifrost/semantic-models`:

- `bifrost.node-runtime-values-javascript` 0.1.0 (`process.argv`).
- `bifrost.web-network-javascript` 1.1.0. Version 1.0.0 declares only
  `fetch(input, init)`, so a one-argument `fetch(url)` did not bind. 1.1.0
  adds the one-argument member `globalThis.fetch(input)` with the same
  complete summary: the input flows to the returned promise, the call is
  immediate network I/O, and `init` flows nowhere.

The axios and undici sinks of the lead need third-party npm models. Whether
those are public or premium is an owner decision (#393), so they are not here.
The policy is opt-in.

## Cases

- **Positives** (`main.js`): the argument as the whole URL (line 7), as the
  host of a URL sent with options (13), and interpolated into a template
  literal (19). Each is a definite, complete finding.
- **Near misses** (`main.js`): the argument sent only as the request body to a
  fixed URL, and the argument only choosing which fixed URL is fetched.
- **Incomplete** (`incomplete/`, its own workspace): `url-object` builds the
  URL with `new URL(path, base)`, which has no model, so the run is
  inconclusive with no finding. `response` awaits the promise and reads the
  body. The finding is reported, and the unmodeled calls leave the run
  inconclusive.
- **Inline** (`inline/`): `fetch(process.argv[2])` binds no source
  (bifrost-dev#9986). The run fails (`endpoint_role_unresolved`). In a
  workspace with other cases the failure also drops their findings, so this
  case runs alone.

## Validation

Bifrost `v0.15.4` (`bifrost-v0.15.4-aarch64-apple-darwin`, archive SHA-256
`515dd6e05ece2073f39b52cef2554e22707103453af36e701033b4f60a3f6d26`, which
matches the release `.sha256`; binary SHA-256
`d9e6168d51eece5aeeff6eb28187d27aafeae164c217816a80fd09a4581f8be3`; build
identity `ea8da845e8d702206a9acc0c6f28d8bd18fa71c0`), evaluation date
`2026-11-25`. Each run used `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`--no-builtin-policies`, `--no-incremental` and a fresh `BIFROST_CACHE_DIR`.

- This directory: `proven_by_summary`, 3 definite, complete findings at
  `main.js` lines 7, 13 and 19.
- The same run with `bifrost.web-network-javascript` 1.0.0: `inconclusive
  (partial_discovery)`, 1 definite finding at line 13. The one-argument calls
  do not bind.
- The same run without the web-network model: `failed
  (endpoint_role_unresolved)`, no finding.
- `incomplete/`: `inconclusive (partial_discovery)`, 1 definite finding at
  `response/response.js` line 5.
- `inline/`: `failed (endpoint_role_unresolved)`, no finding.

## Known limits

- Only `process.argv` is a source.
- `Request` objects, `new URL(...)`, `http.request`, `https.get`, axios and
  undici are not sinks or have no model.
- An `encodeURIComponent` segment under a fixed origin is still reported,
  because no sanitizer is modeled.

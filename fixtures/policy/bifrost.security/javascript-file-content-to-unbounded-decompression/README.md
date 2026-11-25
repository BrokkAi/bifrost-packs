# JavaScript file content to unbounded decompression fixture

Qualifies `bifrost.security.javascript.file-content-to-unbounded-decompression`
for the version-independent part of BrokkAi/bifrost-packs#291
(CVE-2024-22025). The source is the `Buffer` that `fs.readFileSync(path)`
returns. The sinks are the input operands of the one-argument `zlib`
convenience methods `gunzipSync`, `inflateSync`, `inflateRawSync`, `unzipSync`
and `brotliDecompressSync`. Called without options, these methods have no
`maxOutputLength` limit. They bind through the reviewed models copied into
`.bifrost/semantic-models`:

- `bifrost.node-fs-javascript-declarations` 0.2.1 and
  `bifrost.node-fs-javascript-summaries` 0.3.0 (source-only,
  review-required; the `readFileSync(path)` `Buffer` return is from PR #407).
- `bifrost.node-zlib-javascript-declarations` 0.1.0 and
  `bifrost.node-zlib-javascript-summaries` 0.1.0 (new, source-only; see
  `semantic-packs/node/zlib/README.md`).

The policy is opt-in.

## Cases

- **Positives** (`main.js`): `gunzipSync` (line 9), `brotliDecompressSync`
  (15), `inflateSync` with the read inline (20), `inflateRawSync` through a
  local copy (26) and `unzipSync` (30). Each is a definite, complete finding.
- **Near misses** (`main.js`): `gunzipSync(data, { maxOutputLength })` binds
  to the two-argument member, which is not a sink. A file read as UTF-8 text
  and never decompressed gives no finding either.
- **Incomplete** (`incomplete/`, its own workspace): `to-string` calls
  `toString` on the decompressed `Buffer`. The finding is reported, but
  `Buffer#toString` has no summary, so the run is inconclusive.
- **Uncovered** (`uncovered/`): `callback` passes the content to
  `zlib.gunzip(buffer, callback)`, which is not declared and whose result is
  unused. `options` passes options without `maxOutputLength`, a known false
  negative. Neither is a sink, so the run is complete with no finding and says
  that no sink bound.

## Validation

Bifrost `v0.15.4` (`bifrost-v0.15.4-aarch64-apple-darwin`, archive SHA-256
`515dd6e05ece2073f39b52cef2554e22707103453af36e701033b4f60a3f6d26`, which
matches the release `.sha256`; binary SHA-256
`d9e6168d51eece5aeeff6eb28187d27aafeae164c217816a80fd09a4581f8be3`; build
identity `ea8da845e8d702206a9acc0c6f28d8bd18fa71c0`, the identity pinned in
`policy-authoring.json`), evaluation date `2026-11-25`. Each run used
`BIFROST_OPEN_PACKS_DISABLE=1`, `BIFROST_WORKSPACE_SEMANTIC_MODELS=on`,
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off`, `--no-builtin-policies`,
`--no-incremental` and a fresh `BIFROST_CACHE_DIR`.

- This directory: `proven_by_summary`, 5 definite, complete findings at
  `main.js` lines 9, 15, 20, 26 and 30.
- The same run without the zlib summaries pack: `inconclusive
  (partial_discovery)`, the same 5 lines as `possible` findings.
- The same run without either zlib pack: `failed (endpoint_role_unresolved)`,
  no finding. The sink selectors are incomplete, so the run is never clean.
- `incomplete/`: `inconclusive (partial_discovery)`, 1 definite finding at
  `to-string/to-string.js` line 8.
- `uncovered/`: `complete`, no finding, "bound no sink endpoint".

## Known limits

- Every `fs.readFileSync(path)` result is a source, whatever the path. A
  program that decompresses its own bundled asset gets a finding.
- `readFileSync` with options, network and request bodies, and `fetch` are not
  sources. The `fetch` part of CVE-2024-22025 is version-gated and needs Node
  runtime evidence (bifrost-dev#9983).
- Calls with options are never sinks, so options that omit
  `maxOutputLength` are missed.
- The callback and stream forms are not modeled.

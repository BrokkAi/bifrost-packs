# JavaScript/TypeScript data-flow CVE leads on Bifrost 0.15.1

Ten Node.js core advisories from OSV, filed as BrokkAi/bifrost-packs#287 to
#296. Each has a taint or typestate policy in theory. **Two version-independent
slices ship as rules; the other eight are blocked by the engine.**
`outcomes.json` records each lead's outcome, the probe hashes and the fixture
runs.

| Lead | Advisory | Outcome |
| --- | --- | --- |
| #287 | CVE-2025-27210 (`path.join` device names) | Implemented: `bifrost.security.javascript.process-input-to-fs-write-path` |
| #288 | CVE-2021-22931 (DNS host names) | Blocked: bifrost-dev#9983, #2446 |
| #289 | CVE-2022-21824 (`console.table`) | Blocked: bifrost-dev#9983 |
| #290 | CVE-2023-30590 (DiffieHellman keys) | Blocked: bifrost-dev#9983 |
| #291 | CVE-2024-22025 (`fetch` Brotli) | Blocked: bifrost-dev#9983, #2446 |
| #292 | CVE-2026-21713 (HMAC comparison) | Blocked: bifrost-dev#9983, #4385 |
| #293 | CVE-2026-105482 (`dns.resolve` NUL) | Blocked: bifrost-dev#9983 |
| #294 | CVE-2026-21712 (`url.format`) | Implemented: `bifrost.security.javascript.process-input-to-legacy-url-parse` |
| #295 | CVE-2024-36138 (batch files) | Blocked: bifrost-dev#9983 |
| #296 | CVE-2026-58041 (`node:sqlite` iterators) | Blocked: bifrost-dev#9983 |

## Selection

Node.js core advisories are in OSV under the Bitnami ecosystem
(`BIT-node-*`), not under `npm`. They came from
`https://osv-vulnerabilities.storage.googleapis.com/Bitnami/all.zip`, filtered
to the `node` package, then deduplicated against every `CVE-` title in
BrokkAi/bifrost-packs and BrokkAi/bifrost-premium-packs. The selection skipped
bugs in OpenSSL, nghttp2, llhttp, c-ares and ICU, memory corruption, request
smuggling, and the permission and policy models, where application code
doesn't decide reachability. All ten are open placement: the contract belongs
to the Node.js runtime.

## Engine

Official `v0.15.1` release, `bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`
(archive SHA-256
`4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`, which
matches the release `.sha256`; binary SHA-256
`78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`; build
identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`). v0.15.2 was not
released on 2026-11-05. Every run used `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off`, `--no-builtin-policies`,
`--no-incremental` and a fresh `BIFROST_CACHE_DIR`.

## Shared blocker: no Node runtime gate

Every lead has a fixed Node release, so a rule that reports the CVE itself
needs the executing runtime's version. `probe/node-runtime-evidence/` shows the
gap ([bifrost-dev#9983](https://github.com/BrokkAi/bifrost-dev/issues/9983)):

- `engines.node` is one `npm-toolchain` row of kind `constraint`, marked
  `does_not_establish_installed_runtime`. `.nvmrc` produces no row, and
  there are no `locked` or `installed` rows.
- `(dependency-evidence :ecosystem npm-toolchain :version-range …)` is
  rejected: `version_ranges` accepts only cargo, rust-toolchain, npm, nuget,
  go-module and go-toolchain.
- `target-of` returns no rows for a JavaScript file, and nothing states the
  target OS. #287 and #295 are Windows-only.

This is the Node form of bifrost-dev#9867 (Go).

## The two shipped slices

Both rules are opt-in. Their only source is `process.argv`, read through the
reviewed Node runtime-values model. Two gaps keep `process.env` out
([bifrost-dev#9986](https://github.com/BrokkAi/bifrost-dev/issues/9986)). The
JavaScript keyed-read pattern must name the environment key. And a keyed read
passed straight into a call, `f(process.argv[2])`, gives no source and an
inconclusive run. No reviewed Node HTTP request source exists, so request
input is not covered either.

- **#287:** `path.join`, `path.normalize` and `path.resolve` resolve `..` and
  never confine a segment on any release (`doc/api/path.md` at v22.11.0,
  SHA-256 `32e309fcfb432b9186a33970311a37cecb59946db59e57dbd391837ebf1e1aa4`).
  So `process.argv` reaching an `fs` write path is reported on every runtime.
  New models live in `semantic-packs/node/path/`, and
  `bifrost.node-fs-javascript-summaries` 0.2.0 adds `appendFileSync` and
  `openSync`. Summaries can't reference a variadic tail
  ([bifrost-dev#9985](https://github.com/BrokkAi/bifrost-dev/issues/9985)),
  so only `join(base, segment)` and `resolve(base, segment)` bind; other
  arities stay inconclusive.
- **#294:** `doc/api/url.md` at v22.11.0 (SHA-256
  `edb9856bf9176279c9b8d2060959256f101fe5e4344daea95c750ed408b64ce7`) says
  `url.parse()` must not be used with untrusted input and gets no CVEs, and
  that `url.format()` passes a string to `url.parse()`. New models live in
  `semantic-packs/node/url/`.

The fixture READMEs list each case and its run.

## The eight blocked leads

All eight are version-gated, so each is blocked by bifrost-dev#9983 first.
Without a runtime gate, every patched project would be reported. Their other
missing capabilities were only listed, not probed: no reviewed `dns`,
`console`, `crypto`, `fetch`, `zlib`, `child_process.spawn` or `node:sqlite`
model; callback-parameter and promise sources (#288, #291; bifrost-dev#2446);
and a comparison-operator sink (#292; bifrost-dev#4385). The typestate schema
can express the #290 and #296 protocols (see
`bifrost.correctness.resource-lifecycle`), but neither was run.

The files under `probe/` are research inputs, not registered pack content.

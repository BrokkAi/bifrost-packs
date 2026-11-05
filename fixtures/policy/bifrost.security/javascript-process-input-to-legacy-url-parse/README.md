# JavaScript process argument to legacy url.parse fixture

Qualifies the version-independent part of the Node lead
BrokkAi/bifrost-packs#294 (CVE-2026-21712). The Node documentation says the
legacy `url.parse()` must not be used with untrusted input and gets no CVEs,
and that `url.format()` passes a string argument to `url.parse()`. So a
process argument that reaches either is reported on every Node runtime. The
CVE's `url.format` crash on affected 24.x and 25.x runtimes needs runtime
evidence the engine does not have (bifrost-dev#9983).

The source is a `process.argv` keyed read. The sinks are the arguments of
the one-argument `url.parse` and `url.format`. They bind through the
reviewed models copied into `.bifrost/semantic-models` and enabled in
`.bifrost/packs.json`:

- `bifrost.node-runtime-values-javascript` 0.1.0 (`process.argv`).
- `bifrost.node-url-javascript-declarations` 0.1.0 and
  `bifrost.node-url-javascript-summaries` 0.1.0.

`package.json` declares `engines.node` `22.11.0`, which activates them.
The policy is opt-in (`"activation": "opt-in"`).

## Cases

- **Positives** (`main.js`): the argument parsed; the argument formatted;
  the argument parsed and the result formatted again (two findings).
- **Near misses** (`main.js`): a constant URL; the argument used only as a
  label next to a constant URL; the WHATWG `new URL(target)`, the
  documented replacement.
- **Incomplete** (`incomplete/`, its own workspace; `.bifrostignore` keeps it
  out of the parent run):
  - `hostname`: `url.parse(target).hostname` checked against an allowlist.
    The finding at `url.parse` is reported, but the `Url` object has no
    property model, so access-path resolution is unknown.

## Validation

Bifrost 0.15.1 (`bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`, checksum
verified against the release; build identity
`90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`), evaluation date `2026-11-05`. Each
run used `BIFROST_OPEN_PACKS_DISABLE=1`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`--no-builtin-policies`, `--no-incremental` and a fresh `BIFROST_CACHE_DIR`.
The authored policy hash is
`2a8d9eb83aaef84e7f39b1960e908d2f909381dec78c1de868f81dcfeebb5fb2`.

- This directory: `proven_by_summary`, with 4 findings, all definite and
  complete: `main.js:8`, `:14`, `:20` and `:21`. The near misses give no
  finding and no diagnostic.
- `incomplete/`: inconclusive (`partial_discovery`), with one definite,
  complete finding at `hostname/hostname.js:8`.
- Without the two `url` models: inconclusive, with no finding. Both sink
  selectors report `SemanticAnalysisPartial`.

## Known limits

- Only `process.argv` is a source. `process.env` reads and HTTP request
  values have no usable reviewed source (bifrost-dev#9986).
- `url.parse` with extra arguments and `url.format(URL, options)` are not
  modeled, and calls with those arities stay fail-closed.

# JavaScript process argument to fs write path fixture

Qualifies the version-independent part of the Node lead
BrokkAi/bifrost-packs#287 (CVE-2025-27210). `path.join`, `path.normalize`
and `path.resolve` resolve `..` and never confine a segment to its base, so
a process argument that reaches an `fs` write path is reported on every Node
runtime. The CVE's Windows device-name part needs runtime and platform
evidence the engine does not have (bifrost-dev#9983).

The source is a `process.argv` keyed read. The sinks are the path operands of
`fs.writeFileSync`, `fs.appendFileSync` and `fs.openSync`. All of them
bind through the reviewed models copied into `.bifrost/semantic-models` and
enabled in `.bifrost/packs.json`:

- `bifrost.node-runtime-values-javascript` 0.1.0 (`process.argv`).
- `bifrost.node-fs-javascript-declarations` 0.1.0 and
  `bifrost.node-fs-javascript-summaries` 0.2.0.
- `bifrost.node-path-javascript-declarations` 0.1.0 and
  `bifrost.node-path-javascript-summaries` 0.1.0.

`package.json` declares `engines.node` `22.11.0`, which activates them.
The policy is opt-in (`"activation": "opt-in"`).

## Cases

- **Positives** (`main.js`): the argument written as given; joined under an
  upload directory; used as the base of a join for `appendFileSync`;
  normalized for `openSync`; resolved under a base.
- **Near misses** (`main.js`): the argument is the written content, not
  the path; a constant path.
- **Incomplete** (`incomplete/`, its own workspace; `.bifrostignore` keeps it
  out of the parent run):
  - `inline`: `fs.writeFileSync(process.argv[2], …)`. The keyed read is
    passed straight into the call, and source discovery is incomplete with no
    finding (bifrost-dev#9986).
  - `variadic`: a three-segment `path.join`. Only the two-argument form has
    a summary, because summaries can't reference a variadic tail
    (bifrost-dev#9985).
  - `helper`: `path.basename` as a guard. It has no reviewed summary.

## Validation

Bifrost 0.15.1 (`bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`, checksum
verified against the release; build identity
`90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`), evaluation date `2026-11-05`. Each
run used `BIFROST_OPEN_PACKS_DISABLE=1`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`--no-builtin-policies`, `--no-incremental` and a fresh `BIFROST_CACHE_DIR`.
The authored policy hash is
`99ac09db7ec74620c40ba6a49b4db91f12007c4fb9324596192a68ae3198ac6b`.

- This directory: `proven_by_summary`, with 5 findings, all definite and
  complete: `main.js:11`, `:18`, `:25`, `:31` and `:37`. The near misses
  give no finding and no diagnostic.
- `incomplete/`: inconclusive (`partial_discovery`), with no finding. Each
  case was also run alone with `--sources <case>`, and each is inconclusive
  on its own.
- Without the two `path` models: inconclusive, with only `main.js:11`.
- With `bifrost.node-fs-javascript-summaries` 0.1.0, which has no
  `appendFileSync` or `openSync` summary: inconclusive, and `main.js:25` and
  `:31` drop to possible and partial.

## Known limits

- Only `process.argv` is a source. `process.env` reads and HTTP request
  values have no usable reviewed source (bifrost-dev#9986).
- Only the synchronous `fs` write members are sinks. Read members, the
  promise and callback APIs, and streams are not covered.
- A containment check (`path.relative` or `startsWith` on the resolved
  path) is not seen as a guard, so a guarded write is still reported.

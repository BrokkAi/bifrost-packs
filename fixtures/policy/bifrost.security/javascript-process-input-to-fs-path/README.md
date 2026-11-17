# JavaScript process argument to fs read, list, test or remove path fixture

Qualifies `bifrost.security.javascript.process-input-to-fs-path` for the
path-traversal part of BrokkAi/bifrost-packs#393. The source is a
`process.argv` keyed read. The sinks are the path operands of
`fs.readFileSync` (one and two arguments), `fs.readdirSync`,
`fs.existsSync`, `fs.statSync`, `fs.lstatSync`, `fs.accessSync(path, mode)`,
`fs.unlinkSync` and `fs.rmSync` (one and two arguments). All of them bind
through the reviewed models copied into `.bifrost/semantic-models` and
enabled in `.bifrost/packs.json`:

- `bifrost.node-runtime-values-javascript` 0.1.0 (`process.argv`).
- `bifrost.node-fs-javascript-declarations` 0.2.0 and
  `bifrost.node-fs-javascript-summaries` 0.3.0, which add the read, list and
  remove members, declarations for the callback and `fs/promises` forms,
  and the missing summaries (#393).
- `bifrost.node-path-javascript-declarations` 0.1.0 and
  `bifrost.node-path-javascript-summaries` 0.1.0.

`package.json` declares `engines.node` `22.11.0`, which activates the fs and
path models. The fs and path packs are source-only and review-required, so a
project has to supply and enable them as this fixture does. The policy is
opt-in.

## Cases

- **Positives** (`main.js`): read as given (line 11); read under a base with
  `path.join` (17); list a directory resolved with `path.resolve` (23);
  `existsSync` and `statSync` on a normalized path (30, 31); `accessSync`
  (39); `unlinkSync` (45); `rmSync` with options (50) and without (55).
- **Near misses** (`main.js`): `lstatSync` on a constant directory (33); the
  argument only compared, with a constant read path; file content read from a
  constant path.
- **Incomplete** (`incomplete/`, its own workspace):
  - `helper` guards the name with `path.basename`, which has no reviewed
    summary: inconclusive, no finding.
  - `callback` calls `fs.readFile(path, options, callback)`.
  - `promises` calls `fs/promises` `unlink(path)`.
  
  The callback and `fs/promises` members bind as sinks through declarations
  with no summary, because they run callbacks or settle promises that a
  summary can't describe. Each gives a `possible` finding and an inconclusive
  run.

## Validation

Bifrost `v0.15.3` (`bifrost-v0.15.3-aarch64-apple-darwin`, binary SHA-256
`1e8d45ae76f1b2920aa7a113e8e80083346f6acbed839c3e113058ae36c8acbc`, build
identity `cc7ebd1676e002b657e10304cfd977bc289e25ed`), evaluation date
`2026-11-17`. Each run used `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`--no-builtin-policies`, `--no-incremental` and a fresh `BIFROST_CACHE_DIR`.

- This directory: `proven_by_summary`, 9 definite findings at `main.js`
  lines 11, 17, 23, 30, 31, 39, 45, 50 and 55. The near misses give none.
- `incomplete/`, each case alone: `helper` inconclusive with no finding;
  `callback` and `promises` inconclusive with 1 possible finding each (line
  6). Run together, the workspace is inconclusive with only the `callback`
  finding: `helper`'s inline `process.argv` read leaves source discovery
  incomplete (bifrost-dev#9986).
- The shipped `process-input-to-fs-write-path` fixture still gives 5 definite
  findings with the 0.2.0 and 0.3.0 fs packs, and the `file-system-race`
  fixture is unchanged.

## Known limits

- Only `process.argv` is a source (bifrost-dev#9986 for `process.env` and
  request values).
- Only the members above are sinks. The callback and `fs/promises` ones give
  possible findings only. Streams and the other fs members are not covered.
- A containment check on the resolved path is not seen as a guard.

# JavaScript process argument to child_process command fixture

Qualifies `bifrost.security.javascript.process-input-to-child-process-command`
for the command-injection part of BrokkAi/bifrost-packs#393. The source is a
`process.argv` keyed read. The sink is the command operand of the
one-argument `child_process.execSync(command)`, which runs it in a shell. It
binds through the released, reviewed models copied into
`.bifrost/semantic-models`:

- `bifrost.node-runtime-values-javascript` 0.1.0 (`process.argv`).
- `bifrost.node-child-process-javascript-declarations` 0.2.0 and
  `bifrost.node-child-process-javascript-summaries` 0.1.0.

All three are in the `packs/v0.14.0` native release, so the rule also works
with only the released packs. The policy is opt-in.

## Cases

- **Positives** (`main.js`): the argument as the whole command (line 8);
  concatenated into a command line (14); inside a template literal (20).
- **Near miss** (`main.js`): a constant command, with the argument only
  compared.
- **Incomplete** (`incomplete/`, its own workspace): `options` calls
  `execSync(command, options)`, and `exec` calls `exec(command)` and uses the
  result. Neither form has a reviewed model, so each run is inconclusive with
  no finding.
- **Uncovered** (`uncovered/`): `execFile` with an argument array is not a
  sink of this rule, so the run is complete with no finding and says that no
  sink bound.

## Validation

Bifrost `v0.15.3` (`bifrost-v0.15.3-aarch64-apple-darwin`, binary SHA-256
`1e8d45ae76f1b2920aa7a113e8e80083346f6acbed839c3e113058ae36c8acbc`, build
identity `cc7ebd1676e002b657e10304cfd977bc289e25ed`), evaluation date
`2026-11-17`. Each run used `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`--no-builtin-policies`, `--no-incremental` and a fresh `BIFROST_CACHE_DIR`.

- This directory: `proven_by_summary`, 3 definite findings at `main.js`
  lines 8, 14 and 20.
- The same run with no `.bifrost/semantic-models` and the `packs/v0.14.0`
  native bundle (`bifrost.public.packs-0.14.0-native.tar.gz`, SHA-256
  `f0f9bb7467aa30ee2d6940d6232094b938f030753f48f2307fb19f98b427794a`) as
  `BIFROST_OPEN_SEMANTIC_PACK_BUNDLE`: the same 3 definite findings,
  `proven_by_summary`.
- `incomplete/`: `inconclusive (partial_discovery)`, no finding; each case
  alone is inconclusive too.
- `uncovered/`: `complete`, no finding, "bound no sink endpoint".

## Known limits

- Only `process.argv` is a source.
- `exec`, `execFile`, `spawn` and `spawnSync`, including their
  `shell: true` forms, and `execSync` with options have no reviewed model
  yet. A tainted command whose call result is used leaves the run
  inconclusive. One whose result is unused gives no finding.

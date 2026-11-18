# JavaScript process argument to vm code fixture

Qualifies `bifrost.security.javascript.process-input-to-vm-code` for the
code-injection part of BrokkAi/bifrost-packs#393. The source is a
`process.argv` keyed read. The sinks are the code operands of
`vm.runInNewContext(code)`, `vm.runInNewContext(code, contextObject)` and
`vm.runInThisContext(code)`. They bind through the reviewed models copied
into `.bifrost/semantic-models`:

- `bifrost.node-runtime-values-javascript` 0.1.0 (`process.argv`).
- `bifrost.node-vm-javascript-declarations` 0.1.0 (new, source-only, see
  `semantic-packs/node/vm/README.md`). It has no summaries on purpose, so
  every finding is `possible` and every run that reaches a `vm` call is
  inconclusive.

The policy is opt-in.

## Cases

- **Positives** (`main.js`): `runInNewContext` on the argument (line 8) and on
  a string built from it (14). Each is a `possible` finding.
- **Near miss** (`main.js`): the argument only selects which constant
  expression runs. It gives no finding, but the run is not proven clean,
  because no `vm` call has a summary.
- **Incomplete** (`incomplete/`, its own workspace): `with-context`
  (`runInNewContext(code, contextObject)`), `this-context`
  (`runInThisContext(code)`) and `script` (`new vm.Script(source)`) each give a
  `possible` finding. `options` passes an options argument to
  `runInThisContext`, which has no declaration, so it gives no finding.

## Validation

Bifrost `v0.15.3` (`bifrost-v0.15.3-aarch64-apple-darwin`, binary SHA-256
`1e8d45ae76f1b2920aa7a113e8e80083346f6acbed839c3e113058ae36c8acbc`, build
identity `cc7ebd1676e002b657e10304cfd977bc289e25ed`), evaluation date
`2026-11-17`. Each run used `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`--no-builtin-policies`, `--no-incremental` and a fresh `BIFROST_CACHE_DIR`.

- This directory: `inconclusive (partial_discovery)`, 2 possible findings at
  `main.js` lines 8 and 14.
- `incomplete/`: `inconclusive (partial_discovery)`, 3 possible findings
  (`with-context` and `this-context` line 7, `script` line 6); each case alone
  is inconclusive.

## Known limits

- `new vm.Script(source)` compiles without running. The rule reports the
  constructor as a possible sink anyway, so compiling input only to check its
  syntax is a possible false positive.

- Only `process.argv` is a source.
- `vm.compileFunction`, `vm.runInContext` and the options forms are not
  sinks. `eval` and the `Function` constructor are reported by
  the lexical `bifrost.correctness.dynamic-evaluation` rule, not by this one.

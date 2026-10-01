# Issue #24: Bifrost C runtime qualification

## Conclusion

No production rule qualifies from this research. Both candidates remain
**unsupported/incomplete**, not clean:

- POSIX/Linux credential-drop sequencing has no active C/POSIX model or catalog
  rule for exact external API identity, successful state transitions, and
  required order.
- C filesystem check/use has no active C/POSIX model or catalog rule for exact
  file API identity, path/object identity, and continuity across the window.

The only default C policy in the built-in catalog is the narrow self-assignment
check. Its semantic hash does not support credential or filesystem semantics.
The Joern filesystem selector is separately recorded as a source-text lead in
`catalog-inventory.md`; it was not prototyped in this runtime probe.

## Worktree and exact runtime provenance

The managed Bifrost CLI was run from this checkout:

- Worktree `/Users/dave/.codex/worktrees/issue-24-joern/bifrost-packs`
- Branch `dave/issue-24-joern`, HEAD
  `f3e5468571d580062522d472d8b145efacc48fde`
- Remote `origin git@github.com:BrokkAi/bifrost-packs.git`
- Active workspace tool result: the same worktree path, with
  `semantic_packs_ready: true` and `usage_index_ready: true`. These are index
  readiness claims, not proof of C/POSIX API coverage.
- Managed binary:
  `/Users/dave/Library/Caches/bifrost-agent/binaries/0.12.0/darwin-arm64/bifrost`
- `bifrost --version`: `0.12.0`; built-in packs
  `code-smells@2.16.0`, `correctness@0.1.0`, `security@1.3.0`, and `effects@1.4.0`
- Opaque `--build-identity`: `676def6c6615002002b1bb9d25211ad1476a5b5d`
- Binary SHA-256:
  `168cf91d61f7504fbabf77974bfe53cdcc6f41abfbb727b7b152db18a3c4b545`
- Built-in policy catalog SHA-256:
  `9d1e4021b68c4dbd8d03c2ab9c10c05578868bd2b38ceae5e9aeca1849ba083e`

The older `/Users/dave/.cargo/bin/bifrost` on `PATH` reports 0.11.4 and was not
used. All fixture queries below use the managed 0.12.0 binary and explicit
`--root .` / `--query-file` arguments.

## Catalog and policy probe

The read-only MCP catalog listed these C policies:

- `bifrost.correctness.c-self-assignment` (C only), capabilities
  `prepared-c-syntax`, `assignment-relations`, `reaching-definitions`, and
  `same-evaluation`; authored and resolved semantic hash
  `613655d61b87df1aa17143ae1d8b1c4f2138300fa20d17fe09fa221bcc1b7dc9`.
- Opt-in `bifrost.security.c.stored-request-to-sql`, with unresolved semantic
  hash (`null`; authored hash
  `c286d4e92032a2e34c5778fc8d395b2d06ac16c77ee695bf0efaad49fd85437c`), and
  opt-in `bifrost.security.c.store-requires-validation`, also with unresolved
  semantic hash (`null`; authored hash
  `42a369670f0ff0346b159394021af9d7296646ee1331ece21348158f68c2fe40`). Neither
  addresses the candidate contracts.
- No C policy in the catalog covers credential transitions or filesystem
  check/use races.

A symbol search for `setuid`, `seteuid`, `setgid`, `setresuid`, `access`,
`stat`, `lstat`, and `openat` reported `total_model_symbols: 0` and
`truncated: false`. This is consistent with the API calls being unmodeled; it
does not identify third-party declarations by spelling.

The MCP `run_policy` probe selected
`bifrost.python-os-command-declarations@0.1.0`,
`bifrost.python-os-command-summaries@0.1.0`,
`bifrost.python-process-inputs@0.1.0`, and `bifrost.scala.case-class@1.0.0`,
not C/POSIX models. No candidate model hash was active. Its self-assignment
result said `clean` but also
reported `empty_selection`, zero scanned files/bytes, and zero findings; that
result is vacuous and is not treated as qualification. MCP did not expose the
immutable workspace SHA or build identity for that request, so only the direct
CLI query results below are attributed to the exact binary and worktree above.

## Replayable fixture-query results

All six retained CodeQuery files ran through Bifrost 0.12.0 with exit code 0,
`truncated: false`, and no diagnostics, except `call-bindings.json`, which
retained nine `semantic_analysis_partial` diagnostics for unresolved external
callees. Queries and source-only fixtures are in
`prototypes/posix-credential-drop/`; `results/outcome.json` records the compact
row counts and input hashes.

- `dispatch-outcomes.json`: 12 call sites. The nine calls in the three
  system-header fixtures (`setgroups`, `setgid`, and `setuid`) all returned
  `outcome: unknown`, `coverage: open`, and `target_count: 0`. The three
  same-named calls in `local-lookalike.c` resolved exhaustively to one local
  declaration each.
- `dispatch-targets.json`: three complete, proven declarations, all in
  `local-lookalike.c`. This is useful control evidence that same-spelled local
  functions are kept distinct from external APIs.
- `call-bindings.json`: external call mappings are `incomplete`, with
  `bound_count: 0`, `selector_exact: false`, and `reason: callee_unresolved`.
  Local lookalikes have exact call-to-declaration selections and exhaustive
  actual/formal counts, but conversion status remains `unknown` for the C/C++
  adapter. No exact Linux API binding is established.
- `procedure-state.json`: six rows, all binding reads; no credential-state
  event is derived. The rows mark `same_evaluation_relation` as uncovered.
- `procedure-guards.json`: three complete, proven opaque guard rows in the
  intentionally unsafe `failure-continues.c`, at its three call checks.
  Guard parsing alone does not connect a guard to the target API or prove that
  the required process state was reached.
- `procedure-exits.json`: both the guarded and failure-continues procedures
  have one complete normal and one complete exceptional exit row. Exit
  boundaries are available, but this query does not associate exact API return
  values or credential states with either boundary.

An exploratory `control_relations` query exceeded its default row limit; a
narrowed retry produced output too large for a bounded retained artifact. It
was removed from the replay set and is not evidence. The retained queries make
the unresolved API identity, absent credential-state model, available guard
shapes, and CFG exit boundaries reproducible without relying on that result.

No C fixture was compiled or executed. The fixtures are deliberately inert
analyzer inputs, including calls that would otherwise change process
credentials.

## Exact replay commands

From the repository root, run each query separately with the managed binary:

```sh
"/Users/dave/Library/Caches/bifrost-agent/binaries/0.12.0/darwin-arm64/bifrost" \
  --root . \
  --query-file research/joern/prototypes/posix-credential-drop/queries/dispatch-outcomes.json
```

Repeat for each retained file in `prototypes/posix-credential-drop/queries/`.
`--query-file` runs that saved query as a complete query. Do not substitute the
older Cargo binary from `PATH`.

## Follow-up owner ledger

| Lead | Route | Boundary |
|---|---|---|
| Credential-drop naming and state-transition lead | Issue #24; analyzer/model owner if API resolution or effects are required | Keep incomplete until external identity, success/failure effects, credential state, ordering, and failure exits are proven |
| File-operation path race (`FileOpRace.scala`) | Issue #24 for research triage; Bifrost filesystem/model owner for any future implementation | Name and expression-string matches do not establish object identity, attacker control, or a check/use window |
| Heap overflow, use-after-free, and printf format candidates | Issue #12 owner | Do not duplicate this batch in #24 |
| Java/Kotlin TLS and certificate checks | Issue #15 owner | Do not create a second TLS batch; preserve the untested broad selector finding for its owner |
| Android and framework-dependent rules | Premium/Android owner | Outside this public source-C / Java issue scope |

The catalog and attribution inventory is in `catalog-inventory.md`; no Joern
query or test code was copied into the public repository. The pinned Joern
revision, repository license hash, query/test authorship metadata, and selected
source/test hashes are recorded there.

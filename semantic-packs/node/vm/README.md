# Node `vm` packs

`bifrost.node-vm-javascript-declarations` 0.1.0 is a source-only pack that
declares the JavaScript Node core `vm` members that compile or run a code
string, for the `process-input-to-vm-code` security policy
(BrokkAi/bifrost-packs#393):

- `vm.runInNewContext(code)` and `vm.runInNewContext(code, contextObject)`;
- `vm.runInThisContext(code)`;
- the `vm.Script(code)` constructor.

The declarations follow `doc/api/vm.md` at Node `v22.11.0`. They let a
policy bind the code operand of these calls as a sink.

## No summaries, on purpose

The pack has no procedure summaries. `vm` is not a security mechanism
(`doc/api/vm.md`), and evaluated code can escape its context and read or write
anything the process can reach: host globals, the caller's context object, the
network. A complete summary would claim that none of that happens, so other
value-flow and effect policies could lose flows or certify a boundary as free
of network I/O. Without a summary, any analysis that has to pass through a
`vm` call stays incomplete. A taint finding at the code operand is `possible`,
and the run is inconclusive.

## Not modeled

`vm.compileFunction`, `vm.runInContext`, `vm.SourceTextModule`, the options
argument of each member, and every other arity.

The pack carries the repository's `Apache-2.0` model license and sets
`safety.review_required: false`. It is source-only: no native release recipe
includes it yet. The Node distribution notice is retained at
`semantic-packs/node/runtime-values/notices/node-v22.11.0.txt`.

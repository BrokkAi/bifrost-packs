# Node `fs` packs

These public packs provide the reviewed JavaScript Node core `fs` namespace
facts used by the file-system-race policy. They are intentionally narrow: the
declaration pack covers the synchronous check and use members needed by that
policy, and the summary pack covers the reviewed `existsSync` and
`writeFileSync` procedure identities.

The model provenance is Node.js `v22.11.0`. The JSON packs are authored Bifrost
semantic facts, carry the repository's `Apache-2.0` model license, and require
reviewed activation (`safety.review_required: true`). The corresponding Node
distribution notice is retained at
`semantic-packs/node/runtime-values/notices/node-v22.11.0.txt`.

## Public model scope

`bifrost.node-fs-javascript-declarations` declares the JavaScript `fs` module
members `existsSync`, `statSync`, `lstatSync`, `accessSync`, `writeFileSync`,
`appendFileSync`, and `openSync`, with their reviewed synchronous signatures.
`bifrost.node-fs-javascript-summaries` identifies the `existsSync` and
`writeFileSync` procedures for the engine's value-flow and call-identity
relations. Calls outside these exact modeled identities, asynchronous APIs,
dynamic aliases, and other Node versions remain outside this pack's coverage.

The packs are partial by design and do not assert that an arbitrary `fs` call
is safe. Workspace path identity, rebinding, control flow, and analysis
completeness remain engine responsibilities. The public file-system-race
fixture includes a reassignment near miss to preserve that boundary: its
findings are useful evidence, but the run remains incomplete when the engine
cannot prove the rebinding identity.

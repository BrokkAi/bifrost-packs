# Node `fs` packs

These public packs provide the reviewed JavaScript Node core `fs` namespace
facts used by the file-system-race policy and the
`process-input-to-fs-write-path` security policy. They are intentionally
narrow: the declaration pack covers the synchronous check and use members
needed by that policy, and the summary pack covers the reviewed `existsSync`,
`writeFileSync`, `appendFileSync` and `openSync` procedure identities.

The model provenance is Node.js `v22.11.0`. The JSON packs are authored Bifrost
semantic facts, carry the repository's `Apache-2.0` model license, and require
reviewed activation (`safety.review_required: true`). The corresponding Node
distribution notice is retained at
`semantic-packs/node/runtime-values/notices/node-v22.11.0.txt`.

## Public model scope

`bifrost.node-fs-javascript-declarations` declares the JavaScript `fs` module
members `existsSync`, `statSync`, `lstatSync`, `accessSync`, `writeFileSync`,
`appendFileSync`, and `openSync`, with their reviewed synchronous signatures.
Version 0.2.0 adds `readFileSync(path)`, `readFileSync(path, options)`,
`readdirSync(path)`, `unlinkSync(path)`, `rmSync(path)` and
`rmSync(path, options)` for the `process-input-to-fs-path` security policy
(#393). It also declares, with no summaries, the callback forms
`readFile(path, callback)`, `readFile(path, options, callback)`,
`readdir(path, callback)` and `unlink(path, callback)`, and an `fs/promises`
module with `readFile`, `readdir`, `unlink` and `rm`. They run callbacks or
settle promises that a summary can't describe, so value flow through them
stays incomplete while their path operands still bind as sinks.
`bifrost.node-fs-javascript-summaries` identifies the `existsSync`,
`writeFileSync`, `appendFileSync` and `openSync` procedures for the engine's
value-flow and call-identity relations. Version 0.2.0 added `appendFileSync`
and `openSync` for the `process-input-to-fs-write-path` security policy. Like
`writeFileSync`, their summaries carry no normal-return transfer: both return no value
derived from their arguments (`undefined` and a numeric descriptor).
Version 0.3.0 adds summaries for `statSync`, `lstatSync`,
`accessSync(path, mode)`, both `readFileSync` and `rmSync` arities,
`readdirSync` and `unlinkSync`. They carry no normal-return transfer either. The
`readFileSync` result is file content, not the path string, and the listing
returned by `readdirSync` holds names found on disk. Summaries are identified
by symbol, so each two-argument form that shares a member name with a
one-argument form uses a parenthesized symbol, such as
`fs.readFileSync(path, options)`. Every summary except `existsSync` also carries every argument to the
exceptional return: a failed call throws an error whose `path` and `message`
name the path, and an invalid argument such as a bad encoding string is quoted
in the error message (`doc/api/errors.md`), so a `catch` block can observe
them. This
applies to the 0.2.0 write summaries too. `existsSync` returns `false` instead
of throwing. Calls
outside these exact modeled identities, asynchronous APIs, dynamic aliases,
and other Node versions remain outside this pack's coverage.

The packs are partial by design and do not assert that an arbitrary `fs` call
is safe. Workspace path identity, rebinding, control flow, and analysis
completeness remain engine responsibilities. The public file-system-race
fixture includes a reassignment near miss to preserve that boundary: its
findings are useful evidence, but the run remains incomplete when the engine
cannot prove the rebinding identity.

# Node `path` packs

These public packs give the reviewed JavaScript Node core `path` members that
compose file paths, so value flow can cross them. The
`bifrost.security.javascript.process-input-to-fs-write-path` policy
(BrokkAi/bifrost-packs#287) uses them.

The model provenance is Node.js `v22.11.0`. The JSON packs are authored Bifrost
semantic facts under the repository's `Apache-2.0` model license. They require
reviewed activation (`safety.review_required: true`) and use the same Node
`22.11.0` activation selector as the `fs` packs. The Node distribution notice
is at `semantic-packs/node/runtime-values/notices/node-v22.11.0.txt`.

## Reviewed claims

The claims rest on `doc/api/path.md` at Node `v22.11.0` (SHA-256
`32e309fcfb432b9186a33970311a37cecb59946db59e57dbd391837ebf1e1aa4`,
`https://github.com/nodejs/node/blob/v22.11.0/doc/api/path.md`):

- `path.join(base, segment)` and `path.resolve(base, segment)` return a string
  built from both arguments. Each argument flows to the normal return.
- `path.normalize(path)` returns its argument normalized, so the argument
  flows to the normal return.
- The namespace receiver flows to itself.
- Each summary claims every outside-workspace implementation of its member
  (`covers_overrides`), matching the builtin-only namespace.

## Scope

Only the two-argument `join` and `resolve` forms and the one-argument
`normalize` form are modeled. Node declares `join` and `resolve` with a rest
parameter, but a summary can't yet reference a variadic tail formal
(bifrost-dev#9985). Calls with other arities don't bind and stay fail-closed.
`basename`, `dirname`, `relative` and the `path.win32` and `path.posix`
namespaces are not modeled. A guard built from them leaves a run
inconclusive.

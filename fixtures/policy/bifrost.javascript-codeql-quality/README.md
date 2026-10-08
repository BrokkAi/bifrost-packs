# Public JavaScript CodeQL quality fixtures

These fixtures cover the public JS02 declaration, binding, class, and
identifier rules in `rules/bifrost.javascript-codeql-quality`. The product
policies combine the JavaScript and TypeScript selectors where the engine
goldens provide both language variants; each fixture preserves the golden
positive and same-shaped near miss.

Every policy retains CodeQL query provenance at commit
`ae741615f3e178ce61289a651790dc67fcc18e19` and requires the unreleased
JavaScript parity engine change. The qualification engine commit is recorded
in the PR description and this pack's validation evidence as
`6b318149a22ce84c2b707937062036d5483cae87`; the content needs the next engine
release containing that change.

`missing-variable-declaration` intentionally retains the dynamic-scope and
direct-eval case. The engine reports its three proven findings but marks the
run incomplete because those constructs prevent exhaustive binding and
liveness resolution. That partial result is not a clean result.

The public follow-up space remains reserved for `alert-call`,
`file-system-race`, and `password-in-configuration-file`; those rules are not
included until their product authoring is ready.

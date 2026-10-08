# Public JavaScript CodeQL quality fixtures

These fixtures cover the public JS02 declaration, binding, class, identifier,
Node, and configuration rules in `rules/bifrost.javascript-codeql-quality`.
The product policies combine the JavaScript and TypeScript selectors where the
engine goldens provide both language variants; each fixture preserves the
golden positive and same-shaped near miss.

Every policy retains CodeQL query provenance at commit
`ae741615f3e178ce61289a651790dc67fcc18e19` and requires the unreleased
JavaScript parity engine change. The qualification engine commit is recorded
in the PR description and this pack's validation evidence as
`e7bc03b3be70b594019b2f4ec27b20af79dc281f`; the content needs the next engine
release containing that change. The `file-system-race` fixture installs the
reviewed public Node `fs` model from `semantic-packs/node/fs/javascript/`.

`missing-variable-declaration` intentionally retains the dynamic-scope and
direct-eval case. The engine reports its three proven findings but marks the
run incomplete because those constructs prevent exhaustive binding and
liveness resolution. That partial result is not a clean result.

`resource-exhaustion-from-deep-object-traversal` (the Ajv rule) remains
excluded because its engine support is not ready. It is not represented by a
public policy, fixture, or model here.

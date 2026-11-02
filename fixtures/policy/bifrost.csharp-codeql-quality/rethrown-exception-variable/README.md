# C# rethrown-exception-variable parity fixture

Mirrors CodeQL `csharp/ql/src/Language Abuse/RethrowException.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. The fixture's local
`Probe.cs` includes positive throws, including a filtered catch, and near
misses: a bare `throw;`, wrapping the exception, a different variable, and
throws in nested scopes. Its policy copy matches the authored rule.

The C# throw-site failure-handler relation selects a `throw` statement that
throws the variable declared by its owning catch, including parenthesized
`throw (error);`. The finding is anchored on that throw statement, as CodeQL
anchors it. The fixture installs the public BCL model for caught exception
types; the upstream query gate also passed without that model.

## Validation

Released Bifrost v0.15.0 (build identity
`09a2503c5f7ced1630a9e3c445ead53dfc5925e8`; macOS arm64 archive SHA-256
`34295669d86aef268f0134c15f5127b90deac2e31e2f89bd3031ffe05cf097a5`),
gated against the original CodeQL query test: EXACT and complete, 2 true
positives, zero false positives, misses, silent misses or abstentions, both
with and without the semantic model. Released v0.14.4 gave the same result.
The earlier v0.14.1 catch-clause anchor is superseded.

# C# nested-if-statements parity fixture

Mirrors CodeQL `csharp/ql/src/Language Abuse/NestedIf.ql` and its query test source
`csharp/ql/test/query-tests/Language Abuse/NestedIf/nestedif.cs` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. The copied source retains
positive and realistic near-miss cases. Two MIT attribution lines precede the
upstream source, shifting its source line numbers by two.

The rule reports an if whose sole consequence is another if; branches with other statements or alternatives are near misses. The policy copy is the exact authored rule.

## Validation

Released Bifrost v0.15.0 (build identity
`09a2503c5f7ced1630a9e3c445ead53dfc5925e8`; macOS arm64 archive SHA-256
`34295669d86aef268f0134c15f5127b90deac2e31e2f89bd3031ffe05cf097a5`),
gated against CodeQL's original upstream query test. Verdict EXACT, complete:
3 true-positive site(s), zero false positives, misses, silent misses, or
abstentions. Released v0.14.4 gave the same result before the v0.15.0
preprocessor and C# flow changes.

## Known limit

Structural C# policies do not yet report the undecided `#if` branch obligation
(bifrost-dev#8723). A nested `if` in an undecided branch is reported definite.
A v0.15.0 `lock-this` probe confirms this for an undefined symbol; a `#if false`
branch is excluded.

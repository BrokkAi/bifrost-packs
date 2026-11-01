# C# misleading-indentation parity fixture

Mirrors CodeQL `csharp/ql/src/Likely Bugs/Statements/UseBraces.ql` and its query test source
`csharp/ql/test/query-tests/UseBraces/UseBraces.cs` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. The copied source retains
positive and realistic near-miss cases. Two MIT attribution lines precede the
upstream source, shifting its source line numbers by two.

The rule reports an if or loop whose successor is visually indented like its body; aligned successors and braced controls are near misses. The policy copy is the exact authored rule.

## Validation

Released Bifrost v0.14.4 (Linux archive SHA-256
`fac867ff504a8637190c99e6818eb6a1cfa93469683526a899f653d7db14685a`),
gated against CodeQL's original upstream query test. Verdict EXACT, complete:
5 true-positive site(s), zero false positives, misses, silent misses, or
abstentions. Gate details are in the M6 wave-1 packaging report.

## Known limit

Structural C# policies do not yet report the undecided `#if` branch obligation
(bifrost-dev#8723). A `lock(this)` in an undecided branch is reported definite.

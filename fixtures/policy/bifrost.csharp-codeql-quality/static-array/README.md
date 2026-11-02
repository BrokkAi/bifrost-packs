# C# static-array parity fixture

This product fixture covers CodeQL `csharp/ql/src/Bad Practices/Implementation Hiding/StaticArray.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

The engine contract is a structural C# field relation: report a public,
static, readonly array field when every definition (field initializer or
static-constructor assignment) is a non-empty or unknown-size array or null.
A field with no definition also qualifies. The private field and the two
known-empty array initializers are same-shaped near misses. The fixture
exercises declaration metadata and tree-sitter initializer shape; the product
policy is listed in the `bifrost.csharp-codeql-quality` manifest.

## v0.14.4 correction

The policy includes fields defined in a static constructor and fields with no
definition at all, while retaining the private and known-empty near misses.
Against the original CodeQL query test at `ae741615f3`, released Bifrost
v0.14.4 (Linux archive SHA-256
`fac867ff504a8637190c99e6818eb6a1cfa93469683526a899f653d7db14685a`) and
released v0.15.0 (build identity `09a2503c5f7ced1630a9e3c445ead53dfc5925e8`;
macOS arm64 archive SHA-256
`34295669d86aef268f0134c15f5127b90deac2e31e2f89bd3031ffe05cf097a5`) both
gate EXACT and complete: 4 true-positive sites, zero false positives,
misses, silent misses or abstentions.

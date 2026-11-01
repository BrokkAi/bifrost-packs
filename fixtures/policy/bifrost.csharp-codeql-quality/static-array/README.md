# C# static-array parity fixture

This product fixture covers CodeQL `csharp/ql/src/Bad Practices/Implementation Hiding/StaticArray.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

The engine contract is a structural C# field relation: report a public,
static, readonly array field with a non-empty or unknown initializer. The
private field and the two known-empty array initializers are same-shaped near
misses. The fixture exercises declaration metadata and tree-sitter initializer
shape; the product policy is listed in the `bifrost.csharp-codeql-quality`
manifest.

## v0.14.4 correction

The policy now includes uninitialized public static readonly array fields
whose static constructor defines a qualifying array, while retaining the
private and known-empty near misses. Against the original CodeQL query test at
`ae741615f3`, released Bifrost v0.14.4 gates EXACT and complete: 4
true-positive sites, zero false positives, misses, silent misses or
abstentions. The archive SHA-256 is
`fac867ff504a8637190c99e6818eb6a1cfa93469683526a899f653d7db14685a`.

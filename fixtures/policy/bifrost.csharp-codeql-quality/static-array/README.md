# C# static-array parity fixture

This product fixture covers CodeQL `csharp/ql/src/Bad Practices/Implementation Hiding/StaticArray.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

The engine contract is a structural C# field relation: report a public,
static, readonly array field with a non-empty or unknown initializer. The
private field and the two known-empty array initializers are same-shaped near
misses. The fixture exercises declaration metadata and tree-sitter initializer
shape; the product policy is listed in the `bifrost.csharp-codeql-quality`
manifest.

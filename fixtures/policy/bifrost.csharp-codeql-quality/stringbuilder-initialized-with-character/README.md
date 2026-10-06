# C# StringBuilder character fixture

This product fixture is based on CodeQL query `csharp/ql/src/Likely Bugs/StringBuilderCharInit.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

The fixture activates the reviewed public BCL model, which declares the
one-argument `System.Text.StringBuilder` overload family for
the `System.Int32` capacity and `System.String` constructors. C# implicitly
converts a `char` to the integer capacity overload. The policy exercises the new
structured `character_literal` kind for the literal case and the fixture's
`value` formal for the typed `char` parameter case; the string literal and the
integer literal remain near misses.

# C# StringBuilder character fixture

This product fixture is based on CodeQL query `csharp/ql/src/Likely Bugs/StringBuilderCharInit.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

The fixture activates the reviewed public BCL model, which declares the
one-argument `System.Text.StringBuilder` overload family for the
`System.Int32` capacity and `System.String` constructors. The policy selects a
character literal by its structured `character_literal` kind. A formal
parameter is selected only when its call-binding row reports
`conversion_status: proven` and `conversion: csharp_implicit_numeric`; that
current C# conversion contract is exactly `char` to `int32`. The parameter name
is arbitrary and is not used as type evidence.

Integer and string literals and formals are same-shaped near misses; both
formal near misses use the name `value` to show that identifier spelling does
not determine the result. Byte and short formals are separate fresh-workspace
typed-unknown controls. The conversion model does not prove those conversions,
so they are not included in the default fixture or treated as clean negative
witnesses.

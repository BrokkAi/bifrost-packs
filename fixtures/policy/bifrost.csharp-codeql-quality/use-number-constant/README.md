# C# use-number-constant parity fixture

This product fixture covers CodeQL `csharp/ql/src/Bad Practices/Magic Constants/MagicNumbersUseConstant.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

The engine contract is a structural C# integer-literal relation: report an
integer literal whose decoded value equals a visible `const` or `static
readonly` field initializer in the same declaring type. The initializer
literal itself and the named constant use are same-shaped near misses.

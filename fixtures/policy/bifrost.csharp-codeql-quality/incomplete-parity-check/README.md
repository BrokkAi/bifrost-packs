# C# incomplete-parity-check parity fixture

Mirrors CodeQL `csharp/ql/src/Likely Bugs/BadCheckOdd.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. The upstream test source keeps
its CodeQL path and an MIT attribution header. The two header lines shift
upstream line numbers by two.

The engine contract is structural. It reports a comparison `x % 2 == 1`,
`x % 2 != 1` or `x % 2 > 0` when the remainder is the left operand and the
divisor and right operand are integer literals with those values, in any
integer spelling (`1L`, `0x1`, `0b1`). Parentheses are transparent. Through
at most two casts, the remainder's dividend is excluded when it is a
non-negative integer literal, a member access named `Length` or a call named
`Count`, following CodeQL's `isDefinitelyPositive`.

Positives in `Probe.cs`: `==`, `!=` and parenthesized `>` tests, a `long`
remainder with `1L`, a cast dividend, a `List<T>.Count` property (CodeQL
excludes only a `Count` call), and a `while` condition.

Near misses: `x % 2 == 0`, `x % 2 != 0`, `Math.Abs(x % 2) == 1`,
`x % 3 == 1`, `x % 2 == -1`, `x % 2 >= 1`, the reversed `1 == x % 2`,
`x % 2 == 1.0`, the pattern `x % 2 is 1`, `args.Length`, a cast
`args.Length`, `values.Count()` and the literal dividend `7`.

## Validation

Bifrost 0.15.0, build identity `09a2503c5f7ced1630a9e3c445ead53dfc5925e8`,
binary SHA-256
`d9acbc7305ed0390457117c48531c82c5ff0778dab4290f5cc670e692280ae45`
(`bifrost-v0.15.0-aarch64-apple-darwin`), evaluation date `2026-11-02`, run
from this directory with `BIFROST_OPEN_PACKS_DISABLE=1`,
`--no-builtin-policies` and `--no-incremental`. The authored policy hash is
`5c1cc7c0c3ebf83e15cde3d913de5c1d01f7d774f1af8cb9753608fd56312924`; its
resolved identity is available and equal.

The run is complete with eleven findings: `Probe.cs:9` through
`Probe.cs:15`, plus the four upstream expected rows `BadCheckOdd.cs:19`,
`:21`, `:23` and `:25` (upstream lines 17, 19, 21 and 23, all at column 17).
The upstream GOOD rows and every near miss produce no finding.

## Known limits

The selection is syntactic, so it differs from CodeQL in these cases:

- Reported here but not by CodeQL: a dividend that is another non-negative
  constant, such as a `const` field or `(3 + 4)`; an implicit-this `Length`
  property read without a receiver; and a dividend under three or more casts.
- Reported here but not by CodeQL: a remainder or comparison on a type with
  user-defined operators, such as `decimal` or `BigInteger`. CodeQL extracts
  those as operator calls, not as `%` and `==` expressions. The parity bug
  is the same for those types.
- Excluded here but not by CodeQL: a field named `Length`, since the engine
  does not distinguish a field read from a property read.

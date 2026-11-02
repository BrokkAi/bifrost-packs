# C# class-name-comparison parity fixture

Mirrors CodeQL `csharp/ql/src/Bad Practices/ErroneousClassCompare.ql` at
commit `ae741615f3e178ce61289a651790dc67fcc18e19`. The pinned CodeQL
checkout has no upstream test for this query. `upstream/` holds the query's
help examples, `ErroneousClassCompare.cs` and `ErroneousClassCompareFix.cs`,
with their CodeQL path and an MIT attribution header. The two header lines
shift upstream line numbers by two.

CodeQL reports an equality `ComparisonTest` between a string literal and a
read of `System.Type.FullName`. No reviewed semantic model declares
`System.Type` or `Object.GetType`, so the engine contract stands in for the
target with the receiver shape: a `FullName` member read from a parameterless
`GetType()` call or a `typeof` expression. The equality forms are `==` in
either operand order, a one-argument instance `Equals` call in either order,
and `Equals` or `ReferenceEquals` called on an explicit `object`, `Object` or
`System.Object` receiver. Parentheses are transparent.

Positives in `Probe.cs`: both `==` orders, `typeof(...).FullName`, an
implicit-this `GetType()`, both instance `Equals` orders, `object.Equals` and
`Object.ReferenceEquals`.

Near misses: `!=` (CodeQL selects equality only), `Name`,
`AssemblyQualifiedName`, a non-literal operand, `GetType() == typeof(...)`,
an `is` check, a source-declared `FullName` field, a source-declared
`GetType(int)` in `Local.cs`, static `string.Equals` (not one of CodeQL's
equality methods) and `StartsWith`.

## Validation

Bifrost 0.15.0, build identity `09a2503c5f7ced1630a9e3c445ead53dfc5925e8`,
binary SHA-256
`d9acbc7305ed0390457117c48531c82c5ff0778dab4290f5cc670e692280ae45`
(`bifrost-v0.15.0-aarch64-apple-darwin`), evaluation date `2026-11-02`, run
from this directory with `BIFROST_OPEN_PACKS_DISABLE=1`,
`--no-builtin-policies` and `--no-incremental`. The authored policy hash is
`025a8ee6724b7109b3a78507ae24fe710c902644b5e0d18bbb87029c133712eb`; its
resolved identity is available and equal.

The run is complete with nine findings: `Probe.cs:7` through `Probe.cs:14`,
plus `ErroneousClassCompare.cs:7` (upstream line 5), the help example's bad
check. `ErroneousClassCompareFix.cs` and every near miss produce no finding.

## Known limits

The receiver shape narrows CodeQL's query. CodeQL also reports these forms,
which this policy does not select:

- `FullName` read from a `Type` local, parameter, field or property, or from
  any other call that returns `System.Type`, such as `Type.GetType(name)`.
  Bifrost 0.15.0 cannot prove the receiver type without a model of
  `System.Type`.
- An unqualified static `Equals(a, b)` or `ReferenceEquals(a, b)`, because a
  source type could declare its own.
- `FullName.CompareTo("...") == 0`, and an operand under a cast such as
  `(object)t.FullName == "..."`.

A source type that hides `Object.GetType()` with its own parameterless
`GetType()` returning a type with a `FullName` member would be reported.

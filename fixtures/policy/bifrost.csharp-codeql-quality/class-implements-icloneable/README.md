# C# class-implements-icloneable parity fixture

Mirrors CodeQL `csharp/ql/src/API Abuse/ClassImplementsICloneable.ql` at
commit `ae741615f3e178ce61289a651790dc67fcc18e19`. The upstream test source
keeps its CodeQL path and an MIT attribution header. The two header lines
shift upstream line numbers by two.

CodeQL reports a non-sealed source type that declares a method named `Clone`
and whose base-interface closure (`getABaseInterface+()`) contains
`System.ICloneable`. That closure follows interfaces only: a class that
inherits `ICloneable` through its base class is not reported unless it names
the interface again.

The engine contract reports a class, record class or interface that declares
`Clone` and either names `ICloneable`, `System.ICloneable` or
`global::System.ICloneable` in its own base list, or directly implements a
source interface that names one of them, itself or through a chain of source
interfaces. The base-list name is read from source: a type reference in a
base list does not resolve to an external declaration, and `supertypes` stops
at source declarations, so the policy cannot prove the `System.ICloneable`
identity. A type that is a subtype of a source declaration named `ICloneable`
is excluded instead. Sealed types and structs are excluded; Roslyn reports
structs as sealed, and CodeQL's extractor records that as the `sealed`
modifier. No semantic model is installed.

Near misses in `Probe.cs`: a sealed class, a struct, a record struct, a
subclass of an `ICloneable` class that redeclares `Clone` with `new`, a
generic constraint `where T : ICloneable`, a class that inherits `Clone` from
its base class, an interface extending `ICloneable` with no `Clone`, and an
outer class with `Clone` whose nested class implements `ICloneable`. In
`Local.cs`, `Local.Widget` implements a source interface `Local.ICloneable`.

## Validation

Bifrost 0.14.2, build identity `073c23790739e33f33abc98338651689eaf8b7c0`,
evaluation date `2026-10-28`, run from this directory with
`BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and `--no-incremental`.
The policy hash is
`52efcbd5ac11e08e2557c3072eeb320b02e794eb7d91162bf1a0391dce062c82`.

The run is complete with eleven findings. The two upstream expected rows are
`ClassImplementsICloneableBad.cs:13` (`Shallow`) and `:22` (`Deep`), upstream
lines 11 and 20. The nine probe positives are `Probe.cs:9` (`Document`),
`:14` (`Settings`, `System.ICloneable` with an explicit `Clone`), `:19`
(`Draft`, through a source interface), `:24` (`Revision`, through two source
interfaces), `:29` (`Table<T>`, `global::System.ICloneable` after a nested
generic base; the row starts at its attribute), `:35` (`Snapshot`, a record),
`:40` (`Point`, a primary constructor), `:45` (`IShape`, an interface that
redeclares `Clone`) and `:52` (the nested `Container.Entry`). There are no
other findings.

## Known limits

- The `ICloneable` name is matched by its spelling, not its binding. A
  `using` alias, such as `using C = System.ICloneable;`, is missed.
- Resolution of a simple base name `ICloneable` to a source declaration is
  not reliable when that declaration shares a file with other types naming
  `ICloneable`. Probes outside this fixture found a class whose base list
  meant `System.ICloneable` linked to a source `ICloneable` in a sibling
  namespace of the same file, so the class was not reported. They also found
  a class meant to implement its own namespace's `ICloneable` with no
  supertype edge when a second source `ICloneable` was in scope, so the class
  was reported. `Local.cs` keeps the source interface in its own file, which
  resolves.
- A comment inside the base list, as in `class C : /* base */ ICloneable`, is
  not reported.
- The type header is read up to its first `{`. An attribute argument that
  contains `{` or `]` can hide the header from the base-list or sealed checks.
- An explicit implementation `object ICloneable.Clone()` counts as declaring
  `Clone`. I have not checked the name CodeQL gives that method.

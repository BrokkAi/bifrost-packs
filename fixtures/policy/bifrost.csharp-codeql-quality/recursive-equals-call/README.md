# C# recursive-equals-call fixture

This fixture mirrors CodeQL `csharp/ql/src/Likely Bugs/RecursiveEquals.ql`
from commit `ae741615f3e178ce61289a651790dc67fcc18e19`. The engine contract
reads the outgoing calls of each `Equals(object)` body and keeps a call whose
exact source-declared target is that same declaration, with the same uncast
parameter and an implicit or `this` receiver. A typed overload selected by a
cast is a near miss, as are a different local and an explicit receiver other
than `this`. Unresolved calls inside an `Equals(object)` body keep the run
inconclusive; unresolved calls elsewhere do not (BrokkAi/bifrost-packs#149).

`Nested.cs` holds two near misses. A lambda inside `Equals(object)` calls
`Equals(other)`. CodeQL attributes that call to the lambda, not to `Equals`,
and so does the outgoing relation. `UnresolvedElsewhere` makes `Equals` calls
that cannot be resolved. Under the earlier incoming-call shape they made the
run inconclusive, and the lambda call was reported.

## Validation

Bifrost 0.15.0, build identity `09a2503c5f7ced1630a9e3c445ead53dfc5925e8`,
evaluation date `2026-11-02`, run from this directory with
`BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and `--no-incremental`.
The authored policy hash is
`ed536bed7679872518aace6172d6936d1c49860681383abd97a1dcfac731f03a`; its
resolved identity is available and equal.

The run is complete with one finding, `Probe.cs:8`. There are no other
findings.

## Known limits

- A call made inside a local function declared in `Equals(object)` is
  attributed to `Equals`, so `bool Local() => Equals(other);` is reported.
  CodeQL attributes it to the local function and does not report it. If
  `Equals` also invokes the local function, that invocation is an unresolved
  candidate and the run is inconclusive.
- The upstream CodeQL test calls `rhs.GetType()` inside both `Equals`
  overrides. No fixture model declares `System.Object.GetType`, so those
  unresolved calls make that test inconclusive; it is not copied here.

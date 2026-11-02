# C# self-assignment parity fixture

Mirrors CodeQL `csharp/ql/src/Likely Bugs/SelfAssignment.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`, narrowed to locals and
parameters. A finding is reported on a simple `=` assignment whose left and
right sides are bare identifiers that resolve to the same lexical binding.
The two sides are compared by binding identity from `binding-of`, not by
spelling. The upstream test source keeps its CodeQL path and an MIT
attribution header. The two header lines shift upstream line numbers by two.

`Probe.cs` reports a constructor parameter assigned to itself while a
same-named field exists (line 20), a parameter (26), a local (30), a pattern
variable (31), an `out var` local (33), a `foreach` body local (34), a lambda
parameter (35) and a local captured by a lambda (36). The following are near
misses and are not reported: an assignment from a parameter to a
`this`-qualified field (21), different bindings (27, 38), a compound
assignment (28), a field assigned from a same-named parameter (47), and
object, anonymous-object and `with` initializers whose right side is a
same-named parameter (48 to 50).

## Upstream parity

Of the eleven upstream expected rows, only `selfassigns.cs:76` (upstream
line 74, `y = y`) is reported. The other ten (upstream lines 73 and 75 to 83)
assign a field, property, indexer or array element and are outside the
narrowed contract. None of the upstream `OK` lines is reported.

## Validation

Bifrost 0.15.0, build identity `09a2503c5f7ced1630a9e3c445ead53dfc5925e8`,
binary SHA-256
`d9acbc7305ed0390457117c48531c82c5ff0778dab4290f5cc670e692280ae45`
(`bifrost-v0.15.0-aarch64-apple-darwin`), evaluation date `2026-11-02`, run
from this directory with `BIFROST_OPEN_PACKS_DISABLE=1`,
`--no-builtin-policies` and `--no-incremental`. The authored policy hash is
`8ad68ec140babae67701c63527e7ee0213314906fa8180a45759cd6cb7e078ed`; its
resolved identity is available and equal.

The run is complete with nine findings: `Probe.cs` lines 20, 26, 30, 31, 33,
34, 35 and 36, and `upstream/Likely Bugs/SelfAssignment/selfassigns.cs:76`.
There are no other findings.

## Known limits

- Field, property, indexer and array-element self-assignments are not
  reported, whether written bare (`size = size`, line 44) or qualified
  (`this.count = this.count`, `other.size = other.size`, `slots[0] =
  slots[0]`, lines 43, 45 and 46). CodeQL reports these when every property
  access on the left is trivial. The engine has no C# member resolution for
  these targets and cannot prove a property accessor free of side effects.
- `bifrost.correctness.local-self-assignment` overlaps this contract through
  assignment relations. In this engine, C# `assignment-relations` rows for
  these assignments are often open (`flow_state_incomplete`), so this policy
  uses lexical bindings instead.

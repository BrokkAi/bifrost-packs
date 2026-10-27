# C# rethrown-exception-variable parity fixture

Mirrors CodeQL `csharp/ql/src/Language Abuse/RethrowException.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. The upstream test source keeps
its CodeQL path and an MIT attribution header. The two header lines shift
upstream line numbers by two.

The engine contract reads `rethrow_kind` from C# failure-handler state. A catch
clause is reported when its own body throws its declared catch variable,
including when the clause has a `when` filter or also contains a bare `throw;`.
The finding is anchored on the catch clause; CodeQL anchors it on the throw
statement.

Near misses: a bare `throw;`, wrapping the exception as an inner exception,
throwing a different variable, and throws inside a nested catch clause, a
lambda or a local function.

The fixture installs the reviewed BCL model so that the caught
`System.InvalidOperationException` resolves. Failure-handler state marks a
catch with an unresolved caught type as incomplete even though this policy
reads only `rethrow_kind`. Without a model for the caught type, the finding is
still reported, but the run is inconclusive (`capability_incomplete`).

## Validation

Bifrost 0.14.1, build identity `9b3a997bf6218a718223960242053e10d9f8eacb`,
evaluation date `2026-10-27`, run from this directory with
`BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and `--no-incremental`.
The policy hash is
`659d34a1fe1ef8afd6231460cb4d4cd5667786372a4ffcc9a3eb11d233b8d571`.

The run is complete with four findings: `Probe.cs:8` and `Probe.cs:18`, plus
`RethrowException.cs:12` and `RethrowException.cs:20`, which are the two
upstream expected rows (upstream lines 12 and 21, anchored on their catch
clauses). There are no other findings.

# C# console-output parity fixture

Mirrors CodeQL `csharp/ql/src/Bad Practices/UseOfSystemOutputStream.ql` at
commit `ae741615f3e178ce61289a651790dc67fcc18e19`. CodeQL has no query test
for this query, so `upstream/` holds the query's own example source. It keeps
its CodeQL path and an MIT attribution header. The two header lines shift
upstream line numbers by two.

The engine contract reports `Console.Write` and `Console.WriteLine` calls,
accesses to `Console.Out`, and accesses to `Console.Error`, outside a `Main`
entry point. `Out` and `Error` must resolve exactly to the `System.Console`
properties that the copy of the BCL model in `.bifrost/semantic-models` adds.

The engine cannot bind the overloaded `Write` and `WriteLine` calls through
the model, so a call is selected by name on a receiver named `Console`.
`System.Console` declares no other methods with those names, and a static
class has no extension methods. A call proven to target a source-declared
`Console` type is a near miss: see `Local.cs`.

A `Console.SetOut` call anywhere in the workspace suppresses the writes and
the `Out` accesses. A `Console.SetError` call suppresses the `Error`
accesses. The upstream example calls `Console.SetError`, so in this directory
`Console.Error` is a near miss. The nested `error-stream/` directory is a
second workspace, with its own `.bifrost` copies, that calls `Console.SetOut`
instead. `.bifrostignore` keeps it out of the root run.

`Main` is a static method named `Main` that returns `void` or `int` and takes
no parameters or one string array, as in CodeQL. Top-level statements are
excluded too. Lambdas and local functions inside `Main` are reported, because
their enclosing callable is not `Main`. So are an instance `Main()` and a
static `Main(string, string)`.

Other near misses: `TextWriter.WriteLine` on a parameter,
`Debug.WriteLine`, `Trace.Write`, `Console.ReadLine`, and the
`TextWriter.WriteLine` call in `Console.Error.WriteLine`.

## Model additions

The fixture model is `semantic-packs/dotnet/bifrost.dotnet.bcl-csharp.json`
plus the abstract class `System.IO.TextWriter` and the static properties
`System.Console.Out` and `System.Console.Error`, both of type `TextWriter`.
The master model is unchanged.

## Validation

Bifrost 0.14.2, build identity `073c23790739e33f33abc98338651689eaf8b7c0`,
evaluation date `2026-10-28`, run from this directory and from
`error-stream/` with `BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies`
and `--no-incremental`. The authored policy hash is
`b1808cdf7720cf826e952d4130dbc2aa75169423b1d0fd24adb5afcc9816ae20`; its
resolved identity is workspace-required.

The root run is complete with ten findings:

- the two upstream rows marked BAD, `UseOfSystemOutputStream.cs:14`
  (`Console.WriteLine`) and `:18` (`Console.Out`), upstream lines 12 and 16;
- `Probe.cs:11`, a lambda inside `Main`;
- `Probe.cs:21`, `:22`, `:23` and `:24`, the plain, character,
  namespace-qualified and `global::`-qualified writes;
- `Probe.cs:29`, `Console.Out`;
- `Probe.cs:34`, an instance `Main()`;
- `Probe.cs:39`, a static `Main(string, string)`.

The `error-stream/` run is complete with two findings: `ErrorProbe.cs:17`
and `ErrorProbe.cs:22`, both on the `Error` identifier of `Console.Error`.
`Main` and the `Console.SetOut` redirect suppress the rest. There are no
other findings in either run.

## Known limits

- Without the model, the property locators do not resolve and the policy is
  `not_run` rather than clean.
- A namespace-qualified property access, `System.Console.Out` or
  `System.Console.Error`, cannot be proven, so the run is inconclusive
  (`partial_discovery`). The probes keep only the unqualified forms. The same
  happens when a source-declared `Console` type has an `Out` or `Error`
  member.
- `using static System.Console;` with a bare `WriteLine`, `Out` or `Error`,
  and an alias such as `using Con = System.Console;`, are not reported,
  although CodeQL reports them. The run still claims to be complete.
- A `Write` or `WriteLine` call on a source-declared `Console` type whose
  target the engine cannot prove is reported. A `SetOut` or `SetError` call on
  such a type suppresses findings.
- Top-level statements are always excluded. CodeQL reports them when the
  file uses `await`, because the synthesized entry point then returns a
  `Task`.
- A `Main` whose return type is spelled `System.Void` or `Int32` is not
  recognized as an entry point, so its uses are reported.
- `Error` findings are anchored on the `Error` identifier, not on the whole
  `Console.Error` expression. The plan tells the three use kinds apart by row
  kind, so each redirect can suppress only its own stream.

# C# path-combine parity fixture

Mirrors CodeQL `csharp/ql/src/Bad Practices/PathCombine.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. The upstream test source keeps
its CodeQL path and an MIT attribution header. The two header lines shift
upstream line numbers by two.

The engine contract reports calls that bind to any `System.IO.Path.Combine`
overload declared by the reviewed BCL model in `.bifrost/semantic-models`.
`Path.Join` and a same-named `Local.Paths.Combine` in `Local.cs` are near
misses.

## Validation

Bifrost 0.14.2, build identity `073c23790739e33f33abc98338651689eaf8b7c0`,
evaluation date `2026-10-27`, run from this directory with
`BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and `--no-incremental`.
The authored policy hash is
`10cb56d8aa9f1b8abecd41d07c648d754848d7a33cc9ea3ec83ab9a2409ebb68`; its
resolved identity is workspace-required.

The run is complete with three findings: `Probe.cs:7` and `Probe.cs:12`, plus
the upstream expected row `PathCombine.cs:9` (upstream line 7). There are no
other findings.

## Known limits

- Without the model, the qualified locator does not resolve and the policy is
  `not_run` rather than clean.
- A call with a `string[]` argument, `Path.Combine(parts)`, leaves the run
  inconclusive. The model declares both `params` overloads, `string[]` and
  `ReadOnlySpan<string>`, as .NET 9 does, and the engine cannot yet convert
  the argument when the span overload is a candidate
  (`UnsupportedConversion`). Removing the span overload makes the call bind,
  but would make the model incomplete, so it stays.
- A namespace-qualified call, `System.IO.Path.Combine(...)`, is reported, but
  the engine cannot prove its call selector, so the run is inconclusive.

# C# call-to-gc parity fixture

Mirrors CodeQL `csharp/ql/src/API Abuse/CallToGCCollect.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. The upstream test source keeps
its CodeQL path and an MIT attribution header. The two header lines shift
upstream line numbers by two.

The engine contract reports calls that bind exactly to the zero-argument
`System.GC.Collect()` declaration, regardless of which pack supplies it. The
fixture BCL model declares all five `GC.Collect` overloads, so the near miss
`GC.Collect(0)` binds to its own overload.
`Local.cs` declares a same-named `Local.GC.Collect()` and an instance
`Collect()` method; calls to them are near misses.

## Validation

Bifrost 0.14.2, build identity `073c23790739e33f33abc98338651689eaf8b7c0`,
evaluation date `2026-10-27`, run from this directory with
`BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and `--no-incremental`.
The authored policy hash is
`2f0512281437bc958337b37e3afb09c6457a958f2b2852e85f0c9278121d1a85`; its
resolved identity is workspace-required.

The run is complete with two findings: `Probe.cs:7` and the upstream expected
row `CallToGCCollectBad.cs:9` (upstream line 7). There are no other findings.

## Known limits

- Without any declaration of `System.GC`, the run is inconclusive rather than
  clean.
- A namespace-qualified call, `System.GC.Collect()`, is reported, but the
  engine cannot prove its call selector, so the run is inconclusive
  (`partial_discovery`). The probe therefore keeps only the unqualified form.
- If one file contains a global-namespace class and a `namespace` block that
  declares a same-named `GC` type, the engine resolves the global class's
  `GC` to that type. The near-miss type lives in its own file, as it would in
  a real project.

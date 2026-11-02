# C# catch-nullreferenceexception parity fixture

Mirrors CodeQL `csharp/ql/src/Bad Practices/CatchOfNullReferenceException.ql`
at commit `ae741615f3e178ce61289a651790dc67fcc18e19`. The pinned CodeQL
checkout has no upstream test for this query, so the probe is authored.

The engine contract reads `caught_type` from C# failure-handler state and
reports catch clauses whose caught type resolves exactly to
`System.NullReferenceException`, with or without a `when` filter. The
reviewed BCL model in `.bifrost/semantic-models` declares the type and its
`System.SystemException` base.

Near misses: a caught `System.InvalidOperationException`, and a catch of the
source-declared `Local.NullReferenceException` in `Local.cs`.

## Validation

Bifrost 0.14.2, build identity `073c23790739e33f33abc98338651689eaf8b7c0`,
evaluation date `2026-10-27`, run from this directory with
`BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and `--no-incremental`.
The policy hash is
`f1b548efc0a2f6aa60d2e161299d66b602ce9e554671af5563a99b9437c852af`.

The run is complete with two findings, `Probe.cs:8` and `Probe.cs:14`. There
are no other findings.

## Known limits

- Without the model, the caught types are unresolved and the run is
  inconclusive (`capability_incomplete`) rather than clean.
- If one file contains a global-namespace class and a `namespace` block that
  declares a same-named `NullReferenceException`, the engine resolves the
  global class's catch to that type with exact proof, and the run silently
  misses the positive. The near-miss type lives in its own file, as it would
  in a real project.

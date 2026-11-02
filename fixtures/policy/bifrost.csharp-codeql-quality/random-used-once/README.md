# C# random-used-once parity fixture

Mirrors CodeQL `csharp/ql/src/Likely Bugs/RandomUsedOnce.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. The upstream test source keeps
its CodeQL path and an MIT attribution header. The two header lines shift
upstream line numbers by two.

The engine contract reports `Next`, `NextBytes` and `NextDouble` calls whose
receiver is an object creation that binds exactly to a `System.Random`
constructor in the reviewed BCL model in `.bifrost/semantic-models`. The
policy joins the call's receiver to the bound constructor site. The constructor
binding proves the created type is `System.Random` itself, as CodeQL requires.

The method is selected by name, not bound. The engine does not infer the
static type of an object-creation receiver, so `new Random().Next()` gets open
dispatch with no target, while `r.Next()` on a `Random` parameter binds
exactly. On a `System.Random` receiver the name can only select a
`System.Random` member or an extension method with the same name.

Near misses: a `Random` kept in a local, `NextInt64`, `Random.Shared.Next()`,
`new SeededRandom().Next()` on a subclass, the upstream
`new Random().Equals(null)`, and in `Local.cs` a source-declared
`Local.Random` with its own `Next`.

## Validation

Bifrost 0.14.2, build identity `073c23790739e33f33abc98338651689eaf8b7c0`,
evaluation date `2026-10-28`, run from this directory with
`BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and `--no-incremental`.
The authored policy hash is
`9bcb83e5ec9fe152b281ee9e94f81bc5df3303e15c23aba1806e616375a6eda1`; its
resolved identity is workspace-required.

The run is complete with eight findings. The five upstream expected rows are
`RandomUsedOnce.cs:13`, `:16`, `:18`, `:19` and `:20` (upstream lines 11, 14,
16, 17 and 18). The three probe positives are `Probe.cs:7` (seeded
constructor), `Probe.cs:12` (`NextBytes(Span<byte>)`) and `Probe.cs:22`
(namespace-qualified `new System.Random()`). There are no other findings.

## Known limits

- Without the model, the qualified constructor locator does not resolve and
  the policy is `not_run` rather than clean.
- A parenthesized receiver, `(new Random()).Next()` at `Probe.cs:17`, is not
  reported, although CodeQL reports it. The call's receiver is the
  parenthesized expression, not the constructor site, so the join fails. The
  run still claims to be complete. The probe keeps the case as
  `KnownMissParenthesized`.
- A source type named `Random` that relies on its implicit default
  constructor leaves `new Random()` unproven, and the run is inconclusive
  (`partial_discovery`). `Local.Random` therefore declares its constructor.
- An extension method named `Next`, `NextBytes` or `NextDouble` on
  `System.Random`, with a signature the instance methods do not take, would be
  reported.

# .NET ProcessStartInfo executable and shell boundary prototype

This is an **unqualified diagnostic prototype** for
[`dotnet-processstartinfo-executable-and-shell-boundary`](../../candidates.md#dotnet-processstartinfo-executable-and-shell-boundary),
the .NET part of [queue item 11](../../qualification-queue.md). It does not
register a security rule, add a reviewed semantic pack, or change scanner
defaults. The outcome is **blocked by the engine** on Bifrost 0.14.2. No part
of the contract can ship as a complete rule, for the reasons below.

## Contract under test

The [`ProcessStartInfo`](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo?view=net-10.0)
`FileName` selects the application or document to start. A positive needs an
untrusted value across an explicit trust boundary to select that executable, or
to reach the command-language operand of a proven interpreter (`cmd.exe /c`,
`/bin/sh -c`). A fixed executable that receives the value as one
[`ArgumentList`](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist?view=net-10.0)
item with no interpreter is the close near miss. Environment variables and
console input are caller-authorized or trusted configuration. A tool chosen
from them is not a violation, so they are not this candidate's source.

The probe model declares the full `Process.Start` family and the
`ProcessStartInfo` constructors and properties from the dotnet/runtime
`release/9.0` reference assembly at
`b0984b273c3b543805fabdfb2aaf65b8c96216fd`. It also declares the
`Environment`, `Console` and `HttpContent` members the probes use as inputs.
It is research-only and must not be copied into `semantic-packs/`.

## Cases and observations

Bifrost 0.14.2 (`073c23790739e33f33abc98338651689eaf8b7c0`). Bifrost 0.14.3
(`a8e935c87ffae45104f08a6baec3abe4e54a4e18`) gives the same completion,
findings and diagnostics for every case. [`outcome.json`](outcome.json) has
the hashes and the diagnostics for each run.

| Case | What it holds | Observation |
| --- | --- | --- |
| `ctor-file-name` | Caller-controlled input reaching `new ProcessStartInfo(string)` directly, through a `var` local and through a helper. Near misses: a literal, a `const` field and a same-named local type | `proven_by_summary`, 3 witness findings (lines 14, 20, 30), no near-miss findings. The constructor binds exactly |
| `typed-local` | The same flow through `string tool = Console.ReadLine()` | Inconclusive: `procedure semantics ... is unknown`. A `var` local works; an explicitly typed local assigned from a call does not |
| `remote-source` | An `HttpContent.ReadAsStringAsync()` body selecting the executable, awaited and through `.Result` | Inconclusive: `async_suspend_resume` is unsupported, and `.Result` is an unknown access path. This is the candidate's real positive, and no source binds |
| `start-overloads` | `Process.Start(string)`, `(string, string)`, `(string, IEnumerable<string>)`, a literal tool and `Start(ProcessStartInfo)` | Inconclusive: no `Start` call binds (`callee_unresolved`, `target_count=0`) |
| `ctor-arguments` | `new ProcessStartInfo(string, string)` and `(string, IEnumerable<string>)` | Inconclusive: `SignatureApplicability` conversion unavailable; every candidate rejected |
| `property-writes` | `info.FileName = ...` through a parameter, a typed local and an object initializer | `file-name-write` probe: inconclusive, `field_write_value requires one precise static member target` and `receiver_site_without_receiver`. Under the call-sink witness the same file is **complete with no findings**: the setter is not a sink at all |
| `argument-list` | Near miss: constant executable, one untrusted `ArgumentList` item, `UseShellExecute = false` | Inconclusive: `access-path resolution ... is unknown` for `info.ArgumentList.Add(...)` and the collection initializer. The safe shape cannot be shown clean |
| `shell-interpreter` | `cmd.exe /c` + input through `Process.Start` and the two-argument constructor, `/bin/sh -c` through `ArgumentList`, `UseShellExecute = true` with an untrusted document | Inconclusive. Only the document case (line 29, a one-argument constructor) is reported. The rest fail on the gates above |

Scratch copies of the model with members removed located the `Process.Start`
blocker (`model_variant_experiments` in `outcome.json`). With only
`Start(string, string)` declared, the call binds and the flow is reported.
Declaring the instance `Start()` next to the static overloads makes every
static `Start` call `callee_unresolved`. Declaring `Start(string, string)` with
`Start(string, IEnumerable<string>)`, or `Start(string)` with
`Start(ProcessStartInfo)`, fails overload conversion for those calls
(`UnsupportedConversion`, `UnsupportedExpression`). This is the same gap as
`WebRequest.Create(String)` vs `Create(Uri)` in
[research/dotnet-cve](../../../dotnet-cve/README.md). A model that drops
overloads to make the calls bind would falsely claim a complete callable
family, so it is not used. A quoted `System.Diagnostics.Process.Start` locator
is also refused as ambiguous once the family mixes `Start()` with static
overloads, so the probes name members by model id.

## Why no rule ships

1. **No trust-boundary source.** The open C# models provide only
   `Environment.GetEnvironmentVariable` and `Console.ReadLine`, which this
   contract treats as trusted. Request sources are blocked: C# action
   parameters (`[FromQuery]`, `[FromBody]`) are not selectable, `HttpRequest`
   access paths stay unknown (see [research/dotnet-cve](../../../dotnet-cve/README.md)),
   and a response body needs `await` or `.Result`.
2. **Most executable sinks do not bind.** `Process.Start(string, ...)` and the
   two-argument constructors fail overload resolution. `FileName` setters and
   object initializers cannot be sinks. A rule built on the one sink that binds,
   `new ProcessStartInfo(string)`, would report a clean run for
   `info.FileName = input`, the most common way to set the executable.
3. **The shell half needs facts the engine does not have.** Proving an
   interpreter needs the constant `fileName` related to the same call's
   argument string. A `resolved-value` filter that rejects every candidate
   marks the run incomplete. The command-language position (`"/c " + input`,
   `"-c"` then the item) needs binary-expression and ordering facts, and C#
   has no comparison facts or program points. `UseShellExecute` state is an
   instance property write, and its default depends on the target framework,
   for which C# has no dependency evidence.
4. **The near miss cannot be proven clean.** Any `ArgumentList` use leaves the
   run incomplete.

## Upstream blockers

| Gate | Issue |
| --- | --- |
| Same-arity overloads and mixed static/instance families fail binding | [bifrost-dev#8296](https://github.com/BrokkAi/bifrost-dev/issues/8296) |
| Explicitly typed locals and `info.ArgumentList.Add(...)` access paths | [bifrost-dev#8299](https://github.com/BrokkAi/bifrost-dev/issues/8299) |
| `resolved-value` that rejects every candidate makes the run inconclusive | [bifrost-dev#8300](https://github.com/BrokkAi/bifrost-dev/issues/8300) |
| No NuGet or target-framework evidence (the `UseShellExecute` default) | [bifrost-dev#8295](https://github.com/BrokkAi/bifrost-dev/issues/8295) |
| Instance property writes and initializers are not sinks | [bifrost-dev#8305](https://github.com/BrokkAi/bifrost-dev/issues/8305) |
| Taint stops at `await` and `.Result` | [bifrost-dev#8306](https://github.com/BrokkAi/bifrost-dev/issues/8306) |
| No request-input source (action parameters, `HttpRequest` reads) | [bifrost-dev#8307](https://github.com/BrokkAi/bifrost-dev/issues/8307) |
| No binary-expression, comparison or program-point facts | [bifrost-dev#8308](https://github.com/BrokkAi/bifrost-dev/issues/8308) |

## Promotion criteria

Requalify when the engine (a) resolves same-arity overloads with different
parameter types and mixed static and instance families, (b) supports instance
property writes and object initializers as sink operands, (c) resolves
`ArgumentList` access paths and explicitly typed locals, and (d) provides at
least one C# request or response source that crosses a trust boundary. The
executable-selection half can then ship as a taint rule over every `fileName`
operand and the `FileName` setter, with this directory's cases as fixtures. The
interpreter half also needs argument-structure facts and target-framework
evidence for `UseShellExecute`.

## Replay

Use the pinned 0.14.2 binary; the `bifrost` on `PATH` may be older. From
`probe/`, for each case directory and policy:

```sh
BIFROST_OPEN_PACKS_DISABLE=1 bifrost --policy --no-builtin-policies --no-incremental \
  --evaluation-date 2026-10-30 --format json \
  --policy-file policies/binding-witness.rqlp --sources ctor-file-name
```

`executable-selection.rqlp` is the policy the candidate would ship, with the
remote source. `binding-witness.rqlp` uses the same sinks with
caller-controlled sources to show which sinks bind. `file-name-write.rqlp`
tests the `FileName` setter. All three are note-severity research probes in
`probe/policies/`, outside `.bifrost/policies`, so nothing runs them by
default. The C# files were not compiled or run.

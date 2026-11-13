# C# lead #167 on Bifrost 0.15.2

Released Bifrost 0.15.2 (build `340cbbdc`) gates C# calls through version-split
model shards activated by restored NuGet evidence, and binds reduced-form calls
to model-declared extension methods. That unblocks the affected-version part of
BrokkAi/bifrost-packs#167 (CVE-2026-96230) as
`bifrost.security.csharp.webassembly-debugging-affected-version`, qualified in
`fixtures/policy/bifrost.security/csharp-webassembly-debugging-affected-version`.

- `genmodels.py` writes `bifrost.dotnet.aspnetcore-hosting-csharp` and
  `bifrost.dotnet.aspnetcore-webassembly-server-csharp` in `semantic-packs/dotnet/`.
- `stub/` builds the marker assembly that stands in for the restored package:
  `dotnet build -c Release -p:AssemblyName=Microsoft.AspNetCore.Components.WebAssembly.Server -o out`.
- `mkfx.py <stub dll>` stages each fixture workspace's restore evidence and
  model copies.

## What binds on 0.15.2

| Receiver | Result |
| --- | --- |
| `IApplicationBuilder` parameter, cast or typed local | exact, resolved |
| explicit `WebAssemblyNetDebugProxyAppBuilderExtensions.UseWebAssemblyDebugging(app)` | exact, resolved (argument conversion `unsupported_conversion`) |
| `WebApplication` parameter or `var app = builder.Build()` in a method | `callee_unresolved` |
| any call in top-level statements (`Program.cs`) | `callee_unresolved` |

The hosting model declares that `WebApplication` implements
`IApplicationBuilder`, but extension lookup doesn't use that edge. Together with
the top-level statement gap this leaves the minimal-hosting template shape
(.NET 6 and later) inconclusive. The rule still reports the
`Startup.Configure(IApplicationBuilder app, ...)` shape. Neither gap is filed
upstream yet.

Not covered: an unguarded `UseWebAssemblyDebugging()` on a fixed release, which
the advisory doesn't affect. That part needs a dominating `IsDevelopment()`
guard and is left for a separate rule.

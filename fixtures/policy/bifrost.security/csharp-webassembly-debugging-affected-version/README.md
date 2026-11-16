# WebAssembly debugging middleware on an affected ASP.NET Core release

Qualifies the affected-version part of BrokkAi/bifrost-packs#167
(CVE-2026-96230, GHSA-qjpx-jqm5-h2c4) as
`bifrost.security.csharp.webassembly-debugging-affected-version`. The rule is a
relational assertion. It reports every `UseWebAssemblyDebugging` call whose
exact binding is to the `affected` shard of
`bifrost.dotnet.aspnetcore-webassembly-server-csharp` 0.1.0. That shard
activates from restored NuGet evidence (`obj/project.assets.json` plus the
package assembly in an approved package folder) for
Microsoft.AspNetCore.Components.WebAssembly.Server 8.0.0 to 8.0.31, 9.0.0 to
9.0.20, 10.0.0 to 10.0.12, or 11.0.0-preview.1 up to 11.0.0-rc.2. The `fixed`
shard declares the same extension method for the fixed side of each line.
`bifrost.dotnet.aspnetcore-hosting-csharp` 0.1.0 declares the hosting types
(`WebApplication`, `WebApplicationBuilder`, `IApplicationBuilder`). The rule is
opt-in.

The advisory affects every call on an affected release, so a call guarded by
`IsDevelopment()` is still reported. Not covered: an unguarded call on a fixed
release, which is outside the advisory.

The package assembly in each `.nuget/packages` folder is a stub built from
`research/dotnet-cve/0152/stub` (one public marker type): Bifrost needs a
restored assembly on disk before it treats the package as activation evidence.
The reviewed model supplies the API. `research/dotnet-cve/0152/mkfx.py` stages
the evidence and model copies.

Each case directory is its own workspace. Run each one separately.

## Cases

- `affected` (8.0.31): `Startup.cs` reports the guarded call in
  `Configure(IApplicationBuilder app, IWebHostEnvironment env)` (line 13), an
  unguarded call (line 19) and the explicit static form (line 24).
- `fixed` (8.0.32): the same `Startup.cs`; the near miss.
- `incomplete/minimal-hosting` (9.0.20): a top-level `Program.cs`
  (`var app = builder.Build(); app.UseWebAssemblyDebugging();`) and a
  `WebApplication` parameter. On Bifrost 0.15.2 calls in top-level statements
  don't bind, and the extension doesn't bind on a `WebApplication` receiver
  even though the hosting model declares that `WebApplication` implements
  `IApplicationBuilder`. Inconclusive, not clean.
- `incomplete/lookalike` (8.0.31): an application type with its own
  `UseWebAssemblyDebugging` method. The call is not reported, but next to the
  stub package import the workspace declaration's compilation membership is
  unproven, so the run is inconclusive.
- `incomplete/unrestored`: no restore output. The package model doesn't
  activate and the run is `not_run`.

## Validation

Bifrost `v0.15.2` (`bifrost-v0.15.2-aarch64-apple-darwin.tar.gz`, archive SHA-256 `58c3745bf0f6be04dbf6e3844fb45747ab60189cfe625eb1ab15ee2228859d00`, binary SHA-256 `f06a8760f4099db712d91dcb0acb406589cd84a66ec3ccacaf4d0d6dbc3952dc`, build identity `340cbbdcea3fc565f6ea8066084ed24962c369d3`), with the `packs/v0.13.0` native bundle (`bifrost.public.packs-0.13.0-native.tar.gz`, SHA-256 `92bc425e60dcc42e05630ff45505aa5bef29abb1090caa10f731cc5a6e4226b4`) as `BIFROST_OPEN_SEMANTIC_PACK_BUNDLE`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off` and a fresh `BIFROST_CACHE_DIR` per run. Evaluation date 2026-11-13. The bundle supplies none of the models these cases use: each case directory carries its own copies in `.bifrost/semantic-models`.

| Case | Completion | Findings |
| --- | --- | --- |
| `affected` | `complete` | 3 definite (`Startup.cs` lines 13, 19, 24) |
| `fixed` | `complete` | 0 |
| `incomplete/minimal-hosting` | `inconclusive (partial_discovery)` | 0 |
| `incomplete/lookalike` | `inconclusive (partial_discovery)` | 0 |
| `incomplete/unrestored` | `not_run` | 0 |

Authored hash `ec07a090217d4a6957c8ab4fc30afe2b34241ea770e8433ad1fa71fa0e739bd5`.

Run from a case directory:

```console
bifrost --root . --policy-file .bifrost/policies/webassembly-debugging-affected-version.rqlp --no-builtin-policies --no-incremental --format json --evaluation-date 2026-11-13
```

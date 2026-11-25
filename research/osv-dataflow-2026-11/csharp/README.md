# C#/.NET OSV data-flow leads on Bifrost 0.15.1

**Outcome: 2 of 10 leads ship as taint rules. The other 8 are blocked by the
engine.** Each lead's theoretical policy is a data-flow policy (taint or
typestate). The leads come from the OSV NuGet export, downloaded 2026-11-05.
Selection rules: only advisories where application code decides reachability;
no native-memory, CMS-app or upgrade-only bugs; no CVE that already has a
`CVE-` title in either pack repository; no API that an existing C# lead
already covers.

Every result was produced with the official `v0.15.1` release
(`bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`, archive SHA-256
`4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`, which
matches the release digest; binary SHA-256
`78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`; build
identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`). Each run used
`BIFROST_OPEN_PACKS_DISABLE=1`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`--no-builtin-policies`, `--no-incremental` and a fresh `BIFROST_CACHE_DIR`.
v0.15.2 was not released at evaluation time. Machine-readable outcomes are in
[`outcomes.json`](outcomes.json).

| Lead | Advisory | Contract | Type | Outcome | Blockers |
| --- | --- | --- | --- | --- | --- |
| [#262](https://github.com/BrokkAi/bifrost-packs/issues/262) | CVE-2020-1147 | External input chooses the XML read by `DataSet`/`DataTable.ReadXml` | taint | **Implemented**: `bifrost.security.csharp.dataset-read-xml-external-location` | Partial: [#8296](https://github.com/BrokkAi/bifrost-dev/issues/8296) (stream overloads), [#8307](https://github.com/BrokkAi/bifrost-dev/issues/8307) (request sources), [#8779](https://github.com/BrokkAi/bifrost-dev/issues/8779) (runtime gate) |
| [#263](https://github.com/BrokkAi/bifrost-packs/issues/263) | CVE-2019-0820 | External input as a `Regex` pattern with no match timeout | taint | **Implemented**: `bifrost.security.csharp.regex-pattern-injection` | Partial: [#9982](https://github.com/BrokkAi/bifrost-dev/issues/9982) (instance methods), [#8299](https://github.com/BrokkAi/bifrost-dev/issues/8299) (typed locals, fields), [#8778](https://github.com/BrokkAi/bifrost-dev/issues/8778) (package gate) |
| [#264](https://github.com/BrokkAi/bifrost-packs/issues/264) | CVE-2026-96958 | Untrusted XML loaded into `SignedXml` on affected versions | taint | Blocked by engine | [#8778](https://github.com/BrokkAi/bifrost-dev/issues/8778), [#8302](https://github.com/BrokkAi/bifrost-dev/issues/8302), [#8307](https://github.com/BrokkAi/bifrost-dev/issues/8307) |
| [#265](https://github.com/BrokkAi/bifrost-packs/issues/265) | CVE-2026-70162 | Untrusted CMS into `EnvelopedCms.Decode` on Windows | taint | Blocked by engine | [#8778](https://github.com/BrokkAi/bifrost-dev/issues/8778), [#8349](https://github.com/BrokkAi/bifrost-dev/issues/8349) |
| [#266](https://github.com/BrokkAi/bifrost-packs/issues/266) | CVE-2023-29331 | Untrusted bytes or paths into the content-sniffing `X509Certificate2` constructors | taint | Blocked by engine | [#8296](https://github.com/BrokkAi/bifrost-dev/issues/8296), [#9981](https://github.com/BrokkAi/bifrost-dev/issues/9981) (new) |
| [#267](https://github.com/BrokkAi/bifrost-packs/issues/267) | CVE-2019-1075 | Request-controlled redirect targets in ASP.NET Core | taint | Blocked by engine | [#8307](https://github.com/BrokkAi/bifrost-dev/issues/8307), [#8779](https://github.com/BrokkAi/bifrost-dev/issues/8779) |
| [#268](https://github.com/BrokkAi/bifrost-packs/issues/268) | CVE-2026-21218 | Decoded COSE message used before verification | typestate | Blocked by engine | [#9498](https://github.com/BrokkAi/bifrost-dev/issues/9498), [#8302](https://github.com/BrokkAi/bifrost-dev/issues/8302), [#8778](https://github.com/BrokkAi/bifrost-dev/issues/8778) |
| [#269](https://github.com/BrokkAi/bifrost-packs/issues/269) | CVE-2026-45491 | Untrusted archive into `TarFile.ExtractToDirectory` on affected runtimes | taint | Blocked by engine | [#8779](https://github.com/BrokkAi/bifrost-dev/issues/8779), [#8307](https://github.com/BrokkAi/bifrost-dev/issues/8307) |
| [premium #457](https://github.com/BrokkAi/bifrost-premium-packs/issues/457) | CVE-2026-75513 | Request values as Marten LINQ dictionary keys | taint | Blocked by engine (premium, not implemented here) | [#8778](https://github.com/BrokkAi/bifrost-dev/issues/8778), [#8307](https://github.com/BrokkAi/bifrost-dev/issues/8307) |
| [premium #458](https://github.com/BrokkAi/bifrost-premium-packs/issues/458) | CVE-2026-55254 | Untrusted NCalc expressions | taint | Blocked by engine (premium, not implemented here) | [#8778](https://github.com/BrokkAi/bifrost-dev/issues/8778), [#8299](https://github.com/BrokkAi/bifrost-dev/issues/8299) |

## Shipped rules

Both rules report the advisory's version-independent part, as the Go gob rule
(#192) does. Neither checks the affected versions. Both use
`:call-modeling (call-modeling :unmodeled require-model)`, so an unmodeled
call on the path leaves the run inconclusive instead of clean. Sources are
`Console.ReadLine` and `Environment.GetEnvironmentVariable` from the reviewed
`bifrost.dotnet.bcl-csharp` 0.4.0 model. C# has no selectable request source
yet (bifrost-dev#8307). Each fixture README lists its cases, runs and known
limits.

- `bifrost.security.csharp.regex-pattern-injection`
  ([fixture](../../../fixtures/policy/bifrost.security/regex-pattern-injection/README.md)).
  It uses the new model `bifrost.dotnet.system-text-regularexpressions-csharp`
  0.1.0. Main fixture: `proven_by_summary`, 9 definite findings, 7 near misses
  unreported. Four incomplete cases stay inconclusive.
- `bifrost.security.csharp.dataset-read-xml-external-location`
  ([fixture](../../../fixtures/policy/bifrost.security/dataset-read-xml-external-location/README.md)).
  It uses the new model `bifrost.dotnet.system-data-csharp` 0.1.0. Main
  fixture: `proven_by_summary`, 3 definite findings, 3 near misses
  unreported. Three incomplete cases stay inconclusive.

Neither model is added to a release recipe. That selection is separate.

## Engine findings

- **Version gates are still blocked by bifrost-dev#8778.** On 0.15.1, NuGet
  `dependency-evidence` returns exact locked and installed rows with
  `declared_by` project digests. But `target-of (file-of ...)` returns no rows
  (`topology_derivation_incomplete`), and `require-both` rejects dependency
  rows. So no C# call site can be tied to the version its project locks. The
  queries are the ones in `research/dotnet-cve/probe/nuget-version-gate`.
  Runtime and shared-framework copies (bifrost-dev#8779) and target platform
  (bifrost-dev#8349) are still missing too.
- **Overload families.** A same-arity family that differs only by parameter
  type doesn't bind (bifrost-dev#8296). A family with one declared member
  binds every call to that member, whatever the argument types
  ([bifrost-dev#9981](https://github.com/BrokkAi/bifrost-dev/issues/9981),
  new, repro `probe/x509-single-overload`). A method name with static and
  instance members makes every static locator ambiguous
  ([bifrost-dev#9982](https://github.com/BrokkAi/bifrost-dev/issues/9982),
  new, repro `probe/regex-static-instance-family`). Constructor families of
  different arity bind correctly.
- **Locals and receivers.** A value flows from a model call through a `var`
  local but not through an explicitly typed local (`string p = Call();`). A
  model instance call binds through a typed local or parameter receiver, but
  not through a `var` local or a field. Evidence was added to
  [bifrost-dev#8299](https://github.com/BrokkAi/bifrost-dev/issues/8299#issuecomment-6659396014).
- **Instance summaries need `covers_overrides`.** Without it, an instance call
  on a non-sealed model type such as `DataSet` has unknown call resolution.
  With it, the call closes.
- **No sink bound means vacuously complete.** A workspace where no sink
  selector matches finishes `complete` with a "zero findings vacuously"
  diagnostic, even when an unmodeled call carries tainted data. That is why
  the Regex model declares the static `Match`, `Matches`, `Split` and
  `Replace` families, and not only `IsMatch`.

The files under `probe/` are research inputs, not registered pack content.

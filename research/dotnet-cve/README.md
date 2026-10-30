# .NET runtime CVE lead qualification

**Outcome: all six leads are blocked by the engine.** This directory records
the qualification of six OSV-derived C# leads against Bifrost 0.14.2. None of
them is promoted to `rules/`. The fixtures, probe policies and probe model here
are research inputs, not registered pack content. They do not change the
locked policy or semantic-pack content.

| Issue | Advisory | Contract | Outcome | Engine blockers beyond version evidence |
| --- | --- | --- | --- | --- |
| [#156](https://github.com/BrokkAi/bifrost-packs/issues/156) | CVE-2024-43483 | Attacker-chosen `IMemoryCache` keys | Blocked by engine | Extension-method calls on `IMemoryCache` don't resolve. C# action parameters can't be selected as sources. |
| [#157](https://github.com/BrokkAi/bifrost-packs/issues/157) | CVE-2024-43484 | Upload stream reaches `Package.Open` | Blocked by engine | Interface source (`IFormFile.OpenReadStream`) stays unproven. `Package.Open(Stream)` vs `Open(String)` overload choice is unsupported. No transitive dependency facts. |
| [#158](https://github.com/BrokkAi/bifrost-packs/issues/158) | CVE-2024-30105 | Request body reaches `DeserializeAsyncEnumerable<T>` | Blocked by engine | No effective-version resolution between package and shared framework. The `HttpRequest.Body` access path stays unknown. |
| [#159](https://github.com/BrokkAi/bifrost-packs/issues/159) | CVE-2024-43485 | Untrusted JSON into a `[JsonExtensionData]` type graph | Blocked by engine | Attributes are name-only. There is no type-graph reachability and no `[FromBody]` source. |
| [#160](https://github.com/BrokkAi/bifrost-packs/issues/160) | CVE-2024-43499 | Untrusted bytes reach `NrbfDecoder.Decode` | Blocked by engine | Interface source stays unproven. The sink binds exactly. |
| [#161](https://github.com/BrokkAi/bifrost-packs/issues/161) | CVE-2023-36049 | Request URI reaches `WebRequest.Create` | Blocked by engine | `Create(String)` vs `Create(Uri)` overload choice is unsupported. No action-parameter source. Scheme guards need comparison facts. |

## Shared blocker: no C# version evidence

Every lead needs the exact NuGet package, shared framework or runtime version
bound to its owning project. Every lead's qualification cases also include a
fixed-version near miss. Bifrost 0.14.2 can't express either:

- `queries/nuget-dependency-evidence.rql` runs over the probe root. Its
  case projects carry `App.csproj` and `packages.lock.json`. The query returns
  no rows and this diagnostic: `CSharp selected dependency publication
  unavailable: static dependency evidence is unavailable for this analyzer`.
- `correlate`'s `dependency-configuration` relation accepts only `npm` and
  `cargo`. Ordinary RQL sets never join code rows with dependency rows.

So a policy can't tell an affected project from a fixed one. Each probe that
reaches its sink also reports the `near-miss-fixed-version` case. Shipping
these as rules would turn every patched project into a false positive. This
violates the leads' own contract: missing version coverage must stay typed
incomplete, not approximated.

## Per-lead evidence

Each probe policy was run on its own lead directory (`--sources <lead>`).
In the combined root, the unrelated source property `Envelope<T>.Body` in
the #159 fixtures stops `HttpRequest.Body` from resolving. The resolver
reports that it `could not prove one unshadowed exact declaration identity`,
and the #158 source then matches nothing. That interference is a separate
engine gap: a same-named source member blocks resolution of a modeled member.

- **#156 MemoryCache.** The probe `156-memorycache-get-or-create.rqlp`
  finds no binding. Every `cache.GetOrCreate(...)` and `cache.Set(...)` call in
  extension form fails with `unsupported_csharp_receiver: receiver for C#
  member GetOrCreate is not resolved`. The interface call `TryGetValue` stays
  unresolved too. A separate probe showed that the static form,
  `CacheExtensions.Set(cache, key, value)`, does bind. Real code doesn't
  write it that way. Neither `[FromQuery]` nor `[FromHeader]` key sources are
  selectable: `(parameter ...)` reports `structural adapter for csharp does not
  support kind(s): parameter`. `near-miss-server-key` holds a constant key and
  a key from a closed enum set. It can't be told apart from a request key
  without a source.
- **#157 Package.Open.** The probe reports `positive` and
  `near-miss-fixed-version` as possible and partial. The `IFormFile.OpenReadStream()`
  source is an interface dispatch with no complete executable target.
  `near-miss-self-created` isn't reported: `Package.Open(MemoryStream,
  FileMode)` fails overload conversion, so the sink selector is incomplete,
  not clean. The `unknown-transitive-openxml` case calls the OpenXML SDK,
  which isn't modeled. Without C# dependency evidence, the engine can't record
  its transitive System.IO.Packaging copy as a dependency fact.
- **#158 DeserializeAsyncEnumerable.** The static generic
  `JsonSerializer.DeserializeAsyncEnumerable<T>(Stream)` binds exactly. The
  probe reports `positive`, `near-miss-fixed-version` and
  `unknown-shared-framework` as possible and partial, with `access-path
  resolution ... is unknown` for `HttpRequest.Body`. The
  `near-miss-other-api` case (`DeserializeAsync`) and the
  `near-miss-local-file` case aren't reported. Package and shared-framework
  copies can't be separated.
- **#159 [JsonExtensionData].** `queries/json-extension-data-attributes.rql`
  finds the attribute on `positive`, `near-miss-fixed-version` and
  `unknown-generic-graph`. It finds it on `near-miss-newtonsoft-attribute`
  too, because the match is by name only. The Newtonsoft
  `JsonExtensionDataAttribute` has the same simple name. The engine has no
  exact attribute type identity. It has no reachability over the type graph
  of a deserialized type (`Envelope<Extras>`). It has no implicit MVC
  `[FromBody]` binding source (`queries/from-body-parameters.rql` reports
  the unsupported `parameter` kind). No probe policy is authored, because
  only a name match would be possible.
- **#160 NrbfDecoder.Decode.** `NrbfDecoder.Decode(Stream, ...)` binds
  exactly once the probe model declares its full overload family. The probe
  reports `positive`, `near-miss-fixed-version` and `unknown-version` as
  possible and partial. The only incomplete step is the interface call
  `IFormFile.OpenReadStream()`. The `near-miss-trusted-bytes` case (a local
  file) and the `near-miss-header-check` case (`StartsWithPayloadHeader`
  only) aren't reported. This is the closest lead to the code-half contract.
  It is still blocked on version evidence.
- **#161 WebRequest.Create.** With both `Create(String)` and `Create(Uri)`
  declared, every call fails overload conversion (`UnsupportedConversion`,
  `UnresolvedSourceType`, `UnsupportedExpression`), so nothing binds. A
  model with only `Create(String)` binds exactly. That model would claim an
  incomplete overload family, so it isn't used. The URI string comes from a
  `[FromQuery]` parameter, which isn't selectable. The
  `near-miss-scheme-allowlist` guard compares `Uri.Scheme` with `!=`, and
  C# comparison facts are unsupported.

## Layout and reproduction

`probe/` is one runnable root. Its `.bifrost/` directory holds the
research-only model `bifrost.research.dotnet-cve-probe`, the enable control
in `packs.json` and five probe policies. Each `probe/<issue>-<slug>/<case>/`
directory is one inert project. Positive and near-miss projects pin their
package with `App.csproj` and `packages.lock.json`. Unknown-version projects
have no package reference, so the assembly comes from the shared framework.
The lock files' `contentHash` values are placeholders. No project was
restored, built or run.

The probe model declares only the members these probes call. It isn't a
reviewed pack and must not be copied into `semantic-packs/`. Where it
declares a full overload family, it sets `callable_family_complete`.
Elsewhere it leaves the flag false.

Run from `probe/` with the exact engine below. The `bifrost` found on `PATH`
may be older.

```sh
BIFROST_OPEN_PACKS_DISABLE=1 bifrost --policy --no-builtin-policies --no-incremental \
  --sources 160-nrbf --policy-file .bifrost/policies/160-nrbf-decode.rqlp
BIFROST_OPEN_PACKS_DISABLE=1 bifrost --root . --query-file queries/nuget-dependency-evidence.rql
```

[`outcomes.json`](outcomes.json) records the engine identity, input hashes and
the observed result of each probe.

## Promotion criteria

A lead can move into `rules/bifrost.security` once the engine publishes C#
static dependency evidence that a policy can join to the owning project of a
call site. Each fixture's fixed-version near miss must then be excluded, and
its unknown-version case must stay typed incomplete. For #157, #160 and #161
the request sources also need complete resolution: interface dispatch on
`IFormFile`, `HttpRequest` access paths and C# action parameters. #156 also
needs extension-method resolution. #159 also needs exact attribute identity
and type-graph reachability.

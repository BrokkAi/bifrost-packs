# .NET CVE leads: NuGet version evidence recheck on Bifrost 0.14.4

**Outcome: no lead ships. All nine rechecked leads stay blocked by the
engine.** Bifrost 0.14.4 publishes NuGet dependency evidence for C#
(bifrost-dev#8295, PR #8358), and its version ranges are correct. But no C#
code row can reach the project that owns a dependency row. So a policy can't
tie a call site to the version that project locks.

Rechecked on 2026-11-01 against the official v0.14.4 release:

- Archive: `bifrost-v0.14.4-universal-apple-darwin.tar.gz`, SHA-256
  `4107616cbd9e9377c7c1c568e9cd2082f5565a4fd9c3e27022a79acd201532ac`
  (matches the release's `.sha256` asset).
- Binary SHA-256
  `a3aa17a18be33e1e841c1bf317c6ca35a6aa3aaef452c607fafbb3b83aeec399`.
- Build identity (`bifrost pack-engine-profile`)
  `ff5cf473f4ad414751911ff93ef79e1df1d35823`.

Fixes for bifrost-dev#8300, #8306 and #8308 are on master but not in 0.14.4.

## Lead outcomes

| Lead | Advisory | Version evidence on 0.14.4 | Outcome | Blockers |
| --- | --- | --- | --- | --- |
| [#152](https://github.com/BrokkAi/bifrost-packs/issues/152) EncryptedXml decryption | CVE-2026-47304 | Package lock: yes. Shared-framework copy: no | Blocked by engine | [#8778](https://github.com/BrokkAi/bifrost-dev/issues/8778) ownership; [#8779](https://github.com/BrokkAi/bifrost-dev/issues/8779) shared framework; no open request-body source; `new EncryptedXml(doc)` receiver ([#8299](https://github.com/BrokkAi/bifrost-dev/issues/8299)) |
| [#153](https://github.com/BrokkAi/bifrost-packs/issues/153) Unbounded EncryptedXml | CVE-2026-26171 | Package lock: yes. Shared-framework copy: no | Blocked by engine | Same as #152 |
| [#155](https://github.com/BrokkAi/bifrost-packs/issues/155) SignedCms.CheckSignature | CVE-2026-84008 | Package lock and assets: yes. In-box copy: no row | Blocked by engine | #8778 ownership; #8779 in-box copy; no proven byte source |
| [#158](https://github.com/BrokkAi/bifrost-packs/issues/158) DeserializeAsyncEnumerable | CVE-2024-30105 | Package lock: yes. Shared-framework copy: no row | Blocked by engine | #8778; #8779; `HttpRequest.Body` access path still unknown ([#8307](https://github.com/BrokkAi/bifrost-dev/issues/8307)) |
| [#160](https://github.com/BrokkAi/bifrost-packs/issues/160) NrbfDecoder.Decode | CVE-2024-43499 | Package lock: yes. Shared-framework copy: no row | Blocked by engine | #8778; `IFormFile.OpenReadStream` still unresolved; #8779 for the unknown-version case |
| [#162](https://github.com/BrokkAi/bifrost-packs/issues/162) LdapConnection on Linux | CVE-2021-41355 | Package lock: yes | Blocked by engine | #8778; Linux target needs [#8349](https://github.com/BrokkAi/bifrost-dev/issues/8349) |
| [#163](https://github.com/BrokkAi/bifrost-packs/issues/163) HttpClient redirects | CVE-2018-8292 | Package only; the in-box handler has no version | Blocked by engine | #8779; #8778; handler property writes ([#8305](https://github.com/BrokkAi/bifrost-dev/issues/8305), [#8303](https://github.com/BrokkAi/bifrost-dev/issues/8303)) |
| [#164](https://github.com/BrokkAi/bifrost-packs/issues/164) Lockout race | CVE-2023-33170 | No: shared-framework servicing releases | Blocked by engine | #8779 |
| [#166](https://github.com/BrokkAi/bifrost-packs/issues/166) Negotiate with LDAP | CVE-2026-47303 | Package lock: yes | Blocked by engine | #8778; `AddNegotiate(o => o.EnableLdap(...))` needs lambda option facts ([#8311](https://github.com/BrokkAi/bifrost-dev/issues/8311)) and extension methods ([#8297](https://github.com/BrokkAi/bifrost-dev/issues/8297)); the vulnerable path is still unconfirmed |

The version gate of the shipped
`bifrost.security.csharp.signedxml-embedded-key-trust` (#154) is blocked by
#8778 in the same way.

Before this recheck, #162 and #166 were expected to need runtime evidence.
Both are package-versioned, and 0.14.4 records their locks. They stay blocked
by ownership and by their own code-half gaps.

## What works: the range gate

`nuget-version-gate/` holds one project per evidence shape. Each has the same
`SignedCms.Decode` then `CheckSignature(true)` call.
`queries/pkcs-affected-locked.rql` selects the CVE-2026-84008 ranges
`[8.0.0,8.0.2) || [9.0.0,9.0.21) || [10.0.0,10.0.13) || [11.0.0-preview.1,11.0.0-rc.2)`
over `:kinds [locked installed]`:

| Case | Evidence | Matches |
| --- | --- | --- |
| `affected-lock` | `packages.lock.json` 9.0.20 | yes |
| `affected-assets` | `obj/project.assets.json` 8.0.1, no lock | yes |
| `prerelease-lock` | lock `11.0.0-rc.1.25451.107` | yes |
| `fixed-lock` | lock 9.0.21 | no |
| `no-lock` | `PackageReference` 9.0.20 only | no row, no diagnostic |
| `inbox-runtime` | no package | no row, no diagnostic |
| `web-implicit` | `Microsoft.NET.Sdk.Web`, not restored | no row, no diagnostic |
| `framework-explicit` | `FrameworkReference Microsoft.AspNetCore.App` | versionless `framework` row |

The same ranges on `160-nrbf` (`(,9.0.0)`) and
`158-deserialize-async-enumerable` (`[7.0.0,8.0.4)`) match the affected
locks and exclude both fixed-version near misses.

## What blocks a sound rule

1. **No code-to-project relation**
   ([bifrost-dev#8778](https://github.com/BrokkAi/bifrost-dev/issues/8778)).
   Dependency rows carry `declared_by`, the owning BuildProject id. Code rows
   have no field that reaches it.
   - `queries/csharp-file-build-target.rql` returns no rows and
     `topology_derivation_incomplete`, because `target-of` reads Maven only.
   - `queries/require-both-dependency.rql` fails to load: `require_both`
     accepts only `configuration_fact` rows.
   - A relational plan can join the two bindings, but no field is shared.

   A rule that reported the call wherever some lock in the workspace matched
   would report the fixed project in a mixed-version solution.
2. **Unknown versions can't be typed per project.** With
   `:kinds [locked installed]`, `no-lock` drops out and the answer is
   complete. Without the kind filter
   (`queries/pkcs-affected-all-kinds.rql`), every project's own `declared`
   row reports `no complete exact version evidence`, including projects whose
   lock matches. With an ownership key, a policy could anti-join declared rows
   against exact rows on `declared_by`.
3. **No runtime or shared-framework version**
   ([bifrost-dev#8779](https://github.com/BrokkAi/bifrost-dev/issues/8779)).
   `Microsoft.NETCore.App` is never a row. An unrestored web project
   publishes no `Microsoft.AspNetCore.App` row. An explicit
   `FrameworkReference` row has no version
   (`queries/aspnetcore-framework-range.rql` reports it as unresolved, which
   is correct). The in-box and shared-framework unknown cases of #152, #153,
   #155, #158 and #160 would answer complete and empty, not incomplete.
4. **Input cap**
   ([bifrost-dev#8780](https://github.com/BrokkAi/bifrost-dev/issues/8780)).
   Past about 36 projects, the answer is truncated and incomplete
   (`dependency input file cap exceeded`). Absent candidate inputs count
   toward the cap, and the diagnostic cites a file that doesn't exist. The
   full `probe/` root, about 40 projects, hits it. Run the queries on
   `nuget-version-gate/` or a lead directory instead.

## Code halves on 0.14.4

The 0.14.2 probe policies were rerun unchanged on their lead directories:

- `160-nrbf-decode.rqlp`: inconclusive (`partial_discovery`). `positive`,
  `near-miss-fixed-version` and `unknown-version` are reported as possible and
  partial. `IFormFile.OpenReadStream` still has neither a resolved target nor
  an applicable complete model. The sink still binds exactly.
- `158-deserialize-async-enumerable.rqlp`: inconclusive
  (`partial_discovery`). Three possible, partial findings, with
  `access-path resolution ... is unknown` for `HttpRequest.Body`.

Even with a version gate, #160 would ship only with the upload case
incomplete, and #158 would not ship at all. No open-pack source for request
bytes binds completely.

## Reproduction

```sh
cd research/dotnet-cve/probe/nuget-version-gate
BIFROST_OPEN_PACKS_DISABLE=1 bifrost --root . --query-file queries/pkcs-affected-locked.rql
cd ../160-nrbf
BIFROST_OPEN_PACKS_DISABLE=1 bifrost --root . --query-file queries/nrbf-affected-locked.rql
cd ..
BIFROST_OPEN_PACKS_DISABLE=1 bifrost --policy --no-builtin-policies --no-incremental \
  --sources 160-nrbf --policy-file .bifrost/policies/160-nrbf-decode.rqlp
```

Use the exact binary above. The `bifrost` on `PATH` may be older.
[`outcomes.json`](outcomes.json) records input hashes and observations under
`rechecks`.

## Promotion criteria

A lead can move into `rules/bifrost.security` when:

- #8778 lands, so the policy can join a call site to its project's
  locked or installed row and type a project with no exact row as incomplete;
- for in-box or shared-framework copies, #8779 lands, or the rule scopes
  itself to package copies and keeps the framework case typed incomplete;
- its source binds completely (`IFormFile`, `HttpRequest`, action parameters).

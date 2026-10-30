# .NET crypto and auth CVE leads: qualification on Bifrost 0.14.2

Leads BrokkAi/bifrost-packs#152–#155 and #162–#167, qualified on 2026-10-30
against Bifrost 0.14.2, build identity
`073c23790739e33f33abc98338651689eaf8b7c0`.

| Lead | Advisory | Outcome |
| --- | --- | --- |
| #152 EncryptedXml decryption of untrusted documents | CVE-2026-47304 | Blocked by engine |
| #153 Unbounded EncryptedXml processing | CVE-2026-26171 | Blocked by engine |
| #154 KeyInfo trust in signature validation | CVE-2026-96222 | Implemented without the version gate: `bifrost.security.csharp.signedxml-embedded-key-trust` |
| #155 SignedCms.CheckSignature over untrusted CMS | CVE-2026-84008 | Blocked by engine |
| #162 Credentialed LdapConnection binds on Linux | CVE-2021-41355 | Blocked by engine |
| #163 Auth data across HttpClient redirects | CVE-2018-8292 | Blocked by engine |
| #164 Lockout race in sign-in | CVE-2023-33170 | Blocked by engine |
| #165 Reset mail sent to the request address | CVE-2026-70175 | Blocked by engine |
| #166 Negotiate with LDAP role resolution | CVE-2026-47303 | Blocked by engine |
| #167 WebAssembly debugging outside development | CVE-2026-96230 | Blocked by engine |

## Shared blocker: no C# version evidence

`(dependency-evidence :ecosystem nuget)` on a project with a `PackageReference`
and a `packages.lock.json` returns no rows and this typed diagnostic:

```
semantic_analysis_partial / incomplete:
dependency evidence Missing at :0..0: CSharp selected dependency publication
unavailable: static dependency evidence is unavailable for this analyzer
```

The 0.14.2 code-query reference lists dependency evidence for Cargo and
JavaScript/TypeScript only. The `dependency-configuration` relation accepts
only `npm` and `cargo`. No C# policy can gate a finding on a NuGet package,
shared framework or runtime version. The "fixed version" near miss of every
lead in this set cannot be expressed.

Seven leads have no weakness apart from the affected version: #152, #153,
#155, #162, #163, #164 and #166. A policy without the version gate would report
correct use of the API on fixed versions, so none is written.

## Per-lead blockers beyond version evidence

- **#152, #153 (EncryptedXml):** the open packs model no ASP.NET Core request
  body or message source. The only public C# source is
  `Environment.GetEnvironmentVariable`. The issue's own positive,
  `new EncryptedXml(doc).DecryptDocument()`, has a `new T().M()` receiver,
  which 0.14.2 does not infer.
- **#154 (KeyInfo trust):** `SignedXml.CheckSignature()` and
  `CheckSignatureReturningKey` verify with the document's own key on every
  version, which is a weakness (CWE-347) without the CVE. The policy reports
  that part. The affected-version claim of CVE-2026-96222 stays blocked.
  Library-mediated validation (WIF, SAML middleware) stays unmodeled.
- **#155 (SignedCms):** same-receiver `Decode` then `CheckSignature` is
  expressible with a receiver join, but the lead is a CPU-cost bug in the
  library. Without the version it reports every CMS signature check.
- **#162 (LdapConnection on Linux):** XML configuration facts can read a
  `RuntimeIdentifier` from a `.csproj`, but the package version (before
  5.0.1) cannot be established.
- **#163 (HttpClient redirects):** the fix is in System.Net.Http 4.3.4 and in
  the in-box handler of supported runtimes. Credentials with
  `AllowAutoRedirect` are not a weakness on fixed versions.
- **#164 (lockout race):** `lockoutOnFailure: true` is the correct call. Only
  the shared-framework version makes it a finding.
- **#165 (reset mail to the request address):** the code contract is
  version-independent, but it is not expressible. The open packs have no
  ASP.NET Core model-binding source (bound `Input.Email` properties). The
  sender is an injected `IEmailSender` field. On 0.14.2 a field receiver makes
  the call binding incomplete, so the realistic positive is inconclusive.
- **#166 (Negotiate with LDAP):** `EnableLdap` is the supported API. Only the
  package version makes it a finding. The issue also requires confirming from
  the fix that LDAP resolution is the vulnerable path. That check was not done.
- **#167 (WebAssembly debugging):** `program-point-of` is unsupported for C#
  (`semantic_capability_unsupported`), so an `IsDevelopment()` guard cannot
  be related to the `UseWebAssemblyDebugging()` call. A lexical
  `not-inside` approximation would treat `if (!env.IsDevelopment())` and
  `else` arms as guarded. The minimal-hosting receiver, `var app =
  builder.Build()`, is a `var` local and does not bind.

## Engine finding: instance calls need a summary

An instance call on a model type, such as `signedXml.CheckSignature()` on a
typed parameter, produces the finding, but without a procedure summary the
run is inconclusive (`call_binding_dispatch_partial`, dispatch outcome
`unproven`). A complete summary with `has_receiver: true`, the exact
`parameter_count` and `covers_overrides: true` gives the engine an authored
selector proof. Typed parameter and typed local receivers then bind
completely. `var` locals and field receivers stay incomplete.

## What would unblock these leads

- NuGet and shared-framework dependency evidence for C# (`dependency-evidence
  :ecosystem nuget`), owned by the project, with the locked or restored
  version: #152, #153, #155, #162, #163, #164, #166, #167, and the version
  gate of #154.
- Receiver type inference for `var` locals, `new T().M()` and fields: #152,
  #153, #165, #167.
- C# program points, so a dominating guard can be tied to a call: #167.
- A reviewed ASP.NET Core model-binding source model: #152, #153, #165.

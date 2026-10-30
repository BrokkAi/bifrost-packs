# C# SignedXml embedded-key trust fixture

Qualifies the version-independent part of lead BrokkAi/bifrost-packs#154
(CVE-2026-96222, GHSA-vrv5-2jg9-4mmr). `SignedXml.CheckSignature()` and
`CheckSignatureReturningKey(out AsymmetricAlgorithm)` verify a signature with
the key from the document's own `KeyInfo`. The policy reports calls that bind
to those two members in the reviewed
`bifrost.dotnet.security-cryptography-xml-csharp` model in
`.bifrost/semantic-models`.

- **Positives** (`Probe.cs`): a typed local built from the posted assertion,
  a `SignedXml` parameter, and `CheckSignatureReturningKey`.
- **Near misses** (`Probe.cs`, `Local.cs`): the pinned-certificate,
  pinned-key and shared-secret `CheckSignature` overloads, and a same-named
  `Local.Signatures.SignedXml` type. The model declares every
  `CheckSignature` overload, so each near miss binds to its own member.
- **Incomplete** (`incomplete/`): a `var` local and a field receiver. This
  workspace runs on its own, and `.bifrostignore` keeps it out of the parent
  run.

## Validation

Bifrost 0.14.2, build identity `073c23790739e33f33abc98338651689eaf8b7c0`,
evaluation date `2026-10-30`, run from this directory and from `incomplete/`
with `BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and
`--no-incremental`. The authored policy hash is
`f16b5ec60628cbca5d31ea10e2003542bba1214e7a9a819ac7b0c8bcfec7ef86`; its
resolved identity is workspace-required.

- This directory: the run is complete with three findings, `Probe.cs:16`,
  `Probe.cs:20` and `Probe.cs:25`. There are no other findings.
- `incomplete/`: the run is inconclusive (`partial_discovery`) with no
  findings. Both calls carry `semantic_analysis_partial` because the receiver
  type is not established.

## Known limits

- The advisory's affected versions are not checked. Bifrost 0.14.2 publishes
  no NuGet or shared-framework dependency evidence for C#, so the "fixed
  version" near miss of the lead cannot be expressed. The policy reports the
  embedded-key check on every version. It is a weakness on every version,
  because the check does not decide whether the key is trusted.
- A `var` local or field receiver makes the run inconclusive rather than
  clean. Expect that on code that keeps `SignedXml` in a field.
- The model's summaries for the two reported members make their instance
  calls bind as complete. Without the model, the qualified locators do not
  resolve and the policy is `not_run`.
- Validation inside a library, such as WIF or SAML middleware, is not
  modeled and is not reported.
- An application that checks the returned key against a trusted set after
  `CheckSignatureReturningKey` is still reported. The engine cannot relate a
  later trust decision to the returned key.

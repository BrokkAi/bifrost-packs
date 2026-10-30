# C# XmlDocument external entity resolution fixture

Qualifies the XmlDocument part of the stdlib candidate
`dotnet-xmlreader-external-dtd-resolution`
(`research/stdlib/candidates.md`). `XmlDocument.Load` and `LoadXml` always
parse a DTD, and they resolve external entities with the document's
`XmlResolver`. The policy reports assignments of a new `XmlUrlResolver` to
`XmlDocument.XmlResolver` that bind to the reviewed
`bifrost.dotnet.system-xml-csharp` model in `.bifrost/semantic-models`.

- **Positives** (`Probe.cs`): a typed local loaded from posted XML, and an
  `XmlDocument` parameter loaded from a request body.
- **Reported, known limit** (`Probe.cs`): a document that loads a bundled
  configuration file. The policy does not establish where the XML comes from.
- **Near misses** (`Probe.cs`): the default resolver, `XmlResolver = null`,
  `XmlReaderSettings` with `DtdProcessing.Prohibit` and an `XmlUrlResolver`,
  `XmlReaderSettings` with `DtdProcessing.Parse` and a null resolver, and an
  `XmlTextReader` with a null resolver. The model declares the
  `XmlReaderSettings` and `XmlTextReader` `XmlResolver` properties, so those
  writes bind to their own members.
- **Incomplete** (`incomplete/`): a `var` local, an object initializer, a
  field receiver, a source subclass of `XmlDocument`, and a same-named
  source `Local.Xml.XmlDocument` type. This workspace runs on its own, and
  `.bifrostignore` keeps it out of the parent run.

## Validation

Bifrost 0.14.2, build identity `073c23790739e33f33abc98338651689eaf8b7c0`,
evaluation date `2026-10-30`, run from this directory and from `incomplete/`
with `BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and
`--no-incremental`. The authored policy hash is
`16800e801cbbf4107aa6a13cf6b6dcd596951abd31f18e8f2966ce057e4a6546`; its
resolved identity is workspace-required. The model is
`bifrost.dotnet.system-xml-csharp` 0.1.0.

- This directory: the run is complete with three findings, `Probe.cs:12`,
  `Probe.cs:20` and `Probe.cs:29`. There are no other findings.
- `incomplete/`: the run is inconclusive (`partial_discovery`) with no
  findings. Each of the five cases was also run alone, and each alone is
  inconclusive. The `var` local, initializer, field and subclass cases carry
  `semantic_analysis_partial` (no exact declaration identity for the
  `XmlResolver` target). The same-named source type carries
  `call_binding_selector_rejected`.
- Without the model, the policy is `not_run`: the
  `System.Xml.XmlDocument.XmlResolver` locator does not resolve.

No Bifrost 0.14.3 build was available for a cross-check.

## Known limits

- Untrusted provenance is not established. The public C# packs have no taint
  source for request XML, so a trusted local file is reported as well.
- The policy reports the configuration, not a load. Bifrost 0.14.2 has no C#
  binding (`binding-of`), points-to or property reaching facts, so the write
  cannot be related to a later `Load` or `LoadXml` on the same instance. A
  document that is only ever loaded through a hardened `XmlReader` is still
  reported.
- Only a new `XmlUrlResolver` is reported. A resolver from a parameter, a
  field, a factory, `XmlSecureResolver` or a custom subclass is not reported,
  because the resolver's behavior is not established.
- `XmlReaderSettings` and `XmlTextReader` are not reported. Reporting them
  needs the `DtdProcessing` state and the resolver of the same settings or
  reader object, and the reader that consumes the settings. None of those
  identities is available for C# on 0.14.2, and the overloaded
  `XmlReader.Create` call does not bind (model signature conversion is
  unavailable). The candidate records this as blocked by the engine.
- Any `XmlResolver` write the engine cannot bind (the incomplete cases above)
  makes the whole run inconclusive, including writes to other types.

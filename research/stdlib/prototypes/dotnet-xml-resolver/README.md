# .NET XML resolver and DTD configuration attempt

Candidate: [dotnet-xmlreader-external-dtd-resolution](../../candidates.md#dotnet-xmlreader-external-dtd-resolution)
(queue item 13). Evaluated on 2026-10-30 with Bifrost 0.14.2, build identity
`073c23790739e33f33abc98338651689eaf8b7c0`, `BIFROST_OPEN_PACKS_DISABLE=1`,
`--no-builtin-policies` and `--no-incremental`, against the reviewed
`bifrost.dotnet.system-xml-csharp` 0.1.0 model.

## Outcome

- **Implemented slice:** `bifrost.security.csharp.xmldocument-url-resolver`.
  It reports `XmlDocument.XmlResolver = new XmlUrlResolver()` when both sides
  bind to the model. XmlDocument always parses DTDs, and the explicit write
  overrides the framework-specific default, so this one assignment is a
  version-independent external-entity configuration. Fixtures and the run
  record are in
  `fixtures/policy/bifrost.security/xmldocument-url-resolver/`.
- **Blocked by the engine:** the candidate's main contract. That contract is
  untrusted XML reaching `XmlReader.Create` with a settings object whose
  effective state is `DtdProcessing.Parse` plus an external-capable resolver,
  and the matching `XmlTextReader` state. No part of it is reported, and no
  text or name match stands in for it.
- **Not established by the slice:** untrusted provenance, a later load on the
  same instance, and the target framework.

## Probes

The probes used a wider draft of the model that also declared
`XmlReader.Create`, `XmlReaderSettings.DtdProcessing`, the `DtdProcessing`
enum and `XmlDocument.Load`. The shipped model keeps only what the rule needs.
All probes used typed locals unless stated. "Exact" means the row bound to
the model member through a qualified locator in a loaded policy.

| Fact needed | Probe | Result on 0.14.2 |
| --- | --- | --- |
| Property target of `settings.DtdProcessing`, `doc.XmlResolver`, `reader.XmlResolver` | `(resolved-value :resolves-to "<Type>.<Property>" :proof exact (field_access ...))` | Exact for typed locals and parameters |
| Enum value `DtdProcessing.Parse` | `resolved-value` on the field access | Exact, with the enum field declared without `value_type` (schema version 2 rejects `value_type`; it needs version 15) |
| `new XmlUrlResolver()` | `resolved-call ... (call-bindings (call-shape (call :callee (name "XmlUrlResolver"))))` | Exact |
| `XmlReader.Create(stream, settings)` with the 12 overloads modeled | `resolved-call :resolves-to "System.Xml.XmlReader.Create"` | Partial: `call_bindings model signature conversion is unavailable: SignatureApplicability` |
| Write value via `field-write-value` | `(field-write-value (member-targets (assignment :left (field_access))))` | Works for source members only; model members give `member_target_analysis` outcome `unknown` |
| Same object across two writes and the `Create` argument | `(binding-of (occurrences ...))` | C# occurrence roles unsupported (`occurrence_role_unsupported`) |
| Same object, by value | `(points-to (field_access ...))` | Outcome `unknown` |
| Write ordered before `Create` or `Load` | `(state-events-of (procedure-of ...))` | `flow_state_axis_unsupported`: property events and property reaching/dominance relations are uncovered |
| Object initializer `new XmlReaderSettings { DtdProcessing = ... }` | `resolved-value` on the initializer member identifier | Partial: `resolver could not prove one unshadowed exact declaration identity` |
| `var` local, field, source subclass receiver | `resolved-value` on the member access | Partial, same diagnostic |
| Same-named source member `Local.Xml.XmlDocument.XmlResolver` | `resolved-value` on the member access | Partial: `call_binding_selector_rejected` |
| Untrusted XML source | Public C# taint sources | Only `Environment.GetEnvironmentVariable`; no request-body or model-binding source |

A typestate policy is not a substitute. Its events are call observations, and
a C# property write with a particular enum value is not one.

## What would unblock the main contract

1. C# object identity between a receiver and a later argument: `binding-of`
   occurrences, points-to, or property reaching relations on a binding base.
2. `XmlReader.Create` overload binding through model signatures.
3. Object-initializer member binding.
4. A public request-XML taint source, or a premium framework source, for the
   provenance proof.

With 1 and 2, the `XmlReaderSettings` part could report
`DtdProcessing.Parse` plus `new XmlUrlResolver()` on the same settings object
that reaches `Create`. The `XmlTextReader` part also needs 1, so that a later
`DtdProcessing.Prohibit` on the same reader is a near miss.

These gaps are recorded here. No engine issue was filed from this attempt.

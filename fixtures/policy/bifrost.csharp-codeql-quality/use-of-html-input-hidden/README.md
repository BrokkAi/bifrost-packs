# C# use-of-html-input-hidden parity fixture

Mirrors CodeQL `csharp/ql/src/Bad Practices/UseOfHtmlInputHidden.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. Upstream has no query test for
this query. `upstream/` keeps the query-help example
`csharp/ql/src/Bad Practices/UseOfHtmlInputHidden.cs` with an MIT attribution
header. The two header lines shift upstream line numbers by two.

The engine contract reports object creations that bind exactly to the
`System.Web.UI.HtmlControls.HtmlInputHidden` constructor in the reviewed
System.Web model in `.bifrost/semantic-models`. The constructor binding
proves the created type is `HtmlInputHidden` itself, as CodeQL's
`ObjectCreation.getType()` requires.

Near misses: a field and a parameter of type `HtmlInputHidden` with no
creation, `typeof(HtmlInputHidden)`, `new AuditedHiddenField()` on a
subclass, and in `Local.cs` a source-declared `Local.HtmlInputHidden`.

## Validation

Bifrost 0.14.2, build identity `073c23790739e33f33abc98338651689eaf8b7c0`,
evaluation date `2026-10-28`, run from this directory with
`BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and `--no-incremental`.
The authored policy hash is
`eb54150fc63fea0f129441c5405ae70b85bc6e7ee49b0371add1d00b1c50384c`; its
resolved identity is workspace-required.

The run is complete with four findings. The upstream example row is
`UseOfHtmlInputHidden.cs:13` (upstream line 11). The three probe positives are
`Probe.cs:10` (object initializer), `Probe.cs:15` (namespace-qualified
creation) and `Probe.cs:20` (creation kept in a `var` local). There are no
other findings.

## Known limits

- Without the model, the qualified constructor locator does not resolve and
  the policy is `not_run` rather than clean.
- A target-typed creation, `HtmlInputHidden field = new();` at `Probe.cs:27`,
  is not reported, although CodeQL reports it. The engine emits no call fact
  for an implicit object creation, so the run still claims to be complete.
  The probe keeps the case as `KnownMissTargetTyped`.
- A source type named `HtmlInputHidden` that relies on its implicit default
  constructor leaves the creation unproven, and the run is inconclusive
  (`partial_discovery`). `Local.HtmlInputHidden` therefore declares its
  constructor.

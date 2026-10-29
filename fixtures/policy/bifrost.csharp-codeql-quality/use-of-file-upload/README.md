# C# use-of-file-upload parity fixture

Mirrors CodeQL `csharp/ql/src/Input Validation/UseOfFileUpload.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. Upstream has no query test for
this query. `upstream/` keeps the query-help example
`csharp/ql/src/Input Validation/UseOfFileUpload.cs` with an MIT attribution
header. The two header lines shift upstream line numbers by two.

The engine contract reports member accesses named `PostedFile` that resolve
exactly to `System.Web.UI.HtmlControls.HtmlInputFile.PostedFile` in the
reviewed System.Web model in `.bifrost/semantic-models`. Accesses are
selected by name first, so other members take no part in the run.

Near misses: `HtmlInputFile.Accept`, `HttpPostedFile.FileName` and
`HtmlInputHidden.Value`.

## Validation

Bifrost 0.14.2, build identity `073c23790739e33f33abc98338651689eaf8b7c0`,
evaluation date `2026-10-28`, run from this directory with
`BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and `--no-incremental`.
The authored policy hash is
`77800689791cd272c00d3928e90952e45e724eef1d60e4955a7615605d1dd36a`; its
resolved identity is workspace-required.

The run is complete with five findings. The upstream example row is
`UseOfFileUpload.cs:14` (upstream line 12), on a typed local. The four probe
positives are `Probe.cs:9` (parameter receiver), `Probe.cs:15` (chained
`.ContentLength`), `Probe.cs:20` (parenthesized cast receiver) and
`Probe.cs:25` (namespace-qualified parameter type). There are no other
findings.

## Known limits

- Without the model, the qualified value locator does not resolve and the
  policy is `not_run` rather than clean.
- The property resolves only on a parameter, a typed local or a cast
  receiver. These `PostedFile` accesses make the run inconclusive
  (`partial_discovery`, `resolved_value rejected every witnessed call-binding
  candidate`) instead of producing a finding:
  - on a field or property of type `HtmlInputFile`, the usual Web Forms
    designer pattern
  - on `new HtmlInputFile()`
  - on a lambda parameter
  - on a receiver whose type is a subclass of `HtmlInputFile` (CodeQL
    reports these)
- A `PostedFile` that resolves to another declaration also makes the run
  inconclusive instead of being a near miss. Examples are a source-declared
  property and a modelled `System.Web.UI.WebControls.FileUpload.PostedFile`.
  `resolved-value` has no proven negative for a member access, so this
  fixture keeps no same-named near miss.

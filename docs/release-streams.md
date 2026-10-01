# Independent public release streams

Public policy rules and semantic packs have separate identities and version
sequences:

| Stream | Manifest pack ID | Release tag |
| --- | --- | --- |
| Policy rules | `bifrost.public.rules` | `rules/vX.Y.Z` |
| Semantic packs | `bifrost.public.packs` | `packs/vX.Y.Z` |

A rules release does not imply a packs release, and matching version numbers do
not imply the contents were qualified together. Legacy releases keep their
existing manifest schema, engine range, and qualification semantics.

## Intended next releases

The intended next semantic-pack release is `packs/v0.2.0`, generated with the
public Bifrost `bifrost-semantic-pack` tool at version `0.12.0`, source commit
`62fc36c09ddb96746e716c1c3456a99957521d91`. The generator pin is provenance
for produced bytes. A prior successful generation run at source commit
`97374bacf203cba1c1c28f5f9da4884f061864e2` produced an archive with native
model schema versions 2 and 5 and release index schema 3. This is diagnostic
evidence, not a fresh `v0.2.0` candidate or a publication claim; inspect the
exact release archive before recording its values. It does not establish
consumer compatibility or behavior.

The intended `rules/v0.1.1` content is the exact 49-policy baseline from public
Bifrost `v0.11.5`, source commit
`4ec4489e850b809c9cc7750e4c450c7560c45de0`. Its actual schema requirements
come from those policies and the built-in catalog: policy-document, RQL, and
built-in-catalog axes. Its 49 policies declare 46 distinct required capability
identifiers. The consumer profile must advertise them; the current engine
profile advertises none, and an engine version does not supply or imply them.
The exact policy documents and required capabilities must be derived from the
pinned 49-policy baseline, not the repository's larger authoring copy. The rules
manifest pins exactly
`bifrost.public.packs` release `0.2.0` from this repository. That dependency
is under review and must resolve to the exact release before the rules stream can
be selected or published.

These are intended release identities, not claims that either tag or artifact
has been published. The v2 release manifest describes schemas and capabilities
without an engine-version range. It records integrity and behavior separately;
format compatibility does not prove full behavior. The native pack artifact
currently still carries per-pack `compatibility.bifrost` gates. The generated
Java pack declares `=0.12.0`; the other packs declare version ranges that also
cap at `<1.0.0`. Native catalog and runtime validation enforce that field, so a
version-independent native release cannot be published honestly until the
native schema and runtime are migrated. Publication must stay blocked while that
gate remains. The engine profile also currently advertises no capabilities, so
it cannot satisfy policies that declare required capabilities.

The native gate is reproducible at public Bifrost commit
`62fc36c09ddb96746e716c1c3456a99957521d91`: `crates/bifrost-analysis/src/analyzer/semantic_model/model.rs:1172` requires the legacy compatibility field, and the catalog and runtime enforce it at `catalog/mod.rs:5210, 5318` and `runtime.rs:3290`. The generated Java pack's `=0.12.0` value rejects other engine versions; the other ranges are still engine-version gates, not format compatibility. See the [recorded blocker evidence](native-publication-blocker.json) for all eight constraints, the prior run identity, and artifact hash.

## Legacy baseline

The legacy `rules/v0.1.0` stream contains the exact 49 policies (four native
catalogs) from public Bifrost `v0.11.5`, commit
`4ec4489e850b809c9cc7750e4c450c7560c45de0`. The repository's larger policy
copy remains available for authoring. The legacy `packs/v0.1.0` archive is the
upstream `bifrost-semantic-packs-v0.11.5.tar.gz` (SHA-256
`d16f94892ddd01cf9e1a2e77f4bda48fe09720f9b3bab7d1b41efd6413ebb3b1).
It preserves authored pack versions, generated production versions, and
`partial` completeness. Its release metadata uses the exact legacy engine range
`>=0.11.5, <0.11.6` and legacy qualification rules. Those values and semantics
remain unchanged for v1 manifests.

For new pack artifacts, `semantic_model_read` and `release_index` are the
relevant release-schema axes; the manifest records the exact values found in the
generated content when known. Do not fill in unknown future schema values from
the generator version. Per-content completeness remains explicit, including
`partial`.

The existing release baseline pins source commits, policy files, and the native
archive checksum. Release-building verifies those inputs and archive contents.
Manual dispatch stages raw generation evidence. A stream tag can publish only
after the native schema/runtime gate and exact dependency pass; current tag
publication fails closed.

See [the shared contract](../release-contract/README.md) for schema 1 and 2
selection semantics, and [generation](generation.md) for the generator pin,
integrity evidence, and behavioral limits.

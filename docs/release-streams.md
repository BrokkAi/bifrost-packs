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

The intended next semantic-pack release is `packs/v0.2.0`, generated with
public Bifrost tooling version `0.13.0` at source
`948f6700d2e668ee830aa42abf7ed4151d5bf560`. The source archive, lockfile,
Rust toolchain and build receipt are pinned in `native-generation.json`.
Generator identity does not prove consumer compatibility or behavior. Inspect
actual schemas in the exact generated archive. The seven generation-spec
corrections and reviewed ordinary Python baseline imports carry per-entry
`source_revision` provenance in `content-lock.json`. Newer schema-14 authoring
models are excluded from this schema-8 native recipe.

The intended `rules/v0.1.2` content is the exact 49-policy baseline from public
Bifrost `v0.11.5`, source commit
`4ec4489e850b809c9cc7750e4c450c7560c45de0`. Its actual schema requirements
come from those policies and the built-in catalog: policy-document, RQL, and
built-in-catalog axes. Its 49 policies declare 46 distinct required capability
identifiers. The exact consumer profile must advertise them. The earlier 0.12.0 profile
advertised none; an engine version does not supply or imply capabilities.
The exact policy documents and required capabilities must be derived from the
pinned 49-policy baseline, not the repository's larger authoring copy. The rules
manifest pins exactly
`bifrost.public.packs` release `0.2.0` from this repository. That dependency
is under review and must resolve to the exact release before the rules stream can
be selected or published.

These are intended release identities, not claims that either tag or artifact
has been published. The v2 release manifest describes schemas and capabilities
without an engine-version range. It records integrity and behavior separately;
format compatibility does not prove full behavior. The pinned schema-8 producer/reader migration removes engine-version gates
from newly generated native content. The specs now use that contract; legacy
native artifacts retain their original gates. The publication guard still
rejects any inner `bifrost` or `engine` gate. A fresh generation receipt and
exact-archive inspection are required before claiming eligibility. The
[historical blocker evidence](native-publication-blocker.json) remains attributed
to the earlier public 0.12.0 generator and its eight gated descriptors.

Concurrent legacy releases `rules/v0.1.1` and `packs/v0.1.1` were published
from `28babf267ce4602549588082d5801d78ba549edf`. They retain contract schema 1,
engine range `>=0.12.0, <0.12.1`, and pending qualification. Their manifests and
assets remain immutable. The rules `0.1.2` candidate deliberately retains the
49-policy baseline scope described here; it does not absorb the concurrent
branch's larger Bifrost 0.12 policy update.

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

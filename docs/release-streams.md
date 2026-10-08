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

See [release versioning](release-versioning.md) for the independent stream bump
rules and compatibility boundaries.

## Intended next releases

These pending plans predate the versioning policy; reassess candidate versions
and dependency pins together against all included changes before tagging.

The published `packs/v0.2.0` release contains 8 native model entries using
schema 8 from public
Bifrost tooling version `0.13.0` at source
`948f6700d2e668ee830aa42abf7ed4151d5bf560`. The source archive, lockfile,
Rust toolchain and build receipt are pinned in `native-generation.json`.
Its source archive pins the authored inputs present at commit
`8711584116169d94475cc8dd4a18caebd5a9e8e4`; it does not contain the later Go,
Rust, Python, or expanded typeshed additions. Its native integrity is separate
from consumer behavior, which remains pending;
inspect actual schemas in the exact archive. The intended next semantic-pack
release is `packs/v0.2.1`, using the same pinned schema-8 recipe unless a
separately audited recipe change is made. The selected generation-spec
corrections and reviewed ordinary Python baseline imports carry per-entry
`source_revision` provenance in `content-lock.json`. Newer schema-14 authoring
models are excluded from this schema-8 native recipe. The `packs/v0.2.1`
source archive carries the newly authored Go embed declarations, the expanded
Python typeshed import closure used by the selected Python native input, and
Rust and Python standard-library models. The Go, Rust, and other Python models
remain outside the existing native recipe; all newly authored models remain
subject to separate consumer qualification.

The published `rules/v0.1.3` release contains 105 unique rules across 8 policy
packs and 113 content entries, with limited behavior evidence from its narrow
smoke. The intended next `rules/v0.1.4` content is the current locked
authoring copy. The current inventory contains 170 unique rules across 11
policy packs: 65 additional rules comprising 19 Java quality rules, 34 Python
quality rules, 10 Python security rules, and 2 Rust rules. The release descriptor derives its exact policy
inventory and required capability identifiers from the checked-in manifests. The source archive carries the checked-in
policy files, focused smoke fixtures, and tracked research evidence. Research
files are archive metadata and are not entries in `content-lock.json` or the
release policy inventory. The rules manifest pins exactly
`bifrost.public.packs` release `0.2.1` from this repository. That dependency
is under review and must resolve to the exact release before the rules stream can
be selected or published.

Source-byte integrity and consumer qualification remain separate. The release
records the locked policy bytes and required capabilities, while a consumer must
prove that its exact build supports those capabilities and then qualify behavior.
The focused dynamic-evaluation smoke uses the published Bifrost `v0.12.0`
Linux binary, verifies its release sidecar checksum, and records one positive and
one realistic near-miss. It is limited evidence for that policy and does not
qualify the full released policy set.

The `packs/v0.2.1` and `rules/v0.1.4` entries above are intended release
identities, not claims that either tag or artifact has been published. The v2 release manifest describes schemas and capabilities
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
assets remain immutable. The `rules/v0.1.3` release remains the historical
105-rule, 113-content stream; the `rules/v0.1.4` candidate publishes the
current locked policy authoring copy while preserving those immutable legacy
artifacts.

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

The existing release baseline remains available for historical baseline builds and
continues to pin source commits, policy files, and the native archive checksum.
The current rules stream is selected from `content-lock.json`; release-building
verifies its locked bytes and archive contents. Manual dispatch stages raw
generation evidence. A stream tag can publish after the exact dependency and
verified-integrity checks; schema-2 behavior may remain pending or limited.
Consumer capability and behavior proof remains required before default
selection or a consumer cutover.

See [the shared contract](../release-contract/README.md) for schema 1 and 2
selection semantics, and [generation](generation.md) for the generator pin,
integrity evidence, and behavioral limits.

Smoke evidence is also retained in `smoke-evidence.zip`, including exact zero-byte logs that GitHub cannot accept as standalone release assets. The ZIP has stable member ordering, timestamps, and permissions. The `rules/v0.1.2` publication attempt passed packaging and dependency verification but failed uploading an empty log; it has no published release.

# Independent public release streams

Public policy rules and semantic packs have separate identities and version
sequences:

| Stream | Manifest pack ID | Release tag |
| --- | --- | --- |
| Policy rules | `bifrost.public.rules` | `rules/vX.Y.Z` |
| Semantic packs | `bifrost.public.packs` | `packs/vX.Y.Z` |

Each stream advances on its own schedule. A rules release does not require a
packs release, and matching version numbers do not imply that the contents were
qualified together. Existing legacy pack IDs keep the `vX.Y.Z` tag form.

Each source archive contains the selected stream's locked content and a filtered
`content-lock.json`. The lock is checked against the extracted archive, so its
file list and aggregate hash describe that stream's bytes. The rules archive
excludes semantic-pack content; the packs archive excludes policy-rule content.
Common release metadata may be present in both archives.

Stream tags establish release identity and source commit only. Source artifacts
remain pending until the relevant engine and semantic-model qualification has
been completed with recorded evidence. Pending bundles can support review and
reproduction, but do not establish runtime compatibility or enable scanning.

An initial native artifact may reuse a verified Bifrost-published bundle if the
primary release flow supplies it. The release must preserve the published
bundle's provenance and verify its bytes before indexing it. If that verified
input is unavailable, native qualification remains pending; a source archive or
a matching version number does not substitute for it.

The initial `rules/v0.1.0` release contains the exact 49 policies (four native
catalogs) from public Bifrost `v0.11.5`, commit
`4ec4489e850b809c9cc7750e4c450c7560c45de0`. The repository's 70-policy copy
remains available for future authoring releases; it is newer than that baseline.
The initial `packs/v0.1.0` archive is byte-for-byte the upstream
`bifrost-semantic-packs-v0.11.5.tar.gz` (SHA-256
`d16f94892ddd01cf9e1a2e77f4bda48fe09720f9b3bab7d1b41efd6413ebb3b1`).
Its seven authored pack versions and generated production versions are preserved,
including `partial` completeness. It uses the native Bifrost format.

`release-baseline.json` pins the public engine commit, each rules file, and the
native archive checksum. `scripts/build-release.py` checks those inputs, the
native checksum inventory, manifest descriptors, and shard payloads before
creating release metadata. It never executes downloaded source. The workflow
runs twice and compares outputs before publishing. Manual dispatch stages only;
publishing requires a stream tag. Future authoring releases can remove the
`baseline` key from the selected component config to bundle that component's
current locked source.

Rules metadata pins `bifrost.public.packs` release `0.1.0` independently of the
rules version. Discovery resolves the exact dependency with the same engine
profile and verifies its artifacts; missing, incompatible, corrupt, or cyclic
dependencies fail closed. Cross-repository dependencies require explicit
discovery and are currently refused. The initial engine bound is narrowly
`>=0.11.5, <0.11.6`; this is a baseline bound, not a claim of full qualification.
Use `--allow-unqualified` explicitly for download/reproduction of these initial
releases. Default selection still refuses pending releases.

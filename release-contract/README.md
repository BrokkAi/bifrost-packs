# Shared pack release contract v2

This directory defines the release metadata and selection contract shared by
public and private pack repositories. Schema 2 is the current contract for new
releases. Schema 1 remains available for immutable historical manifests.

## Compatibility and qualification

Schema 2 compatibility declares required schema versions and semantic
capabilities. The schema axes are policy document, RQL, built-in catalog,
premium policy bundle, semantic-model read/write, semantic spec, release index,
and runtime. Each release declares only the axes its included content actually
uses; an empty axis means no requirement. The selector checks those declarations
against the consumer profile and checks each content item's requirements against
the release aggregate. It also resolves exact release dependencies by pack ID,
release version, and repository. Engine-version bounds are not part of schema 2
compatibility.

Qualification keeps byte integrity separate from behavior:

- `integrity.status` is `pending`, `verified`, or `failed`.
- `behavior.status` is `pending`, `limited`, `qualified`, or `failed`.

Default schema 2 selection requires verified integrity and behavior that has not
failed. Pending or limited behavior does not make a format-incompatible release
compatible, and compatible formats do not prove full behavior or completeness.
`--allow-unqualified` permits pending integrity for reproduction; it never
permits failed integrity or failed behavior. It does not change schema,
capability, channel, pin, or dependency checks. Preserve partial completeness
and typed incomplete outcomes in any scan result.

Optional provenance may record engine version, build identity, and source
commit. `provenance.testing` records measured test engine identities separately
from generation/origin provenance, retaining original source commits. Those
fields document how evidence was collected; engine version never
gates schema 2 acceptance and must not be used to invent missing capabilities.

Schema 1 releases retain their original single qualification field and exact
engine-range behavior. Keep their manifests and interpretations unchanged; do
not convert them to schema 2 or infer new evidence for them.

## Artifacts and selection

Each GitHub release contains `pack-release.json`, its source, native, or policy
artifact, and SHA-256 sidecars. Archive names use
`<pack-id>-<independent-semver>-<role>.<format>`. Public source archives include
`content-lock.json`; premium policy archives retain `policy-bundle.json`.
Native `index.json` and model schemas remain separate from release metadata.
Source archives are review and reproduction inputs; they are not native
installable bundles.

Selection validates every candidate, checks the declared schemas and actual
required capabilities, applies channel and exact pins, and resolves exact
dependencies before selecting the newest eligible release. It verifies all
selected artifact bytes before writing a receipt containing the exact release,
source commit, manifest hash, dependency identities, and artifact hashes. Resolve
once per scan and retain that receipt throughout the scan. An empty finding set
under incomplete coverage is not a clean result.

`discover.py` enumerates GitHub release pages rather than relying on GitHub's
latest pointer. It checks repository, tag-to-commit binding, manifest identity,
and artifact hashes. Online private discovery needs authenticated `gh` access.
Offline selection uses cached manifests and hash-addressed artifacts. Refresh is
explicit.

For the premium repository, pin one immutable public commit and verify hashes for
the schema 2 `manifest.schema.json`, the legacy `manifest.v1.schema.json`, and
the shared reader/selector and discovery code from that same commit. Keep the
full commit and hashes in the premium repository's `release-config.json`; never
fetch a moving branch or maintain an independently edited schema copy. A contract update requires an
explicit pin and renewed validation.

The published `packs/v0.2.0` release uses the schema-8 native model contract;
its behavior qualification remains pending. The new public streams described in
[release streams](../docs/release-streams.md) are intended artifacts, not
evidence of publication. Native release publication runs the current
version-independent schema-2 guard against the actual archive and exact
dependency manifests; see [generation](../docs/generation.md) and the
[v0.13 transition](../docs/v013-transition.md).

New publication also runs `publication.py` against the actual archive bytes and
verified exact dependency manifests. The publication guard rejects an archive
with remaining inner `compatibility.bifrost` or `engine` declarations; the
published schema-8 `packs/v0.2.0` artifact is the current live baseline. The
[recorded reproduction](../docs/native-publication-blocker.json) preserves the
earlier pre-schema-8 blocker and does not classify other generation or
publication failures. Manual and pull-request native
workflows generate and stage the candidate `pack-release.json`, native archive,
sidecars, and raw generation evidence without creating a published GitHub
release. Rules smoke runs attach checksum-indexed inputs, raw reports and
executable identity with `behavior.status = limited`; release notes are
generated from the manifest's actual requirements.

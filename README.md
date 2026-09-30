# Bifrost packs

Public policies and native semantic-pack content for
[Bifrost](https://github.com/BrokkAi/bifrost), copied from reviewed public paths at
canonical source `aa291b97e55e48efc931ea89a16068404c3aad3e`.

This is an additive copy. Bifrost still owns its existing built-in selection and
release artifacts. v0.13.0 is the intended future consumer transition; it has
not been implemented or qualified here. Pack versions are independent of engine
versions.

- `rules/`: four built-in policy packs, with unchanged IDs, authored/resolved
  semantic hashes, queries and endpoint documents.
- `semantic-packs/`: authored source/specifications/notices, `models/` inputs,
  and `embedded/` native manifests/shards. Preserve completeness and safety fields.
- `fixtures/`: reviewed public policy and upstream semantic fixtures.
- `scripts/upstream/`: byte-identical engine-bound generation/install recipes;
  consult [generation instructions](docs/generation.md) before running them.
- `content-lock.json`: exact source path, classification, license and byte hashes.
- `release-contract/`: shared public/premium release metadata and selection tools.

Verify and create a reproducible **source** archive offline:

```sh
python3 scripts/content.py verify
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/content.py bundle --output /tmp/bifrost-packs-source.tar.gz
```

The source archive includes mixed-license fixtures. It is not the native
`bifrost-semantic-packs` install bundle and must not be passed to its installer.
No runtime download, scanner enablement or engine default change happens here.
Compatibility declarations are separate from exact-build behavior qualification;
see [validation](validation.json) and [transition sequencing](docs/v013-transition.md).

Read [NOTICE.md](NOTICE.md) and preserved per-source notices. Apache-2.0 applies
to Brokk public material; third-party licenses and exceptions remain in force.

Public releases use separate `rules/vX.Y.Z` and `packs/vX.Y.Z` tags. The initial
streams match the public Bifrost `v0.11.5` release, while the newer content stored
here remains available for authoring. See [release streams](docs/release-streams.md)
for baseline provenance, exact dependencies, packaging, and qualification limits.

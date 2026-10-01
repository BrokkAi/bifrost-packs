# Bifrost packs

Public policy and native semantic-pack content for
[Bifrost](https://github.com/BrokkAi/bifrost), copied from reviewed public paths
at canonical source `aa291b97e55e48efc931ea89a16068404c3aad3e`.

This is an additive copy. Bifrost still owns its existing built-in selection and
release artifacts. A future v0.13.0 consumer transition is not implemented or
qualified here. Pack versions are independent of engine versions.

- `rules/`: four built-in policy packs, with unchanged IDs, authored/resolved
  semantic hashes, queries, and endpoint documents.
- `semantic-packs/`: authored source/specifications/notices, `models/`
  inputs, and `embedded/` native manifests/shards. Preserve completeness and
  safety fields.
- `fixtures/`: reviewed public policy and upstream semantic fixtures.
- `scripts/upstream/`: byte-identical engine-bound generation/install recipes;
  read [generation instructions](docs/generation.md) before running them.
- `content-lock.json`: exact source path, classification, license, and byte
  hashes.
- `release-contract/`: shared public/premium release metadata and selection
  tools.
- [`research/stdlib/`](research/stdlib/README.md): source-linked stdlib taint and
  typestate hypotheses, ownership routing and a proposed qualification queue.
  These are research leads, not enabled or qualified rules.

Verify and create a reproducible **source** archive offline:

```sh
python3 scripts/content.py verify
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/content.py bundle --output /tmp/bifrost-packs-source.tar.gz
```

The source archive includes mixed-license fixtures. It is not the native
`bifrost-semantic-packs` install bundle and must not be passed to its
installer. No runtime download, scanner enablement, or engine default change
happens here. Compatibility declarations are separate from exact-build
behavior evidence; see [validation](validation.json) and
[transition sequencing](docs/v013-transition.md).

New release manifests use contract schema 2: they match declared schema axes,
actual required capabilities, and exact release dependencies without an engine
version bound. Integrity and behavior qualification remain separate, and
partial completeness remains explicit. Legacy schema 1 releases retain their
existing engine-range and qualification semantics. See the
[shared release contract](release-contract/README.md).

The intended next public streams are `packs/v0.2.0` and `rules/v0.1.2`;
neither is a publication claim. The native archive still contains enforced
engine-version compatibility fields, so the native schema/runtime migration
must finish before a version-independent native release can be published. See
the [recorded publication blocker](docs/native-publication-blocker.json), which
identifies the prior diagnostic run and native source gates. The rules release pins the exact `packs/v0.2.0` dependency and remains contingent
on that release. See [release streams](docs/release-streams.md) for the exact
baseline and current gates, and [generation](docs/generation.md) for the pinned
generator and behavioral evidence limits.

For the standalone LSP engine/content tuple, use the
[qualification and handoff procedure](docs/standalone-qualification.md).

Read [NOTICE.md](NOTICE.md) and preserved per-source notices. Apache-2.0 applies
to Brokk public material; third-party licenses and exceptions remain in force.

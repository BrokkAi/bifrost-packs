# Bifrost packs

Public policy and native semantic-pack content for
[Bifrost](https://github.com/BrokkAi/bifrost), copied from reviewed public paths
at canonical source `aa291b97e55e48efc931ea89a16068404c3aad3e`.

This is an additive copy. Bifrost still owns its existing built-in selection and
release artifacts. A future v0.13.0 consumer transition is not implemented or
qualified here. Pack versions are independent of engine versions.

- `rules/`: public policy packs, with unchanged IDs, authored/resolved
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

## Rule inventory

<!-- rule-stats:start -->
**91 unique rules across 7 policy packs.**

| Breakdown | Value | Rules |
| --- | --- | ---: |
| Pack | bifrost.c-jpl | 4 |
| Pack | bifrost.code-smells | 31 |
| Pack | bifrost.correctness | 1 |
| Pack | bifrost.cpp-jsf | 14 |
| Pack | bifrost.cpp-power-of-10 | 2 |
| Pack | bifrost.effects | 10 |
| Pack | bifrost.security | 29 |
| Category | correctness | 42 |
| Category | effects | 10 |
| Category | performance | 10 |
| Category | security | 29 |
| Severity | error | 37 |
| Severity | note | 18 |
| Severity | warning | 36 |

Languages are explicit manifest declarations; a rule may appear in multiple rows.
13 declared languages; 191 rule-language pairs.

| Manifest supported language | Rules |
| --- | ---: |
| c | 3 |
| cpp | 23 |
| csharp | 9 |
| go | 12 |
| java | 28 |
| javascript | 24 |
| kotlin | 10 |
| php | 6 |
| python | 28 |
| ruby | 4 |
| rust | 16 |
| scala | 4 |
| typescript | 24 |

Activation labels: opt-in 26, unspecified 65. Omitted labels remain unspecified.
Metadata is an inventory, not evidence of enablement or behavior qualification.
[Full rule catalog](docs/rule-catalog.md).
<!-- rule-stats:end -->

Regenerate with `python3 tools/rule_stats.py --write`. The
[inventory guide](docs/rule-stats.md) covers JSON export and the optional
pre-commit hook; CI checks the generated tables for drift.

## Source verification

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

The next public streams are `packs/v0.2.0` and `rules/v0.1.2`. The pinned
public schema-8 producer removes native engine-version gates while retaining
legacy compatibility. The [recorded blocker](docs/native-publication-blocker.json)
describes historical generator output. New publication verifies the actual
archive and exact dependency: rules pin `bifrost.public.packs@0.2.0`.
The packs release also carries a source archive of current authored inputs and
research; models outside the native recipe remain reproduction inputs with
pending consumer qualification. The rules release packages the current locked
policy inventory. Research probes remain research and are not enabled policies.
See [release streams](docs/release-streams.md) and
[generation](docs/generation.md) for exact pins and behavioral evidence limits.

For the standalone LSP engine/content tuple, use the
[qualification and handoff procedure](docs/standalone-qualification.md).

Read [NOTICE.md](NOTICE.md) and preserved per-source notices. Apache-2.0 applies
to Brokk public material; third-party licenses and exceptions remain in force.

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
- [Release versioning](docs/release-versioning.md): independent stream bump
  rules and compatibility boundaries.
- [`research/stdlib/`](research/stdlib/README.md): source-linked stdlib taint and
  typestate hypotheses, ownership routing and a proposed qualification queue.
  These are research leads, not enabled or qualified rules.

## Rule inventory

<!-- rule-stats:start -->
**170 unique rules across 11 policy packs.**

| Breakdown | Value | Rules |
| --- | --- | ---: |
| Pack | bifrost.c-jpl | 4 |
| Pack | bifrost.code-smells | 31 |
| Pack | bifrost.correctness | 1 |
| Pack | bifrost.cpp-jsf | 14 |
| Pack | bifrost.cpp-power-of-10 | 2 |
| Pack | bifrost.csharp-codeql-quality | 9 |
| Pack | bifrost.effects | 10 |
| Pack | bifrost.java-codeql-quality | 19 |
| Pack | bifrost.python-codeql-quality | 34 |
| Pack | bifrost.rust-codeql-quality | 1 |
| Pack | bifrost.security | 45 |
| Category | correctness | 69 |
| Category | effects | 10 |
| Category | performance | 10 |
| Category | quality | 36 |
| Category | security | 45 |
| Severity | error | 55 |
| Severity | note | 20 |
| Severity | warning | 95 |

Languages are explicit manifest declarations; a rule may appear in multiple rows.
13 declared languages; 352 rule-language pairs.

| Manifest supported language | Rules |
| --- | ---: |
| c | 14 |
| cpp | 34 |
| csharp | 29 |
| go | 18 |
| java | 47 |
| javascript | 25 |
| kotlin | 14 |
| php | 15 |
| python | 74 |
| ruby | 15 |
| rust | 28 |
| scala | 14 |
| typescript | 25 |

Activation labels: opt-in 26, unspecified 144. Omitted labels remain unspecified.
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
python3 scripts/content.py bundle --output ./bifrost-packs-source.tar.gz
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

The next public streams are `packs/v0.2.1` and `rules/v0.1.4`. The published
`packs/v0.2.0` release contains 8 native model entries using schema 8, with
behavior qualification pending. Its source archive pins the authored inputs
present at commit `8711584116169d94475cc8dd4a18caebd5a9e8e4`; later Go, Rust,
Python, and expanded typeshed additions belong to the next source archive. The
pinned schema-8 producer removes native engine-version gates while
retaining legacy compatibility. The [recorded blocker](docs/native-publication-blocker.json)
describes historical generator output. New publication verifies the actual
archive and exact dependency: the intended rules release pins
`bifrost.public.packs@0.2.1`.
The version choices recorded below predate this policy. Preserve already
published releases; reassess unpublished candidate versions and dependency pins
together against all included changes before tagging.
The next packs source archive carries the newly authored Go embed declarations,
the expanded Python typeshed import closure used by the selected Python native
input, and Rust and Python standard-library models. The Go, Rust, and other
Python models remain outside the existing native recipe with pending consumer
qualification. The intended
rules release packages the current locked policy inventory. The published
`rules/v0.1.3` release remains the historical 105-rule, 113-content stream
across 8 policy packs with limited narrow-smoke evidence. Research probes
remain research and are not enabled policies.
See [release streams](docs/release-streams.md) and
[generation](docs/generation.md) for exact pins and behavioral evidence limits.

For the standalone LSP engine/content tuple, use the
[qualification and handoff procedure](docs/standalone-qualification.md).

Read [NOTICE.md](NOTICE.md) and preserved per-source notices. Apache-2.0 applies
to Brokk public material; third-party licenses and exceptions remain in force.

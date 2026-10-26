# Bifrost packs

Public policy and native semantic-pack content for
[Bifrost](https://github.com/BrokkAi/bifrost), initially copied from reviewed public paths
at canonical source `aa291b97e55e48efc931ea89a16068404c3aad3e`.

Product rules are delivered in external packs; the engine's built-in product
rule catalog is empty. Pack versions are independent of engine versions.

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
**239 unique rules across 12 policy packs.**

| Breakdown | Value | Rules |
| --- | --- | ---: |
| Pack | bifrost.c-jpl | 4 |
| Pack | bifrost.code-smells | 37 |
| Pack | bifrost.correctness | 1 |
| Pack | bifrost.cpp-jsf | 14 |
| Pack | bifrost.cpp-power-of-10 | 2 |
| Pack | bifrost.csharp-codeql-quality | 9 |
| Pack | bifrost.effects | 12 |
| Pack | bifrost.java-codeql-quality | 20 |
| Pack | bifrost.javascript-codeql-quality | 12 |
| Pack | bifrost.python-codeql-quality | 82 |
| Pack | bifrost.rust-codeql-quality | 1 |
| Pack | bifrost.security | 45 |
| Category | correctness | 109 |
| Category | effects | 12 |
| Category | maintainability | 5 |
| Category | performance | 10 |
| Category | quality | 56 |
| Category | security | 47 |
| Severity | error | 72 |
| Severity | note | 21 |
| Severity | warning | 146 |

Languages are explicit manifest declarations; a rule may appear in multiple rows.
13 declared languages; 477 rule-language pairs.

| Manifest supported language | Rules |
| --- | ---: |
| c | 19 |
| cpp | 39 |
| csharp | 33 |
| go | 20 |
| java | 52 |
| javascript | 42 |
| kotlin | 17 |
| php | 20 |
| python | 128 |
| ruby | 20 |
| rust | 32 |
| scala | 17 |
| typescript | 38 |

Activation labels: opt-in 46, unspecified 193. Omitted labels remain unspecified.
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

Published `packs/v0.6.0`, `rules/v0.5.0`, `packs/v0.5.0`, `rules/v0.4.0`,
`packs/v0.4.0`, `rules/v0.3.1`, `packs/v0.3.0` and `rules/v0.2.1` remain
immutable. The proposed `rules/v0.5.1` patch replaces synonym capability names
with the canonical names engines advertise and corrects the arity of
`bifrost.cpp-jsf.av-rule-159` (see [release streams](docs/release-streams.md)).
`packs/v0.6.0` added the reviewed
`bifrost.python-performance-summaries` model to the native recipe, and
`rules/v0.5.0` made its Python performance arms read that model's declared
effects and its selected-boundary effects policies import their declaration
selection. The native pack stream carries eight reviewed direct result-use
model families, two Go standard-library `os` model outputs (procedure result
contracts and declarations), the generated `bifrost.php-builtin` declaration
pack from the existing pinned PHP specification, and the Python performance
summaries. The existing PHP pack notes record an earlier partial output with
852 rejects/warnings; local generations with the selected 0.14.0 generator
reported 854. The CI generation report remains the release record and must
stay explicit. No full PHP runtime coverage is claimed; see the
[PHP pack notes](semantic-packs/php/README.md). The generated bundle also
retains its schema-8 and schema-17 content. Both rules releases keep every
policy ID and depend exactly on `bifrost.public.packs@0.6.0`. Integrity, compatibility, completeness and
consumer behavior remain separate qualification requirements; this preparation
does not authorize a tag or publication.
Historical `packs/v0.2.1` and `rules/v0.1.4` also remain immutable. The published
`packs/v0.2.0` release contains 8 native model entries using schema 8, with
behavior qualification pending. Its source archive pins the authored inputs
present at commit `8711584116169d94475cc8dd4a18caebd5a9e8e4`; later Go, Rust,
Python, and expanded typeshed additions belong to the next source archive. The
pinned schema-8 producer removes native engine-version gates while
retaining legacy compatibility. The [recorded blocker](docs/native-publication-blocker.json)
describes historical generator output. New publication verifies the actual
archive and exact dependency: the intended rules release pins
`bifrost.public.packs@0.6.0`.
The Python performance summaries job is the native addition in the proposed
pack successor.
The full generated bundle and all model and policy bytes remain retained in this
source preparation. Other source-only catalog content still requires separate
consumer qualification.

For the standalone LSP engine/content tuple, use the
[qualification and handoff procedure](docs/standalone-qualification.md).

Read [NOTICE.md](NOTICE.md) and preserved per-source notices. Apache-2.0 applies
to Brokk public material; third-party licenses and exceptions remain in force.

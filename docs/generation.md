# Generation and qualification

Public semantic-pack sources and generation recipes are authored in this
repository. Bifrost owns the compiler, installer, catalog and activation code.
The engine copy remains for existing embedded sources and focused fixtures;
new public content belongs here. Storing authoring content does not select it
for a release or enable it in a scanner.

## Pinned native candidate

The published `packs/v0.3.0` and `rules/v0.2.1` releases remain immutable.
The current rule-content baseline is `rules/v0.3.0`; the proposed `rules/v0.3.1`
is a patch and dependency successor.
The proposed next `packs/v0.4.0` recipe builds the public
`bifrost-semantic-pack` producer version `0.13.1` from the generator-only
preparation source
`8c64332281245b6ea3bfae343645f78d0faf2d23` with Rust `1.97.1`.
`native-generation.json` pins the source archive SHA-256, Cargo.lock SHA-256,
source revision and toolchain. The build receipt records the actual executable
SHA-256. These are generator provenance; this public source has not thereby
become a qualified or published engine release.

The plan contains ten direct jobs: eight reviewed result-use models and the
Go standard-library `os` procedure result-contract and declarations models. It
retains five recipes: four existing native recipes plus the existing pinned PHP
builtin recipe. That recipe builds `bifrost.php-builtin` from
`semantic-packs/php/phpstorm-stubs-2026.8.29.json`, pinned to phpstorm-stubs
revision `748ab87d16253a5b5d648b5fe4dae1ff4152bb03` and its recorded source-set
digest. It is distinct from the PHP result-use model among the eight direct jobs.
The source specification and model bytes are unchanged. The existing PHP pack
notes describe a prior partial output with 852 rejects (warnings) for the pinned
source set. The selected 0.13.1 generator has not run this recipe here, so that count is
historical; the current generation report
remains unverified and must stay explicit. This bounded declaration slice does
not claim complete PHP runtime coverage. See the
[PHP pack notes](../semantic-packs/php/README.md). The successor also preserves
the full generated bundle, including schema-8 and schema-16 content. Generation,
integrity, compatibility and consumer behavior remain separate outcomes, and
behavior qualification remains pending.

The refreshed producer retains Scala declarations whose repeated parameters
span multiple parameter lists, but withholds the unrepresentable executable
signature and its flows. The native artifact retains a scoped warning and
partial completeness. Successful generation and schema compatibility do not
turn that bounded result into complete analysis.

The eight reviewed result-use specs and two Go `os` specs use the
version-independent schema-8 native compatibility shape and retain their
activation, artifact, toolchain, target, configuration and provenance pins. The
Go migration changes only each model schema label from 2 to 8 and removes its
`compatibility.bifrost` predicate; all shard payload bytes, toolchains, IDs,
provenance, completeness and BSD-3-Clause licensing remain intact. The two Go
models are explicit direct jobs, not recipe outputs or copied embedded assets.
This source preparation does not establish a generated candidate. The producer
and reader enforce compatibility by actual schemas; legacy artifacts keep their
original engine gates. Models outside the selected jobs remain retained in the
source catalog and require separate producer and consumer qualification when
used. Never lower a schema label or remove fields to fit this release.

The earlier public `62fc36c09ddb96746e716c1c3456a99957521d91` generation
produced model schemas 2 and 5 with engine gates. The historical
[native publication blocker](native-publication-blocker.json) describes those
bytes; it is not evidence about the new candidate. Inspect the exact new archive
before claiming its actual schemas or version-independent eligibility.

Run from a clean committed pack checkout with the exact source-built executable:

```sh
python3 -B release-contract/native_generation.py --root . \
  --config native-generation.json --binary /absolute/path/bifrost-semantic-pack \
  --build-receipt /absolute/scratch/generator-build.json --output /absolute/scratch/native
python3 -B release-contract/native_release.py --root . \
  --config release-config.packs.json --version 0.4.0 \
  --archive /absolute/scratch/native/native.tar.gz \
  --receipt /absolute/scratch/native/generation.json --output /absolute/scratch/dist
```

Every language is generated in two fresh scratch roots. Partial and merged
bundles are verified, and native content must match between runs.
`measurements.json` records observed timing data and is excluded from content
comparison. Both original measurement records are retained; timings are not
rewritten and the full archives are not claimed to reproduce byte for byte.
`generation.json` binds the exact pack source commit, configuration, executable,
input plan and archive. Metadata binds that receipt and the archive.

CI caches the producer by source archive, lock and toolchain pins. It also caches
upstream inputs by the recipe/specification hashes; every reused input must pass
its own pinned checksum. `SEMANTIC_PACK_SOURCE_CACHE` provides the same verified
input reuse locally. It does not permit network-free consumer acceptance to rely
on the generator's source cache. Consumer offline reuse has its own selected
release receipt and isolated runtime cache.

Generation, byte integrity, format compatibility and consumer behavior are
separate outcomes. The current narrow Python dynamic-evaluation smoke does not
qualify the historical 49-policy baseline, the current rule inventory, or a complete
cross-language pack set. Preserve `partial`, unsupported and incomplete results.
Empty findings with incomplete coverage cannot become a clean result.

Manual dispatch stages generation evidence. A stream tag still invokes
`native_release.py` and the fail-closed publication guard, which reject remaining
inner engine gates. A successful integrity run does not authorize a tag or
publication. The release contract permits pending behavior with verified integrity;
engine/library witnesses and live external-content/offline Docker acceptance
remain required before claiming a qualified consumer tuple or default cutover.
The pack prerequisite may retain pending behavior after its exact archive,
receipt, checksum and dependency guards pass; this does not authorize engine
default activation or its final proof gates.

The authored unittest assertion input retains its upstream CPython v3.13.5
provenance and notice. Its engine-version keys were removed from both the
selected authored model and its generation spec for the native migration. The
authored model uses schema 8, whose compatibility shape supports this omission; the
spec pins the exact bifrost-packs artifact commit and SHA-256. Assertion shards,
toolchain requirements and activation conditions are unchanged. Historical
embedded and published payloads retain their original compatibility metadata.

The reviewed TypeScript String input separates its four ES5 methods from
`trimStart` and `trimEnd`, whose TypeScript 7.0.2 declarations are in
`lib/lib.es2019.string.d.ts`. The full ES2019 selection includes ES5 and
activates all six summaries and their declarations; ES5 alone activates only
the four ES5 methods. The direct generation measurement selects ES2019 and
queries all six methods. This source correction still requires fresh native
generation and engine behavior qualification.

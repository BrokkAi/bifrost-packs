# Generation and qualification

Public semantic-pack sources and generation recipes are authored in this
repository. Bifrost owns the compiler, installer, catalog and activation code.
The engine copy remains for existing embedded sources and focused fixtures;
new public content belongs here. Storing authoring content does not select it
for a release or enable it in a scanner.

## Pinned native candidate

The published `packs/v0.3.0` and `rules/v0.2.1` releases remain immutable.
The proposed next `packs/v0.4.0` recipe builds the public
`bifrost-semantic-pack` producer version `0.13.1` from the generator-only
preparation source
`76d1e16c5ad68b5b2918e3206aecbeeb359dfbb2` with Rust `1.97.1`.
`native-generation.json` pins the source archive SHA-256, Cargo.lock SHA-256,
source revision and toolchain. The build receipt records the actual executable
SHA-256. These are generator provenance; this public source has not thereby
become a qualified or published engine release.

The plan contains eight reviewed direct result-use jobs and four existing
recipes. The successor preserves the full generated bundle, including schema-8
and schema-16 content, and this preparation does not rewrite model or policy
bytes. Generation, integrity, compatibility and consumer behavior remain
separate outcomes.

The refreshed producer retains Scala declarations whose repeated parameters
span multiple parameter lists, but withholds the unrepresentable executable
signature and its flows. The native artifact retains a scoped warning and
partial completeness. Successful generation and schema compatibility do not
turn that bounded result into complete analysis.

The eight selected specifications use the version-independent schema-8 native
compatibility shape and retain their activation, artifact, toolchain, target,
configuration and provenance pins. The producer and reader enforce
compatibility by actual schemas; legacy artifacts keep their original engine
gates. Models outside the selected jobs remain retained in the source catalog
and require separate producer and consumer qualification when used.
Never lower its schema label or remove fields to fit this release.

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

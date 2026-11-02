# Generation and qualification

Public semantic-pack sources and generation recipes are authored in this
repository. Bifrost owns the compiler, installer, catalog and activation code.
The engine copy remains for existing embedded sources and focused fixtures;
new public content belongs here. Storing authoring content does not select it
for a release or enable it in a scanner.

## Legacy built-in packs

The prepared `packs/v0.8.0` adds 36 direct jobs after the twelve of
`packs/v0.7.0`, one for each public pack that Bifrost's legacy embedded
registry (`BIFROST_EMBEDDED_PACKS`) provides and the 0.7.0 bundle did not
ship (bifrost-dev#4438). These are the Go standard-library, concurrency and
testify packs, the Node `child_process` and Buffer packs, and the Python
os-command, security-sink and stdlib-api packs. Their authored models move
from schema 2 or 4 to the version-independent schema 8 by removing
`compatibility.bifrost`, as the Go `os` models did; shard payloads,
identities, provenance, licenses and completeness are unchanged. Each spec
names one or more representative lookups taken from the model's own
declarations or summaries, and pins the artifact URL to the migration commit.

The published `packs/v0.8.0` keeps six built-in packs source-only: Lombok,
Getset, Scala case-class, Python process-inputs and the two Node runtime-values
packs. They carry only `rules` or `runtime_values` records. Their jobs, added
after 0.8.0, use the `rule` and `runtime_exposure` measurement lookups from
bifrost-dev#8324, which still require each lookup to resolve at least one
record. They need the Bifrost 0.15.0 generator pin below and its release index
schema 4, so they ship in the next packs release, not in 0.8.0.

The 13 Go declaration models among those jobs mark every function and
method member `callable_family_complete` (#213). Go has no overloading, so a
declared package function, or a method on its receiver type, is its whole
callable family. Without the flag, Bifrost 0.15.0 refuses a `resolved-call`
to `net.Dial`, `os.Open` or `sync.Mutex.Lock` as
`qualified-call-locator-partial`. Each pack takes a minor version, and its
spec pins the commit that made the change. Pack completeness stays
`partial`, because the packages are not fully enumerated. Fields, receivers,
identities and provenance are unchanged. The schema-2 errgroup and embed
declaration models are not jobs and are left as they were.

## Previous native packaging repair

The published `packs/v0.7.0` keeps the generator, the twelve direct jobs and the
five recipes of `packs/v0.6.1`. Only the `python-performance-summaries` input
changes: its model is 1.1.0 and activates on `cpython >=3.10.0, <3.15.0`. The
companion rules 0.7.0 updates the exact packs dependency. The published 0.6.1
plan is described in the [release repair plan](result-use-native-release.md).

## Bifrost 0.15.0 generator and authoring pin

After `packs/v0.8.0` and `rules/v0.8.0`, `native-generation.json` pins public
Bifrost 0.15.0 source `fc4a2da2b78c938e811c496b3c21e5b02f415048` (archive
SHA-256 `7b89b11d272921e6078408014d90d79a7fea51112698173a1bcc8760618b7dcf`,
Cargo.lock SHA-256
`03cc61929856fc31be6619ce69f5c8ffa28de074a185b69414158e7c5b624dab`, Rust
`1.99.1`). The same pin builds the native producer and the policy authoring CLI
that checks every locked policy identity. Producers from 0.15.0 can write
release index schema 4 (bifrost-dev#8336), so `native_generation.py` and
`native_release.py` accept index schema 3 or 4 and each content declares the
index schema its bundle actually has. Engines that read only schema 3 skip a
schema-4 release during selection. The released v0.15.0 CLI reproduced all 254
locked authoring identities unchanged. The published 0.8.0 releases stay
immutable and keep the 0.14.0 generator they were built with.

## Pinned native candidate

The published `packs/v0.6.0`, `rules/v0.5.0`, `packs/v0.5.0`, `rules/v0.4.0`,
`packs/v0.4.0`, `rules/v0.3.1`, `packs/v0.3.0` and `rules/v0.2.1` releases
remain immutable. `packs/v0.6.0` keeps the 0.5.0 jobs and recipes and adds the
authored `bifrost.python-performance-summaries` job; `rules/v0.5.0` and the
proposed `rules/v0.5.1` depend on it.
The proposed next `packs/v0.6.0` recipe builds the public
`bifrost-semantic-pack` producer version `0.14.0` from public source
`c11a13ffa03ebea154f587b899954e412b5b871e`, the projection of the Bifrost
v0.14.0 release candidate, with Rust `1.99.1`.
`native-generation.json` pins the source archive SHA-256, Cargo.lock SHA-256,
source revision and toolchain. The build receipt records the actual executable
SHA-256. These are generator provenance; this public source has not thereby
become a qualified or published engine release.

The plan contains eleven direct jobs: eight reviewed result-use models, the
Go standard-library `os` procedure result-contract and declarations models, and
the reviewed Python performance summaries. It
retains five recipes: four existing native recipes plus the existing pinned PHP
builtin recipe. That recipe builds `bifrost.php-builtin` from
`semantic-packs/php/phpstorm-stubs-2026.8.29.json`, pinned to phpstorm-stubs
revision `748ab87d16253a5b5d648b5fe4dae1ff4152bb03` and its recorded source-set
digest. It is distinct from the PHP result-use model among the eight direct jobs.
The source specification and model bytes are unchanged. The existing PHP pack
notes describe a prior partial output with 852 rejects (warnings) for the pinned
source set. A local two-run generation with the selected 0.14.0 generator
produced a partial `bifrost.php-builtin` with 854 rejects, the same count as the
published `packs/v0.4.0` and `packs/v0.5.0`; the CI generation report remains the release record
and must stay explicit. This bounded declaration slice does
not claim complete PHP runtime coverage. See the
[PHP pack notes](../semantic-packs/php/README.md). The successor also preserves
the full generated bundle, including schema-8 and schema-17 content. Generation,
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
  --config release-config.packs.json --version 0.6.0 \
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
its own pinned checksum, so a pull request may start from main's latest input set
when its own hashes differ. Pushes to main save both caches, since a pull request
can restore only what its own merge ref or main saved. `SEMANTIC_PACK_SOURCE_CACHE` provides the same verified
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

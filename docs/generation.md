# Generation and qualification

Public semantic-pack sources and generation recipes are authored in this
repository. Bifrost owns the compiler, installer, catalog and activation code.
The engine copy remains for existing embedded sources and focused fixtures;
new public content belongs here. Storing authoring content does not select it
for a release or enable it in a scanner.

## Legacy built-in packs

The published `packs/v0.8.0` added 36 direct jobs after the twelve of
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

The published `packs/v0.8.0` kept six built-in packs source-only: Lombok,
Getset, Scala case-class, Python process-inputs and the two Node runtime-values
packs. They carry only `rules` or `runtime_values` records. Their jobs, added
after 0.8.0, use the `rule` and `runtime_exposure` measurement lookups from
bifrost-dev#8324, which still require each lookup to resolve at least one
record. They need the Bifrost 0.15.0 generator pin below and its release index
schema 4. The published `packs/v0.9.0` ships them, built by the released
0.15.0 producer binary. Its bundle index lists 62 packs, including all 46
`pack_id` values under `crates/bifrost-semantic-packs/embedded/` on
bifrost-dev master, and records no rejects for the six.

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

## Go gob jobs and net interface summaries

Two authored jobs follow the legacy set: `go-stdlib-encoding-gob-declarations`
and `go-stdlib-encoding-gob` (`bifrost.go.stdlib.encoding-gob-declarations` and
`bifrost.go.stdlib.encoding-gob`, both 0.1.0, BSD-3-Clause, go1.26.0
provenance). They declare `NewDecoder`, `NewEncoder`, `Register`,
`RegisterName` and the pointer-receiver `Decoder` and `Encoder` methods, each a
complete callable family. The summaries cover the same calls except
`Decoder.Decode` and `Decoder.DecodeValue`.
`bifrost.go.stdlib.net` moves to 2.1.0. It adds complete summaries for the
`net.Conn` and `net.Listener` members other than `Read` and `Write`, and those
summaries claim `covers_overrides`. On Bifrost 0.15.1 a call through a
model-declared interface closes only through such a summary (bifrost-dev#9053).
The specs pin commit `3745e66f03f8599337aa2d72b58c43611414d37e`, except the
gob summaries spec, which pins `9849718fe0945d4c77011b28616b8f3ad375ba05`.
`tests/test_go_gob_native_jobs.py` pins the jobs. The policy
`bifrost.security.go.gob-decode-network-input` depends on all four Go net and
gob packs.

The semantic-model schema has no transfer output for a write through a pointer
argument. A complete `Decode` summary with no transfers would claim that
decoding writes nothing into its argument, so `Decode` and `DecodeValue` stay
unmodeled. A `require-model` policy that sees a decode is therefore
inconclusive. A summary pack's `complete` envelope covers the summaries it
contains: Bifrost rejects complete summaries in a partial envelope
(`summary.completeness_exceeds_pack`).

## Go gzip and io jobs

Four authored jobs follow the gob jobs: `go-stdlib-compress-gzip`,
`go-stdlib-compress-gzip-declarations`, `go-stdlib-io` and
`go-stdlib-io-declarations` (`bifrost.go.stdlib.compress-gzip`,
`bifrost.go.stdlib.compress-gzip-declarations`, `bifrost.go.stdlib.io` and
`bifrost.go.stdlib.io-declarations`, all 0.1.0, BSD-3-Clause, go1.26.0
provenance). They declare `gzip.NewReader`, `Reader.Close`,
`Reader.Multistream`, `io.ReadAll`, `io.Copy` and `io.LimitReader`, each a
complete callable family. The summaries cover the same calls except `io.Copy`,
whose write into `dst` the schema cannot express, as with gob `Decode`. The
specs pin commit `65b68f55b537ab77b7ecd8569b0c838aac9be0ea`.
`tests/test_go_read_all_native_jobs.py` pins the jobs. The policy
`bifrost.security.go.network-read-all-unbounded` depends on the Go net, gzip
and io packs. The io declarations pack does not yet declare the `io.Reader`
family of interfaces that #209 asks for.

## Previous native packaging repair

The published `packs/v0.7.0` keeps the generator, the twelve direct jobs and the
five recipes of `packs/v0.6.1`. Only the `python-performance-summaries` input
changes: its model is 1.1.0 and activates on `cpython >=3.10.0, <3.15.0`. The
companion rules 0.7.0 updates the exact packs dependency. The published 0.6.1
plan is described in the [release repair plan](result-use-native-release.md).

## Bifrost 0.15.0 generator and authoring pin

After `packs/v0.8.0` and `rules/v0.8.0`, the generator moves to Bifrost
0.15.0, and CI uses its released binaries instead of compiling them, which took
up to an hour per job. `native-generation.json` pins the prebuilt producer
`bifrost-semantic-pack-v0.15.0-x86_64-unknown-linux-gnu.tar.gz` from the
`v0.15.0` release of public commit `fc4a2da2b78c938e811c496b3c21e5b02f415048`
(archive SHA-256
`825294fb3ddda0c97c44c222b544b451818f04dd11817dcd79069d1c856bac79`, executable
SHA-256 `d6c19acdcbf37d495e4c0b3f7490746e6235da3522aba5deba4c78f904312031`).
Without `build` metadata, `native_generation.py` treats it as prebuilt: it
checks the executable hash and takes no build receipt. `policy-authoring.json`
separately pins the released `bifrost` CLI that checks every locked policy
identity, with the build identity it reports
(`09a2503c5f7ced1630a9e3c445ead53dfc5925e8`). `native_generation.py` still accepts a source-built
configuration with `build` metadata and a build receipt, but CI no longer
compiles one, so the producer build cache (`native_generator_cache.py`) is
removed. Producers from 0.15.0 can write
release index schema 4 (bifrost-dev#8336), so `native_generation.py` and
`native_release.py` accept index schema 3 or 4 and each content declares the
index schema its bundle actually has. Engines that read only schema 3 skip a
schema-4 release during selection. The released v0.15.0 CLI reproduced all 254
locked authoring identities unchanged. The published 0.8.0 releases stay
immutable and keep the 0.14.0 generator they were built with.

After `packs/v0.9.0`, both pins move to the v0.15.1 release (public commit
`04fdd17d2606d13a7a5f13b012bfbe3ad9729d1e`). The producer is
`bifrost-semantic-pack-v0.15.1-x86_64-unknown-linux-gnu.tar.gz` (archive
SHA-256 `8989298644bda041997308823122f904291a22010d93359ed3580053aa052f8e`,
executable SHA-256
`7322cdbd653830aaba349c9a278eceb97573965739b2845412a3074080b6acc2`). The
authoring CLI reports build identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`.
The released v0.15.1 CLI reproduced all 264 locked authoring identities
unchanged. Its pack-engine profile advertises the same capability names as
0.15.0. The published `packs/v0.9.0` keeps the 0.15.0 producer it was built
with.

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

# Generation and qualification

The native installer/catalog tool `bifrost-semantic-pack` stays with Bifrost.
This repository owns copied data, manifests, specifications, source pins and
recipes. Engine tooling, activation/catalog implementation and compiler semantics
are not duplicated here. `semantic-packs/embedded/` contains native compiled
artifacts, while the top-level specifications are inputs, not installable shards.

`scripts/upstream/` preserves upstream recipes byte for byte. Some recipes invoke
Cargo, read engine source for catalog schema, or depend on engine checkout paths.
Do not run them blindly from this repository. Use a disposable engine checkout at
`aa291b97e55e48efc931ea89a16068404c3aad3e`, overlay the locked data into the original
paths listed in content-lock.json, and run the recipe from that checkout. Alternatively
provide an exact, trusted `BIFROST_SEMANTIC_PACK_BIN` for recipes supporting it.
The PHP builder still requires the engine checkout. Inputs use pinned hashes;
network is explicit during generation and can be replaced by verified cached inputs.
Source packaging CI does not execute the recipes; the native generation workflow does.

For behavioral qualification beyond native generation: generate against the exact recorded
engine build, retain upstream input hashes, run the native tool's `verify`, then
record each generated manifest/shard hash and catalog installation result. Repeat
the build with the same inputs and compare bytes before claiming reproducibility.
Run the offline installation acceptance recipe with a disposable scratch directory
and Linux Docker image already available locally; it removes its scratch path.
Its positive, constant, overload and unrelated-same-name cases remain preserved
inside the script. Record all four typed outcomes and model provenance.

Private root engine suites and the private semantic authoring suite are not copied.
Their historical existence does not qualify this copy. The small public fixtures
and integrity checks establish copying/packaging properties; broad engine behavior
qualification remains separate. Empty findings with incomplete coverage remain
unreliable. CSMI interoperability epic #3668 remains open and is not addressed by
moving native data.

## Repository-owned native generation

`Generate native packs` runs the JVM, Python, TypeScript and Rust recipes from
this repository. It builds the exact public generator source declared in
`native-generation.json`, verifies the source archive and Cargo lockfile checksums,
and records the compiler and executable hash before executing it. A prebuilt tool
can instead be configured with an exact executable checksum. Private engine
implementation is not imported.
`workflow_dispatch` stages reviewable artifacts; `packs/vX.Y.Z` publishes the
result only after generation and verification succeed. Rules retain their separate
release workflow. The existing `packs/v0.1.0` baseline remains immutable.

For a source-built executable and its build receipt, use:

```sh
python3 -B release-contract/native_generation.py --root . \
  --config native-generation.json --binary /absolute/path/bifrost-semantic-pack \
  --build-receipt /absolute/scratch/generator-build.json --output /absolute/scratch/native
python3 -B release-contract/native_release.py --root . \
  --config release-config.packs.json --version 0.2.0 \
  --archive /absolute/scratch/native/native.tar.gz \
  --receipt /absolute/scratch/native/generation.json --output /absolute/scratch/dist
```

Run from a clean, committed checkout. The generator pin identifies the tool that
produced the bytes; `release-config.packs.json` independently declares consumer
engine bounds. Pack release versions, generator versions and consumer versions
need not match. A 0.12 generator can produce content intended for 0.13 consumers
when it emits the required schemas and capabilities. New format or compiler
requirements can require a newer generator. Consumer selection still checks the
actual consumer profile and the declared requirements; generation alone does not
qualify behavior against a future engine. Current consumer bounds are preserved. The v0.12 public source pin is required
for the current JDK activation specification; the released v0.11.5 generator
rejects that specification. This is a generator capability requirement, separate
from consumer compatibility.

Every language is generated in two fresh scratch roots, each partial bundle is
verified, and the merged bundles are verified. Native content must match between
runs. `measurements.json` contains observed timing data, so its bytes are excluded
from the content comparison. Both original measurement records are retained;
timings are not rewritten and the full archives are not claimed to reproduce
byte for byte. Packaging uses deterministic archive metadata and preserves the
first run's measurements. `generation.json` binds the source commit, generation
configuration, exact generator and produced archive. Release metadata indexes
that receipt as a checksum-verified artifact alongside the native archive.

The same public tooling can run in a private pack repository with repository-owned
recipes or pinned spec/artifact pairs. An empty plan fails explicitly rather than
producing an empty release. Private content and artifacts remain in that private
repository. Generation, content integrity, installation and consumer behavioral
qualification are distinct evidence; completeness and rejects remain unchanged.

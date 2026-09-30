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
The recipes are not automatically executed by source packaging CI.

For a future independent native release: generate against the exact recorded
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

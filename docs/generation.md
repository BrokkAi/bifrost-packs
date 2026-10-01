# Generation and qualification

The native installer/catalog tool `bifrost-semantic-pack` stays with Bifrost.
This repository owns copied data, manifests, specifications, source pins, and
recipes. Engine tooling, activation/catalog implementation, and compiler
semantics are not duplicated here. `semantic-packs/embedded/` contains native
compiled artifacts; top-level specifications are inputs, not installable
shards.

`scripts/upstream/` preserves upstream recipes byte for byte. Some recipes
invoke Cargo, read engine source for catalog schema, or depend on engine
checkout paths. Do not run them blindly from this repository. Use a disposable
engine checkout at `aa291b97e55e48efc931ea89a16068404c3aad3e`, overlay the locked
data into the original paths listed in `content-lock.json`, and run the recipe
from that checkout. Alternatively, provide an exact trusted
`BIFROST_SEMANTIC_PACK_BIN` for recipes supporting it. The PHP builder still
requires the engine checkout. Inputs use pinned hashes; network is explicit
during generation and can be replaced by verified cached inputs. Source
packaging CI does not execute the recipes; the native generation workflow does.

## Planned native release and current gate

`Generate native packs` runs the JVM, Python, TypeScript, and Rust recipes from
this repository. The intended `packs/v0.2.0` release uses the independently
pinned public Bifrost generator version `0.12.0` at commit
`62fc36c09ddb96746e716c1c3456a99957521d91`. The pin identifies the tool that
produced the bytes; it does not declare what consumer engine accepts them.
A prior successful generation run at source commit
`97374bacf203cba1c1c28f5f9da4884f061864e2` produced native model schema
versions 2 and 5 and release index schema 3. Treat this as diagnostic evidence,
not a fresh `v0.2.0` candidate or final release declaration; inspect the exact
archive before recording its values. See the [native publication blocker
evidence](native-publication-blocker.json).

The v2 release manifest declares the actual `semantic_model_read` and
`release_index` schema requirements, required capabilities, exact release
dependencies, and separate integrity/behavior evidence. It does not use engine
version as an acceptance bound. The native model manifests embedded in the
generated archive still have a `compatibility.bifrost` engine-version field:
the generated Java pack says `=0.12.0`, and the other generated packs have
engine ranges capped at `<1.0.0`. At pinned public Bifrost commit
`62fc36c09ddb96746e716c1c3456a99957521d91`,
`crates/bifrost-analysis/src/analyzer/semantic_model/model.rs:1172` requires
`compatibility.bifrost`; catalog checks at `catalog/mod.rs:5210, 5318` and
runtime validation at `runtime.rs:3290` enforce it. The publication guard
rejects native archives that retain this field. The intended
`packs/v0.2.0` and dependent `rules/v0.1.1` are not eligible for publication
until the native schema/runtime gate is resolved.

For a source-built executable and its build receipt, the generation command is:

```sh
python3 -B release-contract/native_generation.py --root . \
  --config native-generation.json --binary /absolute/path/bifrost-semantic-pack \
  --build-receipt /absolute/scratch/generator-build.json --output /absolute/scratch/native
python3 -B release-contract/native_release.py --root . \
  --config release-config.packs.json --version 0.2.0 \
  --archive /absolute/scratch/native/native.tar.gz \
  --receipt /absolute/scratch/native/generation.json --output /absolute/scratch/dist
```

Run from a clean, committed checkout. The source archive, Cargo lockfile, build
receipt, and executable checksum must match the generator pin. Pack release
version, generator version, and consumer version are independent. A newer
generator can emit older or newer data formats; selection uses actual schema
and capability declarations, not version inference.

Every language is generated in two fresh scratch roots. Each partial bundle and
the merged bundles are verified, and native content must match between runs.
`measurements.json` records observed timing data, so its bytes are excluded
from content comparison. Both original measurement records are retained;
timings are not rewritten and the full archives are not claimed to reproduce
byte for byte. `generation.json` binds the source commit, generation
configuration, exact generator, and archive. Release metadata hashes that
receipt and the archive.

Generation and integrity are distinct from consumer behavior. The current
behavior evidence is limited to one Python structural dynamic-evaluation
policy with a positive and a realistic near-miss case; it does not qualify the 49-policy release baseline, the 70-policy authoring
copy, a cross-language policy set, or generated packs across JVM, Python,
TypeScript, and Rust. Preserve incomplete and unsupported outcomes and each
pack's declared completeness, including `partial`. Empty findings under
incomplete coverage remain unreliable.

The workflow_dispatch path stages raw generation evidence only; a release tag
runs manifest indexing and the fail-closed publication guard. The same public
tooling can run in a private pack repository with its own
recipes or pinned spec/artifact pairs. Private content and artifacts remain in
that private repository. See [release streams](release-streams.md) for the
intended dependency and publication boundary.

# Batch 10 reviewed result-use content

This document records the source-only transition for the five reviewed result-use
models landed with the batch-10 policy arms. The model bytes are copied from the
reviewed engine inputs without identity or provenance changes.

## Policy version

The code-smells manifest remains at `2.17.0`. That version is already the
unreleased authoring version on this branch, so extending it preserves the pack
identity without implying a published release. Release baselines and release
configuration are intentionally unchanged.

## Model identities and evidence

| Source | Pack ID | Evidence retained |
| --- | --- | --- |
| [C libc model](../semantic-packs/c/c-libc-result-use-obligations.json) | `bifrost.c.libc.result-use-obligations` | C17/POSIX.1-2017; C/C++ header declarations; license remains `NOASSERTION` pending review |
| [C# BCL model](../semantic-packs/csharp/csharp-bcl-result-use-obligations.json) | `bifrost.csharp.bcl-result-use-obligations` | Microsoft.NETCore.App.Ref 8.0.0, net8.0, System.Runtime/System.Collections assemblies |
| [JavaScript String model](../semantic-packs/javascript/javascript-string-result-use-obligations.json) | `bifrost.javascript.string-result-use-obligations` | Node.js 22.11.0 artifact and pinned activation digest |
| [TypeScript String model](../semantic-packs/typescript/typescript-string-result-use-obligations.json) | `bifrost.typescript.string-result-use-obligations` | TypeScript 7.0.2 `lib/lib.es5.d.ts` activation |
| [Python status model](../semantic-packs/python/python-status-result-use-obligations.json) | `bifrost.python.status-result-use-obligations` | CPython 3.13.5 and typeshed revision `1620e225476597f34177351ef913dc8390dade30` |

Each source has a matching `.spec.json` with the exact source SHA, activation,
measurement query, compatibility, provenance, license, and notice declaration.

## Native generation transition

No embedded manifest or shard is added for these five packs. The offline
checkout has no executable built from the re-land engine commit
`e14a898c9e` on `1152b43f5d` (the integrated re-land worktree is
`2e205ac8ba`), and building a Rust generator would violate the workspace
build-cache constraint for this delegated lane. The available older semantic
pack executable rejects the `eof`, `nonzero`, and `minus_one` result
predicates used by the C and Python status models, so its output would not be
the reviewed producer output.

Generation remains a separate, pinned transition:

1. Build or obtain the exact `bifrost-semantic-pack` executable from the
   re-land engine source, recording its build receipt and source/archive
   digest. Do not use the older executable as a substitute.
2. Supply the exact artifacts named by the specs: Microsoft.NETCore.App.Ref
   8.0.0 reference assemblies, Node.js 22.11.0, TypeScript 7.0.2 with
   `lib/lib.es5.d.ts`, and CPython 3.13.5/typeshed at the pinned revision.
   Verify every artifact digest before generation.
3. For each valid spec/model pair, run:
   ```sh
   bifrost-semantic-pack validate semantic-packs/<ecosystem>/<model>.json --format json
   bifrost-semantic-pack lint semantic-packs/<ecosystem>/<model>.json --format json
   bifrost-semantic-pack generate /absolute/scratch/batch10-native \
     semantic-packs/<ecosystem>/<model>.spec.json \
     semantic-packs/<ecosystem>/<model>.json
   bifrost-semantic-pack verify /absolute/scratch/batch10-native
   ```
   The C pair additionally requires an SPDX license decision before the spec
   can pass the generator's fail-closed `NOASSERTION` check.
4. Review the generated `index.json`, manifests, shards, rejects, notices,
   measurements, and `SHA256SUMS`. Copy only the deterministic manifest and
   shard outputs into `semantic-packs/embedded/`, then add their hashes to
   `content-lock.json`. Run the two-pass native generation recipe from
   [generation.md](generation.md) and retain both measurement records.

Until that transition completes, source presence is not native installation or
runtime qualification. The existing `verify-native.py` result covers only
the already-embedded packs; these five source models are not included in that
count.

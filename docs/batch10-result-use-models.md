# Batch 10 reviewed result-use content

This document records the source-only transition for the seven reviewed result-use
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
| [C libc model](../semantic-packs/c/c-libc-result-use-obligations.json) | `bifrost.c.libc.result-use-obligations` | C17/POSIX.1-2017; C/C++ header declarations; Apache-2.0 (Brokk-authored facts, owner decision 2026-10-08) |
| [C# BCL model](../semantic-packs/csharp/csharp-bcl-result-use-obligations.json) | `bifrost.csharp.bcl-result-use-obligations` | Microsoft.NETCore.App.Ref 8.0.0, net8.0, System.Runtime/System.Collections assemblies |
| [JavaScript String model](../semantic-packs/javascript/javascript-string-result-use-obligations.json) | `bifrost.javascript.string-result-use-obligations` | Node.js 22.11.0 artifact and pinned activation digest |
| [TypeScript String model](../semantic-packs/typescript/typescript-string-result-use-obligations.json) | `bifrost.typescript.string-result-use-obligations` | TypeScript 7.0.2 `lib/lib.es5.d.ts` activation |
| [Python status model](../semantic-packs/python/python-status-result-use-obligations.json) | `bifrost.python.status-result-use-obligations` | CPython 3.13.5 and typeshed revision `1620e225476597f34177351ef913dc8390dade30` |
| [PHP result-use model](../semantic-packs/php/php-result-use-obligations.json) | `bifrost.php.result-use-obligations` | JetBrains phpstorm-stubs revision `748ab87d16253a5b5d648b5fe4dae1ff4152bb03`, artifact SHA `270cfce465ac9e1de4abaa4f1facf70982f1becf70e040635f0519bd4a773bb9`; PHP 8.0-8.x manual; Apache-2.0 |
| [Ruby core result-use model](../semantic-packs/ruby/ruby-core-result-use-obligations.json) | `bifrost.ruby.core-result-use-obligations` | Ruby core RBS/Sorbet review at engine fixture revision `c5620808cb`; Ruby License recorded; `Kernel#system` model stores `false`, while the policy also documents the reviewed `nil` failure outcome |

Each source has a matching `.spec.json` with the exact source SHA, activation,
measurement query, compatibility, provenance, license, and notice declaration.
The PHP model is deliberately scoped to resolver-proven `_php_global_` calls;
the Ruby model is deliberately scoped to the reviewed core identities and leaves
open subclass, monkey-patched, and unknown receiver cases.

## Native generation transition

No embedded manifest or shard is added for these seven packs. The offline
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
   `lib/lib.es5.d.ts`, CPython 3.13.5/typeshed at the pinned revision, the
   phpstorm-stubs artifact named by the PHP spec, and the Ruby RBS core
   signature source named by the Ruby spec. Verify every artifact digest before
   generation.
3. For each valid spec/model pair, run:
   ```sh
   bifrost-semantic-pack validate semantic-packs/<ecosystem>/<model>.json --format json
   bifrost-semantic-pack lint semantic-packs/<ecosystem>/<model>.json --format json
   bifrost-semantic-pack generate /absolute/scratch/batch10-native \
     semantic-packs/<ecosystem>/<model>.spec.json \
     semantic-packs/<ecosystem>/<model>.json
   bifrost-semantic-pack verify /absolute/scratch/batch10-native
   ```

4. Review the generated `index.json`, manifests, shards, rejects, notices,
   measurements, and `SHA256SUMS`. Copy only the deterministic manifest and
   shard outputs into `semantic-packs/embedded/`, then add their hashes to
   `content-lock.json`. Run the two-pass native generation recipe from
   [generation.md](generation.md) and retain both measurement records.

Until that transition completes, source presence is not native installation or
runtime qualification. The existing `verify-native.py` result covers only
the already-embedded packs; these seven source models are not included in that
count.

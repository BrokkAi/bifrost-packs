# Batch 10 reviewed result-use content

This document records the native transition for the eight reviewed result-use
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
| [Python str model](../semantic-packs/python/python-str-result-use-obligations.json) | `bifrost.python.str-result-use-obligations` | CPython 3.13.5 and typeshed revision `1620e225476597f34177351ef913dc8390dade30` |
| [PHP result-use model](../semantic-packs/php/php-result-use-obligations.json) | `bifrost.php.result-use-obligations` | JetBrains phpstorm-stubs revision `748ab87d16253a5b5d648b5fe4dae1ff4152bb03`, artifact SHA `270cfce465ac9e1de4abaa4f1facf70982f1becf70e040635f0519bd4a773bb9`; PHP 8.0-8.x manual; Apache-2.0 |
| [Ruby core result-use model](../semantic-packs/ruby/ruby-core-result-use-obligations.json) | `bifrost.ruby.core-result-use-obligations` | Ruby core RBS/Sorbet review at engine fixture revision `c5620808cb`; Ruby License recorded; `Kernel#system` model stores `false`, while the policy also documents the reviewed `nil` failure outcome |

Each source has a matching `.spec.json` with the exact source SHA, activation,
measurement query, compatibility, provenance, license, and notice declaration.
The PHP model is deliberately scoped to resolver-proven `_php_global_` calls;
the Ruby model is deliberately scoped to the reviewed core identities and leaves
open subclass, monkey-patched, and unknown receiver cases.

## Native generation transition

The eight packs were generated with the pinned public producer at
`778bc8d1dd9a050092c4cb3ea3c1b78fc1b2b63e` (short form `778bc8d1dd9a`),
version `0.13.1`. The producer build used the release-pinned lockfile and
identity override:

```sh
BIFROST_BUILD_IDENTITY_OVERRIDE=778bc8d1dd9a050092c4cb3ea3c1b78fc1b2b63e \
  nice -n 10 cargo build --locked -p brokk-bifrost-semantic-packs \
  --features release-tooling --bin bifrost-semantic-pack
```

The release config has no direct jobs for these authored models, so the
documented direct `generate` command was used with all eight `.spec.json` /
model pairs, followed by `verify`. Two fresh output directories were generated
and verified. Both runs contained eight packs with zero rejected and zero
suppressed entries. The native trees were byte-identical when compared with
`diff -ru --exclude=measurements.json`; `index.json` matched at
`6e3cacfb8b2fa0c144be209a75acec5db116bdf69948321d9a5c2789bccde3ee`, and
`SHA256SUMS` matched at
`ba667635dfc1669262e8370b640719bffd7727568708ab8de2775dab8923346f`.
The index records generator version `0.13.1`. Only the eight deterministic
manifests and thirteen compressed shard files were copied into
`semantic-packs/embedded/`; notices, measurements, indexes, and rejects remain
generation evidence. Their hashes are locked in `content-lock.json`.

Native generation and byte integrity do not by themselves qualify consumer
behavior. The existing `verify-native.py` result now covers the embedded packs;
consumer qualification remains a separate end-to-end gate.

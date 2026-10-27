# JDK 21 native delivery repair (#129)

## Current status (2026-10-27)

`packs/v0.6.1` is published with the reviewed JDK 21 result-use model. The
planned `rules/v0.5.2` dependency-only follow-up was not published. The next
rules release is planned as `rules/v0.6.0`, retaining the exact dependency on
`packs/v0.6.1` and including the later C# policy additions and catch behavior
correction described in [release streams](release-streams.md).

No additional native release is required: the native generation inputs and
recipe have not changed since `packs/v0.6.1`. The source pack
`bifrost.jdk-golden-summaries` advances from 0.2.0 to 0.2.1 with fourteen
reviewed receiver-return identity classifications. This correction remains
source-only and is not selected for native generation; it does not change the
independent release versions. See the [identity review](qualification/receiver-return-identity.md).

The original preparation and verification plan below is preserved as historical
context. It describes the state before `packs/v0.6.1` was published; the
unreleased `rules/v0.5.2` step is superseded by `rules/v0.6.0` above.

## Original preparation plan (historical)

### What changes

Prepare `packs/v0.6.1` and then `rules/v0.5.2`. This is a patch under
[release versioning](release-versioning.md): it restores native delivery of
reviewed JDK 21 obligations for existing policies, without expanding their
stated scope or narrowing consumer requirements. Rules 0.5.2 changes only the
exact release dependency; all 238 policy files and identities stay unchanged.
Neither release is published by this preparation.

`native-generation.json` is an explicit input list, not a scan of the source
catalog or `semantic-packs/embedded`. `native_generation.py` generates every
listed job and recipe in two fresh roots, verifies each output, merges them,
and compares native content. The JVM shell recipe selects JDK declarations,
Scala and Kotlin; it never selects the separate JDK result-use model.
`release-baseline.json` is the historical 0.11.5 baseline, not an input selection
for this native workflow. `release-config.json` describes the shared source
archive. `release-config.packs.json` controls the independently generated native
release; `release-config.rules.json` controls the rules stream and its dependency.

The JDK model was source-only because it had no direct job or generation spec.
Its schema-5 envelope also retained `compatibility.bifrost`, which the native
publication guard rejects. This repair migrates the envelope to schema 8 and
removes that engine gate, following the existing schema-8 migrations. No shard,
summary, activation, identity, provenance, license or completeness changes.
The retained historical embedded manifest and shard are not rewritten or merged
into the release. The new spec pins the exact authored model SHA-256 and adds
an Apache-2.0 notice for the Brokk-authored facts.

The Bifrost engine still embeds its own schema-5 copy of
`bifrost.jdk21.result-use-obligations@1.0.0`, with the engine gate. The native
schema-8 copy has the same ID and version but a different manifest digest.
`bifrost.python.str-result-use-obligations@1.0.0` already ships this way:
embedded at schema 5 in the engine, native at schema 8 here. The engine's
catalog keys rows by manifest digest, so both copies coexist, and their content
is identical, so either selection gives the same answers.

## Other reviewed models

The premise that batch 10 remains source-only is historical. The current
recipe already selects all seven, and the checksum-verified published 0.6.0
native index contains each of them. All remain unchanged:

| Model ID | Native job | Source schema | Result |
| --- | --- | --- | --- |
| `bifrost.jdk21.result-use-obligations` | `jdk21-result-use` (new) | 5 → 8 | Eligible after envelope migration |
| `bifrost.c.libc.result-use-obligations` | `c-libc-result-use` | 8 | Already delivered |
| `bifrost.csharp.bcl-result-use-obligations` | `csharp-result-use` | 8 | Already delivered |
| `bifrost.javascript.string-result-use-obligations` | `javascript-string-result-use` | 8 | Already delivered |
| `bifrost.typescript.string-result-use-obligations` | `typescript-string-result-use` | 8 | Already delivered |
| `bifrost.python.status-result-use-obligations` | `python-status-result-use` | 8 | Already delivered |
| `bifrost.php.result-use-obligations` | `php-result-use` | 8 | Already delivered |
| `bifrost.ruby.core-result-use-obligations` | `ruby-result-use` | 8 | Already delivered |

Python String is also already selected. The plan now has twelve direct jobs
and five unchanged recipes. The producer remains public Bifrost 0.14.0 at
`c11a13ffa03ebea154f587b899954e412b5b871e`, archive SHA-256
`71fba3d9337b83e923c54f7ad05b1a36bb5d81cf719a0ee6a6cdfdd47a79038a`,
lock SHA-256 `5a4b9f69c765fc88c5b30c12b28bfc220b46ab8311be4d4e5fd5c81af0f0bcee`,
Rust 1.99.1. Its reader accepts schemas 2–17 and its authored-input path checks
identity, metadata, exact source hash and activation before compiling. It supports
the reviewed `eof`, `nonzero` and `minus_one` predicates that blocked the older
batch-10 tooling. JDK obligations use the schema-5 result-use fields, supported
by schema 8; no newer model feature is introduced.

Current Bifrost master `bcecf14673a9aa0120a5ef84984f058a23ef3f8d` accepts
schemas 2–19 (`crates/bifrost-semantic/src/analyzer/semantic_model/model.rs`).
The supplied local engine checkout `caf6cae25e810c3dfb4c14c498940dabf6bf336c`
accepts only 2–16; it is older than master and cannot accept the full existing
schema-8/schema-17 native bundle. This repair does not lower generated schemas.
All eight reviewed models fit both readers individually after the JDK migration;
full bundle compatibility must use the current reader. Producer CI and consumer
behavior evidence are separate requirements.

## Acquisition and release order

`crates/bifrost-semantic-packs/src/download.rs` selects a root rules release,
then `inspect_candidate` requires exact equality with each declared dependency
version. A newer packs release is never substituted for that pin. Preferred
selection chooses the newest eligible root unless a preferred version is
explicitly requested; strict requests retain their exact versions and hashes.

| Published change | Normal newest-compatible selection |
| --- | --- |
| Packs 0.6.1 only | Rules 0.5.1 + packs 0.6.0 |
| Rules 0.5.2 before its packs dependency | Reject 0.5.2 (dependency missing); keep eligible older rules + packs 0.6.0 |
| Packs 0.6.1, then rules 0.5.2 | Rules 0.5.2 + packs 0.6.1 |
| Explicit rules 0.5.1 strict pin | Rules 0.5.1 + packs 0.6.0 until the request is updated |

After PR review and merge, the owner can create and push `packs/v0.6.1` at the
reviewed commit. The **Generate native packs** workflow (`native-packs.yml`)
builds the exact pinned producer (or verifies its cached executable receipt),
generates and compares both runs, indexes the native and source archives with
`native_release.py`, runs the publication guard, then publishes the tag's GitHub
release with `bifrost.public.packs-0.6.1-native.tar.gz`, its source archive,
checksums, `pack-release.json` and generation receipt. Manual dispatch with version
0.6.1 stages evidence and does not publish.

Only after that publication passes, create and push `rules/v0.5.2` at the same
reviewed commit. **Rules release** (`pack-release.yml`) builds the locked rules
archive twice, checks identity and integrity, performs its focused smoke, verifies
the exact published packs 0.6.1 dependency and tag commit, then publishes the
rules archive, checksums, manifest and smoke evidence. Manual dispatch stages
artifacts without publishing. Neither success claims full behavior qualification.

## Verification after publication

Download the exact native archive, checksum, generation receipt and
`pack-release.json` from `packs/v0.6.1`. Run the checksum check and
`release-contract/publication.py` on those assets. Extract into a fresh directory
and run the pinned producer's `verify` command. Inspect `index.json` and require
every model ID in the table above exactly once. Check each manifest's schema,
compatibility, original selector and provenance, then decode the named shards
(raw DEFLATE) and compare reviewed result-use obligations to the authored source.
For JDK, require both `java.lang.string.trim.result-use` and
`java.nio.file.files.delete-if-exists.result-use`, including the latter's
`fallible_status` obligation and partial completeness. Preserve the full bundle
and existing partial/reject accounting; do not accept an index-only name match.

Acquire through an updated rules 0.5.2 request in a fresh cache, recording selected
rules and dependency versions and artifact hashes. Rerun the oracle's regressed,
repaired and consumed-status cases with a JDK 21 binding and inspect structured
coverage as well as findings. Empty findings under incomplete coverage do not
prove a clean program. The exact oracle command and binding procedure are in
the task evidence report because that harness lives in the engine repository.

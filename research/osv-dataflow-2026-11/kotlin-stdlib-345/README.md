# Kotlin stdlib lead #345 on Bifrost 0.15.1

**Outcome: blocked by the engine. No rule ships.**
[#345](https://github.com/BrokkAi/bifrost-packs/issues/345) (CVE-2020-29582)
asks for a rule on secrets written through the legacy
`kotlin.io.createTempFile` and `kotlin.io.createTempDir` helpers. Those helpers
create the file or directory in the shared temporary directory with default
permissions. Kotlin 1.4.21 deprecated them rather than changing them, so the
misuse doesn't depend on the stdlib version. Every form of the rule (an
assertion on the calls, or taint from a secret to a write under the result)
starts by selecting those calls. On 0.15.1 none of them gets a target.

This batch's Java and Kotlin library leads (BrokkAi/bifrost-premium-packs
#504–#531, #553–#555) are recorded in that repository. Their shared version
gate is [bifrost-dev#11371](https://github.com/BrokkAi/bifrost-dev/issues/11371).

## Engine

Official `v0.15.1` release, `bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`,
archive SHA-256 `4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`
(matches the release `.sha256`), binary SHA-256
`78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`, build
`90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`. Host: Temurin 21.0.8,
`kotlinc` 2.4.10, Maven. The `packs/v0.11.0` native bundle
(`055f25de…9695`) provides `bifrost.kotlin-stdlib` 2.2.20. Evaluation date
2026-11-10. [`outcomes.json`](outcomes.json) has the full identity.

## Probe

[`probe/root`](probe/root) is a Maven project with `kotlin-maven-plugin` and
`kotlin-stdlib` 2.2.20. `src/main/kotlin/app/Tmp.kt` has three positives:
`createTempDir()`, `createTempFile("export", ".json")` and
`kotlin.io.createTempDir("x")`. Each writes a secret under the result. The
near miss writes through `Files.createTempDirectory("app", perms)` with
`rwx------` permissions.

```sh
BIFROST_BIN=/path/to/bifrost-v0.15.1/bifrost sh research/osv-dataflow-2026-11/kotlin-stdlib-345/probe/run.sh
```

| Setup | `createTempDir` / `createTempFile` binding | Cause |
| --- | --- | --- |
| `kotlin-stdlib` 1.4.21 (affected), binary jar only | `unproven, open, 0`, `callee_incomplete` | "kotlin default import package `kotlin.io` has no selected source or classpath owner for `createTempDir`" |
| `kotlin-stdlib` 2.2.20, with `kotlin-stdlib-2.2.20-sources.jar` | `unproven, open, 0`, `callee_incomplete` | `bifrost.external.kotlin` is selected ("matched toolchain kotlin 2.2.20 … matched package org.jetbrains.kotlin:kotlin-stdlib 2.2.20"), but "supplies kotlin.io.createTempDir with incomplete package member inventory" (`JvmPackPackageMemberOpen`) |
| Same, with `bifrost.kotlin-stdlib` enabled from the bundle | unchanged | The bundled pack stays `incompatible`: "the shard selector also requires artifact sha256 27b9b867…", although that exact sources jar is in `~/.m2` |

The second row is [bifrost-dev#8542](https://github.com/BrokkAi/bifrost-dev/issues/8542):
the Kotlin source-jar producer doesn't certify package-member completeness, so
every stdlib top-level function call stays open. This lead's reproduction was
added there as a comment. The third row (the bundled pack not activating
against a matching sources jar) wasn't investigated further.

## Promotion criteria

1. Rerun `probe/run.sh` on a release that closes #8542. Both calls must be
   `resolved, exhaustive, 1` and exact.
2. Then add a version-independent assertion over the two deprecated helpers to
   `bifrost.security`, with `Tmp.kt`'s positives and near miss as its
   fixture. The secret-source taint form also needs a reviewed secret-source
   model. If the rule should be limited to stdlib releases before 1.4.21, it
   also needs [#11371](https://github.com/BrokkAi/bifrost-dev/issues/11371)
   and [#10005](https://github.com/BrokkAi/bifrost-dev/issues/10005).

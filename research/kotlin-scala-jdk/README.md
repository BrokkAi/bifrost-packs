# Kotlin and Scala JDK leads on Bifrost 0.15.0

**Outcome: no Kotlin or Scala rule can ship on Bifrost 0.15.0.** This pass
covered the Kotlin and Scala rows of four JDK candidates in
[`research/stdlib/candidates.md`](../stdlib/candidates.md), plus the four
Scala standard-runtime leads tracked in
[#16](https://github.com/BrokkAi/bifrost-packs/issues/16). Every one of them
starts at a JDK or Scala standard-library call. On 0.15.0, no Kotlin or Scala
call to a JDK member gets a proven target, even with a JDK selected. The same
calls in a Java file in the same root do resolve. A rule that selected these
calls by spelling instead would be the name-based approximation the candidate
contracts rule out. So nothing is promoted to `rules/`, and the candidates
keep their `research-only` status.

The files under `probe/` are research inputs, not registered pack content.
They don't change locked policy or semantic-pack content.

## Engine

Official `v0.15.0` release, `bifrost-v0.15.0-universal-apple-darwin.tar.gz`,
downloaded with `gh release download v0.15.0 --repo BrokkAi/bifrost`.

- Archive SHA-256: `c91c0bd38e4c6c0def86dc75acf8fa6d750b23a45894a28a76115fb8af034eda`. It matches the release `.sha256`.
- Binary SHA-256: `47e3e2da0a64ba65b447337b43952478deebbed7af3aa92d835d3a5ad458da96`.
- Build identity: `09a2503c5f7ced1630a9e3c445ead53dfc5925e8`, the `policy-authoring.json` pin. Model set `91461455dea3dccbaabba343d7c2fd639002cead21eca7c4786a0b03876fd013`.
- Host JDK 21.0.8. Runs report `matched toolchain jdk 21.0.8`.
- Environment: `BIFROST_OPEN_PACKS_DISABLE=1`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`, `BIFROST_WORKSPACE_SEMANTIC_MODELS=on`.
- Workspace model: `semantic-packs/framework-decls/bifrost.jdk-framework-decls.json` 0.2.1, enabled through `probe/.bifrost/packs.json`.
- Evaluation date: 2026-11-03.

## Shared capability probes

The probes ran once per capability, and every lead below reuses the result.

### 1. Call binding to JDK members

`probe/bind/{java,kotlin,scala}/Calls.*` make the same JDK calls in each
language: ZIP entry reads, `Path.resolve`, `FileOutputStream`,
`Cipher.getInstance`/`init`, `GCMParameterSpec`, `CipherInputStream`,
`DirContext.search`, `URL.openConnection` and `System.getenv`. The table
shows `dispatch_outcome` for each call (outcome, coverage, target count).

| Call shape | Java | Kotlin | Scala |
| --- | --- | --- | --- |
| JDK constructor (`ZipInputStream(input)`, `CipherInputStream(…)`, `GCMParameterSpec(…)`, `URL(…)`) | resolved, exhaustive, 1 | unknown, open, 0 | not a call site (`new T(…)` produces no row) |
| JDK static (`System.getenv`, `Cipher.getInstance`) | resolved, exhaustive, 1 | unproven, open, 1 | unproven, open, 0 |
| Instance call, one overload (`zis.getNextEntry()`, `url.openConnection()`) | unproven, open, 1 | unproven, open, 1 | unproven, open, 1 |
| Overloaded instance call (`cipher.init(…)`, `ctx.search(…)`, `root.resolve(…)`) | unproven, open, 1 | ambiguous, open, 0 | `init`: unknown, open, 0; `search`/`resolve`: unproven, open, 1 |
| Java getter through language syntax (`zis.nextEntry.name`, `entry.getName`) | n/a | not a call site | not a call site |

`call-bindings` (`probe/queries/`) shows the cause for Kotlin, for example on
`Runtime.getRuntime().exec(cmd)`:

```
UnsupportedCallApplicability … spelling "exec"
UnsupportedExternalSignatureType: The external declaration type term has no proven exact native substitution
jvm-default-import-package-open: kotlin default import package `java.lang` has no selected source or classpath owner for `Runtime`
```

Kotlin treats `java.lang` as unowned even though the run selected the JDK.
Adding a Maven `pom.xml` (with `kotlin-maven-plugin`) or a
`build.gradle.kts` (with `jvmToolchain(21)`) doesn't change any row.
Reported as [bifrost-dev#9323](https://github.com/BrokkAi/bifrost-dev/issues/9323)
(Kotlin) and [bifrost-dev#9324](https://github.com/BrokkAi/bifrost-dev/issues/9324)
(Scala).

### 2. A shipped JDK taint rule, ported

`probe/.bifrost/policies/getenv-exec-{java,kotlin,scala}.rqlp` copies the
shipped `bifrost.security.java.system-getenv-to-runtime-exec` rule under a
research ID, changing only the selector language. It runs over
`probe/env/<language>/`, the same two-line flow in each language.

| Language | Completion | Findings |
| --- | --- | --- |
| Java | inconclusive (partial_discovery) | 1 possible, unproven, partial |
| Kotlin | inconclusive (partial_discovery) | 0; source and sink both `empty_selection` (`call_binding_selector_rejected`) |
| Scala | inconclusive (partial_discovery) | 0; source and sink both `empty_selection` (`call_binding_selector_rejected`) |

The Kotlin and Scala runs correctly stay inconclusive instead of reporting
clean. But they can't select the source or the sink, so the existing Java rule
can't be extended to these languages.

### 3. Kotlin and Scala standard libraries

`probe/bind/kotlin/Stdlib.kt` and `probe/bind/scala/Stdlib.scala` cover the
calls the Kotlin and Scala runtime leads start from. `runCatching`,
`Result.getOrElse` and `String.toByteArray` give unproven, open, 0 targets, and
`SecretKeySpec(…)` gives unknown, open, 0. In Scala, `Process(command)` and
`Regex.matches` give unknown, open, 0. `Process(command).!` and `"…".r` aren't
call sites. Both reported in bifrost-dev#9323 and #9324.

Dependency evidence and build-target ownership were also probed, in the
premium repository, because only library leads need them. Neither changes
any outcome here, since none of these leads is version-gated. Every JVM
analyzer reports `static dependency evidence is unavailable` for a Maven
`pom.xml` ([bifrost-dev#9325](https://github.com/BrokkAi/bifrost-dev/issues/9325)).

## Per-lead outcomes

The Java rows of the four JDK candidates weren't qualified here. They stay in
the [qualification queue](../stdlib/qualification-queue.md). The Java column
above shows that Java constructors and statics resolve, but instance calls stay
open-world, as the Java getenv baseline's partial finding also shows.

| Lead | Kotlin/Scala outcome | Blockers |
| --- | --- | --- |
| [jvm-zip-entry-containment](../stdlib/candidates.md#jvm-zip-entry-containment) | Blocked by engine | Kotlin and Scala `ZipInputStream`/`FileOutputStream` constructors don't bind. The `getName` read through property syntax isn't a call site. Overloaded `Path.resolve` is ambiguous in Kotlin. bifrost-dev#9323, #9324. |
| [jvm-jndi-filter-escaping](../stdlib/candidates.md#jvm-jndi-filter-escaping) | Blocked by engine | Kotlin `DirContext.search` is ambiguous with 0 targets, so the raw-filter overload can't be told apart from the filter-arguments overload. The Scala row is open. bifrost-dev#9323, #9324. |
| [jvm-aead-cipherinputstream-integrity](../stdlib/candidates.md#jvm-aead-cipherinputstream-integrity) | Blocked by engine | `CipherInputStream` and `GCMParameterSpec` constructors don't bind, `Cipher.getInstance` stays unproven, and `cipher.init` is ambiguous in Kotlin and unknown in Scala. So the AEAD transformation and the decrypt mode can't be tied to the stream. bifrost-dev#9323, #9324. |
| [gcm-nonce-reuse-same-key](../stdlib/candidates.md#gcm-nonce-reuse-same-key) | Blocked by engine | Has the same `Cipher`/`GCMParameterSpec` binding gaps, and is deferred as proof-heavy for Java too. bifrost-dev#9323, #9324. |
| lit-scala-03 `Regex` backtracking ([#16](https://github.com/BrokkAi/bifrost-packs/issues/16)) | Blocked by engine | `"…".r` isn't a call site, and `Regex.matches` gives unknown, 0 targets. A structural nested-quantifier match on a string literal can't prove the literal is compiled as a Scala `Regex`. bifrost-dev#9324. |
| lit-scala-05 `Process(String)` command text (#16) | Blocked by engine | `Process(command)` gives unknown, 0 targets, and `.!` isn't a call site. bifrost-dev#9324. |
| lit-scala-06 process-builder serialization gadget (#16) | Blocked by engine | Needs a bound `ObjectInputStream.readObject` entry point and the `scala-library` version, which doesn't publish ([bifrost-dev#9325](https://github.com/BrokkAi/bifrost-dev/issues/9325)). The audit finding is on Scala 3.8-RC1. bifrost-dev#9324. |
| lit-scala-08 `Parser.tokenize` uncaught `ParseException` (#16) | Blocked by engine | Has the same `Process(String)` binding gap. The exception path also needs a library-private exception type. bifrost-dev#9324. |

## Layout and reproduction

```
probe/
  .bifrost/packs.json                     enables bifrost.jdk-framework-decls for the jvm ecosystem
  .bifrost/policies/getenv-exec-*.rqlp    the shipped Java rule under research IDs, one per language
  bind/{java,kotlin,scala}/               the same JDK calls; Kotlin and Scala stdlib calls
  env/{java,kotlin,scala}/                getenv to Runtime.exec, one flow per language
  queries/call-bindings-*.rql             per-call binding diagnostics
  run.py                                  replays everything in a temporary root
```

Nothing was compiled or run. `run.py` copies the probe and the reviewed JDK
declaration pack into a temporary root, checks the build identity, and prints
the dispatch table, the binding diagnostics and the three policy runs as JSON:

```sh
BIFROST=/path/to/bifrost-v0.15.0/bifrost python3 -I research/kotlin-scala-jdk/probe/run.py
```

[`outcomes.json`](outcomes.json) records the engine identity, input hashes and
observations.

## Promotion criteria

- A Kotlin row can be qualified once bifrost-dev#9323 lands. Rerun
  `run.py`. Kotlin constructors and statics must reach `resolved, exhaustive`
  like Java, and the overloaded `init`/`search`/`resolve` calls must select one
  target. Then the Kotlin getenv probe must bind its source and sink. After
  that, write the rule with Kotlin positive and near-miss cases, including a
  local same-named class.
- A Scala row needs bifrost-dev#9324: `new T(…)`, parameterless and postfix
  members must be call sites with member identity. The same rerun then
  applies.
- The Scala runtime leads also need `scala-library` members to bind.
  lit-scala-06 also needs bifrost-dev#9325 for the library version.

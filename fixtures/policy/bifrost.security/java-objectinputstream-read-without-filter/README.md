# Java ObjectInputStream read without a filter fixture

Qualifies the version-independent part of the Java CVE lead
BrokkAi/bifrost-packs#301 (CVE-2026-41586, fabric-sdk-java). The
`java.io.ObjectInputStream` documentation and JEP 290 put the defence against
hostile serialized data in an `ObjectInputFilter` set on the stream before its
first read. So a stream whose `readObject()` runs before
`setObjectInputFilter` is reported on every JDK. The library's affected-version
part is not checked.

The policy is a typestate. Its subject is the result of
`ObjectInputStream(InputStream)`. `setObjectInputFilter(ObjectInputFilter)`
moves the stream from `unfiltered` to `filtered`, and `readObject()` while it
is still `unfiltered` is the error. All three calls bind with `:proof declared`
to the generated JDK members. Those member IDs are the same on Temurin 17.0.16
and 21.0.8. No workspace semantic model is needed.

The policy is opt-in (`"activation": "opt-in"`). It does not run by default.

**Every run is inconclusive on Bifrost 0.15.1, and every finding is
`possible`.** The findings carry `typestate-external-call`, and the run reports
`partial_discovery` with no diagnostic
([bifrost-dev#10001](https://github.com/BrokkAi/bifrost-dev/issues/10001),
related to [#9431](https://github.com/BrokkAi/bifrost-dev/issues/9431)).
Reviewed summaries for the three members were tried and changed nothing, so
none ship.

## Cases

- **Positives** (`src/ois/Channels.java`): a stream read with no filter, the
  same in one chained expression, and a filter set only after the first read.
- **Near misses** (`src/ois/Channels.java`): a filter set before the first
  read, and a stream that is created but never read.
- **Incomplete** (`incomplete/`): the stream escapes to a helper that sets
  the filter. `.bifrostignore` keeps this workspace out of the parent run.

## Validation

Bifrost 0.15.1 (`bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`, checksum
verified against the release; build identity
`90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`), host Temurin 21.0.8, evaluation
date `2026-11-05`. Each run used `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off`, `BIFROST_WORKSPACE_SEMANTIC_MODELS=on`,
`--no-builtin-policies`, `--no-incremental` and a fresh `BIFROST_CACHE_DIR`.
The authored policy hash is
`2ce2f8532a6a169802337732c4295fc354860a6f2c35620a744ab35dc856e297`.

- This directory, `--sources src`: inconclusive (`partial_discovery`, no
  diagnostic), with 3 findings, all `possible`, `unproven` and `partial`:
  `src/ois/Channels.java:13`, `:18` and `:25`. Neither near miss produces a
  finding.
- `incomplete/`, `--sources src`: inconclusive (`partial_discovery`), no
  finding.
- The same results with Temurin 17.0.16 selected.
- With Temurin 25.0.1 selected: inconclusive, no finding. The subject
  selector reports `dispatch outcome=resolved, coverage=exhaustive,
  target_count=0`
  ([bifrost-dev#10000](https://github.com/BrokkAi/bifrost-dev/issues/10000)).

## Known limits

- Only `ObjectInputStream(InputStream)` creates a subject. A subclass
  constructor, the protected no-argument constructor, and streams returned by
  helpers are not tracked.
- `readUnshared()` and `defaultReadObject()` are not events.
- A process-wide filter (`ObjectInputFilter.Config.setSerialFilter`,
  `jdk.serialFilter`, a filter factory) is deployment knowledge that the
  policy can't see. Those streams are still reported for review.
- The policy does not judge whether a filter set with `setObjectInputFilter`
  is strict enough.

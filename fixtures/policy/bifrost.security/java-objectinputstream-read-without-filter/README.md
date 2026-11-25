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
and 21.0.8.

The policy runs with `:unmodeled require-model`, so an unmodeled call before
`readObject()` keeps the stream's finding only when the engine can prove the
call can't reach the stream. That proof needs a fresh subject. The reviewed
`bifrost.jdk-object-input-stream-summaries` pack
([semantic-packs/jvm/object-input-stream](../../../../semantic-packs/jvm/object-input-stream/README.md))
gives the constructor an allocation of its result, and Bifrost with
[bifrost-dev#14546](https://github.com/BrokkAi/bifrost-dev/pull/14546) uses it
to make each constructed stream fresh
([bifrost-dev#14542](https://github.com/BrokkAi/bifrost-dev/issues/14542)).
Both workspaces carry a copy of the pack in `.bifrost/semantic-models/`.
Without it, or on an older engine, the stream in a method with an unmodeled
call or a second stream before the read reports nothing.

The policy is opt-in (`"activation": "opt-in"`). It does not run by default.

**Every run is inconclusive, and every finding is `possible`.** The findings
carry `typestate-external-call`, and the run reports `partial_discovery`
([bifrost-dev#10001](https://github.com/BrokkAi/bifrost-dev/issues/10001),
related to [#9431](https://github.com/BrokkAi/bifrost-dev/issues/9431)).

## Cases

- **Positives** (`src/ois/Channels.java`): a stream read with no filter, the
  same in one chained expression, a filter set only after the first read, an
  unmodeled call (`System.err.println`) between construction and the read, two
  streams read with no filter in one method, and the unfiltered second of two
  streams whose first is filtered.
- **Near misses** (`src/ois/Channels.java`): a filter set before the first
  read, a stream that is created but never read, the filtered first of two
  streams, and a filter set before the read with an unmodeled call after it.
- **Incomplete** (`incomplete/`): the stream escapes to a helper that sets
  the filter. `.bifrostignore` keeps this workspace out of the parent run.

## Validation

Bifrost built from bifrost-dev master `ea5a7e3884f` (contains #14546),
`--profile measure`, and released Bifrost 0.15.3
(`bifrost-v0.15.3-aarch64-apple-darwin`), evaluation date `2026-11-19`. Each
run used `BIFROST_OPEN_PACKS_DISABLE=1`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `--no-builtin-policies`,
`--no-incremental`, `--sources src` and a fresh `BIFROST_CACHE_DIR`, with
Temurin 21.0.8 unless noted. The authored policy hash is
`2ce2f8532a6a169802337732c4295fc354860a6f2c35620a744ab35dc856e297`.

- This directory, master build: inconclusive (`partial_discovery`), with 7
  findings, all `possible` (`typestate-external-call`) and `partial`:
  `src/ois/Channels.java:13`, `:18`, `:25`, `:47`, `:55`, `:56` and `:66`. No
  near miss produces a finding. The same with Temurin 17.0.16.
- The same without the workspace pack: only `:13`, `:18` and `:25`.
- This directory, Bifrost 0.15.3: the pack is selected and the result is the
  same as without it, `:13`, `:18` and `:25`.
- `incomplete/`, master build: inconclusive (`partial_discovery`), no finding.
- Bifrost 0.15.1 with Temurin 25.0.1 selected (2026-11-05): inconclusive, no
  finding. The subject selector reports `dispatch outcome=resolved,
  coverage=exhaustive, target_count=0`
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

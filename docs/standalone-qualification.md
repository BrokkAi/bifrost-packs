# Standalone consumer tuple qualification

Issue [#7](https://github.com/BrokkAi/bifrost-packs/issues/7) owns the public
content tuple. Engine publication and proven profile capabilities belong to
[Bifrost #3791](https://github.com/BrokkAi/bifrost-dev/issues/3791) and
[#3792](https://github.com/BrokkAi/bifrost-dev/issues/3792). LSP process and
platform release tests remain in `bifrost-lsp`.

## Current immutable inputs

Observed 2026-10-01 through GitHub release assets and tag API. Both tags point
to pack source `28babf267ce4602549588082d5801d78ba549edf`.

| Input | SHA-256 |
| --- | --- |
| rules/v0.1.1 descriptor | `6f188826fe5b4918967100d8c0816c8b230a13d4a47300497d2294390a112388` |
| rules/v0.1.1 source archive | `7389ddcd556ca6d0e65a9149adfb8ce4af29cad63a1b411d52ac3975b3808792` |
| packs/v0.1.1 descriptor | `f28356cb17e85d84de3432de837f2d045e554e6d3d8d1f08018015e4960446d8` |
| packs/v0.1.1 native archive | `f14fc2edc1d58bca1662262f1f89e690a81baca0cfe48ed92bd463e8b8269f32` |

The checked-in [audit observation](qualification/2026-10-01-public-release-audit.json)
retains exact identities, schema requirements, capabilities, and completeness.

These immutable schema 1 releases require engine `>=0.12.0,<0.12.1` and
retain pending qualification. Rules contain 70 policies in four catalogs and
require 60 distinct capabilities. This is different from the intended 49-policy
`rules/v0.1.2` baseline in [release streams](release-streams.md); neither
scope may be substituted for the other without recording the chosen contents.

The native bundle has release index schema 3, native model schemas 2 and 5,
and eight descriptors. Four declare partial completeness: JDK, Kotlin, Rust,
and generated external Java. The external Java manifest additionally requires
engine `=0.12.0`. Descriptor/hash verification does not establish runtime
compatibility with a successor engine.

## Acceptance and handoff

Record the immutable public engine source/version, registry-only crate closure
and Cargo.lock hash, executable/library build identity, actual profile JSON and
hash, and the exact descriptor/archive hashes. Obtain the profile from that
engine. Required capability strings in pack metadata are requirements, never
proof of engine support.

Download each release into its own directory so descriptors cannot overwrite
each other. Audit downloaded artifacts offline with the repository tuple audit:

```sh
gh release download rules/v0.1.1 --repo BrokkAi/bifrost-packs --dir /tmp/rules-0.1.1
gh release download packs/v0.1.1 --repo BrokkAi/bifrost-packs --dir /tmp/packs-0.1.1
python3 -B scripts/audit_tuple.py --manifest /tmp/packs-0.1.1/pack-release.json \
  --output /tmp/packs-audit.json
python3 -B scripts/audit_tuple.py --manifest /tmp/rules-0.1.1/pack-release.json \
  --dependency-manifest /tmp/packs-0.1.1/pack-release.json \
  --output /tmp/rules-audit.json
```

The commands use already-downloaded adjacent descriptors, archives, and checksum
sidecars without network access. Add `--engine-profile /path/to/profile.json`
only with the actual engine-produced profile. `--allow-unqualified` permits
legacy pending qualification for diagnostic selection; it cannot bypass schema,
capability, engine-range, dependency, or integrity checks. A diagnostic rejection
remains explicit in the report, and successful selection still leaves behavior
pending.

Preserve
its integrity evidence separately from behavior. Compatibility rejection is a
valid diagnostic outcome; it cannot be replaced by copied capabilities or a
wider engine range. The audit cannot establish tag binding or registry
publication by itself; check those against the remote immutable coordinates.

After #3792 then #3791 release their heavy validation slots and provide a
qualified public engine, run real library acceptance in a fresh isolated cache:

1. Select the exact rules release and its exact packs dependency against the
   engine's real profile. Keep a single receipt for the run. Reject schema,
   capability, version, dependency and pin mismatches before installation.
2. Install the selected real native archive. Record installed packs separately
   from activated packs and query-covered models. Activate a named supported
   public declaration/model and prove its exact identity through the engine
   query API. Repeat offline with the same selected content and an isolated
   warmed cache. A new empty offline cache must fail.
3. Load the selected real policy catalogs, verify selected catalog/policy IDs
   and authored/resolved identities, and execute a named policy against positive
   and realistic near-miss fixtures. Record exact policy/language coverage,
   completion and uncertainty. The existing dynamic-evaluation CLI smoke is
   useful focused evidence, but does not establish library catalog selection or
   semantic-model activation.
4. Reject changed archive, inner manifest/model/shard and policy bytes. Retain
   raw engine errors and reports. Invalid selected content must not fall back
   to a different embedded model or policy.
5. Publish an accurately scoped immutable successor through the existing
   native/content/dependency gates. Preserve historical assets and ranges.
   Native schema 2 publication remains blocked by inner engine-version gates.
6. Hand `bifrost-lsp` exact engine/content coordinates, descriptors, hashes,
   profile, crate lock, commands, raw reports, installed/activated/covered
   identities, offline reuse results and all typed negative outcomes. LSP owns
   its real-process and platform qualification.

Until those runs and publication pass, issue #7 remains incomplete. Artifact
availability, synthetic tests, byte integrity and a compatible descriptor each
provide narrower evidence than the requested runtime tuple.

## Outer selection versus inner native acceptance

There are two separate compatibility axes. Immutable release schema 1 outer
metadata gates selection by engine version as well as schemas and capabilities.
New release schema 2 outer metadata deliberately selects by schemas,
capabilities, and exact dependencies without an engine-version range.

The current native payload contract separately requires `compatibility.bifrost`
in models/specs and enforces it in catalog installation and runtime activation.
The pack repository's schema 2 publication gate goes further than outer
selection: `release-contract/publication.py` inspects native bytes and
`native_release.require_version_independent_native` rejects any inner `bifrost`
or `engine` gate. Therefore successful schema 2 outer selection alone cannot
satisfy current native publication policy, nor prove inner activation.
Regenerating Java with a newer exact pin would change its valid engine but
would retain the publication conflict. A correct engine-owned producer/reader
handoff must be checked against current code; the source locations below are
reproducible observations of pinned public source, not claims about a moving
branch.

At public source `62fc36c09ddb96746e716c1c3456a99957521d91`,
`crates/bifrost-analysis/src/analyzer/semantic_model/model.rs:1172` requires the
inner field, `catalog/mod.rs:5210,5318` validates its version requirement, and
`runtime.rs:3290` enforces it for activation. The real JDK production path at
`crates/bifrost-semantic-packs/src/release_bundle.rs:970-990` invokes
`JvmDependencyPackAdapter`. Its request builder at
`crates/bifrost-analysis/src/analyzer/jvm/external.rs:1347-1356` writes the exact
producer package version. Pack-only descriptor edits cannot change that
producer/reader contract. Current verification and any migration decisions
remain with the engine sessions.

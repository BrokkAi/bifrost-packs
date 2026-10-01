# Future v0.13.0 consumer transition

This repository's work copies and prepares content. It does not change Bifrost
defaults, custom selection, installation, projection, or publication. Preserve
the existing built-ins and releases until a separate consumer cutover is
qualified.

## Contract and consumer migration

New release manifests use schema 2. Compatibility is the match between each
consumer's supported schema axes and the release's actual requirements, plus
the consumer's advertised required capabilities and exact release dependencies.
Schema 2 has no engine-version range. Optional engine version, build identity,
and source commit are evidence provenance only. The selector must preserve the
separate integrity and behavior statuses: default schema 2 selection requires
verified integrity and behavior not marked failed; pending or limited behavior
may remain format-compatible. `--allow-unqualified` allows pending integrity
for reproduction only; it never permits failed integrity or behavior. It does
not bypass schema, capability, channel, pin, or dependency checks.

Schema 1 remains a legacy path. Its manifests retain exact engine-version
ranges and the original single qualification semantics. Keep old releases
immutable and apply those rules only to schema 1 manifests.

The current JS engine and LSP release selectors support schema 1 only and need
schema 2 support. Native selection has a separate gate: embedded native model
manifests still require `compatibility.bifrost`, and Bifrost's catalog and
runtime enforce it. The staged generated Java content declares
`=0.12.0`; the other packs have engine ranges capped at `<1.0.0`. At pinned
public Bifrost commit `62fc36c09ddb96746e716c1c3456a99957521d91`,
`crates/bifrost-analysis/src/analyzer/semantic_model/model.rs:1172` requires
`compatibility.bifrost`; catalog checks at `catalog/mod.rs:5210, 5318` and
runtime validation at `runtime.rs:3290` enforce it. See the [recorded native
publication blocker](native-publication-blocker.json). The new native release
cannot be published as version-independent until the native schema and runtime
are migrated. The intended 49-rule baseline declares 46 distinct required capability
identifiers; the current engine capability profile is empty and cannot satisfy
them. Do not infer capabilities from
engine SemVer or a favorable metadata field.

The intended `packs/v0.2.0` release uses generator version `0.12.0` from
public Bifrost commit `62fc36c09ddb96746e716c1c3456a99957521d91`; this is tool
provenance, not consumer qualification. A prior successful generation run
observed model schema versions 2 and 5 and release index schema 3; it is
diagnostic evidence, not a fresh release candidate. Verify any final values from
the exact archive. The intended `rules/v0.1.1` contains
the exact 49-policy `v0.11.5` baseline and depends on the exact
`bifrost.public.packs` `0.2.0` release. The dependency is under review, and
neither intended tag is a publication claim. See
[release streams](release-streams.md) and [generation](generation.md) for the
current native publication blocker and evidence scope.

## Future sequence

1. Keep the source copy additive. Preserve policy IDs and hashes, source
   provenance, language scope, exact dependencies, and completeness.
2. Migrate native schema/catalog/runtime validation to express and enforce
   actual format and capability requirements without an engine-version gate.
   Update the JS engine and LSP selectors to validate both manifest schemas,
   preserve the v1 path, resolve schema 2 dependencies exactly, and write
   receipts with release, source, manifest, dependency, and artifact identities.
3. Advertise only capabilities the exact consumer build can prove. Match every
   nonempty schema axis and declared capability; an empty profile or unavailable
   capability must reject the candidate. Preserve typed unavailable,
   incompatible, corrupt, and incomplete states.
4. Qualify exact artifacts against exact consumer builds and model sets. Verify
   native bytes, install/catalog behavior, policy positives and near misses,
   realistic unsupported cases, and partial-coverage outcomes. The one Python
   structural-policy smoke is narrow evidence, not cross-language qualification.
5. Stage verified content with engine binaries and packages so offline
   installs need no hidden runtime network. Keep exact pins and verified cache
   receipts. Private online discovery requires authenticated access; missing
   access is a typed failure, not an empty pack.
6. Run source projection and classification checks before a separately reviewed
   publication or cutover. Retire duplicate engine data only after consumers
   and rollback paths have passed review.

Rollback must restore an earlier exact compatible content pin and its verified
cache, or an earlier engine release if needed. Never substitute `latest` for
an immutable rollback identity. Native format migration remains separate from
CSMI interoperability #3668.

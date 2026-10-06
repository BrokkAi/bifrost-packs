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

The v0.13 engine selector and schema-8 native producer/reader migration are
available in pinned public source `948f6700d2e668ee830aa42abf7ed4151d5bf560`.
This source availability is not public engine qualification. The new native
recipe uses that exact producer, corrected specs and verified input caches;
see [generation](generation.md). Historical 0.12.0 payloads remain immutable
and gated. Inspect new bytes, install/catalog behavior, real profile capability
support and exact dependency selection before admitting a candidate.

The intended `rules/v0.1.2` remains the exact 49-policy historical baseline and
its exact `packs/v0.2.0` dependency. This preparation does not substitute the
larger rule-authoring copy. Newly reconciled schema-14 Python authoring content
is not part of the schema-8 native recipe and needs its own supporting engine
qualification. The intended tags are not publication claims.

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

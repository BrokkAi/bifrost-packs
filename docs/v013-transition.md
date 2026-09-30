# Future v0.13.0 consumer transition

This task copies content. It does not alter Bifrost's defaults, custom selection,
installation, projection or publication. Existing releases and artifacts remain.

The engine currently embeds policy documents in `bifrost-policy/src/builtin.rs`,
semantic model sources and manifests/shards in `bifrost-semantic-packs`, and keeps
a separate release index from the runtime SQLite catalog. `install.sh`, language
builders, plugin/npm/wheel/Cargo packaging and release readiness all need coordinated
changes at cutover. The Linux semantic-pack executable is installer/catalog tooling;
the cross-platform archive is data. Tooling stays with the engine.

Sequence the future change as follows:

1. Merge the shared release contract and copy PRs, qualify exact content against
   the intended v0.13 engine build/model set, and prepare independently versioned
   content releases. Retain policy IDs, authored hashes, model provenance and all
   supported-language/capability/completeness contracts.
2. Implement the engine consumer using the shared manifest schema. Enumerate all
   accessible releases, filter schemas/capabilities/engine compatibility/channel,
   resolve once and persist exact release/source/artifact identities per scan.
   Preserve explicit custom policy selection and validate native data before
   catalog mutation. Do not change a resolved model set mid-scan.
3. Stage compiled/installable content beside engine binaries and packages so offline
   installations need no hidden runtime network. Exact-version/commit pins and
   verified cache receipts must remain available. Private release discovery requires
   authenticated access; missing access is a typed failure, not an empty pack.
4. Prove fresh/offline installs, CLI/MCP/plugin default selection, custom selections,
   cache corruption, unsupported schema/capability, realistic positives/near misses
   and incomplete outcomes on all affected platforms. Run exact-source projection
   and classification gates before publishing any public engine change.
5. Only after the replacement and consumers pass, perform atomic classification/path
   retirement and remove duplicate engine data publication in a separate reviewed
   change. Do not delete historical releases or older engine artifacts.

Rollback before retirement keeps engine built-ins intact. After cutover, restore
an earlier exact compatible content pin and its verified cache; restore an earlier
engine release if necessary. Never substitute `latest` for an immutable rollback
identity. Native format migration is independent of CSMI interoperability #3668.

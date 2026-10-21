# Policy authoring identity verification

Rules 0.4.0 is prepared as a minor successor to `rules/v0.3.1`. It adds 57
policies, for 238 policy source files, preserves the existing policy IDs,
language scopes, required engine capabilities, policy bytes and typed
incomplete outcomes, and depends exactly on
`bifrost.public.packs@0.5.0`. The independent native successor carries eight
direct result-use model families, two Go `os` model outputs, and the generated
PHP builtin declaration slice. The existing PHP pack notes describe an earlier
partial output with 852 rejects (warnings); a local generation with the
selected 0.14.0 generator reported 854, and the CI generation report remains the
release record and must stay explicit. Neither stream change claims complete PHP coverage or qualifies
consumer behavior; see the [PHP pack notes](../semantic-packs/php/README.md).

The earlier authoring-identity preparation corrected 84 authored fields, 43
available resolved fields and 15 stale resolved values to explicit null. The
other 26 workspace-dependent policies already had null fields; all 41 retain a
workspace-required outcome.

Each public policy is checked through the production `policy-source-identity`
command. Its source ID is `builtin:bifrost.public.rules/` followed by the
repository policy path. The verifier independently compares the raw file digest,
authored identity and available resolved identity against the manifest. An
explicit `workspace-required` result requires a null resolved manifest field;
raw file hashes and authored identities never substitute for resolution.

Normal content CI and rules packaging build the production CLI from the public
source archive, Rust toolchain and Cargo lock pinned in `native-generation.json`.
The archive commit identifies that authoring build; it is not a claim of
release-candidate compiled-input equivalence. Records retain the executable hash,
exact command, environment, raw output and process status for every policy.
Mismatch, malformed output, process failure, timeout and output overflow fail
verification.

Source authoring verification does not execute policies, establish findings,
complete workspace binding, advertise engine contracts or qualify an engine
release. Runtime semantic hashes and positive, near-miss and incomplete witnesses
remain separate requirements. The 0.4.0 preparation remains pending the
independent public producer check; no successor release is claimed here.

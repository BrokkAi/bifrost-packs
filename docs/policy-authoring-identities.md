# Policy authoring identity verification

Rules 0.2.2 is prepared as a metadata and dependency successor. It carries the
same 181 policy source files, policy IDs, language scopes, required engine
capabilities and policy bytes as the immutable `rules/v0.2.1` release. Native
`packs/v0.3.0` also remains immutable; the successor depends exactly on
`bifrost.public.packs@0.4.0`.
The correction changes 84 authored fields, 43 available resolved fields and
15 stale resolved values to explicit null. The other 26 workspace-dependent
policies already have null fields; all 41 retain a workspace-required outcome.

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
remain separate requirements. The 0.2.2 preparation remains pending the
independent public producer check; no successor release is claimed here.

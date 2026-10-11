# Policy authoring identity verification

Rules 0.2.1 is prepared as a metadata correction. All 181 policy source files,
policy IDs, language scopes and required engine capabilities remain unchanged.
Rules 0.2.0 and native packs 0.3.0 remain immutable published releases.
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
remain separate requirements. The proposed metadata is pending the independent
public producer check; no successor release is claimed here.

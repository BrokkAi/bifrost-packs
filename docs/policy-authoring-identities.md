# Policy authoring identity verification

Rules 0.3.1 is prepared as a patch and dependency successor to the corrected
`rules/v0.3.0` policy baseline. It preserves the 181 policy source files, policy
IDs, language scopes, required engine capabilities, policy bytes and typed
incomplete outcomes, and depends exactly on
`bifrost.public.packs@0.4.0`. The independent native successor adds eight
direct result-use model families and the generated PHP builtin declaration
slice. The existing PHP pack notes describe an earlier partial output with 852
rejects (warnings). The selected 0.13.1 generator has not run this recipe here,
so its current completeness/reject report remains unverified and must stay
explicit. Neither stream change claims complete PHP coverage or qualifies
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
remain separate requirements. The 0.3.1 preparation remains pending the
independent public producer check; no successor release is claimed here.

# Policy authoring identity verification

Rules 0.5.1 is prepared as a patch successor to `rules/v0.5.0`. It changes the
declared required capabilities of twenty-seven policies to canonical names and
the arity filter of `bifrost.cpp-jsf.av-rule-159`; the av-rule-159 source and
its fixture copy are the only policy files whose identities change.

Rules 0.5.0 was a minor successor to `rules/v0.4.0`. It keeps the
238 policy source files and their IDs. Twenty existing policies change their
consumer requirements: the Python arms of the ten `bifrost.performance` loop
policies require exact declared effects (`bifrost.code-smells` 4.0.0), and the
ten `bifrost.effects` selected-boundary policies import their declaration
selection and are opt-in (`bifrost.effects` 2.0.0). It depends exactly on
`bifrost.public.packs@0.6.0`, whose native recipe adds the reviewed
`bifrost.python-performance-summaries` model those Python arms read. Neither
stream change qualifies consumer behavior.

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
remain separate requirements. The pinned 0.14.0 CLI verified all 238 source
authoring identities for the 0.5.0 preparation; no successor release is
claimed here.

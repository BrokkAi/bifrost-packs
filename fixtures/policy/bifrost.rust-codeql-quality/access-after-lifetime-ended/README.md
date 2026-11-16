# Rust access after lifetime ended

CodeQL query: rust/ql/src/queries/security/CWE-825/AccessAfterLifetime.ql
CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
Stable policy ID: bifrost.rust-codeql-quality.access-after-lifetime-ended
Engine: Bifrost 0.15.2 (policy-authoring.json), no semantic packs activated.

Source adapted from bifrost-dev tests/fixtures/golden/codeql-cq14/access-after-lifetime-ended.
`read_after_helper_returns` reads through a pointer to a local that `dangling_local` returned;
`live_owner_remains_valid` keeps its owner alive and is the near miss.

Recorded outcome on 0.15.2 (`bifrost --root crate --policy-file .bifrost/policies/access-after-lifetime-ended.rqlp`):
one finding at crate/src/lib.rs:5:14, certainty possible, proof unproven, completeness partial; run incomplete
(`semantic_analysis_partial`, `partial_discovery`). No stdlib pointer model is active here, so the pointer solver
reports unknown allocation extent and ambiguous alias. The near miss reports nothing. An empty result on this
fixture under incomplete coverage would not show a clean program.

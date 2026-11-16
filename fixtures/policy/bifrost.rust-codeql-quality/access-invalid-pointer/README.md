# Rust access through invalid pointer

CodeQL query: rust/ql/src/queries/security/CWE-825/AccessInvalidPointer.ql
CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
Stable policy ID: bifrost.rust-codeql-quality.access-invalid-pointer
Engine: Bifrost 0.15.2 (policy-authoring.json), no semantic packs activated.

Source adapted from bifrost-dev tests/fixtures/golden/codeql-cq14/access-invalid-pointer.
`read_after_release` reads a pointer after `release` deallocated it; `read_before_release` reads before the
release and is the near miss.

Recorded outcome on 0.15.2: one finding at crate/src/lib.rs:6:14, certainty possible,
completeness partial; run incomplete (`semantic_analysis_partial`). The near miss reports nothing.

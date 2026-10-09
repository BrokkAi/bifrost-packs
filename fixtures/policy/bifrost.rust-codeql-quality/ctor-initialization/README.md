# Rust constructor initialization

CodeQL query: rust/ql/src/queries/security/CWE-696/BadCtorInitialization.ql
CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
Engine source revision: 26c360ce219bab07f6224a490468741151b64623

Stable policy ID: bifrost.rust-codeql-quality.ctor-initialization. Expected: one definite, complete finding at app/src/startup.rs:2 where the constructor reaches std::fs::read through a helper. The libc-only helper and empty destructor remain clean.

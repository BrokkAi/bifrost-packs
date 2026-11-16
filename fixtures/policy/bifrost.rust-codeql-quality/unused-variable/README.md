# Rust unused variable

CodeQL query: rust/ql/src/queries/unusedentities/UnusedVariable.ql (and UnusedVariable.qll)
CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
Stable policy ID: bifrost.rust-codeql-quality.unused-variable
Engine: Bifrost 0.15.2 (policy-authoring.json); needs the `whole_let_initializer` and
`whole_match_arm_identifier` binding fields, first present in 0.15.2.

Expected on 0.15.2: three definite, complete findings at crate/src/lib.rs: `ignored` (18:36), `right` (24:16)
and `item` (25:9). Near misses report nothing: the `self` receiver, `_kept`, a used `used`, a read closure
parameter and `let stale = 1;`. CodeQL counts an initializer as a use of the variable, so an initialized local
that is never read belongs to the unused-value policy.

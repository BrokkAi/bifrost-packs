# Rust unused value

CodeQL query: rust/ql/src/queries/unusedentities/UnusedValue.ql
CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
Stable policy ID: bifrost.rust-codeql-quality.unused-value
Engine: Bifrost 0.15.2 (policy-authoring.json); needs the `dead-write` assignment relation, first present in 0.15.2.

Expected on 0.15.2: four definite, complete findings at crate/src/lib.rs: 7:5 (value replaced before any read),
15:5 and 16:5 (compound write replaced, then a final write never read) and 39:5 (`let _scratch = compute();`).
The run is inconclusive (`capability_incomplete`): the engine does not enumerate formal-parameter
writes (warning `formal_parameter_write_unenumerated`).

Known deviation from CodeQL: the engine row carries no variable name, so the policy cannot exclude
underscore-prefixed locals as CodeQL does. `_scratch` at 39:5 is reported though CodeQL would not report it.
Near misses that report nothing: values read between writes (`read_between_writes`) and a value read on
one branch before the other branch replaces it (`read_on_some_path`).

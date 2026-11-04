# Rust std io write model fixtures

These reproduction inputs live under `tests/cases/rust-io-write` so source
archives retain both Cargo projects and their Rust sources. They are archive
metadata, separate from the locked production content and native recipe.

The positive case sends a `password` value to stdout and stderr. The near-miss writes the same value to a `std::fs::File`; file writes are declarations for call resolution and are not cleartext-logging sinks.

Per-entry source locators are recorded in
[`bifrost.rust-std-io-write.json`](../../../semantic-packs/rust-codeql-parity/bifrost.rust-std-io-write.json).
The stock CodeQL 2.27.1 Rust sink rows are in `codeql/rust/frameworks/log.model.yml`: `_print`/`_eprint` at lines 11-12 and `StdoutLock`/`StderrLock` `write`/`write_all` at lines 13-16.

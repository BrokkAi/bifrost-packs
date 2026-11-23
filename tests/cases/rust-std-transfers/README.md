# Rust standard-library transfer summary fixtures

These reproduction inputs live under `tests/cases/rust-std-transfers` so source
archives retain both Cargo projects and their Rust sources. They are archive
metadata, separate from the locked production content and native recipe.

- `parse-ok-positive`: sends a sensitive input through `<core::str>::parse`
  into the `Result::Ok(0)` payload (`?`, `Result::unwrap`, `Result::unwrap_or`,
  `Result::unwrap_or_default`), `Result::unwrap_or` fallback argument flow, and
  `<std::fs::Metadata>::is_dir`.
- `parse-err-near-miss`: reads only the `Result::Err` side of
  `<core::str>::parse` (via `unwrap_err` and `if let Err`), which must not be
  tainted because the `str::parse` transfer targets `Result::Ok(0)` only.

Per-entry source locators and upstream CodeQL `1be292a1e54696ca543b4ad0f9b4537b9687caa7`
model rows (`rust/ql/lib/codeql/rust/frameworks/stdlib/core.model.yml:131`,
`rust/ql/lib/codeql/rust/frameworks/stdlib/fs.model.yml:84`, and
`rust/ql/lib/ext/generated/modelgenerator/rust.model.yml:4169,4172-4174`, MIT)
are recorded in [`bifrost.rust-std-transfers.json`](../../../semantic-packs/rust-codeql-parity/bifrost.rust-std-transfers.json).

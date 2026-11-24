# Rust std::fs path-injection fixture

Qualifies `bifrost.security.rust.path-injection` (CWE-22 / CWE-23 / CWE-36 /
CWE-73 / CWE-99), aligned with all 24 standard-library `path-injection` sinks
in CodeQL 0.1.46 (`github/codeql@1be292a1e54696ca543b4ad0f9b4537b9687caa7`)
`frameworks/stdlib/fs.model.yml`:

- 17 `std::fs` free functions (`copy`, `create_dir`, `create_dir_all`,
  `hard_link`, `metadata`, `read`, `read_dir`, `read_link`, `read_to_string`,
  `remove_dir`, `remove_dir_all`, `remove_file`, `rename`, `set_permissions`,
  `soft_link`, `symlink_metadata`, `write`; both arguments 0 and 1 for `copy`,
  `hard_link`, `rename`, and `soft_link`).
- 5 `std::fs::File` constructors (`create`, `create_buffered`, `create_new`,
  `open`, `open_buffered`).
- `std::fs::OpenOptions::open` and `std::fs::DirBuilder::create`.

Each workspace copies the reviewed standard-library models into
`.bifrost/semantic-models`:

- `bifrost.rust-std-sql-taint` 0.1.0 (`std::env`, `std::io::stdin`, `Stdin::read_line`, `Args::nth`, `Result::unwrap`, `Option::unwrap`).
- `bifrost.rust-std-fs` 0.1.0 (declares and summarizes all 24 sinks plus `OpenOptions` and `DirBuilder` builder methods, sharing `type.rust-sql.std` and `type.rust-codeql.std-fs-file` with `bifrost.rust-std-sql-taint` and `bifrost.rust-std-io-write`).

The policy is opt-in.

## Cases

- **`positive/`** (`src/lib.rs`): `std::env::var` values flowing into all stable `std::fs` free-function sinks (including both source and destination arguments of `copy`, `rename`, and `hard_link`), `File::{open, create, create_new}`, `OpenOptions::open`, and `DirBuilder::create` (23 definite findings at lines 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 90, 96, 102, 108, 114, 120, 126, 132, 138, and 144). (`File::{create_buffered, open_buffered}` are unstable nightly APIs; they are declared and selected in the pack and policy but omitted from the stable `rustc` fixture crate.)
- **`near-miss/`** (`src/lib.rs`): constant paths with unused environment reads, tainted data passed only as the contents argument (`arg 1`) of `fs::write`, and a local `local_lookalike` module defining `File::{open, create}` and `read` receiving untrusted environment input.
- **`incomplete/`** (`src/lib.rs`): `std::env::args().nth(1)` into `fs::read` (line 8) and `std::io::stdin().read_line(&mut line)` into `File::open` (line 15). Both flows are reported as `possible` findings while remaining `inconclusive (partial_discovery)` on Bifrost 0.15.4 due to schema-2 receiver summaries in `bifrost.rust-std-sql-taint`.

## Validation

Bifrost `v0.15.4` (`bifrost-v0.15.4-x86_64-unknown-linux-gnu`, binary SHA-256
`9375d159a40f1e3f36fdfc0b53af079e863692f8c6b438e31fa5d4665efc48a3`, build
identity `ea8da845e8d702206a9acc0c6f28d8bd18fa71c0`), evaluation date
`2026-11-24`. Each run used `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`--no-builtin-policies`, `--no-incremental`, and a fresh `BIFROST_CACHE_ROOT`.
All three fixture crates compile cleanly with `rustc 1.99.1 --edition 2021 --crate-type lib`.

- `positive/`: `proven_by_summary`, 0 diagnostics, 23 definite findings.
- `near-miss/`: `proven_by_summary`, 0 diagnostics, 0 findings.
- `incomplete/`: `inconclusive (partial_discovery)`, 2 possible findings at `src/lib.rs` lines 8 and 15.

## Known limits

- Covers only standard-library `std::fs` sinks and reviewed `std::env` / `std::io::stdin` sources.
- Source-only model pack; not added to `native-generation.json` or a release manifest.

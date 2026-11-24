# Rust std::process::Command command-injection fixture

Qualifies `bifrost.security.rust.command-line-injection` (CWE-78 / CWE-88),
aligned with CodeQL 0.1.46 (`github/codeql@1be292a1e54696ca543b4ad0f9b4537b9687caa7`)
`frameworks/stdlib/process.model.yml` standard-library sinks
(`std::process::Command::{new, arg, args}`).

Each workspace copies the reviewed standard-library models into
`.bifrost/semantic-models`:

- `bifrost.rust-std-sql-taint` 0.1.0 (`std::env::{var, var_os, args, args_os, vars, vars_os}`, `std::io::stdin`, `Stdin::read_line`, `Args::nth`, `Result::unwrap`, `Option::unwrap`).
- `bifrost.rust-std-process` 0.1.0 (`std::process::Command::{new, arg, args, env, env_clear, env_remove, current_dir, spawn, output, status}`).

The policy is opt-in.

## Cases

- **`positive/`** (`src/lib.rs`): `std::env::var` values flowing directly and through a helper into `Command::new` (lines 11, 17), `Command::arg` (lines 23, 29), and `Command::args` (lines 36, 43).
- **`near-miss/`** (`src/lib.rs`): constant program and arguments with unused environment reads, plus a local `local_lookalike::Command` type with matching `new`, `arg`, and `args` methods receiving untrusted environment input.
- **`incomplete/`** (`src/lib.rs`): `std::env::args().nth(1)` into `Command::new` (line 8) and `std::io::stdin().read_line(&mut line)` into `Command::arg` (line 15). Both flows are reported as `possible` findings while remaining `inconclusive (partial_discovery)` on Bifrost 0.15.4 because the `bifrost.rust-std-sql-taint` receiver summaries (`Args::nth`, `Stdin::read_line`) use schema 2.

## Validation

Bifrost `v0.15.4` (`bifrost-v0.15.4-x86_64-unknown-linux-gnu`, binary SHA-256
`9375d159a40f1e3f36fdfc0b53af079e863692f8c6b438e31fa5d4665efc48a3`, build
identity `ea8da845e8d702206a9acc0c6f28d8bd18fa71c0`), evaluation date
`2026-11-24`. Each run used `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`--no-builtin-policies`, `--no-incremental`, and a fresh `BIFROST_CACHE_ROOT`.
All three fixture crates compile cleanly with `rustc 1.99.1 --edition 2021 --crate-type lib`.

- `positive/`: `proven_by_summary`, 0 diagnostics, 6 definite findings at `src/lib.rs` lines 11, 17, 23, 29, 36, and 43.
- `near-miss/`: `proven_by_summary`, 0 diagnostics, 0 findings.
- `incomplete/`: `inconclusive (partial_discovery)`, 2 possible findings at `src/lib.rs` lines 8 and 15.

## Known limits

- Covers only standard-library `std::process::Command` sinks and reviewed `std::env` / `std::io::stdin` sources.
- Source-only model pack; not added to `native-generation.json` or a release manifest.

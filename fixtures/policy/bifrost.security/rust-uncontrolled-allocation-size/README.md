# Rust std::alloc uncontrolled-allocation-size fixture

Qualifies `bifrost.security.rust.uncontrolled-allocation-size` (CWE-770 /
CWE-789), aligned with CodeQL 0.1.46
(`github/codeql@1be292a1e54696ca543b4ad0f9b4537b9687caa7`)
`frameworks/stdlib/alloc.model.yml` standard-library allocation sinks and
`Layout` taint transfers:

- `std::alloc` / `alloc::alloc`: `alloc(layout)` (arg 0), `alloc_zeroed(layout)`
  (arg 0), `realloc(ptr, layout, new_size)` (arg 2).
- `GlobalAlloc` / `System`: `alloc` (arg 0), `alloc_zeroed` (arg 0), `realloc`
  (arg 2).
- `Allocator`: `allocate` (arg 0), `allocate_zeroed` (arg 0), `grow` (arg 2),
  `grow_zeroed` (arg 2).
- `Layout` transfers: `from_size_align`, `from_size_align_unchecked`, `array`,
  `repeat`, `repeat_packed`, `extend`, `extend_packed`, `align_to`,
  `pad_to_align`, and `size`.

Each workspace copies the reviewed standard-library models into
`.bifrost/semantic-models`:

- `bifrost.rust-std-sql-taint` 0.1.0 (`std::env`, `std::io::stdin`, `Stdin::read_line`, `Args::nth`, `Result::unwrap`, `Option::unwrap`).
- `bifrost.rust-std-alloc` 0.1.0 (declares and summarizes `std::alloc` / `alloc::alloc`, `Layout`, `GlobalAlloc`, `System`, and `Allocator`, sharing `type.rust-sql.std` with `bifrost.rust-std-sql-taint`).

The policy is opt-in.

## Cases

- **`positive/`** (`src/lib.rs`): `std::env::var` lengths flowing into `std::alloc::realloc` (line 8), `std::alloc::alloc` via `Layout::from_size_align_unchecked` (line 16), `std::alloc::alloc_zeroed` via `Layout::from_size_align` (line 24), `std::alloc::alloc` via `Layout::array::<u64>` (line 32), `std::alloc::alloc` via `Layout::pad_to_align` (line 40), `std::alloc::alloc_zeroed` via `Layout::align_to` (line 48), and `std::alloc::alloc` via `Layout::repeat_packed` (line 57).
- **`near-miss/`** (`src/lib.rs`): constant layout and size passed to `std::alloc::{alloc, realloc}` with unused environment reads, plus a local `local_lookalike` module defining `alloc` and `realloc` receiving untrusted sizes.

## Validation

Bifrost `v0.15.4` (`bifrost-v0.15.4-x86_64-unknown-linux-gnu`, binary SHA-256
`9375d159a40f1e3f36fdfc0b53af079e863692f8c6b438e31fa5d4665efc48a3`, build
identity `ea8da845e8d702206a9acc0c6f28d8bd18fa71c0`), evaluation date
`2026-11-24`. Each run used `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`--no-builtin-policies`, `--no-incremental`, and a fresh `BIFROST_CACHE_ROOT`.
Both fixture crates compile cleanly with `rustc 1.99.1 --edition 2021 --crate-type lib`.

- `positive/`: `inconclusive (partial_discovery)`, 7 possible findings at `src/lib.rs` lines 8, 16, 24, 32, 40, 48, and 57.
- `near-miss/`: `inconclusive (partial_discovery)`, 0 findings.

## Known limits

- On Bifrost 0.15.4, passing an external `std::alloc::Layout` value by value into `std::alloc::{alloc, alloc_zeroed, realloc}` crosses an external by-value argument boundary, so runs stay `inconclusive (partial_discovery)` and findings are reported as `possible` rather than `definite`.
- `GlobalAlloc` / `Allocator` trait-method dispatch on external types is declared in the model and policy but does not yet bind trait-method call sites without a trait-impl relation on Bifrost 0.15.4.
- Source-only model pack; not added to `native-generation.json` or a release manifest.

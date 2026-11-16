# Rust std lock models

`bifrost.rust-std-sync.json` is an authored companion to the generated
`bifrost.rust-stdlib` pack (Rust nightly 2026-08-24). It summarizes three
blocking acquisitions of the poisoning std locks: `Mutex::lock` (exclusive),
`RwLock::read` (shared) and `RwLock::write` (exclusive), each as a
`lock_acquire` concurrency effect on the receiver.

- No `lock_release`: the returned guard's drop releases the lock, which the
  engine models from the guard's lifetime, not from a call.
- `try_lock`, `try_read` and `try_write` are not modeled. They return a
  `Result`, which `call_result_true` cannot test, and they never block.
- The guard-carrying members (`Result::unwrap`, `expect`, `unwrap_or_else`,
  `PoisonError::into_inner`) are deliberately absent: another pack may
  summarize them, and a second summary for one member makes binding ambiguous.
- `std::sync::nonpoison` (unstable) and the private `std::sys` locks are not
  modeled.
- Requires `bifrost.rust-stdlib` active, with the same toolchain activation.
  The summaries bind to its member identities and fail closed without it.
- Under an approximate stdlib activation the stdlib members lose
  `callable_family_complete`. See the engine's target-independence claim
  (bifrost-dev#13674) before relying on binding there.

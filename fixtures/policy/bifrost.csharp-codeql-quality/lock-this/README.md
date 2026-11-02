# C# lock-this parity fixture

Mirrors CodeQL `csharp/ql/src/Concurrency/LockThis.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. The upstream test source keeps
its CodeQL path and an MIT attribution header. The two header lines shift
upstream line numbers by two.

The engine contract reports `lock` statements whose locked expression is
exactly `this`. CodeQL selects a `ThisAccess` that is the lock expression.
Its extractor drops parentheses, so `lock ((this))` is reported in both. The
lock row's `value` role is read with `\Athis\z`; it looks through
parentheses, surrounding whitespace and a leading comment. No semantic model
is read, so the run needs no pack.

Near misses in `Probe.cs`: a private field, a field read through `this`
(`lock (this.sync)`), a cast `(object)this`, `typeof(...)`, `this` used only
in the body, and a `base` member call. The upstream `lock (lck)` is also a
near miss.

## Validation

Bifrost 0.15.0, build identity `09a2503c5f7ced1630a9e3c445ead53dfc5925e8`,
binary SHA-256
`d9acbc7305ed0390457117c48531c82c5ff0778dab4290f5cc670e692280ae45`
(`bifrost-v0.15.0-aarch64-apple-darwin`), evaluation date `2026-11-02`, run
from this directory with `BIFROST_OPEN_PACKS_DISABLE=1`,
`--no-builtin-policies` and `--no-incremental`. The authored policy hash from
`bifrost policy-source-identity` is
`3e78057c43b3fd4942e136ab48311dba887f6cae5a88c50ad4740f4bbe2ab0f5`; its
resolved identity is available with the same hash.

The run is complete with five findings: `Probe.cs:11`, `:19`, `:24` and
`:29`, and the upstream expected row `LockThis.cs:11` (upstream line 9).
There are no other findings.

## CodeQL parity

| Upstream expected row | Bifrost finding |
| --- | --- |
| `LockThis.cs:9:15:9:18` this access | `upstream/Concurrency/LockThis/LockThis.cs:11` |

## Known limits

- The finding is on the first line of the `lock` statement. CodeQL reports
  the `this` access, which is on a later line when the lock expression
  starts on a new line.
- A comment inside nested parentheses, as in `lock (( /* c */ this ))`, is
  not reported. On 0.15.0 the `value` role binds to the comment there.

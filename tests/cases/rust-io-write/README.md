# Rust std io write model fixtures

These reproduction inputs live under `tests/cases/rust-io-write` so source
archives retain both Cargo projects and their Rust sources. They are archive
metadata, separate from the locked production content and native recipe.

The positive case sends a `password` value to stdout and stderr. The near-miss writes the same value to a `std::fs::File`; file writes are declarations for call resolution and are not cleartext-logging sinks.

Per-entry source locators are recorded in
[`bifrost.rust-std-io-write.json`](../../../semantic-packs/rust-codeql-parity/bifrost.rust-std-io-write.json).
The stock CodeQL 2.27.1 Rust sink rows are in `codeql/rust/frameworks/log.model.yml`: `_print`/`_eprint` at lines 11-12 and `StdoutLock`/`StderrLock` `write`/`write_all` at lines 13-16.

## String view flow (source version 0.3.1)

The model also supplies the string views used to prepare logging arguments:
`String::as_bytes` and `String::as_str`. Keeping `as_str` beside the existing
`as_bytes` declaration and receiver-to-return summary preserves that carrier
scope; the core logging pack remains declarations-only. Version 0.3.0 is a
minor source bump for this added capability, with no release or native recipe
change.

The new `as_str` summary translates the MIT-licensed
[CodeQL alloc model at dd4405c2](https://github.com/github/codeql/blob/dd4405c2c2a8cd5ee7d200e7230ab8dd52e13dc6/rust/ql/lib/codeql/rust/frameworks/stdlib/alloc.model.yml#L51),
Copyright (c) GitHub, Inc.; see `licenses/CodeQL-MIT.txt`. Its
`Argument[self].Reference` to `ReturnValue.Reference` taint flow uses the
existing logical receiver and normal-return ports. The declaration returns `by_ref(named std.primitive.str)`, representing
`&str`. Both `String::as_bytes` and `str::as_bytes` declare
`by_ref(slice(named u8))`, representing `&[u8]`, using existing schema forms. This model does not claim to fix macro result typing or
`Option::expect` dispatch; upstream cleartext-logging line 229 remains unqualified.

Version 0.3.1 corrects these return declarations without adding a new capability.
The 0.3.1 checkout validation receipt is
`cfe2ebacd45405ab0443b1b9765d5cdb1be28a086715f8cdf5fd8434b4ad3975`.
Accept this exact digest when enabling the updated source model; prior
0.2.0/0.3.0 receipts do not review the corrected return declarations.

The focused receiver cases are described in
[`rust-cleartext-logging`](../rust-cleartext-logging/README.md).
Source selection includes sensitive receiver reads; runtime findings retain
their actual certainty and incomplete drop-classification status.

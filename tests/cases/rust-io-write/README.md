# Rust std io write model fixtures

These reproduction inputs live under `tests/cases/rust-io-write` so source
archives retain both Cargo projects and their Rust sources. They are archive
metadata, separate from the locked production content and native recipe.

The positive case sends a `password` value to stdout and stderr. The near-miss writes the same value to a `std::fs::File`; file writes are declarations for call resolution and are not cleartext-logging sinks.

Per-entry source locators are recorded in
[`bifrost.rust-std-io-write.json`](../../../semantic-packs/rust-codeql-parity/bifrost.rust-std-io-write.json).
The stock CodeQL 2.27.1 Rust sink rows are in `codeql/rust/frameworks/log.model.yml`: `_print`/`_eprint` at lines 11-12 and `StdoutLock`/`StderrLock` `write`/`write_all` at lines 13-16.

## String view and conversion flow (source version 0.4.0)

The model also supplies the string views used to prepare logging arguments:
`String::as_bytes` and `String::as_str`. Keeping `as_str` beside the existing
`as_bytes` declaration and receiver-to-return summary preserves that carrier
scope; the core logging pack remains declarations-only. Version 0.3.0 is a
minor source bump for this added capability, with no release or native recipe
change.

The `as_str` summary translates the MIT-licensed
[CodeQL alloc model at dd4405c2](https://github.com/github/codeql/blob/dd4405c2c2a8cd5ee7d200e7230ab8dd52e13dc6/rust/ql/lib/codeql/rust/frameworks/stdlib/alloc.model.yml#L51),
Copyright (c) GitHub, Inc.; see `licenses/CodeQL-MIT.txt`. Its
`Argument[self].Reference` to `ReturnValue.Reference` taint flow uses the
existing logical receiver and normal-return ports. The declaration returns `by_ref(named std.primitive.str)`, representing
`&str`. Both `String::as_bytes` and `str::as_bytes` declare
`by_ref(slice(named u8))`, representing `&[u8]`, using existing schema forms. Macro result typing and `Option::expect` dispatch also require engine support;
the linked qualification table records the measured upstream line 229 result.

Version 0.3.1 corrects these return declarations without adding a new capability.
The 0.4.0 checkout validation receipt is
`82e103499418fc720cd9b7811fad5c9f4ced365284a330e90b63e7cb5acf82df`.
Accept this exact digest when enabling the updated source model; earlier
receipts do not review the added conversion models.

The focused receiver cases are described in
[`rust-cleartext-logging`](../rust-cleartext-logging/README.md).
Source selection includes sensitive receiver reads; runtime findings retain
their measured certainty and completion status.

Source version 0.4.0 is a minor capability addition for Clone, ToString,
ToOwned and From standard trait flow summaries. They stay alongside the
existing string-view carriers used to prepare I/O arguments; the core logging
pack remains declarations-only and no new pack is introduced. Models retain
CodeQL's trait-wide contract identities, with reviewed `implements` edges for
String/str, rather than synthesizing inherent methods. Clone's upstream value
flow supplies data propagation without claiming alias or copy identity.
`Self`/associated return substitutions remain unknown where not expressible.

See the [per-method conversion witnesses](../rust-cleartext-logging/string-conversions/README.md)
for the exact MIT model rows, binding limitations and intentional omissions.
`into_bytes` has no pinned upstream row. Generic Into Element projections
cannot be encoded by the current logical transfer ports and are not replaced
by broader receiver-to-return transfers. Runtime impl binding must be proven
by the engine; valid source compilation alone is not qualification.

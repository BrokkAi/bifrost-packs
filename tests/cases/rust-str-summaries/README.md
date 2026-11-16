# Rust `str::trim` summary fixtures

Reproduction inputs for the `std.primitive.str.trim` member and summary in
[`bifrost.rust-std-io-write`](../../../semantic-packs/rust-codeql-parity/bifrost.rust-std-io-write.json)
0.6.0. They are archive metadata, not locked production content.

| Project | Witness | Expected |
| --- | --- | --- |
| `trim` | `password.trim()` stored in a local, then printed | one cleartext-logging finding; the `encrypted_password` control adds none |
| `trim-lookalike` | user-defined `Padded::trim` returning a fixed string | no standard `str::trim` summary applies |

Upstream row (MIT, Copyright (c) GitHub, Inc.; see `licenses/CodeQL-MIT.txt`),
`rust/ql/lib/codeql/rust/frameworks/stdlib/core.model.yml:132` at
`1be292a1e54696ca543b4ad0f9b4537b9687caa7`:

    ["<core::str>::trim", "Argument[self].Reference", "ReturnValue.Reference", "taint", "manual"]

The summary uses the logical receiver and normal-return ports and a
`by_ref(str)` return, as `str::as_bytes` does. These fixtures are not a runtime
qualification claim; the gate cell for `rust/weak-sensitive-data-hashing`
(`md5::Md5::digest(password.trim())`) is the measured witness.

## Not modelled: `str::parse`

CodeQL's `<core::str>::parse` row (`core.model.yml:131`) flows the receiver to
`ReturnValue.Field[core::result::Result::Ok(0)]`. No summary is authored for it:
a receiver-to-normal-return transfer would taint the whole `Result`, which is a
different contract. See the tracking issue for a Result-payload summary.

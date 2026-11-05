# Rust core logging declarations

`bifrost.rust-core-logging.json` is a partial, reviewed declaration slice for
`core::panicking::panic_fmt`, `core::panicking::assert_failed` and
`core::option::Option::expect`. It supports the public Rust cleartext-logging
policy together with `bifrost.rust-std-io-write` 0.4.0. It contains no procedure
body summaries and does not claim complete standard-library coverage.

The general Rust stdlib pack is generated from an immutable rustdoc JSON pin;
this authored slice does not alter that source specification. The other
hand-authored Rust packs cover I/O, SQL taint carriers or golden summaries.
These core logging declarations have their own scope and identity. The
`Option` type and `expect` member retain the `std::option::Option` reexport
aliases used by the Rust prelude. The declaration retains the `T` type
parameter and the `expect` return type `T`. The activation selector deliberately covers
all Rust Cargo targets; workspace configuration explicitly enables the pack. The compiler lint reports this broad selector
as an advisory.

Argument positions follow
[CodeQL's log.model.yml](https://github.com/github/codeql/blob/dd4405c2c2a8cd5ee7d200e7230ab8dd52e13dc6/rust/ql/lib/codeql/rust/frameworks/log.model.yml):

| Callable | CodeQL sink | Declaration |
| --- | --- | --- |
| `panic_fmt` | `Argument[0]` | one `fmt::Arguments` parameter |
| `assert_failed` | `Argument[3].Field[core::option::Option::Some(0)]` | four parameters, with `Option<fmt::Arguments>` at index 3 |
| `Option::expect` | `Argument[0]` | instance method with one message parameter; receiver excluded from formal indices |

The policy binds formal argument 3 for `assert_failed`. The current endpoint
schema does not expose a variant payload port, so reaching the sensitive
payload relies on the engine's native `Some` content-flow relation. The model
does not assert that this projection is implemented or qualified. The upstream
gate records the resulting engine coverage separately.

For checkout validation, install both authored model JSON files under the
workspace's `.bifrost/semantic-models/` and enable both IDs in
`.bifrost/packs.json`:

```json
{
  "schema_version": 1,
  "ecosystems": ["cargo"],
  "enable": ["bifrost.rust-core-logging", "bifrost.rust-std-io-write"]
}
```

A complete, exactly bound summary from an active pack can prove a finding
without a separate workspace approval. Activation does not make incomplete
bindings or declarations-only models complete. Compiler manifest hashes are
integrity and provenance data, not a runtime authorization step.

Declarations, activation, summary applicability and behavior qualification
remain separate. This source addition does not select the model in a native
release recipe, publish an artifact, or enable it for arbitrary workspaces.

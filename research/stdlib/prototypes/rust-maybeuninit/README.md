# Rust `MaybeUninit` initialization-state probe

**Outcome: incomplete; stop at declaration identity and modeled state.** This
prototype retains original, source-only Rust fixtures and diagnostic queries. It
does not register a production policy.

The structural call query found `uninit`, `new`, `write`, and
`assume_init`-family call shapes, including the application lookalike. That is
discovery evidence only. Against the exact fixture scope, declaration and
definition navigation returned `unresolvable_import_boundary` for the
`std::mem::MaybeUninit` import and `::uninit`; receiver method lookup returned
`no_declaration` / `no_definition` because the receiver type was unavailable.
The `call-sites-to` query for an indexed `assume_init` method returned no rows
and explicitly reported an omitted unresolved local lookalike candidate.
Therefore no selector in this probe proved the std declaration identity, and
no selector or RQLP can safely connect the state transition to the consuming
operation.

The repository's Rust semantic-pack specification pins a nightly rustdoc JSON
source set, but it is a pack input contract, not an activated model for this
run. No semantic model was activated. The fixture run used the installed
Bifrost 0.12.0 binary identified in `outcome.json`; no run established this
candidate's library declarations or initialization-state protocol. The primary
[Rust `MaybeUninit` documentation](https://doc.rust-lang.org/std/mem/union.MaybeUninit.html)
supports the semantic contract: `uninit` creates
uninitialized storage, `new` creates initialized storage, `write` initializes
the receiver, and the `assume_init` family requires initialized, valid `T`.
The documentation also describes pointer, partial aggregate, and zeroed-value
cases that must remain outside this bounded slice.

## Fixtures

Fixtures are source-only analyzer inputs. They include uninitialized positives,
same-object write and `new` near misses, an unrelated-object write, an alias,
one-branch and both-branch writes, a helper initializer, an unknown FFI escape,
and an application-defined lookalike type. Unsafe positives must not be
compiled or run as ordinary tests; none was compiled or executed here.

## Reproduction

From the repository root, copy `fixtures/*.rs` to a temporary root under
`fixtures/`, copy `queries/*` under `queries/`, then run the pinned binary with
the template commands recorded in `outcome.json`. Do not replace the binary
with a different `bifrost` found on `PATH`; version, executable digest, query
and fixture digests are recorded there. Raw host-local outputs are kept outside
the public repository.

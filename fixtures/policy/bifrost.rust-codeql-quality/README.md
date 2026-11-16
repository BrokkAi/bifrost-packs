# Public Rust CodeQL quality fixtures

Each fixture directory holds a `crate/` with the policy under `.bifrost/policies/`, positive cases, near
misses and a README that records the engine and the observed outcome. Run one with
`bifrost --root <fixture>/crate --policy-file .bifrost/policies/<policy>.rqlp`.

- `ctor-initialization`: a constructor reaching a standard-library call through a helper, with a libc-only helper and a destructor as near misses.
- `access-after-lifetime-ended`, `access-invalid-pointer`: raw-pointer accesses after a stack origin ended or an allocation was released.
- `unused-variable`: unread bindings with the CodeQL exclusions as near misses.
- `unused-value`: locals written and never read, with read-before-replace near misses.

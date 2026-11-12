# Held out: Cargo SSH git fetch without host-key verification

`bifrost.security.rust.cargo-ssh-git-host-key-unverified` (#248, lead #60,
CVE-2022-46176) shipped opt-in in `bifrost.security` 2.2.0 through 2.4.0
(rules 0.10.0 through 0.12.0). It is held out of the shipped rules from
`bifrost.security` 3.0.0 (rules 0.13.0).

The policy reads the Rust toolchain dependency evidence that Bifrost 0.15.1
introduced. No capability name covers that evidence, so its
`required_capabilities` list is empty. Released Bifrost engines through 0.15.2
treat an empty list as incomplete inventory metadata and reject the whole
rules catalog, so no policy loaded with rules 0.10.0 through 0.12.0.
bifrost-dev#10941 makes later engines accept an empty list.

Restore it in a rules release that requires an engine with bifrost-dev#10941:

- move `policy/cargo-ssh-git-host-key-unverified.rqlp` back to
  `rules/bifrost.security/policies/rust/`;
- add `manifest-entry.json` to the `policies` of
  `rules/bifrost.security/manifest.json`, with its `path` set to
  `policies/rust/cargo-ssh-git-host-key-unverified.rqlp`, and bump the pack
  minor;
- move `fixture/` back to
  `fixtures/policy/bifrost.security/cargo-ssh-git-host-key-unverified/`, add
  the rule back to `RULES` in `scripts/rust-sast-gate.py`, and move
  `qualification.json` back to `docs/qualification/rust-cargo-ssh-git.json`.

The fixture cases are described in [fixture/README.md](fixture/README.md).

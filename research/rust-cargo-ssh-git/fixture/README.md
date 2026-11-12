# Cargo SSH git fetch without host-key verification fixture

Qualifies lead BrokkAi/bifrost-packs#60 (CVE-2022-46176). Cargo before the one
bundled with Rust 1.66.1 doesn't verify the SSH host key when its built-in git
support fetches a git dependency
([advisory](https://blog.rust-lang.org/2023/01/10/cve-2022-46176/)). The
policy `bifrost.security.rust.cargo-ssh-git-host-key-unverified` joins a locked
`git+ssh://` Cargo dependency to a `rust-toolchain` row of the same package
whose pinned release is before 1.66.1.

Each directory is its own Cargo package. `scripts/rust-sast-gate.py` runs each
one with the manifest policy and fresh caches. It checks every case in
`expectations.json`: the run completion, the finding count, and the anchor
line of each finding.

| Case | Toolchain | Expected |
| --- | --- | --- |
| `positive-direct` | `rust-toolchain.toml` 1.66.0 | complete, 1 finding at the `wire-format` lock entry |
| `positive-transitive` | 1.64.0 | complete, 1 finding: an HTTPS git dependency pulls in the SSH one |
| `positive-legacy-toolchain-file` | legacy `rust-toolchain` 1.65.0 | complete, 1 finding |
| `near-miss-fixed-toolchain` | 1.66.1 | complete, no findings |
| `near-miss-https-source` | 1.66.0, HTTPS git source | complete, no findings |
| `unknown-no-toolchain-file` | none | inconclusive, no findings |
| `unknown-stable-channel` | `stable` | inconclusive, no findings |
| `unknown-msrv-only` | `rust-version = "1.60"` only | inconclusive, no findings |
| `unknown-missing-lockfile` | 1.66.0, no `Cargo.lock` | inconclusive, no findings |
| `unknown-workspace-git-fetch-with-cli` | 1.66.0, `.cargo/config.toml` sets `net.git-fetch-with-cli = true` | inconclusive, no findings |

The inconclusive cases carry `semantic_analysis_partial` diagnostics. An
unpinned toolchain gives `dependency version predicate unresolved ... no
complete exact version evidence`. A missing lockfile leaves the declaration
unassociated with a lock entry. A workspace `.cargo/config.toml` is reported
as unsupported dependency evidence.

## Validation

Bifrost 0.15.1 release asset `bifrost-v0.15.1-aarch64-apple-darwin`, build
identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`, binary SHA-256
`78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`.
Evaluation date 2026-11-05. The authored and resolved policy hash is
`6e27a37b6e1f966ab42e45a3b743fbcfdca585342a973a6f069d04fd3da69f6f`.
All 10 cases pass:

```sh
python3 scripts/rust-sast-gate.py --binary /path/to/bifrost-v0.15.1 \
  --output /empty/evidence/directory --rule cargo-ssh-git-host-key-unverified
```

Bifrost 0.15.0 rejects the policy at validation: `version_ranges requires
exactly one supported ecosystem: cargo, npm or nuget`. It doesn't run with a
clean result. See `docs/qualification/rust-cargo-ssh-git.json`.

## Known limits

- **Ambient configuration isn't read.** That includes `$CARGO_HOME/config.toml`,
  `CARGO_NET_GIT_FETCH_WITH_CLI`, git `insteadOf` rewrites that turn an HTTPS
  URL into SSH, `RUSTUP_TOOLCHAIN` and rustup directory overrides. Any of them
  can change the outcome. The toolchain row reports
  `rust.toolchain_override: unobserved`.
- **A workspace `git-fetch-with-cli = true` isn't proven safe.** Bifrost
  0.15.1 reports Cargo config as unsupported, so the run is inconclusive
  rather than clean.
- **Patched Cargo builds aren't detected.** A distributor's independently
  patched Cargo still matches by release number.
- **SSH registry indexes aren't covered.** Only git dependencies are.
- **No capability is declared.** Bifrost 0.15.1 advertises no capability name
  for dependency evidence or relational assertions, so the manifest declares
  `required_capabilities: []`.

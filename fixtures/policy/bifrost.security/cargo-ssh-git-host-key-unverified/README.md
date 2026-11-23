# Cargo SSH git fetch without host-key verification fixture

Qualifies lead BrokkAi/bifrost-packs#60 (CVE-2022-46176). Cargo before the one
bundled with Rust 1.66.1 doesn't verify the SSH host key when its built-in git
support fetches a git dependency
([advisory](https://blog.rust-lang.org/2023/01/10/cve-2022-46176/)). The
policy `bifrost.security.rust.cargo-ssh-git-host-key-unverified` joins a locked
`git+ssh://` Cargo dependency to a `rust-toolchain` row of the same package
whose pinned release is before 1.66.1, unless a workspace-root
`.cargo/config.toml` sets `net.git-fetch-with-cli = true`, the pinned release
is 1.39.0 or later (the first Cargo that reads `.cargo/config.toml`), and no
`.cargo/config.toml` in a subdirectory sets the key to anything else.

Each directory is its own Cargo package. `scripts/rust-sast-gate.py` runs each
one with the manifest policy and fresh caches. It checks every case in
`expectations.json`: the run completion, the finding count, and the anchor
line of each finding.

| Case | Toolchain | Expected |
| --- | --- | --- |
| `positive-direct` | `rust-toolchain.toml` 1.66.0 | complete, 1 finding at the `wire-format` lock entry |
| `positive-transitive` | 1.64.0 | complete, 1 finding: an HTTPS git dependency pulls in the SSH one |
| `positive-legacy-toolchain-file` | legacy `rust-toolchain` 1.65.0 | complete, 1 finding |
| `positive-git-fetch-with-cli-false` | 1.66.0, `.cargo/config.toml` sets `net.git-fetch-with-cli = false` | complete, 1 finding |
| `positive-pre-1-39-config-toml` | 1.38.0, root `.cargo/config.toml` sets `true` | complete, 1 finding: Cargo 1.38 doesn't read `.cargo/config.toml` |
| `positive-nested-git-fetch-with-cli-false` | 1.66.0, root `.cargo/config.toml` sets `true`, `tools/.cargo/config.toml` sets `false` | complete, 1 finding: Cargo run in `tools/` uses the built-in fetcher |
| `near-miss-fixed-toolchain` | 1.66.1 | complete, no findings |
| `near-miss-https-source` | 1.66.0, HTTPS git source | complete, no findings |
| `near-miss-workspace-git-fetch-with-cli` | 1.66.0, `.cargo/config.toml` has `[net]` `git-fetch-with-cli = true` | complete, no findings |
| `near-miss-dotted-git-fetch-with-cli` | 1.66.0, `.cargo/config.toml` has the dotted key `net.git-fetch-with-cli = true` | complete, no findings |
| `near-miss-legacy-toolchain-git-fetch-with-cli` | legacy `rust-toolchain` 1.65.0, root `.cargo/config.toml` sets `true` | complete, no findings |
| `near-miss-unrelated-toml-override` | 1.66.0, root `true`, and `docs/cargo-example.toml`, which Cargo never reads, sets `false` | complete, no findings |
| `unknown-no-toolchain-file` | none | inconclusive, no findings |
| `unknown-stable-channel` | `stable` | inconclusive, no findings |
| `unknown-msrv-only` | `rust-version = "1.60"` only | inconclusive, no findings |
| `unknown-missing-lockfile` | 1.66.0, no `Cargo.lock` | inconclusive, no findings |

The inconclusive cases carry `semantic_analysis_partial` diagnostics. An
unpinned toolchain gives `dependency version predicate unresolved ... no
complete exact version evidence`. A missing lockfile leaves the declaration
unassociated with a lock entry.

The `git-fetch-with-cli` near misses were inconclusive cases before Bifrost
0.15.3. Bifrost 0.15.1 and 0.15.2 reported `.cargo/config.toml` as unsupported
dependency evidence. Bifrost 0.15.3 no longer does, so without the
configuration-fact negation the run was complete with a false positive. The
policy now reads the TOML configuration fact `net.git-fetch-with-cli` of the
root `.cargo/config.toml` and suppresses the finding only for the boolean
`true`, only for a pinned release of 1.39.0 or later, and only when no
`.cargo/config.toml` in a subdirectory overrides it.

## Validation

Bifrost 0.15.3 release asset `bifrost-v0.15.3-aarch64-apple-darwin`, build
identity `cc7ebd1676e002b657e10304cfd977bc289e25ed`, binary SHA-256
`1e8d45ae76f1b2920aa7a113e8e80083346f6acbed839c3e113058ae36c8acbc`.
Evaluation date 2026-11-17. The authored and resolved policy hash is
`b5179d04ae335487e2726278f15775ad0f1fa1d8fafe796790db172bc94a3294`.
All 16 cases pass:

```sh
python3 scripts/rust-sast-gate.py --binary /path/to/bifrost-v0.15.3 \
  --output /empty/evidence/directory --rule cargo-ssh-git-host-key-unverified
```

Bifrost 0.15.2 and earlier reject the whole rules catalog, because this policy
declares an empty `required_capabilities` list ("incomplete inventory
metadata"). Bifrost 0.15.3 accepts it (bifrost-dev#10941). See
`docs/qualification/rust-cargo-ssh-git.json`.

## Known limits

- **Ambient configuration isn't read.** That includes `$CARGO_HOME/config.toml`,
  `CARGO_NET_GIT_FETCH_WITH_CLI`, git `insteadOf` rewrites that turn an HTTPS
  URL into SSH, `RUSTUP_TOOLCHAIN` and rustup directory overrides. Any of them
  can change the outcome. The toolchain row reports
  `rust.toolchain_override: unobserved`.
- **Only workspace `.cargo/config.toml` files are read.** Only the root one
  can suppress the finding, and only with the boolean `true`; a subdirectory
  one that sets anything else keeps it. A `.cargo/config.toml` above the root
  and the legacy extensionless `.cargo/config` aren't read. Cargo prefers
  `.cargo/config` over `.cargo/config.toml` in the same directory, and
  `CARGO_NET_GIT_FETCH_WITH_CLI=false` overrides every file, so either can
  make a suppressed project use the built-in fetcher again.
- **Patched Cargo builds aren't detected.** A distributor's independently
  patched Cargo still matches by release number.
- **SSH registry indexes aren't covered.** Only git dependencies are.
- **No capability is declared.** Bifrost 0.15.1 advertises no capability name
  for dependency evidence or relational assertions, so the manifest declares
  `required_capabilities: []`. Bifrost 0.15.3 is the first release that
  accepts an empty list.

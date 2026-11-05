# Rust OSV data-flow leads on Bifrost 0.15.1

**Outcome: 10 leads filed, no rule shipped.** All three open (`std`/toolchain)
leads are blocked by the engine. The seven crate leads are premium, so they
are not implemented here.

The leads come from the OSV `crates.io` archive
(`https://osv-vulnerabilities.storage.googleapis.com/crates.io/all.zip`,
downloaded 2026-11-05) and from the Rust toolchain advisories
(`rust-lang/rust` security advisories, through the osv.dev API). Only leads
whose theoretical policy is taint, flow or typestate were kept, and only where
app code or config decides reachability. Native-memory, unsound-`unsafe`,
CMS-app and upgrade-only bugs were skipped. Every CVE was checked against the
existing `CVE-` titles in `BrokkAi/bifrost-packs` and
`BrokkAi/bifrost-premium-packs`.

The files under `probe/` are research inputs, not registered pack content.
`bifrost.research.rust-std-fs-remove` is a research model. Promote it to
`semantic-packs/` only together with a rule that passes.

## Engine

- Official `v0.15.1` release, `bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`.
  Archive SHA-256 `4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`
  matches the release `.sha256`. Binary SHA-256
  `78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`. Build
  identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`. v0.15.2 was not
  released on 2026-11-05.
- Semantic packs: `packs/v0.10.0`, `bifrost.public.packs-0.10.0-native.tar.gz`,
  SHA-256 `3f39f9f5ec2d028e293a238ff796260101915e50963a44a93c812d9d02860945`,
  through `BIFROST_OPEN_SEMANTIC_PACK_BUNDLE`.
- Every run used a fresh `BIFROST_CACHE_DIR`, `BIFROST_WORKSPACE_SEMANTIC_MODELS=on`
  and `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`.

## Outcomes

| Lead | Advisory | Outcome | Blockers |
| --- | --- | --- | --- |
| [bifrost-packs#297](https://github.com/BrokkAi/bifrost-packs/issues/297) | CVE-2022-21658, `std::fs::remove_dir_all` | Blocked by engine | [bifrost-dev#10004](https://github.com/BrokkAi/bifrost-dev/issues/10004) (new), [#9920](https://github.com/BrokkAi/bifrost-dev/issues/9920), [#6542](https://github.com/BrokkAi/bifrost-dev/issues/6542); affected-toolchain part [#10005](https://github.com/BrokkAi/bifrost-dev/issues/10005) (new) |
| [bifrost-packs#298](https://github.com/BrokkAi/bifrost-packs/issues/298) | CVE-2021-29922, `std::net` IP parsing | Blocked by engine | [#10005](https://github.com/BrokkAi/bifrost-dev/issues/10005), [#6542](https://github.com/BrokkAi/bifrost-dev/issues/6542) |
| [bifrost-packs#299](https://github.com/BrokkAi/bifrost-packs/issues/299) | CVE-2025-11233, Cygwin `Path` checks | Blocked by engine | [#9902](https://github.com/BrokkAi/bifrost-dev/issues/9902), [#10005](https://github.com/BrokkAi/bifrost-dev/issues/10005), [#4307](https://github.com/BrokkAi/bifrost-dev/issues/4307), [#4319](https://github.com/BrokkAi/bifrost-dev/issues/4319), [#10004](https://github.com/BrokkAi/bifrost-dev/issues/10004) |
| [premium#462](https://github.com/BrokkAi/bifrost-premium-packs/issues/462) | CVE-2025-58160, tracing-subscriber ANSI | Premium, not implemented here | version gate: #10005, #9919 |
| [premium#463](https://github.com/BrokkAi/bifrost-premium-packs/issues/463) | CVE-2024-21530, cocoon nonce reuse (typestate) | Premium, not implemented here | as above |
| [premium#464](https://github.com/BrokkAi/bifrost-premium-packs/issues/464) | CVE-2025-27498, ascon-aead buffer after failed decrypt | Premium, not implemented here | as above |
| [premium#465](https://github.com/BrokkAi/bifrost-premium-packs/issues/465) | CVE-2025-25194, activitypub_federation SSRF | Premium, not implemented here | as above |
| [premium#466](https://github.com/BrokkAi/bifrost-premium-packs/issues/466) | CVE-2022-45299, `webbrowser::open` | Premium, not implemented here | as above |
| [premium#467](https://github.com/BrokkAi/bifrost-premium-packs/issues/467) | CVE-2021-45712, `RustEmbed::get` traversal | Premium, not implemented here | as above |
| [premium#468](https://github.com/BrokkAi/bifrost-premium-packs/issues/468) | CVE-2024-23644, trillium header CRLF | Premium, not implemented here | as above |

## #297: the version-independent slice

A path that the caller or environment chooses, given to a recursive delete,
removes whatever tree it names on any toolchain. So the probe policy
`probe/297-remove-dir-all/.bifrost/policies/remove-dir-all.rqlp` is a
may-taint policy with `require-model`. Its sources are `std::env::var` and
`std::env::args`, from the public `bifrost.rust-std-sql-taint` model. Its sink
is formal 0 of `std::fs::remove_dir_all`. The research model declares that
function with `callable_family_complete` and gives it a complete summary with
no transfers.

Run each case with `--sources src/<case>.rs`:

| Case | Completion | Findings |
| --- | --- | --- |
| `a_var`: `env::var(..).unwrap()` → `remove_dir_all(target)` | `proven_by_summary` | 1 at line 3, `possible`, `partial` |
| `f_var_borrow`: `remove_dir_all(&target)` | `proven_by_summary` | 1, `possible`, `partial` |
| `h_no_sink_unwrap`: the sink result is returned | inconclusive, procedure semantics unknown | 1, `possible`, `partial` |
| `b_args_nth`, `c_args_binding`: `args().nth(1).unwrap()` | inconclusive, procedure semantics unknown | 1, `possible`, `partial` |
| `d_stdin_trim`: `read_line` then `trim()` | inconclusive | 0 |
| `g_iflet`: `if let Ok(target) = env::var(..)` | inconclusive, `unsupported (values)` | 0 |
| `e_constant`: constant path (near miss) | `proven_by_summary` | 0 |
| `a_var` with `bifrost.rust-stdlib` enabled, unpinned or pinned to `nightly-2026-08-24` | `not_run`, `qualified-call-locator-partial` | none |

No positive gives a definite, complete finding. The resolved,
summarized `remove_dir_all` call still reports `uncovered_boundary=true` and
"call target requires whole-program Rust dispatch refinement", so
`scripts/rust-sast-gate.py` would reject every positive. Promoting a rule now
would ship findings that never prove themselves, so the lead stays blocked on
bifrost-dev#10004.

## #298 and #299: toolchain-gated flows

Rust toolchain evidence works on 0.15.1. A `rust-toolchain.toml` pin gives a
`locked` row, `:version-range` selects it, and `target-of` of a call site
returns the `build_project_id` that the row carries as `declared_by`. But no
policy form joins that evidence to a taint sink. A sink selector that wraps a
`join` fails validation (`unknown S-expression form` for `join`), and an
assertion can't consume taint findings. That gap is bifrost-dev#10005. It
blocks every affected-version data-flow lead, including the premium crate
leads.

- #298: `raw.parse()` and `raw.parse::<Ipv4Addr>()` have no target
  (`dispatch outcome=unproven, coverage=open, target_count=0`).
  `Ipv4Addr::from_str(&raw)` resolves, but its binding coverage is
  `unknown`. Fixed toolchains reject leading zeros, so there is no
  version-independent slice.
- #299: `build-configuration-of` reports `os cygwin`, `target
  x86_64-pc-cygwin`, `os_source configuration`. The same
  `.cargo/config.toml` that sets the target also makes the toolchain
  predicate incomplete (bifrost-dev#9902), so every positive would be
  inconclusive.

## Reproduce

```sh
cd probe/297-remove-dir-all
BIFROST_OPEN_SEMANTIC_PACK_BUNDLE=<packs-0.10.0>/bifrost-semantic-packs \
BIFROST_WORKSPACE_SEMANTIC_MODELS=on BIFROST_SEMANTIC_PACK_DOWNLOAD=off \
BIFROST_CACHE_DIR=$(mktemp -d) bifrost --policy --no-builtin-policies \
  --no-incremental --root . --policy-file .bifrost/policies/remove-dir-all.rqlp \
  --sources src/a_var.rs --format json
# std-pack variant: copy with-rust-stdlib-packs.json to .bifrost/packs.json
# (and pinned-rust-toolchain.toml to rust-toolchain.toml for the exact pin)

cd ../298-ip-parse
for q in toolchain bindings bindings2 target; do bifrost --root . --query-file $q.rql; done
bifrost --policy --no-builtin-policies --no-incremental --root . \
  --policy-file .bifrost/policies/gated.rqlp --format json   # validation error

cd ../299-cygwin
for q in build-configuration toolchain; do bifrost --root . --query-file $q.rql; done
```

Use the exact engine above. The `bifrost` on `PATH` may be older. Nothing in
the probes is built or run. [`outcomes.json`](outcomes.json) records the
engine identity, input hashes and observations.

## Promotion criteria

- #297 ships as an opt-in rule once bifrost-dev#10004 closes the
  model-declared `remove_dir_all` call. Then `a_var` must give a definite,
  complete finding, `e_constant` must be clean, and the `args`, `stdin`
  and `if let` cases must stay explicitly inconclusive until #9920 and the
  `values` gap close. The research model then moves to `semantic-packs/`
  with its native job.
- #298, #299 and the affected-toolchain part of #297 need bifrost-dev#10005.
  #298 also needs `str::parse` resolved to `FromStr` (bifrost-dev#6542).
  #299 also needs bifrost-dev#9902.

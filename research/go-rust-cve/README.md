# Go and Rust CVE lead qualification on Bifrost 0.15.0

**Outcome: no Go or Rust CVE lead can ship as a rule on Bifrost 0.15.0.**
All 26 open `[Go] CVE-…` leads and all 4 `[Rust] CVE-…` leads depend on the
toolchain that builds the project. The engine publishes no Go toolchain,
module or target evidence, and no Rust toolchain or target evidence. Each
lead also has a fixed-toolchain near miss, so without that evidence every
patched project would be reported. The leads require that missing version
coverage stays typed incomplete rather than approximated, so none is
promoted to `rules/`.

The one version-independent slice tried, gob decoding of network data (#192),
reaches a definite, complete finding once its models are fixed. It still
can't ship, because any call through `net.Conn` or `net.Listener` keeps the
run inconclusive (see below).

The files under `probe/` are research inputs, not registered pack content.
They don't change locked policy or semantic-pack content.

## Engine

Official `v0.15.0` release, `bifrost-v0.15.0-universal-apple-darwin.tar.gz`,
downloaded with `gh release download v0.15.0 --repo BrokkAi/bifrost`.

- Archive SHA-256: `c91c0bd38e4c6c0def86dc75acf8fa6d750b23a45894a28a76115fb8af034eda`. It matches the release `.sha256`.
- Binary SHA-256: `47e3e2da0a64ba65b447337b43952478deebbed7af3aa92d835d3a5ad458da96`.
- Build identity: `09a2503c5f7ced1630a9e3c445ead53dfc5925e8`.
- Evaluation date: 2026-11-02.

## Shared blockers

| Blocker | Issue | Leads |
| --- | --- | --- |
| No Go toolchain or module version evidence. `(dependency-evidence)` on a module with `go 1.19`, `toolchain go1.19.0` and a `require` returns no rows: `Go selected dependency publication unavailable: static dependency evidence is unavailable for this analyzer`. | [bifrost-dev#9047](https://github.com/BrokkAi/bifrost-dev/issues/9047) | All 26 Go CVE leads |
| No GOOS/GOARCH or build-constraint fact for a Go file. `build_target` has no platform field, and `target-of` is Maven-only. | [bifrost-dev#9048](https://github.com/BrokkAi/bifrost-dev/issues/9048) | #172, #181, #182, #183, #185, #194 |
| No Rust toolchain or target evidence. Cargo rows exist, including `serde` from `git+ssh://…`, but nothing exposes `rust-toolchain.toml`, `rust-version` or build targets. | [bifrost-dev#9049](https://github.com/BrokkAi/bifrost-dev/issues/9049) | #58, #59, #60, #61 |
| Go calls through a model-declared stdlib interface (`conn.Close()`, `ln.Accept()`) stay `dispatch unproven, coverage open`, even with complete interface-member summaries. | [bifrost-dev#9053](https://github.com/BrokkAi/bifrost-dev/issues/9053) | #192, and any Go network-input slice |
| The public Go declaration models set no `callable_family_complete`, so `resolved-call "net.Dial"` and `"os.Open"` are refused as partial. | [#213](https://github.com/BrokkAi/bifrost-packs/issues/213) (this repository) | #192, and any Go `resolved-call` rule |

## #192 gob decoding: the version-independent slice

The `encoding/gob` package documentation says the decoder is not hardened
against adversarial input. So network bytes reaching `gob.NewDecoder` are
worth reviewing on any toolchain, not only on the toolchains affected by
CVE-2024-34156. The probe policy `probe/.bifrost/policies/192-gob-network.rqlp`
is a may-taint policy with `require-model`. Its sources are `net.Dial` and
`net.Listener.Accept`, bound with `(result :index 0)`. Its sink is formal 0
of `encoding/gob.NewDecoder`.

Models in `probe/.bifrost/semantic-models/`:

- `bifrost.research.go-cve-probe-declarations` declares `gob.NewDecoder` and
  `(*gob.Decoder).Decode`, with `callable_family_complete` and the pointer
  receiver form. `bifrost.research.go-cve-probe` has complete procedure
  summaries for those two calls and for `net.Conn.Close()` and
  `net.Listener.Accept()`. These are research models only. They must not
  be copied into `semantic-packs/`.
- `go-stdlib-net-declarations.callable-family-complete.json` is
  `bifrost.go.stdlib.net-declarations` 2.0.0 with only one change:
  `callable_family_complete: true` on `Dial`, `Accept` and both `Close`
  members. It keeps the published pack ID, so it overrides the copy the
  engine embeds. That change is what #213 asks for.

Results, run from `probe/` with `--sources 192-gob-network/<case>`:

| Case | Result |
| --- | --- |
| `positive-dial` | 1 finding at `main.go:17`, definite, proven, complete. The run is "proven by summary", the same shape as the shipped C# model-backed rules. |
| `unknown-defer-close` | The same finding, but the run is `inconclusive (partial_discovery)`. `defer conn.Close()` leaves the procedure's value-flow snapshot unknown. |
| `unknown-accept` | 0 findings, `inconclusive`. The `Listener.Accept` source selector is partial: `dispatch outcome=unproven, coverage=open`. |
| `near-miss-local-reader` | 0 findings, complete. |
| `positive-dial` without the patched net model | inconclusive, `qualified-call-locator-partial` for `net.Dial` and `net.Listener.Accept` |

`192-gob-network/go-close-bindings.rql` shows the cause directly. Run over
the whole probe root, `conn.Close()` reports `callee_unresolved`,
`dispatch_outcome=unproven`, `dispatch_coverage=open`.

Nearly every real connection is closed with `defer conn.Close()`, and the
server-side case (`Accept`) never binds. A rule built on this would be
inconclusive on almost all real code. It also can't report the server-side
case the advisory describes. It stays a research probe until #213 and
bifrost-dev#9053 land.

## Per-lead outcomes

Every Go CVE lead is blocked by bifrost-dev#9047. The table lists further
blockers where this pass established them. "Not probed" means the lead
already fails on version evidence, and its code half was not exercised on
0.15.0.

| Lead | Advisory | Outcome | Further blockers |
| --- | --- | --- | --- |
| #50 | CVE-2023-39325 | Blocked by engine | Not probed: HTTP/2 server configuration facts. |
| #51 | CVE-2023-29406 | Blocked by engine | Not probed: request `Host` field flow. No public Go request source binds (#213). |
| #52 | CVE-2022-30633 | Blocked by engine | Not probed: struct-tag facts for `xml:",any"`. |
| #53 | CVE-2023-24538 | Blocked by engine | Not probed: html/template context modeling. |
| #54 | CVE-2022-2879 | Blocked by engine | Not probed: archive/tar input flow. |
| #55 | CVE-2023-29409 | Blocked by engine | Not probed: TLS peer-certificate flow. |
| #56 | CVE-2021-41771 | Blocked by engine | Not probed: debug/macho input flow. |
| #57 | CVE-2021-33197 | Blocked by engine | Not probed: proxy topology. |
| #172 | CVE-2026-56857 | Blocked by engine | bifrost-dev#9048 (GOOS). |
| #173 | CVE-2026-94448 | Blocked by engine | Not probed: html/template context modeling. |
| #174 | CVE-2026-78667 | Blocked by engine | Otherwise a version fact on an exact `http.FileServer`/`ServeContent` call, which also needs #213. |
| #175 | CVE-2026-42504 | Blocked by engine | Not probed: untrusted mail-header source. |
| #181 | CVE-2022-29804 | Blocked by engine | bifrost-dev#9048 (GOOS). |
| #182 | CVE-2023-45283 | Blocked by engine | bifrost-dev#9048 (GOOS). |
| #183 | CVE-2022-30580 | Blocked by engine | bifrost-dev#9048 (GOOS). |
| #184 | CVE-2025-47906 | Blocked by engine | Not probed: request source into `exec.Command` (#213). |
| #185 | CVE-2022-41720 | Blocked by engine | bifrost-dev#9048 (GOOS). |
| #186 | CVE-2023-45289 | Blocked by engine | Not probed: `http.Client` field facts and URL provenance. |
| #187 | CVE-2025-47910 | Blocked by engine | Not probed: ServeMux registration facts. |
| #188 | CVE-2024-24790 | Blocked by engine | Not probed: guard-to-dial correlation. |
| #189 | CVE-2025-22874 | Blocked by engine | Not probed: composite-literal slice facts. |
| #190 | CVE-2024-24785 | Blocked by engine | Not probed: template context modeling. |
| #191 | CVE-2022-32190 | Blocked by engine | No Go request source binds (#213). A version-independent traversal slice exists, because `JoinPath` with an absolute base path still resolves `..` on fixed toolchains. It needs request sources first. |
| #192 | CVE-2024-34156 | Blocked by engine | Version-independent slice probed above: bifrost-dev#9053 and #213. |
| #193 | CVE-2024-24784 | Blocked by engine | Not probed: result-field flow into comparisons. |
| #194 | CVE-2025-0913 | Blocked by engine | bifrost-dev#9048 (GOOS). |
| #58 | CVE-2024-24576 | Blocked by engine | bifrost-dev#9049 (toolchain and Windows target). |
| #59 | CVE-2024-43402 | Blocked by engine | bifrost-dev#9049 (toolchain and Windows target). |
| #60 | CVE-2022-46176 | Blocked by engine | bifrost-dev#9049 (Cargo toolchain). The `git+ssh` dependency row exists. `net.git-fetch-with-cli` precedence belongs to bifrost-dev#3768. |
| #61 | CVE-2022-36113 | Blocked by engine | bifrost-dev#9049 (Cargo toolchain). Alternate-registry rows were not probed. |

## Layout and reproduction

```
probe/
  .bifrost/policies/192-gob-network.rqlp
  .bifrost/semantic-models/               research models (see above)
  192-gob-network/                        one Go module; one package per case
  version-evidence/go-module/             go.mod with go/toolchain directives, a _windows.go file
  version-evidence/rust-crate/            Cargo.toml with an ssh git dependency, rust-toolchain.toml
```

The `go.sum` hashes are placeholders. Nothing was built or run.

Run with the exact engine above. The `bifrost` on `PATH` may be older.

```sh
cd probe
BIFROST_OPEN_PACKS_DISABLE=1 BIFROST_SEMANTIC_PACK_DOWNLOAD=off bifrost --policy \
  --no-builtin-policies --no-incremental --root . \
  --sources 192-gob-network/positive-dial \
  --policy-file .bifrost/policies/192-gob-network.rqlp
BIFROST_WORKSPACE_SEMANTIC_MODELS=on BIFROST_OPEN_PACKS_DISABLE=1 bifrost --root . \
  --query-file 192-gob-network/go-close-bindings.rql
cd version-evidence/go-module && bifrost --root . --query-file dependency-evidence.rql
cd ../rust-crate && bifrost --root . --query-file dependency-evidence.rql
```

[`outcomes.json`](outcomes.json) records the engine identity, input hashes and
observations.

## Promotion criteria

- A Go CVE lead can move into `rules/` once the engine publishes Go
  toolchain evidence that a policy can join to the module owning a call site.
  The fixed-toolchain near miss must then be excluded, and an unknown
  toolchain must stay incomplete. Windows-only leads also need
  bifrost-dev#9048.
- The #192 gob slice can ship once #213 is released and bifrost-dev#9053
  lets `defer conn.Close()` and `Accept` bind. Rerun the four probe cases
  then. `unknown-defer-close` and `unknown-accept` must become complete,
  `unknown-accept` must report its flow, and the near miss must stay clean.
- A Rust CVE lead needs bifrost-dev#9049. #58 and #59 also need
  `std::process::Command` argument flow, and the std receiver declarations
  in #208.

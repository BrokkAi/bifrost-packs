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
reaches a definite, complete finding once its models are fixed. On 0.15.0 it
couldn't ship, because any call through `net.Conn` or `net.Listener` kept the
run inconclusive. On 0.15.1 it ships as a rule; see the 0.15.1 recheck below.
No toolchain-gated Go lead ships on 0.15.1.

The files under `probe/` are research inputs, not registered pack content.
They don't change locked policy or semantic-pack content.

## Bifrost 0.15.1 recheck

Rechecked on 2026-11-05 against the official `v0.15.1` release
(`bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`, archive SHA-256
`4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`, which matches
the release digest; binary SHA-256
`78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`; build
identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`). Every run used a fresh
`BIFROST_CACHE_DIR`. Inside a worktree of this repository, the engine otherwise
reuses the main checkout's `.bifrost/cache`, even with `--no-incremental`.

- **#192 ships its version-independent slice** as
  `bifrost.security.go.gob-decode-network-input`. It uses the new
  `bifrost.go.stdlib.encoding-gob` models and the `net.Conn` and `net.Listener`
  summaries in `bifrost.go.stdlib.net` 2.1.0. Those summaries claim
  `covers_overrides`. On 0.15.1 a call through a model-declared interface binds
  (bifrost-dev#9053), but dispatch closes only through a summary that makes
  that claim. `Decoder.Decode` has no summary, because the schema can't
  express its write into the argument. So every run that decodes is
  inconclusive, although its findings are definite. The fixture README has
  the details.
- **The toolchain gate is still missing.** Go `dependency-evidence` exists now
  (bifrost-dev#9047), but the `go` and `toolchain` directives are only
  `constraint` rows. `probe/version-evidence/go-module/toolchain-range.rql`
  returns no rows, and every predicate is unresolved. No `locked` or
  `installed` Go toolchain row exists, even with `GOTOOLCHAIN` set.
  `go-target-of.rql` returns no rows (`topology_derivation_incomplete`), so a
  Go call site can't reach its module's evidence either. The Go
  platform-leads session filed both gaps as
  [bifrost-dev#9867](https://github.com/BrokkAi/bifrost-dev/issues/9867).
  Every toolchain-gated Go lead is blocked on it.
- **Request sources** (#51, #184, #191, and the #56 slice) still wait on draft
  [#225](https://github.com/BrokkAi/bifrost-packs/pull/225). Its engine
  prerequisite, bifrost-dev#9255, closed on 2026-11-03 through PR #9288,
  before v0.15.1. The draft itself was not rechecked here.
- **Code-half facts, probed with `--list-row-schemas`:** there are no Go
  struct-tag rows (#52) and no html/template context rows (#53, #173, #190).

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
| 0.15.0: no Go toolchain or module version evidence. `(dependency-evidence)` on a module with `go 1.19`, `toolchain go1.19.0` and a `require` returns no rows: `Go selected dependency publication unavailable: static dependency evidence is unavailable for this analyzer`. Fixed in 0.15.1. | [bifrost-dev#9047](https://github.com/BrokkAi/bifrost-dev/issues/9047) | All 26 Go CVE leads |
| 0.15.1: no exact Go toolchain version and no Go code-to-module relation (see the recheck above). | [bifrost-dev#9867](https://github.com/BrokkAi/bifrost-dev/issues/9867) | Every toolchain-gated Go CVE lead |
| No GOOS/GOARCH or build-constraint fact for a Go file. `build_target` has no platform field, and `target-of` is Maven-only. | [bifrost-dev#9048](https://github.com/BrokkAi/bifrost-dev/issues/9048) | #172, #181, #182, #183, #185, #194 |
| No Rust toolchain or target evidence. Cargo rows exist, including `serde` from `git+ssh://…`, but nothing exposes `rust-toolchain.toml`, `rust-version` or build targets. | [bifrost-dev#9049](https://github.com/BrokkAi/bifrost-dev/issues/9049) | #58, #59, #60, #61 |
| Go calls through a model-declared stdlib interface (`conn.Close()`, `ln.Accept()`) stay `dispatch unproven, coverage open`, even with complete interface-member summaries. Fixed in 0.15.1 for summaries that claim `covers_overrides`. | [bifrost-dev#9053](https://github.com/BrokkAi/bifrost-dev/issues/9053) | #192, and any Go network-input slice |
| The public Go declaration models set no `callable_family_complete`, so `resolved-call "net.Dial"` and `"os.Open"` are refused as partial. Fixed by #215. | [#213](https://github.com/BrokkAi/bifrost-packs/issues/213) (this repository) | #192, and any Go `resolved-call` rule |

## #192 gob decoding: the version-independent slice

This section records the 0.15.0 probe. The 0.15.1 outcome is in the recheck
above and in the rule's fixture README.

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

On 0.15.0 every Go CVE lead was blocked by bifrost-dev#9047. The rows for
#50-#57, #173, #175, #184, #186-#193 reflect the 0.15.1 recheck. "Not probed"
means the lead already fails on version evidence, and its code half was not
exercised.

| Lead | Advisory | Outcome | Further blockers |
| --- | --- | --- | --- |
| #50 | CVE-2023-39325 | Blocked by engine | bifrost-dev#9867. No version-independent slice, because patched toolchains fix the bug. No public model declares `net/http.Server` or its HTTP/2 settings. |
| #51 | CVE-2023-29406 | Blocked by engine | bifrost-dev#9867. No public Go request source binds yet (draft #225). |
| #52 | CVE-2022-30633 | Blocked by engine | bifrost-dev#9867. 0.15.1 has no Go struct-tag rows, so `xml:",any"` can't be selected. |
| #53 | CVE-2023-24538 | Blocked by engine | bifrost-dev#9867. 0.15.1 has no html/template context rows. |
| #54 | CVE-2022-2879 | Blocked by engine | bifrost-dev#9867. No version-independent slice, because fixed toolchains bound header sizes. |
| #55 | CVE-2023-29409 | Blocked by engine | bifrost-dev#9867. No version-independent slice, because fixed toolchains cap the RSA key size. |
| #56 | CVE-2021-41771 | Blocked by engine | bifrost-dev#9867. A version-independent slice exists, because `debug/macho` is documented as not hardened against adversarial input. It has no untrusted byte source: upload sources wait on #225, and `io.ReadAll` and `Conn.Read` are unmodeled. |
| #57 | CVE-2021-33197 | Blocked by engine | bifrost-dev#9867. Not probed: proxy topology. |
| #172 | CVE-2026-56857 | Blocked by engine | bifrost-dev#9048 (GOOS). |
| #173 | CVE-2026-94448 | Blocked by engine | bifrost-dev#9867. 0.15.1 has no html/template context rows. |
| #174 | CVE-2026-78667 | Blocked by engine | Otherwise a version fact on an exact `http.FileServer`/`ServeContent` call, which also needs #213. |
| #175 | CVE-2026-42504 | Blocked by engine | bifrost-dev#9867. No version-independent slice. No public `mime` or `net/mail` model. |
| #181 | CVE-2022-29804 | Blocked by engine | bifrost-dev#9048 (GOOS). |
| #182 | CVE-2023-45283 | Blocked by engine | bifrost-dev#9048 (GOOS). |
| #183 | CVE-2022-30580 | Blocked by engine | bifrost-dev#9048 (GOOS). |
| #184 | CVE-2025-47906 | Blocked by engine | bifrost-dev#9867. Request source into `exec.Command` waits on draft #225. |
| #185 | CVE-2022-41720 | Blocked by engine | bifrost-dev#9048 (GOOS). |
| #186 | CVE-2023-45289 | Blocked by engine | bifrost-dev#9867. No public model declares `http.Client` fields or `CheckRedirect`. |
| #187 | CVE-2025-47910 | Blocked by engine | bifrost-dev#9867 only. The code half is one exact call, `(*http.CrossOriginProtection).AddInsecureBypassPattern`, which needs only a declaration. No version-independent slice, because 1.25.1 fixes it. |
| #188 | CVE-2024-24790 | Blocked by engine | bifrost-dev#9867. Not probed: guard-to-dial correlation. |
| #189 | CVE-2025-22874 | Blocked by engine | bifrost-dev#9867. The public crypto/x509 declarations cover only `IsEncryptedPEMBlock`, so `VerifyOptions` isn't declared. |
| #190 | CVE-2024-24785 | Blocked by engine | bifrost-dev#9867. 0.15.1 has no html/template context rows. |
| #191 | CVE-2022-32190 | Blocked by engine | bifrost-dev#9867. A version-independent traversal slice exists, because `JoinPath` with an absolute base path still resolves `..` on fixed toolchains. It still needs request sources (draft #225). |
| #192 | CVE-2024-34156 | **Version-independent slice implemented** | `bifrost.security.go.gob-decode-network-input` reports definite findings, but runs that decode are inconclusive (`Decode` is unmodeled). The affected-toolchain part is blocked by bifrost-dev#9867. |
| #193 | CVE-2024-24784 | Blocked by engine | bifrost-dev#9867. Not probed: result-field flow into comparisons. No public `net/mail` model. |
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
- The #192 gob slice shipped on 0.15.1 (see the recheck above). Its
  affected-toolchain part follows the first criterion.
- A Rust CVE lead needs bifrost-dev#9049. #58 and #59 also need
  `std::process::Command` argument flow, and the std receiver declarations
  in #208.

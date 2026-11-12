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
| No Rust toolchain or target evidence. Cargo rows exist, including `serde` from `git+ssh://…`, but nothing exposes `rust-toolchain.toml`, `rust-version` or build targets. Fixed in Bifrost 0.15.1; see [Rust leads on Bifrost 0.15.1](#rust-leads-on-bifrost-0151). | [bifrost-dev#9049](https://github.com/BrokkAi/bifrost-dev/issues/9049) (closed) | #58, #59, #60, #61 |
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

## Bifrost 0.15.1 recheck: Windows and toolchain leads

**Outcome: #172, #174, #181, #182, #183, #185 and #194 are still blocked by
engine on Bifrost 0.15.1.** bifrost-dev#9047 and #9048 shipped, but only the
platform half is usable. A toolchain range over Go evidence can never match,
so a rule can't tell an affected toolchain from a fixed one.

Engine: official `v0.15.1` release, `bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`.

- Archive SHA-256: `4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`. It matches the release `.sha256`.
- Binary SHA-256: `78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`.
- Build identity: `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`.
- Host Go: `go1.26.0 darwin/arm64`.
- Evaluation date: 2026-11-05.

The probe is `probe/platform-toolchain/`. It has three modules, each with the
same unconstrained `main.go`, a `lock_windows.go` and a `lock_linux.go`
(`//go:build linux`):

| Module | `go.mod` | Case |
| --- | --- | --- |
| `affected/` | `go 1.26`, `toolchain go1.26.8` | positive for the CVE-2026-78667 range |
| `fixed/` | `go 1.27`, `toolchain go1.27.2` | fixed-toolchain near miss |
| `none/` | `go 1.26`, no `toolchain` | unknown toolchain |

What works:

- `build-configuration-of` reports each file's own constraint, whatever the
  host: `lock_windows.go` has `os_scope restricted`, `os_values windows`.
  `lock_linux.go` has `os_values android linux`, so it is never built for
  Windows. `main.go` has `os_scope any`, so it is undecided. This is enough
  to drop the other-GOOS and constraint-excluded near misses.

What still blocks a rule:

| Gap | Observation | Issue |
| --- | --- | --- |
| No exact Go toolchain evidence | `go` and `toolchain` directives are only `constraint` rows. `toolchain-range.rql` (`<1.26.9 \|\| >=1.27 <1.27.2`) returns 0 rows for all three modules, each with `dependency version predicate unresolved ... no complete exact version evidence`. `toolchain-exact.rql` (`:kinds [locked installed]`) returns nothing. Affected, fixed and unpinned modules can't be told apart. | [bifrost-dev#9867](https://github.com/BrokkAi/bifrost-dev/issues/9867) |
| No Go code-to-module ownership | `target-of.rql` returns no rows (`topology_derivation_incomplete`; the step reads Maven only). A call site can't reach the `declared_by` of its module's toolchain rows. | [bifrost-dev#9867](https://github.com/BrokkAi/bifrost-dev/issues/9867) |
| Windows-only files aren't analyzed on other hosts | `openfile-binding.rqlp`, with the public `go-stdlib-os` models: in `affected/` and `none/`, only `main.go` binds. The calls in `lock_windows.go` and `lock_linux.go` stay `dispatch outcome=unknown, coverage=open`, so the run is inconclusive. That is correctly explicit, but a Windows-only call site needs a scan under `GOOS=windows`. | none needed |
| Failed discovery reports complete | In `fixed/`, `go list` fails (`go.mod requires go >= 1.27`, `GOTOOLCHAIN=local`). All three calls bind as definite and the run is complete, while `build-configuration-of` still says the two files are `excluded`. | [bifrost-dev#9869](https://github.com/BrokkAi/bifrost-dev/issues/9869) |

The public Go models also lack the leads' APIs. None declares
`http.FileServer`, `ServeContent`, `ServeFile`, `http.Dir`, `os.DirFS`,
`os.OpenRoot`, `(*os.Root).MkdirAll`, `filepath.Clean`, `IsAbs`, `IsLocal`
or `exec.Cmd`. A `resolved-call "net/http.FileServer"` locator resolves to no
exact identity. Only `os.OpenFile` (#194) binds. That model work belongs in
this repository, but it is moot until the toolchain gate can answer.

## Rust leads on Bifrost 0.15.1

**#60 ships as an opt-in rule. #58, #59 and #61 stay blocked.**

Engine: the official `v0.15.1` release asset
`bifrost-v0.15.1-aarch64-apple-darwin`. Its binary SHA-256 is
`78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33` and its
build identity is `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`. Evaluation date:
2026-11-05.

### What 0.15.1 exposes

- **Exact toolchain pins.** `rust-toolchain.toml` `channel = "1.66.0"` and a
  legacy `rust-toolchain` file give a `rust-toolchain` row with
  `evidence_kind locked` and `exact_version`. `:version-range "<1.66.1"`
  selects it, and a fixed release doesn't.
- **Unpinned toolchains stay unresolved.** `stable`, `nightly-2022-12-01`,
  `1.65` and a host-qualified channel are unresolved, and so is a project with
  only `rust-version` or no toolchain file. The range answer is then
  `dependency version predicate unresolved ... no complete exact version
  evidence`, which is incomplete, not empty.
- **Package join.** Toolchain and Cargo rows of one package share
  `declared_by`, which is the `build_project_id` that `target-of` gives a
  Rust file. A relational assertion can join them. A locked row carries
  `declared_by` only once its declaration-to-lock association resolves.
- **Targets.** `build-configuration-of` reports `.cargo/config.toml`
  `build.target` as `os windows`, `os_source configuration`. A toolchain
  file's `targets` list adds an `os_source toolchain` row next to the host
  row, but that list only names targets to install. The file's own `#[cfg]`
  stays `unknown`.
- **Cargo config isn't read.** A workspace `.cargo/config.toml` makes every
  Cargo row incomplete: `dependency evidence Unsupported at
  .cargo/config.toml: Cargo configuration overrides are owned by #3768`.
  bifrost-dev#3768 is closed, but no 0.15.1 row exposes `[registries]`,
  `[source]` replacement or `[net] git-fetch-with-cli`. That's now tracked
  in bifrost-dev#9902.
- **No capability name.** No advertised capability name covers dependency
  evidence. Bifrost 0.15.0 rejects a `rust-toolchain` version range at
  validation: `version_ranges requires exactly one supported ecosystem:
  cargo, npm or nuget`.

### Outcomes

| Lead | Outcome | Evidence |
| --- | --- | --- |
| #60 CVE-2022-46176 | Rule: `bifrost.security.rust.cargo-ssh-git-host-key-unverified`, opt-in, `bifrost.security` 2.2.0 | The rule joins a locked `git+ssh://` Cargo row to a toolchain row before 1.66.1 in the same package. 10 fixture cases pass. Three positives (direct, transitive, legacy toolchain file) are complete with one finding each. Two near misses (1.66.1, an HTTPS source) are complete with none. Five unknowns (no toolchain file, `stable`, `rust-version` only, no `Cargo.lock`, a workspace `git-fetch-with-cli = true`) are inconclusive. See `research/rust-cargo-ssh-git/qualification.json`; held out of `bifrost.security` 3.0.0 (rules 0.13.0). |
| #61 CVE-2022-36113 | Blocked by engine | `probe/version-evidence/rust-alt-registry/`. The declared row has source `registry-name:corp`, but it never associates with its `sparse+https://…` lock entry. The registry index lives in the unread Cargo config. The declared-row join reports the dependency, but the run is inconclusive. The locked-row join finds no group, because the unassociated lock row has no `declared_by`. Every alternate-registry positive would be inconclusive. Crates.io-only can't be proven when a config file is present. Engine issue: bifrost-dev#9902. |
| #58 CVE-2024-24576 | Blocked: #208 | Toolchain and target evidence are now available. Without std declarations, `Command::new("run.bat").arg(arg)` gives `callee_unresolved`, `dispatch_outcome unproven`, `coverage open` (`probe/version-evidence/rust-crate/command-arg-bindings.rql`). #208 lists `std.process.Command` `new`, `arg` and `args`. Not probed: binding the batch-file program and the untrusted argument to one builder. |
| #59 CVE-2024-43402 | Blocked: #208 | As #58. It also needs Windows trailing-space and trailing-period normalization of the program name, and the 1.77.2 to 1.80.x range. |

Known limits of the #60 rule: ambient configuration isn't read. That covers
`$CARGO_HOME/config.toml`, `CARGO_NET_GIT_FETCH_WITH_CLI`, git `insteadOf`
rewrites, `RUSTUP_TOOLCHAIN` and rustup overrides (rows report
`rust.toolchain_override: unobserved`). An independently patched Cargo
matches by release number. SSH registry indexes aren't covered.

Reproduce from `probe/version-evidence/`:

```sh
cd rust-crate && bifrost --root . --query-file dependency-evidence.rql
bifrost --root . --query-file build-configuration.rql
bifrost --root . --query-file command-arg-bindings.rql
cd ../rust-alt-registry && bifrost --root . --query-file dependency-evidence.rql
bifrost --policy --no-builtin-policies --no-incremental --root . \
  --policy-file alt-registry-declared.rqlp --format json
```

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
| #172 | CVE-2026-56857 | Blocked by engine | 0.15.1: no exact toolchain or module ownership (bifrost-dev#9867); no `os.Root` model. |
| #173 | CVE-2026-94448 | Blocked by engine | bifrost-dev#9867. 0.15.1 has no html/template context rows. |
| #174 | CVE-2026-78667 | Blocked by engine | 0.15.1: bifrost-dev#9867. #213 is fixed, but no model declares `FileServer`/`ServeContent`/`ServeFile`. |
| #175 | CVE-2026-42504 | Blocked by engine | bifrost-dev#9867. No version-independent slice. No public `mime` or `net/mail` model. |
| #181 | CVE-2022-29804 | Blocked by engine | 0.15.1: bifrost-dev#9867; no `filepath.Clean` model or Go request source. |
| #182 | CVE-2023-45283 | Blocked by engine | 0.15.1: bifrost-dev#9867; no `Clean`/`IsAbs`/`IsLocal` model. |
| #183 | CVE-2022-30580 | Blocked by engine | 0.15.1: bifrost-dev#9867; no `exec.Cmd` model. Struct-literal field facts not probed. |
| #184 | CVE-2025-47906 | Blocked by engine | bifrost-dev#9867. Request source into `exec.Command` waits on draft #225. |
| #185 | CVE-2022-41720 | Blocked by engine | 0.15.1: bifrost-dev#9867; no `http.Dir`/`FileServer`/`os.DirFS` model. |
| #186 | CVE-2023-45289 | Blocked by engine | bifrost-dev#9867. No public model declares `http.Client` fields or `CheckRedirect`. |
| #187 | CVE-2025-47910 | Blocked by engine | bifrost-dev#9867 only. The code half is one exact call, `(*http.CrossOriginProtection).AddInsecureBypassPattern`, which needs only a declaration. No version-independent slice, because 1.25.1 fixes it. |
| #188 | CVE-2024-24790 | Blocked by engine | bifrost-dev#9867. Not probed: guard-to-dial correlation. |
| #189 | CVE-2025-22874 | Blocked by engine | bifrost-dev#9867. The public crypto/x509 declarations cover only `IsEncryptedPEMBlock`, so `VerifyOptions` isn't declared. |
| #190 | CVE-2024-24785 | Blocked by engine | bifrost-dev#9867. 0.15.1 has no html/template context rows. |
| #191 | CVE-2022-32190 | Blocked by engine | bifrost-dev#9867. A version-independent traversal slice exists, because `JoinPath` with an absolute base path still resolves `..` on fixed toolchains. It still needs request sources (draft #225). |
| #192 | CVE-2024-34156 | **Version-independent slice implemented** | `bifrost.security.go.gob-decode-network-input` (opt-in) reports definite findings, but runs that decode are inconclusive (`Decode` is unmodeled). The affected-toolchain part is blocked by bifrost-dev#9867. |
| #193 | CVE-2024-24784 | Blocked by engine | bifrost-dev#9867. Not probed: result-field flow into comparisons. No public `net/mail` model. |
| #194 | CVE-2025-0913 | Blocked by engine | 0.15.1: bifrost-dev#9867 and #9869. `os.OpenFile` binds. |
| #58 | CVE-2024-24576 | Blocked (0.15.1) | Toolchain and target evidence now exist. `Command::arg` is unresolved without the std declarations in #208. |
| #59 | CVE-2024-43402 | Blocked (0.15.1) | As #58, plus Windows program-name normalization. |
| #60 | CVE-2022-46176 | Rule (0.15.1) | `bifrost.security.rust.cargo-ssh-git-host-key-unverified`, opt-in. A workspace `git-fetch-with-cli = true` stays inconclusive: Cargo config is unread, although bifrost-dev#3768 is closed (now bifrost-dev#9902). |
| #61 | CVE-2022-36113 | Blocked by engine (0.15.1) | Alternate-registry declarations never associate with their lock entries, because the Cargo config is unread. |

## Layout and reproduction

```
probe/
  .bifrost/policies/192-gob-network.rqlp
  .bifrost/semantic-models/               research models (see above)
  192-gob-network/                        one Go module; one package per case
  version-evidence/go-module/             go.mod with go/toolchain directives, a _windows.go file
  version-evidence/rust-crate/            Cargo.toml with an ssh git dependency, rust-toolchain.toml
  platform-toolchain/                     0.15.1: affected/fixed/none modules, Windows- and Linux-only files
  version-evidence/rust-alt-registry/     alternate-registry dependency, Cargo.lock, .cargo/config.toml (0.15.1)
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

For `probe/platform-toolchain/`, use the 0.15.1 engine. Run the queries from
the probe root. Run the binding policy once per module, with the two public
`go-stdlib-os` models copied into that module's `.bifrost/semantic-models/`:

```sh
cd probe/platform-toolchain
for q in toolchain-rows toolchain-range toolchain-exact build-configuration target-of; do
  BIFROST_OPEN_PACKS_DISABLE=1 BIFROST_SEMANTIC_PACK_DOWNLOAD=off \
    bifrost --root . --query-file $q.rql
done
m=affected   # then fixed, none
mkdir -p $m/.bifrost/semantic-models $m/.bifrost/policies
cp ../../../../semantic-packs/models/go-stdlib-os-declarations.json \
   ../../../../semantic-packs/models/go-stdlib-os.json $m/.bifrost/semantic-models/
cp .bifrost/policies/openfile-binding.rqlp $m/.bifrost/policies/
BIFROST_WORKSPACE_SEMANTIC_MODELS=on BIFROST_OPEN_PACKS_DISABLE=1 \
  BIFROST_SEMANTIC_PACK_DOWNLOAD=off bifrost --policy --no-builtin-policies \
  --no-incremental --root $m --policy-file .bifrost/policies/openfile-binding.rqlp
rm -rf $m/.bifrost
```

[`outcomes.json`](outcomes.json) records the engine identity, input hashes and
observations.

## Promotion criteria

- A Go CVE lead can move into `rules/` once the engine publishes Go
  toolchain evidence that a policy can join to the module owning a call site.
  The fixed-toolchain near miss must then be excluded, and an unknown
  toolchain must stay incomplete. Windows-only leads also need
  bifrost-dev#9048.
- On 0.15.1, #172, #174, #181, #182, #183, #185 and #194 have the GOOS facts
  they need, and wait on bifrost-dev#9867. Then add the public declaration
  models for each lead's API, and rerun `probe/platform-toolchain/`.
  `toolchain-range.rql` must match `affected/` only, `fixed/` must be a
  complete non-match, and `none/` must stay incomplete. #194 also needs
  bifrost-dev#9869, so that an excluded file can't produce a complete answer.
- The #192 gob slice shipped on 0.15.1 (see the recheck above). Its
  affected-toolchain part follows the first criterion.
- Bifrost 0.15.1 fixed bifrost-dev#9049, and #60 shipped on it. #58 and #59
  need the `std::process::Command` declarations in #208 first. Then rerun
  `command-arg-bindings.rql`, and probe builder correlation of the program
  and the argument. #61 needs Cargo config registries read, so that an
  alternate-registry declaration associates with its lock entry.

# Go data-flow CVE leads on Bifrost 0.15.1

Ten new Go standard-library leads from OSV, each with a taint or typestate
theoretical policy: BrokkAi/bifrost-packs#252–#261. **One ships**: the
version-independent part of #252 as
`bifrost.security.go.network-read-all-unbounded` (opt-in). The other nine are
blocked. Six wait on the engine, and three wait on the public request-source
declarations in draft #225. Every lead that depends on the toolchain version also
waits on bifrost-dev#9867. `outcomes.json` holds the full record.

The files under `probe/` are research inputs, not registered pack content. The
`bifrost.research.*` models in them are probe-only and record public Go 1.26.0
API names and signatures (BSD-3-Clause).

## Selection

Source: `https://osv-vulnerabilities.storage.googleapis.com/Go/all.zip`,
downloaded on 2026-11-05. I kept `stdlib` advisories where application code
decides reachability and the policy is a source-to-sink flow or an object
protocol. I dropped advisories whose CVE already appears in a `CVE-` title in
BrokkAi/bifrost-packs or BrokkAi/bifrost-premium-packs, along with `cmd/go`,
compiler, native-memory and upgrade-only advisories. I also dropped classes the
existing leads already cover: `filepath.Clean` on Windows (#181, #182), XML
recursion (#52) and redirect credentials (#186). Eight leads have a
version-independent part, where the API stays dangerous for untrusted input on
fixed toolchains. All ten are open placement.

## Engine

Official `v0.15.1` release, `bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`
(archive SHA-256
`4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`, matching
the release `.sha256`; binary SHA-256
`78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`; build
identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`). v0.15.2 was not out on
2026-11-05. Every run used `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off`, `--no-builtin-policies`,
`--no-incremental` and a fresh `BIFROST_CACHE_DIR`.

## Outcomes

| Lead | Advisory | Outcome | Blockers |
| --- | --- | --- | --- |
| #252 gzip / unbounded read | CVE-2022-30631 | **Implemented**, version-independent part | Scope: #9987. Toolchain: #9867 |
| #253 zip entry names | CVE-2021-27919 | Blocked by engine | #8282, #4687, #9867 |
| #254 tar header names | CVE-2025-58183 | Blocked by engine | #8282, #9867 |
| #255 regexp patterns | CVE-2022-24921 | Blocked (request declarations) | bifrost-packs#225, #9867 |
| #256 glob patterns | CVE-2022-30632 | Blocked (request declarations, filepath models) | bifrost-packs#225, #9867 |
| #257 varint reads | CVE-2020-16845 | Blocked by engine (toolchain only) | #9867 |
| #258 tls.Config mutation | CVE-2025-68121 | Blocked by engine | #9990, #9431, #9867 |
| #259 cgi Content-Type | CVE-2020-24553 | Blocked (request declarations) | bifrost-packs#225, #9867 |
| #260 DNS results | CVE-2021-33195 | Blocked by engine | #4687, #9988, #9989, #9867 |
| #261 SMTP PLAIN before STARTTLS | CVE-2017-15042 | Blocked by engine | #9431, #9867 |

Bare issue numbers are in BrokkAi/bifrost-dev. I filed #9987, #9988, #9989 and
#9990 in this round. The others already existed.

## Shipped rule (#252)

`bifrost.security.go.network-read-all-unbounded` reports `net.Dial`,
`net.DialTimeout` and `net.Listener.Accept` connections that reach
`io.ReadAll` or the source of `io.Copy`, directly or through
`gzip.NewReader`, with no `io.LimitReader` between them. It uses the new
`bifrost.go.stdlib.compress-gzip` and `bifrost.go.stdlib.io` models and their
declaration packs. The main fixture is `proven_by_summary` with four definite
findings, and both near misses are clean. The `incomplete/` cases (`bufio`,
`io.Copy`, a `go` handler) are inconclusive. Details are in
`fixtures/policy/bifrost.security/go-network-read-all-unbounded/README.md`.

The rule is broader than "decompression bomb": it also reports a raw
connection read to EOF. Narrowing it needs a label added at `gzip.NewReader`,
and `probe/252-gzip-transform` shows that such a transform finds the flow but
drops the source origin (bifrost-dev#9987; minimal repro in
`probe/transform-origin-model`, control in `probe/transform-origin-local`).

## What the probes show

- **Model fields** (#253, #254): reading `hdr.Name` from a `tar.Reader.Next`
  result is inconclusive with `access-path resolution … unknown`. That is
  bifrost-dev#8282: the native Go member walk cannot select model fields.
  `probe/253-zip-entry-name` also ranges over a model field slice
  (bifrost-dev#4687). With a `defer` in the same procedure the run is
  `unsupported (exceptional_control_flow)`.
- **Request sources** (#255, #256, #259): with a workspace-only declaration
  and summary for `net/http.Request.FormValue`, `probe/255-regexp-request` is
  `proven_by_summary`. It reports the positive, and the `regexp.QuoteMeta`
  near miss is clean. The engine is ready. The public declaration belongs to
  draft #225, which owns `go-stdlib-net-http-declarations`, so these leads wait
  for it rather than editing that pack here.
- **DNS results** (#260): `LookupCNAME` into `exec.Command(name, "-v")` is
  definite and complete. A `LookupTXT` slice element is `capability_incomplete
  (index_memory)` (bifrost-dev#4687). Any `append` of a tainted value fails the
  whole run with `internal_invariant` (`probe/append-invariant`,
  bifrost-dev#9988). `exec.Command(name)`, with no variadic argument, does not
  bind its summary (`probe/variadic-empty`, bifrost-dev#9989).
- **Typestate** (#258, #261): automaton events accept only `:calls`, so
  `probe/258-tls-typestate` is rejected (`unknown field :field-write for
  event`, bifrost-dev#9990). The SMTP protocol is expressible. Both its
  positive and its `StartTLS` near miss are possible/partial
  (`typestate-external-call`), because reviewed external summaries cannot
  state protocol-complete coverage (bifrost-dev#9431).
- **Toolchain** (all ten for their version-gated part): Go has no exact
  toolchain row and no code-to-module relation (bifrost-dev#9867, see
  `research/go-rust-cve/README.md`).

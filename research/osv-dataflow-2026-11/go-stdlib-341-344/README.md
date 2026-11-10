# Go standard-library CVE leads #341–#344 on Bifrost 0.15.1

Four Go standard-library leads filed on 2026-11-10:
BrokkAi/bifrost-packs#341–#344. **None ships.** Each advisory is fixed in a
Go release, and nothing in the affected API stays dangerous on a fixed
toolchain. A rule would have to report only call sites built by an affected
toolchain, and Bifrost 0.15.1 can't gate a call site on the Go toolchain
(bifrost-dev#9867). Three of the four are taint policies, and a taint policy
can't gate its sink on toolchain evidence even where that evidence exists
(bifrost-dev#10005). `outcomes.json` holds the record.

The earlier Go batch (#252–#261) is in [`../go/`](../go/README.md). Its
blockers still apply; this batch adds no new engine gap.

## Engine

Official `v0.15.1` release, `bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`
(archive SHA-256
`4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`, matching
the release `.sha256`; binary SHA-256
`78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`; build
identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`), with go1.26.0
darwin/arm64 on `PATH`. Runs used `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off` and a fresh `BIFROST_CACHE_DIR`.

## Outcomes

| Lead | Advisory | Kind | Outcome | Blockers |
| --- | --- | --- | --- | --- |
| #341 textproto error text in logs | CVE-2026-42507 | taint | Blocked by engine | #9867, #10005 |
| #342 `os.Root` trailing-slash symlinks | CVE-2026-39822 | taint | Blocked by engine | #9867, #10005; request sources in bifrost-packs#225 |
| #343 `ParseForm` parameter count | CVE-2025-61726 | call on an affected toolchain | Blocked by engine | #9867 |
| #344 NUL in `Cmd.Env` on Windows | CVE-2022-41716 | taint | Blocked by engine | #9867, #10005; request sources in bifrost-packs#225 |

Bare issue numbers are in BrokkAi/bifrost-dev. All were already filed; this
batch files nothing new.

## Why each lead needs the toolchain

- **#341.** Before Go 1.25.11 and 1.26.4, `net/textproto` put rejected peer
  input into its error text unescaped. The fixed releases quote it. Logging a
  textproto error is fine on a fixed toolchain, so there is no
  version-independent rule.
- **#342.** Before 1.25.12, 1.26.5 and 1.27.0-rc.2, `os.Root` followed a final
  symlink outside the root when the name ended in `/` (Unix). On fixed
  releases `os.Root` is the correct confinement, so an untrusted name reaching
  `Root.Open` is the intended use. The rule also needs an untrusted-path source
  (the Go request declarations are in draft bifrost-packs#225).
- **#343.** Before 1.24.12 and 1.25.6, `url.ParseQuery` (and so
  `Request.ParseForm`, `FormValue` and `PostFormValue`) had no limit on the
  number of parameters. This one needs no flow: a call to a parsing method in
  a module built by an affected toolchain is the finding. The probe shows it
  still can't be written (below).
- **#344.** Before 1.18.8 and 1.19.3, an embedded NUL in one `Cmd.Env` entry
  started another variable on Windows. The fixed releases reject it. It also
  needs Windows file selection (the analysis has to run with `GOOS=windows`;
  see the observation in bifrost-dev#9867) and a request source.

## Probe: #343 toolchain gate

[`probe/343-parseform-toolchain`](probe/343-parseform-toolchain/) is one
module with `go 1.25` and `toolchain go1.25.5` (an affected release) and a
handler that calls `r.ParseForm()`.

- `toolchain.rql`, `(dependency-evidence :ecosystem go-toolchain :version-range
  "<1.24.12 || >=1.25.0 <1.25.6")`: no rows, `truncated: true`, and
  `dependency version predicate unresolved … no complete exact version
  evidence` for both the `go` and `toolchain` directive rows. They are
  `constraint` rows, and no `locked` or `installed` toolchain row exists.
- `owner.rql`, `(target-of (file-of (language go (function))))`: no rows, with
  `topology_derivation_incomplete`. A Go file can't reach the module that
  declares the toolchain.

Both are the two gaps in bifrost-dev#9867, unchanged on 0.15.1. An assertion
rule for #343 needs both: an exact toolchain row and a relation from the call
site to its module.

## Next gates

1. bifrost-dev#9867: an exact (`locked` or `installed`) `go-toolchain` row and
   code-to-module ownership. Then #343 can ship as an assertion.
2. bifrost-dev#10005: a taint sink selector that can join dependency or
   toolchain evidence. Then #341 can be qualified, and #342 and #344 once the
   request declarations in bifrost-packs#225 land.

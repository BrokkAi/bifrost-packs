# Go network connection read to EOF fixture

Qualifies the version-independent part of the Go CVE lead
BrokkAi/bifrost-packs#252 (CVE-2022-30631). `compress/gzip` inflates without a
size bound and `io.ReadAll` reads until EOF, so a peer that controls a
connection controls how much the program allocates. A small gzip stream can
inflate to gigabytes. That holds on every Go toolchain. The CVE's own
stack-exhaustion part needs toolchain evidence the engine does not have
(`research/osv-dataflow-2026-11/go/README.md`).

The policy's sources are `net.Dial`, `net.DialTimeout` and
`net.Listener.Accept`. Its sinks are the reader operand of `io.ReadAll` and the
source operand of `io.Copy`. `io.LimitReader` is the sanitizer. All of them
bind through the reviewed models copied into `.bifrost/semantic-models`:

- `bifrost.go.stdlib.net-declarations` 2.1.0 and `bifrost.go.stdlib.net`
  2.1.0, unchanged from #192.
- `bifrost.go.stdlib.compress-gzip-declarations` 0.1.0 and
  `bifrost.go.stdlib.compress-gzip` 0.1.0. `NewReader` passes its reader to
  result 0. `Reader.Close` and `Reader.Multistream` have no transfers.
  `Reader.Read` is not modeled.
- `bifrost.go.stdlib.io-declarations` 0.1.0 and `bifrost.go.stdlib.io` 0.1.0.
  `ReadAll` passes its reader to result 0 and `LimitReader` passes its reader
  to its result. `io.Copy` is declared but not summarized: the schema cannot
  express its write into `dst`, and a complete summary with no transfers would
  claim it writes nothing.
- `bifrost.go.stdlib.os-declarations` and `bifrost.go.stdlib.os`, for the
  local-file near miss.

**Scope.** The policy also reports a connection read to EOF without
decompression. A decompression-only policy would add a label at
`gzip.NewReader`, but on Bifrost 0.15.1 a transform on a model-summarized call
drops the source origin and the finding is not projected
(bifrost-dev#9987). A raw connection read to EOF is the same unbounded
allocation, only without the amplification.

The policy is opt-in (`"activation": "opt-in"`). It has no corpus precision
measurement yet, and common real shapes (`bufio`, `io.Copy`, a handler started
with `go`) are inconclusive.

## Cases

- **Positives** (`probe.go`): `net.Dial` with `gzip.NewReader` and
  `io.ReadAll`, `Listener.Accept` with the same, `net.DialTimeout` read raw
  with `io.ReadAll`, and an accepted connection inflated by a helper.
- **Near misses** (`probe.go`): `io.ReadAll(io.LimitReader(zr, n))` on a dialed
  gzip stream, and a gzip file opened with `os.Open`.
- **Incomplete** (`incomplete/`, one package per case). `.bifrostignore` keeps
  this workspace out of the parent run.
  - `wrapped`: `gzip.NewReader(bufio.NewReader(conn))`. `bufio` has no
    reviewed model.
  - `copied`: `io.Copy(buf, zr)`. `io.Copy` has no summary, so the finding is
    `possible` and `partial`.
  - `goroutine`: the accept loop with `go handle(conn)`. The handler's call
    resolution is unknown.

## Validation

Bifrost 0.15.1 (`bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`, archive SHA-256
`4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`, checksum
verified against the release; binary SHA-256
`78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`; build
identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`), evaluation date
`2026-11-05`. Each run used `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off`, `--no-builtin-policies`,
`--no-incremental` and a fresh `BIFROST_CACHE_DIR`. The authored policy hash is
`01e9aa33b308535761ffafd882063e659ffb1672e2740e7229b122e67088b56a`. Its
resolved identity is workspace-required.

- This directory: `proven_by_summary`, 4 findings, all definite and complete:
  `probe.go:24` (source `:14`), `:38` (`:29`), `:48` (`:43`) and `:66`
  (`:53`). The two near misses report nothing.
- `incomplete/`: inconclusive (`partial_discovery`), with one possible, partial
  finding at `copied/copied.go:22`. Each case was also run alone with
  `--sources <case>`, and each is inconclusive on its own.
- Without the gzip and io models, the policy is `not_run`.

# Go gob decoding of network input fixture

Qualifies the version-independent part of the Go CVE lead
BrokkAi/bifrost-packs#192 (CVE-2024-34156). The `encoding/gob` documentation
says the decoder is not hardened against adversarial input, so a connection
that reaches `gob.NewDecoder` is reported on every Go toolchain. The CVE's
affected-toolchain part is not checked (see `research/go-rust-cve/README.md`).

The policy's sources are `net.Dial`, `net.DialTimeout` and
`net.Listener.Accept`. Its sink is the reader operand of
`encoding/gob.NewDecoder`. All of them bind through the reviewed models copied
into `.bifrost/semantic-models`:

- `bifrost.go.stdlib.net-declarations` 2.1.0 and `bifrost.go.stdlib.net`
  2.1.0. The 2.1.0 summaries cover the `net.Conn` and `net.Listener` members
  and claim `covers_overrides`, so calls through those interfaces close.
- `bifrost.go.stdlib.encoding-gob-declarations` 0.1.0 and
  `bifrost.go.stdlib.encoding-gob` 0.1.0.

## Cases

- **Positives** (`probe.go`): `net.Dial` with and without a deferred `Close`,
  `net.DialTimeout`, `Listener.Accept` with a deferred `Close`, and an
  accepted connection decoded in a helper.
- **Near misses** (`probe.go`): a function that holds an open connection but
  decodes a local snapshot reader, and an encoder over a local writer.
- **Incomplete** (`incomplete/`, one package per case). `.bifrostignore` keeps
  this workspace out of the parent run.
  - `wrapped`: `gob.NewDecoder(bufio.NewReader(conn))`. `bufio` has no
    reviewed model, so the sink selector is partial.
  - `goroutine`: the usual accept loop with `go handleConn(conn)`. The
    handler's call resolution is unknown.
  - `exchange`: `gob.NewEncoder(conn).Encode(q)` before decoding from the same
    connection. The procedure's call resolution is unknown. This happens even
    with no `Encoder.Encode` summary, so it isn't caused by the model.
  - `constant`: `net.DialTimeout(..., 5*time.Second)`. `time.Second` has no
    reviewed declaration, so the procedure's semantics are unknown.
  - `listenerclose`: `net.Listen`, `Accept`, deferred `Close` calls and a
    helper that decodes. The helper's call resolution is unknown. The same
    helper is complete when `Accept` is called on a listener parameter
    (`serveWithHelper`).
  - `deadline`: `conn.SetReadDeadline(...)` before decoding. The run is
    proven by summary, but the finding is `possible` and `partial`.

## Validation

Bifrost 0.15.1 (`bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`, checksum
verified against the release; build identity
`90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`), evaluation date `2026-11-05`. Each
run used `BIFROST_OPEN_PACKS_DISABLE=1`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`--no-builtin-policies`, `--no-incremental` and a fresh `BIFROST_CACHE_DIR`.
The authored policy hash is
`9ff3e4211e721dce4ae46c0b1a2caf931b7dc991610cd76e77be6af0b4dc8ff9`. Its
resolved identity is workspace-required.

- This directory: `proven_by_summary`, with 5 findings, all definite and
  complete: `probe.go:21`, `:33`, `:45`, `:57` and `:73`. The near misses
  produce no findings.
- `incomplete/`: inconclusive (`partial_discovery`). Each case was also run
  alone with `--sources <case>`. `deadline` is `proven_by_summary` with one
  possible, partial finding. Every other case is inconclusive on its own.
- Without the two gob models: `not_run` (`qualified-call-locator-zero` for
  `encoding/gob.NewDecoder`).
- With `bifrost.go.stdlib.net` 2.0.0, which has no interface-member
  summaries: inconclusive. Every function that calls `Close` or `Accept`
  reports unknown call resolution, and two findings drop to possible.

## Known limits

- Only raw `net` connections are sources. `tls.Dial`, `net.Dialer`,
  `*net.TCPListener.AcceptTCP` and HTTP request bodies have no reviewed
  source. A call to an unmodeled API leaves the run inconclusive instead of
  clean, because the policy uses `require-model`.
- `Decoder.Decode` and `Decoder.DecodeValue` are modeled with no transfer into
  the decoded value. The semantic-model schema has no output for a write
  through a pointer argument. The rule is unaffected, because its sink is the
  reader operand. Don't use these summaries for rules that follow decoded data.
- A peer that is authenticated, or a stream that is bounded before decoding,
  is still reported. The policy can't see either guard.

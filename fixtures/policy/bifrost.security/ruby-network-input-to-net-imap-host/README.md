# Network-chosen IMAP server on an affected net-imap

Qualifies `bifrost.security.ruby.network-input-to-net-imap-host` for
BrokkAi/bifrost-packs#284 (CVE-2026-42245,
[GHSA-q2mw-fvj9-vvcw](https://github.com/advisories/GHSA-q2mw-fvj9-vvcw)).
Affected net-imap releases rescan the whole receive buffer for every literal,
so a hostile server can keep the client CPU busy. OSV: fixed in 0.4.24, 0.5.14
and 0.6.4.

The rule reports a `Net::HTTP.get` response body (the reviewed
`bifrost.web-network-ruby` source) that reaches the host argument of
`Net::IMAP.new`, for example a mail autoconfiguration document that names the
server. The sink is the `new` member of the `cve-2026-42245-affected` shard of
`bifrost.ruby.net-imap` 0.2.0, which activates from a Gemfile.lock net-imap
version before 0.4.24, from 0.5.0 up to 0.5.14, or from 0.6.0 up to 0.6.4. The
`cve-2026-42245-unaffected` shard declares the same constructor for the fixed
ranges, except 0.6.4. The rule uses `require-model` and is opt-in.

The model declares the constructor that net-imap prepends to `Net::IMAP`,
`DeprecatedClientOptions#initialize(host, port_or_options = nil, *deprecated,
**options)`, so positional, deprecated positional and keyword calls all bind.
Ruby summaries are matched by call arity, so the model summarizes `new` for 1
to 8 arguments: the host plus up to seven keyword or positional arguments. A
longer call has no summary and stays inconclusive.

Each case directory is its own workspace with its own `Gemfile.lock`. Run each
one separately.

## Cases

`mail_autoconfig.rb` is the same in every case except
`incomplete/double-splat`. Each method has one sink, so no method reaches the
several-sinks attribution budget regression (bifrost-dev#14210).

- **Positives**: the network value as the host of
  `Net::IMAP.new(host, port: 993, ssl: true)` (line 7), `Net::IMAP.new(host)`
  (line 11), the positional port form `Net::IMAP.new(host, 143)` (line 16), and
  three keywords (line 21).
- **Near misses**: a literal host after a network read (line 26), and a
  network value as the port of a literal host (line 31). The port is not the
  server choice this rule covers.

Cases:

- `net-imap-0.4.23`, `net-imap-0.5.13` and `net-imap-0.6.3`: affected, one per
  OSV range.
- `net-imap-0.4.24` and `net-imap-0.5.14`: fixed-version near misses.
- `incomplete/unlocked`: no lock, so no shard activates.
- `incomplete/net-imap-0.6.4`: the fixed 0.6.4. The model leaves 0.6.4 inactive
  because Bifrost reads 0.6.4.1 as 0.6.4 with build metadata, and the
  `network-input-to-net-imap-raw-arguments` advisories split there. The run
  stays inconclusive rather than clean.
- `incomplete/double-splat` (0.5.13): `Net::IMAP.new(host, **options)`. A keyword
  splat does not bind to the `**options` formal, so the call has no target and
  the run is inconclusive.

Not covered: request parameters as the source (no reviewed Rails or Rack model
binds them yet), and a host stored and read back later. Taint into a keyword
formal after position 0 is a silent false clean on Bifrost 0.15.3
(bifrost-dev#14211); this rule's sink is formal 0, so it does not depend on
that.

## Validation

Bifrost `v0.15.3` (`bifrost-v0.15.3-aarch64-apple-darwin`, binary SHA-256
`1e8d45ae76f1b2920aa7a113e8e80083346f6acbed839c3e113058ae36c8acbc`, build
identity `cc7ebd1676e002b657e10304cfd977bc289e25ed`), `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`
and a fresh `BIFROST_CACHE_DIR` per run. Evaluation date 2026-11-17. Each case
directory carries its own copies of the models in `.bifrost/semantic-models`.

| Case | Completion | Findings |
| --- | --- | --- |
| `net-imap-0.4.23` | `proven_by_summary` | 4 definite (lines 7, 11, 16, 21) |
| `net-imap-0.5.13` | `proven_by_summary` | 4 definite (lines 7, 11, 16, 21) |
| `net-imap-0.6.3` | `proven_by_summary` | 4 definite (lines 7, 11, 16, 21) |
| `net-imap-0.4.24` | `complete` | 0 |
| `net-imap-0.5.14` | `complete` | 0 |
| `incomplete/unlocked` | `inconclusive (partial_discovery)` | 0 |
| `incomplete/net-imap-0.6.4` | `inconclusive (partial_discovery)` | 0 |
| `incomplete/double-splat` | `inconclusive (partial_discovery)` | 0 |

On Bifrost 0.15.2 the same model loads, but keyword calls get no target
(bifrost-dev#11368), so the `net-imap-0.5.13` run is inconclusive with only
the two non-keyword findings (lines 11 and 16).

Authored hash `ece269ca1aefe8b795e74eba4f2bef8d5fe65c19a768836ab5424a0497cffeca`.

Run from a case directory:

```console
bifrost --root . --policy-file .bifrost/policies/network-input-to-net-imap-host.rqlp --no-builtin-policies --no-incremental --format json --evaluation-date 2026-11-17
```

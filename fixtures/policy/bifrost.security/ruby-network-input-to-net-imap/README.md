# Network input sent as raw net-imap command text

Qualifies `bifrost.security.ruby.network-input-to-net-imap-raw-arguments` for
BrokkAi/bifrost-packs#368 (CVE-2026-47240) and #369 (CVE-2026-47241). Both
advisories share one OSV range: net-imap before 0.5.15, and 0.6.0 before 0.6.4.1.

The rule reports a `Net::HTTP.get` response body (the reviewed
`bifrost.web-network-ruby` source) that reaches the raw String argument of
`Net::IMAP` `search`/`uid_search` (keys), `sort`/`uid_sort` and
`thread`/`uid_thread` (search_keys) or `fetch`/`uid_fetch` (attr). Sinks are
the members of the `affected` shard of `bifrost.ruby.net-imap` 0.1.0, which
activates from a Gemfile.lock net-imap version before 0.5.15 or from 0.6.0 up
to 0.6.4. The `unaffected` shard declares the same API for 0.5.15 up to 0.6.0
and for 0.6.5 and later. The rule uses `require-model` and is opt-in.

Each case directory is its own workspace with its own `Gemfile.lock`. Run each
one separately.

## Cases

`mail_rules.rb` is the same in every case except `net-imap-0.5.14-keywords`:

- **Positives** (lines 10 to 13): rules text from `Net::HTTP.get` passed as
  raw criteria to `search`, `uid_search`, `sort` (search_keys) and `fetch`
  (attr) on `imap = Net::IMAP.new(host)`.
- **Near misses**: constant structured criteria (line 21), and the network value
  as one element of a structured criteria array (line 26). The client encodes
  array elements itself, so neither is raw command text.

Cases:

- `net-imap-0.5.14` and `net-imap-0.6.3`: affected (one per OSV range).
- `net-imap-0.5.15`: the fixed-version near miss.
- `incomplete/unlocked`: no lock, so no shard activates.
- `incomplete/net-imap-0.6.4.1`: the fixed 0.6.4.1. Bifrost 0.15.2 reads a
  four-segment gem version as three segments plus build metadata, so 0.6.4.1
  and the affected 0.6.4 can't be told apart. Neither shard activates and the
  run stays inconclusive rather than clean.
- `net-imap-0.5.14-keywords`: `Net::IMAP.new(host, port: 993, ssl: true)`,
  then `search` on the result. It was `incomplete/keywords`: keyword calls to
  model members got no target on Bifrost 0.15.2 (bifrost-dev#11368), so the
  receiver was untyped and the run was inconclusive. Bifrost 0.15.3 binds
  keyword arguments, and `bifrost.ruby.net-imap` 0.2.0 declares the
  constructor net-imap prepends, `(host, port_or_options = nil, *deprecated,
  **options)`, so the keywords reach `options` and the call is typed.

Server capability negotiation (LITERAL+, LITERAL-, IMAP4rev2) is runtime state;
the rule doesn't check it.

## Validation on Bifrost 0.15.3

Bifrost `v0.15.3` (`bifrost-v0.15.3-aarch64-apple-darwin`, binary SHA-256
`1e8d45ae76f1b2920aa7a113e8e80083346f6acbed839c3e113058ae36c8acbc`, build
identity `cc7ebd1676e002b657e10304cfd977bc289e25ed`), `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`
and a fresh `BIFROST_CACHE_DIR` per run, with `bifrost.ruby.net-imap` 0.2.0
in each case. Evaluation date 2026-11-17.

| Case | Completion | Findings |
| --- | --- | --- |
| `net-imap-0.5.14` | `inconclusive (partial_discovery, report_retention_budget)` | 4 definite (lines 10, 11, 12, 13) |
| `net-imap-0.6.3` | `inconclusive (partial_discovery, report_retention_budget)` | 4 definite (lines 10, 11, 12, 13) |
| `net-imap-0.5.15` | `complete` | 0 |
| `net-imap-0.5.14-keywords` | `proven_by_summary` | 1 definite (line 7) |
| `incomplete/unlocked` | `inconclusive (partial_discovery)` | 0 |
| `incomplete/net-imap-0.6.4.1` | `inconclusive (partial_discovery)` | 0 |

The two affected cases regress on Bifrost 0.15.3: the four sinks fed by one
source in `apply_rules` exhaust the source-attribution witness budget
("ICFG source attribution witness coverage stopped: collection_budget"), so
the run is inconclusive although all four findings stay definite
(bifrost-dev#14210). The fixtures are unchanged so that the regression stays
visible. A method with three or fewer such sinks is not affected.

## Validation on Bifrost 0.15.2

Bifrost `v0.15.2` (`bifrost-v0.15.2-aarch64-apple-darwin.tar.gz`, archive SHA-256 `58c3745bf0f6be04dbf6e3844fb45747ab60189cfe625eb1ab15ee2228859d00`, binary SHA-256 `f06a8760f4099db712d91dcb0acb406589cd84a66ec3ccacaf4d0d6dbc3952dc`, build identity `340cbbdcea3fc565f6ea8066084ed24962c369d3`), with the `packs/v0.13.0` native bundle (`bifrost.public.packs-0.13.0-native.tar.gz`, SHA-256 `92bc425e60dcc42e05630ff45505aa5bef29abb1090caa10f731cc5a6e4226b4`) as `BIFROST_OPEN_SEMANTIC_PACK_BUNDLE`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off` and a fresh `BIFROST_CACHE_DIR` per run. Evaluation date 2026-11-13. The bundle supplies none of the models these cases use: each case directory carries its own copies in `.bifrost/semantic-models`, then `bifrost.ruby.net-imap` 0.1.0.

| Case | Completion | Findings |
| --- | --- | --- |
| `net-imap-0.5.14` | `proven_by_summary` | 4 definite (lines 10, 11, 12, 13) |
| `net-imap-0.6.3` | `proven_by_summary` | 4 definite (lines 10, 11, 12, 13) |
| `net-imap-0.5.15` | `complete` | 0 |
| `incomplete/unlocked` | `inconclusive (partial_discovery)` | 0 |
| `incomplete/net-imap-0.6.4.1` | `inconclusive (partial_discovery)` | 0 |
| `incomplete/keywords` (now `net-imap-0.5.14-keywords`) | `inconclusive (partial_discovery)` | 0 |

Authored hash `ebe21fca228b4017538284daa93d742e5ae5e9536adbfc0c0735f56e35f07c14`.

Run from a case directory:

```console
bifrost --root . --policy-file .bifrost/policies/network-input-to-net-imap-raw-arguments.rqlp --no-builtin-policies --no-incremental --format json --evaluation-date 2026-11-13
```

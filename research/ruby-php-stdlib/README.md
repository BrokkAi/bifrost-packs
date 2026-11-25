# PHP and Ruby stdlib lead qualification on Bifrost 0.15.0

**Outcome: no PHP or Ruby lead owned by this repository can ship as a rule on
Bifrost 0.15.0.** That covers the 8 open `[Ruby] CVE-…` leads, the batch
issues #22 (PHP) and #23 (Ruby), and the ten PHP and Ruby rows of
`research/stdlib/candidates.md`. Each blocker now has a focused upstream issue.

Every Ruby CVE lead is version-gated on a default gem (uri, net-imap, rexml,
cgi, date, tmpdir). The engine publishes no Ruby dependency or runtime
evidence (bifrost-dev#9318). The version-independent Ruby slices
(`Marshal.load`, `Psych.unsafe_load`, `Kernel.open` and `Kernel.eval` on
external input) can't be selected exactly either. A call to a model-declared
stdlib singleton method finds its target but never binds (bifrost-dev#9336).
A receiver call named `load` opens dispatch for the whole workspace
(bifrost-dev#9334). And there is no exact Ruby process-input source
(bifrost-dev#9335).

PHP comes closest. With research declarations that mark the builtins
`callable_family_complete`, network bytes reaching `unserialize` give a
**definite, complete finding** ("proven by summary"), and the near miss and
namespaced lookalike are clean and complete. The production
`bifrost.php-builtin` pack, active whenever a project declares a PHP version,
lacks that flag. With it active the same policy is refused (bifrost-dev#9337).
The request-input route (`$_GET[...]`) is blocked separately by bifrost-dev#9330.

The files under `probe/` are research inputs, not registered pack content.
They don't change locked policy or semantic-pack content.

## Engine

Official `v0.15.0` release, `bifrost-v0.15.0-universal-apple-darwin.tar.gz`,
downloaded with `gh release download v0.15.0 --repo BrokkAi/bifrost`.

- Archive SHA-256: `c91c0bd38e4c6c0def86dc75acf8fa6d750b23a45894a28a76115fb8af034eda`. It matches the release `.sha256`.
- Binary SHA-256: `47e3e2da0a64ba65b447337b43952478deebbed7af3aa92d835d3a5ad458da96`.
- Build identity: `09a2503c5f7ced1630a9e3c445ead53dfc5925e8`.
- Production PHP declarations: `bifrost.php-builtin` 2026.9.4 from the `packs/v0.9.0` release, selected by the engine's open-pack activation.
- Evaluation date: 2026-11-03.

## Shared blockers

| Blocker | Issue | Leads |
| --- | --- | --- |
| No Ruby gem or runtime version evidence. With a `Gemfile.lock` pinning `uri 0.12.0`, `rexml 3.2.5`, `net-imap 0.4.0` and `RUBY VERSION ruby 3.2.0p0`, `(dependency-evidence)` returns no rows: `Ruby selected dependency publication unavailable`. | [bifrost-dev#9318](https://github.com/BrokkAi/bifrost-dev/issues/9318) (reused) | All 8 Ruby CVE leads; the Ruby 3.4 or default-gem scoped candidates |
| Model-declared stdlib singleton calls (`Marshal.load`, `Psych.unsafe_load`, `Kernel.open`, `File.open`, and the reviewed `Net::HTTP.get`) find one target but stay `callee_unresolved`, `unproven`, `open`. `YAML.unsafe_load` and implicit-self `open`/`eval` find no target. | [bifrost-dev#9336](https://github.com/BrokkAi/bifrost-dev/issues/9336) | Every Ruby stdlib slice |
| A receiver call named `load` (`Marshal.load(x)`, `JSON.load(x)`, `x.load`) makes every workspace call `unproven`, `open`. | [bifrost-dev#9334](https://github.com/BrokkAi/bifrost-dev/issues/9334) | Any Ruby rule in a workspace that calls `Marshal.load`; likely the cause of part of bifrost-dev#9322 |
| `keyed-read-value` has no `ruby` runtime, so `ENV[...]` and `ARGV[...]` can't be exact sources. | [bifrost-dev#9335](https://github.com/BrokkAi/bifrost-dev/issues/9335) | Process-input variants of the Ruby taint slices |
| The generated `bifrost.php-builtin` pack sets no `callable_family_complete` on `_php_global_` functions, so `resolved-call "_php_global_.unserialize"` is `qualified-call-locator-partial`. | [bifrost-dev#9337](https://github.com/BrokkAi/bifrost-dev/issues/9337) | PHP `unserialize`, `proc_open`, and any PHP builtin `resolved-call` |
| PHP superglobal element reads (`$_GET['x']`) and concatenation make procedure semantics unknown. | [bifrost-dev#9330](https://github.com/BrokkAi/bifrost-dev/issues/9330) (reused) | Every PHP request-input slice (#22) |
| Ruby third-party request sources (Rails `params`) don't bind. | [bifrost-dev#9319](https://github.com/BrokkAi/bifrost-dev/issues/9319) (reused) | Request-input positives of the Ruby CVE leads |

## The PHP `unserialize` slice

`unserialize` documentation warns that untrusted input can instantiate objects
and run their magic methods, on any PHP version, and that `allowed_classes`
isn't a full defense. So network bytes reaching `unserialize` are worth
reviewing everywhere. `probe/.bifrost/policies/php-unserialize-network.rqlp` is a
may-taint policy with `require-model`. Its source is the
`stream_socket_client` connection, with `fread` transferring the stream to its
result. Its sink is formal 0 of `_php_global_.unserialize`.

`probe/.bifrost/semantic-models/bifrost.research.php-stdlib-probe.json`
declares `unserialize`, `json_decode`, `stream_socket_client`, `fread` and
`base64_decode` under the `_php_global_` type id that `bifrost.php-builtin`
uses. Every member is `callable_family_complete`, with complete receiverless
summaries. `fread` and `base64_decode` transfer argument 0 to the result.
This is a research model only and must not be copied into `semantic-packs/`.

Run from `probe/` with `--sources php-unserialize/<case>`:

| Case | Open packs | Result |
| --- | --- | --- |
| `positive` | disabled | 1 finding at `app.php:7`, definite, complete. The run is `proven_by_summary`, the same shape as the shipped C# model-backed rules. Exit 1. |
| `allowed-classes-false` (`unserialize(base64_decode($bytes), ['allowed_classes' => false])`) | disabled | 1 finding, same shape. The contract says `allowed_classes` isn't a blanket guarantee. |
| `near-miss-json` (`json_decode`) | disabled | 0 findings, complete (no sink selected). |
| `namespaced-lookalike` (`App\Codec\unserialize`) | disabled | 0 findings, complete. The unqualified call binds the workspace function. |
| `positive` | enabled (`bifrost.php-builtin` selected through `composer.json` and `.php-version`) | `not_run`: `qualified-call-locator-partial` for `_php_global_.unserialize`. Exit 2. |

`:resolves-to "unserialize"` is `qualified-call-locator-ambiguous`, because the
SPL `::unserialize` methods match too. The pinned stub slice has no
`sockets/sockets.php`, so `socket_read` isn't declared. Adding it is a change
to the spec in this repository, not to the engine.

A rule here needs three things. bifrost-dev#9337 must land in the producer and
reach a released `php-builtin` pack. Reviewed source and summary models for the
stream functions have to ship. And the request-input source needs
bifrost-dev#9330. Until then it stays a probe.

## The Ruby `Marshal.load` slice

`probe/.bifrost/policies/ruby-marshal-network.rqlp` takes the `Net::HTTP.get`
body as its source and formal 0 of `Marshal.load` as its sink.
`bifrost.research.ruby-stdlib-probe` declares the `Marshal`, `Psych`, `Kernel`
and `File` modules with the canonical rubygems type ids. Each id is
`type_declaration_id(TypeIdentity { ecosystem: "rubygems", name })`, the hash
that also gives `Net::HTTP` its id in `bifrost.web-network-ruby`. Any other id
leaves the call with no target. Members are static, `callable_family_complete`,
and have complete receiverless summaries. `bifrost.web-network-ruby.json` is an
unchanged copy of `semantic-packs/web-network/ruby/`.

| Case | Result |
| --- | --- |
| `ruby-marshal/positive` | 0 findings, `inconclusive (partial_discovery)`. Both selectors are incomplete: `call_bindings did not establish complete actual-to-formal coverage (dispatch outcome=unproven, coverage=open, target_count=1)`. |
| `ruby-marshal/near-miss-safe-load` | 0 findings, complete, but vacuous: no sink is selected. |
| `ruby-marshal/workspace-lookalike` (`Codec.load`) | 0 findings, complete, vacuous. |
| `ruby-marshal/constant-blob` | 0 findings, complete, vacuous: no source is selected. |

The three complete results only mean that one side has no selected endpoint.
They don't show that the sink is distinguished from a lookalike.

`ruby-bindings/*.rql`, run over the whole probe root with workspace models on:

| Call (`ruby-bindings/app.rb`) | Targets | Dispatch | Reason |
| --- | ---: | --- | --- |
| `Net::HTTP.get(uri)` | 1 | unproven, open | `callee_unresolved` |
| `Marshal.load(body)`, `Marshal.restore(body)` | 1 | unproven, open | `callee_unresolved` |
| `Psych.unsafe_load(text)` | 1 | unproven, open | `callee_unresolved` |
| `YAML.unsafe_load(text)` | 0 | unknown, open | `callee_unresolved` |
| `Kernel.open(cmd)`, `Kernel.eval(text)`, `File.open(cmd)` | 1 | unproven, open | `callee_unresolved` |
| `open(cmd)`, `eval(text)` | 0 | unknown, open | `callee_unresolved` |
| `LocalCodec.decode(bytes)` (workspace) | 1 | unproven, open | `call_binding_dispatch_partial` |

`ruby-load-dispatch/` isolates the workspace row. Run each directory as its own
root. In `without-load`, the other method calls `Marshal.dump(x)` and
`LocalCodec.decode` is `resolved`, `exhaustive`. In `with-load` it calls
`Marshal.load(x)` and the same call becomes `unproven`, `open`. The issue
(bifrost-dev#9334) lists the calls that open dispatch and the ones that don't.

## Per-lead outcomes

"Not probed" means the lead already fails on an earlier gate. Its later
capability wasn't exercised on 0.15.0.

| Lead | Outcome | Blockers | Notes |
| --- | --- | --- | --- |
| #169 net-imap raw arguments (CVE-2026-42257) | Blocked by engine | bifrost-dev#9318, bifrost-dev#9336 | Not probed: interpolated-string versus array operand facts on `Net::IMAP#search`. Request source belongs to bifrost-dev#9319. |
| #170 uri `URI.parse` (CVE-2023-28755) | Blocked by engine | bifrost-dev#9318, bifrost-dev#9336 | Not probed: `URI.parse`. Implicit-self Kernel calls (`URI(...)` has the same shape as `open(...)`) find no target. |
| #171 rexml SAX2/pull parsers (CVE-2024-41946) | Blocked by engine | bifrost-dev#9318, bifrost-dev#9336 | Not probed: `REXML::Parsers::SAX2Parser.new` constant-path construction. |
| #176 net-imap Symbol arguments (CVE-2026-42258) | Blocked by engine | bifrost-dev#9318, bifrost-dev#9336 | Not probed: `to_sym` propagation and array-element operands. |
| #177 cgi response headers (CVE-2021-33621) | Blocked by engine | bifrost-dev#9318, bifrost-dev#9336 | Not probed: hash-literal header values. |
| #178 date `Date.parse` (CVE-2021-41817) | Blocked by engine | bifrost-dev#9318, bifrost-dev#9336 | Not probed: the `limit:` keyword fact. |
| #179 rexml parse/serialize (CVE-2021-28965) | Blocked by engine | bifrost-dev#9318, bifrost-dev#9336 | Not probed: same-object parse then serialize. |
| #180 tmpdir on Windows (CVE-2021-28966) | Blocked by engine | bifrost-dev#9318, bifrost-dev#9336 | Also needs target-OS evidence, recorded on bifrost-dev#9318. |
| #23 lit-ruby-05 `Kernel.eval` | Blocked by engine | bifrost-dev#9336, bifrost-dev#9335 | `Kernel.eval` is unproven and `eval` has no target. A dynamic `eval` also opens workspace dispatch by design. |
| #23 lit-ruby-06 `Kernel.system/exec/spawn` | Blocked by engine | bifrost-dev#9336, bifrost-dev#9335 | Not probed directly. It has the same implicit-self and `Kernel.` shapes as `open` and `eval`. |
| #23 lit-ruby-07 `Marshal.load` | Blocked by engine | bifrost-dev#9336, bifrost-dev#9334, bifrost-dev#9335 | Probed above. |
| #23 lit-ruby-09 `File.open`/`IO#close` | Blocked by engine | bifrost-dev#9336 | `File.open` is unproven. Typestate not probed. |
| #22 lit-php-08 `unserialize` | Blocked by engine | bifrost-dev#9337, bifrost-dev#9330 | Probed above. The network slice works with research declarations. |
| #22 lit-php-01 to 07 | Blocked by engine | bifrost-dev#9330, bifrost-dev#9337 | Not probed: each needs request input from superglobals. lit-php-01 (`PDO`) also needs PHP class-member binding (bifrost-dev#9329). |
| `php-runtime-deserialization` | Blocked by engine | bifrost-dev#9337, bifrost-dev#9330 | Same as lit-php-08. |
| `php-proc-open-paired-ownership` | Blocked by engine | bifrost-dev#9337, bifrost-dev#9330 | `proc_open` has the same partial family. Not probed: the by-reference `$pipes` out-parameter, its element reads, or blocking order. |
| `ruby-marshal-untrusted-load` | Blocked by engine | bifrost-dev#9336, bifrost-dev#9334, bifrost-dev#9335 | Same as lit-ruby-07. |
| `ruby-psych-unsafe-load-untrusted-yaml` | Blocked by engine | bifrost-dev#9336, bifrost-dev#9335, bifrost-dev#9318 | `Psych.unsafe_load` is unproven, and the `YAML` alias has no target. Psych 5.2.2 scoping needs bifrost-dev#9318. |
| `ruby-kernel-open-pipe-command-taint` | Blocked by engine | bifrost-dev#9336, bifrost-dev#9335, bifrost-dev#9318 | `Kernel.open` is unproven, and bare `open` has no target. The Ruby 3.4-only scope needs runtime evidence. Leading-`\|` string facts not probed. |
| `ruby-net-http-active-peer-verification-disabled` | Blocked by engine | bifrost-dev#9336, bifrost-dev#9318 | `Net::HTTP.new` is unproven. `http.verify_mode = …` publishes no call row, and `field-write-value` needs a member target. Not probed further. |
| `ruby-open3-popen3-owned-pipe-closure` | Blocked by engine | bifrost-dev#9336, bifrost-dev#9318 | Not probed: `Open3.popen3`, which has the singleton shape above. The block form needs block-parameter receivers (bifrost-dev#9322). |
| `ruby-open3-popen3-paired-pipe-draining` | Deferred | none filed | Remains proof-heavy: needs child output volume, pipe capacity and read order. Not probed. |
| `ruby-tempfile-create-unlinked-owner` | Blocked by engine | bifrost-dev#9336, bifrost-dev#9318 | Not probed: `Tempfile.create`. tempfile 0.3.1 scoping needs bifrost-dev#9318. |

## Layout and reproduction

```
probe/
  .bifrost/policies/                    two research taint policies
  .bifrost/semantic-models/             research models (see above)
  composer.json, .php-version           PHP version, read only with open packs enabled
  php-unserialize/<case>/app.php        four PHP cases
  ruby-marshal/<case>/app.rb            four Ruby cases
  ruby-bindings/                        Ruby stdlib call shapes and one query per callee name
  ruby-load-dispatch/{with,without}-load/  the bifrost-dev#9334 contrast, each its own root
  version-evidence/ruby-bundle/         Gemfile, Gemfile.lock, .ruby-version
```

Nothing was installed or run with Ruby or PHP.

Run with the exact engine above. The `bifrost` on `PATH` may be older. Use a
fresh `BIFROST_CACHE_ROOT` for each case.

```sh
cd probe
export BIFROST_WORKSPACE_SEMANTIC_MODELS=on
BIFROST_OPEN_PACKS_DISABLE=1 BIFROST_SEMANTIC_PACK_DOWNLOAD=off bifrost --policy \
  --no-builtin-policies --no-incremental --root . --format json \
  --sources php-unserialize/positive \
  --policy-file .bifrost/policies/php-unserialize-network.rqlp
# Production php-builtin selected: open packs enabled, composer.json read from the root
bifrost --policy --no-builtin-policies --no-incremental --root . --format json \
  --sources php-unserialize/positive \
  --policy-file .bifrost/policies/php-unserialize-network.rqlp
BIFROST_OPEN_PACKS_DISABLE=1 BIFROST_SEMANTIC_PACK_DOWNLOAD=off bifrost --policy \
  --no-builtin-policies --no-incremental --root . --format json \
  --sources ruby-marshal/positive \
  --policy-file .bifrost/policies/ruby-marshal-network.rqlp
BIFROST_OPEN_PACKS_DISABLE=1 bifrost --root . --query-file ruby-bindings/load.rql
BIFROST_OPEN_PACKS_DISABLE=1 bifrost --root ruby-load-dispatch/with-load --query-file decode.rql
cd version-evidence/ruby-bundle && BIFROST_OPEN_PACKS_DISABLE=1 bifrost --root . \
  --query-file dependency-evidence.rql
```

## Promotion criteria

- PHP `unserialize`: bifrost-dev#9337 in a released producer and `php-builtin`
  pack. Reviewed stream source and summary models. bifrost-dev#9330 for
  request input. Then rerun the four cases against the production pack, plus a
  `fclose` and `stream_get_contents` variant.
- Ruby stdlib slices: bifrost-dev#9336 and bifrost-dev#9334, then bifrost-dev#9335 for process input.
  A reviewed Ruby stdlib declaration model would go under `semantic-packs/ruby/`
  and enter a native release only through the release recipe.
- Ruby CVE leads: bifrost-dev#9318 first, then the per-lead capabilities above.

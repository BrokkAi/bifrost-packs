# Ruby OSV data-flow leads on Bifrost 0.15.1

**Outcome: 10 new leads filed, none can ship as a rule on Bifrost 0.15.1.**
Seven are open-pack leads on default and bundled gems (BrokkAi/bifrost-packs
#280 to #286). They're blocked by engine. Three are third-party gem leads
(BrokkAi/bifrost-premium-packs #459 to #461). They belong in premium packs and
weren't implemented here. `outcomes.json` records every lead, case and input
hash.

Each lead's theoretical policy is a taint policy. A request, network or
user-chosen value reaches a sink operand, and the application decides whether
that happens. The leads came from the OSV RubyGems dump. They were deduplicated
by CVE and alias against every `CVE-` title and body in both repositories. They
were also deduplicated by API: the `json` (#227), `uri` (#231) and
`secure_headers` (premium #426) candidates were dropped because existing leads
already model the same flow.

The release blocks every lead, for a reason that no lead-specific capability
explains. On the released binary, a Ruby singleton call that only a semantic
model declares still finds its target and never binds. That includes the
reviewed public `Net::HTTP.get`. bifrost-dev#9336 was closed on 2026-11-03 with
that fix, and its own golden fixture is inconclusive on 0.15.1. The repro for
bifrost-dev#9334 (closed the same day) also still reproduces. Both fixes behave
as if they're missing from the release. Filed as
[bifrost-dev#9979](https://github.com/BrokkAi/bifrost-dev/issues/9979).

The files under `probe/` are research inputs, not registered pack content.
They don't change locked policy or semantic-pack content.

## Engine

Official `v0.15.1` release, `bifrost-v0.15.1-universal-apple-darwin.tar.gz`,
downloaded with `gh release download v0.15.1 --repo BrokkAi/bifrost`. No
v0.15.2 release existed on 2026-11-05.

- Archive SHA-256: `d7ca6901787455bdabf18ec9c36453032a9be354180e54b5ff183b1e4bf83038`. It matches the release `.sha256`.
- Binary SHA-256: `00b279126297d5e9f7805390799493e915eaf4a2d5940dc3e755138a577a6df9`.
- Build identity: `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`.
- Open packs disabled. The `packs/v0.10.0` bundle has no Ruby stdlib declarations, only `bifrost.ruby.core-result-use-obligations`.
- Evaluation date: 2026-11-05.

## Leads

| Lead | Advisory | Sink | Outcome | Blockers |
| --- | --- | --- | --- | --- |
| [#280](https://github.com/BrokkAi/bifrost-packs/issues/280) | CVE-2023-28756 (time) | `Time.rfc2822`, `Time.httpdate`, `Time.parse` | Blocked by engine | bifrost-dev#9979, #9318 |
| [#281](https://github.com/BrokkAi/bifrost-packs/issues/281) | CVE-2025-27219 (cgi) | `CGI::Cookie.parse` | Blocked by engine | bifrost-dev#9979, #9318 |
| [#282](https://github.com/BrokkAi/bifrost-packs/issues/282) | CVE-2025-27220 (cgi) | `CGI.escapeElement`, `CGI.unescapeElement` | Blocked by engine | bifrost-dev#9979, #9318 |
| [#283](https://github.com/BrokkAi/bifrost-packs/issues/283) | CVE-2024-49761 (rexml) | `REXML::Document.new` on Ruby 3.1 | Blocked by engine | bifrost-dev#9979, #9318 |
| [#284](https://github.com/BrokkAi/bifrost-packs/issues/284) | CVE-2026-42245 (net-imap) | host operand of `Net::IMAP.new` | Blocked by engine | bifrost-dev#9979, #9318 |
| [#285](https://github.com/BrokkAi/bifrost-packs/issues/285) | CVE-2024-27281 (rdoc) | argv of `RDoc::RDoc#document` | Blocked by engine | bifrost-dev#9979, #9318 |
| [#286](https://github.com/BrokkAi/bifrost-packs/issues/286) | CVE-2017-0903 (rubygems) | `Gem::Installer.at`, `Gem::Package.new`, `Gem::Specification.from_yaml` | Blocked by engine | bifrost-dev#9979, #9318 |
| [premium #459](https://github.com/BrokkAi/bifrost-premium-packs/issues/459) | CVE-2026-53727 (css_parser) | `CssParser::Parser#load_uri!` | Premium, not implemented here | bifrost-dev#9319, #9318 |
| [premium #460](https://github.com/BrokkAi/bifrost-premium-packs/issues/460) | CVE-2022-31163 (tzinfo) | `TZInfo::Timezone.get` | Premium, not implemented here | bifrost-dev#9319, #9318 |
| [premium #461](https://github.com/BrokkAi/bifrost-premium-packs/issues/461) | CVE-2025-53623 (job-iteration) | `JobIteration::CsvEnumerator` row count | Premium, not implemented here | bifrost-dev#9319, #9318 |

Request-input positives also need a Rack or Rails request source
(bifrost-dev#9319) or a process-input source (bifrost-dev#9335). Only #286 has
a version-independent slice: installing an untrusted gem runs its code on every
RubyGems version. The rest are version-gated. They need `Gemfile.lock` and Ruby runtime evidence, and
`(dependency-evidence)` still reports `Ruby selected dependency publication
unavailable` on 0.15.1 (bifrost-dev#9318).

## Taint probe

Each open lead has one may-taint policy in `probe/.bifrost/policies/` with
`:call-modeling :unmodeled require-model`. Its source is the `Net::HTTP.get`
body from an unchanged copy of the reviewed `bifrost.web-network-ruby` model.
Its sink is formal 0 of the lead's API, selected with `resolved-call ... :proof
declared`. The research model
`probe/.bifrost/semantic-models/bifrost.research.ruby-osv-dataflow-probe.json`
declares the sink types with canonical rubygems type ids. Members are
`callable_family_complete`. Summaries are keyed `has_receiver: true` and
`covers_overrides: true`, the convention bifrost-dev#9425 set.

Every case has a positive (`body` reaches the sink), a near miss (a literal
reaches the sink) and an unknown (`body` passes through an unmodeled
`Opaque.transform` first). All 21 cases are `inconclusive (partial_discovery)`
with zero findings, exit 0. The near misses aren't clean either, because the
`Net::HTTP.get` source selector is itself incomplete.

## Call bindings

`probe/bindings/app.rb`, one `call-bindings` query per callee name:

| Call | Targets | Bound | Result |
| --- | ---: | --- | --- |
| `Net::HTTP.get(uri)` (reviewed public model) | 1 | 0/1 | `callee_unresolved`, unproven, open |
| `Time.rfc2822`, `CGI::Cookie.parse`, `REXML::Document.new`, `Net::IMAP.new`, `Gem::Installer.at` | 1 | 0/1 | `callee_unresolved`, unproven, open |
| `CGI.escapeElement(text, "script")` | 1 | 0/2 | `callee_unresolved`, unproven, open |
| `Net::IMAP.new(text, port: 993)` | 0 | 0/2 | `callee_unresolved`, unknown, open |
| `RDoc::RDoc.new.document(text)` | 1 | 1/1 | mapping exact, `selector_exact`, but unproven, open |

The instance call is the only exact binding. Its dispatch stays open because
its receiver, `RDoc::RDoc.new`, is an unbound singleton call. The
keyword-argument row may be a gap in the research model's signature rather
than in the engine. It is recorded on bifrost-dev#9979 rather than filed
separately.

## Rechecks of the 0.15.0 Ruby blockers

| Issue | State | On 0.15.1 |
| --- | --- | --- |
| bifrost-dev#9336 (singleton calls never bind) | Closed by PR 9425 | Still reproduces. The `ruby-marshal/positive` case in `research/ruby-php-stdlib/` stays inconclusive after rekeying its summaries `has_receiver: true`. The issue's own golden fixture is inconclusive too. |
| bifrost-dev#9334 (`load` opens workspace dispatch) | Closed by PR 9375 | Still reproduces: `ruby-load-dispatch/with-load` is unproven and open, `without-load` is resolved and exhaustive. |
| bifrost-dev#9322, #9321 | Closed | Not rechecked: no lead here depends on them before the singleton binding gate. |
| bifrost-dev#9318, #9319, #9320, #9335 | Open | #9318 reconfirmed: no dependency-evidence rows. |

## Reproduction

Run with the exact engine above, from `probe/`, and use a fresh
`BIFROST_CACHE_DIR` for each case:

```sh
export BIFROST_WORKSPACE_SEMANTIC_MODELS=on BIFROST_OPEN_PACKS_DISABLE=1 BIFROST_SEMANTIC_PACK_DOWNLOAD=off
BIFROST_CACHE_DIR=$(mktemp -d) bifrost --policy --no-builtin-policies --no-incremental \
  --root . --format json --evaluation-date 2026-11-05 \
  --sources time-rfc2822/positive --policy-file .bifrost/policies/time-rfc2822.rqlp
BIFROST_CACHE_DIR=$(mktemp -d) bifrost --root . --query-file bindings/rfc2822.rql
```

Nothing was installed or run with Ruby.

## Promotion criteria

- A Bifrost release in which the bifrost-dev#9336 golden fixture passes. Rerun
  `probe/bindings/` first. Then the seven taint cases need a definite positive
  and clean, complete near misses.
- Promoting a lead needs a reviewed Ruby stdlib declaration model under
  `semantic-packs/ruby/`. It enters a native release only through the release
  recipe.
- The version-gated leads also need bifrost-dev#9318. #286's install slice can
  ship without it.
- Request-input positives need bifrost-dev#9319 (Rack and Rails) or
  bifrost-dev#9335 (`ENV`, `ARGV`).

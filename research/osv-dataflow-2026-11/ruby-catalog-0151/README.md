# Ruby catalog leads #362 to #370 on Bifrost 0.15.1

**Outcome: none of the nine leads ships on the pinned Bifrost v0.15.1.** All
nine are open-pack leads on default gems (`uri`, `rexml`, `net-imap`, `json`).
Every one depends on an OSV version range, and every entry point is a
singleton call (`URI.parse`, `REXML::Document.new`, `Net::IMAP.new`,
`JSON::ResumableParser.new`). The released binary still lacks both
capabilities. bifrost-dev master has fixes for both. Two lead-specific gaps
reproduce on 0.15.1 independently of those gates, and both are now filed:
[bifrost-dev#11368](https://github.com/BrokkAi/bifrost-dev/issues/11368)
(keyword arguments to model members) and
[bifrost-dev#11369](https://github.com/BrokkAi/bifrost-dev/issues/11369)
(setter and `[]` calls aren't call shapes).
[`outcomes.json`](outcomes.json) records each lead.

The files under `probe/` are research inputs. They aren't registered pack
content, and they don't change locked policy or semantic-pack content.

## Engine

Official `v0.15.1` release, `bifrost-v0.15.1-universal-apple-darwin.tar.gz`,
from `gh release download v0.15.1 --repo BrokkAi/bifrost`. It's the version
`policy-authoring.json` pins. No newer release existed on 2026-11-10.

- Archive SHA-256: `d7ca6901787455bdabf18ec9c36453032a9be354180e54b5ff183b1e4bf83038`. It matches the release `.sha256`.
- Binary SHA-256: `00b279126297d5e9f7805390799493e915eaf4a2d5940dc3e755138a577a6df9`.
- Build identity: `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`.
- Environment: `BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, `BIFROST_OPEN_PACKS_DISABLE=1`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`, with a fresh `BIFROST_CACHE_DIR` for each run.
- Evaluation date: 2026-11-10.

## Why the 0.15.1 gates still hold

The release candidate `candidate/v0.15.1-rc` forked from bifrost-dev master on
2026-11-02. Every Ruby fix these leads need merged later, so none of them is
in the binary (see the release analysis on
[bifrost-dev#9979](https://github.com/BrokkAi/bifrost-dev/issues/9979)):

| Capability | Fix on master | On 0.15.1 |
| --- | --- | --- |
| Model-declared singleton calls bind (`URI.parse`, `X.new`) | bifrost-dev#9425 (#9336), 2026-11-03 | Target found, never bound |
| RubyGems and `ruby-toolchain` dependency-evidence rows, `:version-range` for `rubygems` | bifrost-dev#9371 (#9318 points 1, 2 and 4), 2026-11-03 | No rows. `:version-range` rejects `rubygems` |
| Package-scoped gem models activate from `Gemfile.lock` | bifrost-dev#10010 (#9319), 2026-11-06 | Not checked here. The premium probe covers it |
| Ruby engine evidence (`ruby.engine` for JRuby and TruffleRuby) | In #9371's `ruby-toolchain` rows | No rows |

These leads also need the parts that are still open upstream.
[bifrost-dev#9318](https://github.com/BrokkAi/bifrost-dev/issues/9318) point 3
is the code-to-bundle join.
[bifrost-dev#10005](https://github.com/BrokkAi/bifrost-dev/issues/10005)
would gate a taint sink on dependency evidence. The Rust session's workaround
for #10005 needs model activation from a lockfile. It splits model shards by
version, but default gems such as `uri` and `net-imap` are usually missing
from `Gemfile.lock`. Their version comes from the Ruby runtime row, and model
activation can't read that row.

## Probe results

Each probe subdirectory is its own root. Copy `probe/.bifrost/` into it, then
run `bifrost --root <dir> --query-file <dir>/<query>.rql`. The research model
`bifrost.research.ruby-catalog-0151-probe` declares `URI`,
`REXML::Document`, `Net::IMAP` and `JSON::ResumableParser`, using the
canonical `type_declaration_id(ecosystem "rubygems", name)` ids. A
non-canonical type id leaves every call with zero targets. Members are
`callable_family_complete` and have complete summaries with
`has_receiver: true`.

### Bindings: `probe/bindings/app.rb`

| Line | Call | Targets | Bound | Result |
| ---: | --- | ---: | --- | --- |
| 7 | `URI.parse(text)` | 1 | 0/1 | `callee_unresolved`, unproven, open |
| 8 | `REXML::Document.new(text)` | 1 | 0/1 | `callee_unresolved`, unproven, open |
| 9 | `Net::IMAP.new(host)` | 1 | 0/1 | `callee_unresolved`, unproven, open |
| 10 to 13 | `imap.search`, `uid_search`, `fetch`, `sort` | 1 | all | mapping exact, but dispatch unproven, open. The receiver comes from the unbound `Net::IMAP.new` |
| 14 | `JSON::ResumableParser.new` | 1 | 0/0 | `callee_unresolved`, unproven, open |
| 15, 16 | `parser.parse(text)`, `parser.partial_value` | 0 | 0 | `callee_unresolved`, unknown |

The two `parser` calls get no target, even though `imap.*` binds through the
same construction pattern. Renaming the member and passing a constructor
argument didn't change that. This wasn't filed: the singleton fix changes how
these receivers are typed, so it should be rechecked on the next release
first.

### Keyword arguments: `probe/keywords/` and `probe/workspace-control/`

| Call | Callee | Targets | Bound |
| --- | --- | ---: | --- |
| `imap.fetch(1, attr)` | model member | 1 | 2/2, exact |
| `imap.fetch(1, attr, changedsince: since)` | model member, `changedsince` declared (`named_only` or default passing mode) | **0** | 0/3 |
| `box.fetch(1, attr, changedsince: since)` | workspace `def fetch(set, attr, changedsince: nil)` | 1 | 3/3, resolved, exhaustive |

Filed as [bifrost-dev#11368](https://github.com/BrokkAi/bifrost-dev/issues/11368).

The same workspace control shows that `box.cap = since` is a zero-argument
call named `cap`, and that `box[i]` isn't a call shape at all. Both answers
are complete. Filed as
[bifrost-dev#11369](https://github.com/BrokkAi/bifrost-dev/issues/11369). It
blocks premium Nokogiri leads, not these nine.

### Version evidence: `probe/deps/`

`affected` pins `uri 0.12.1`, `rexml 3.4.1`, `net-imap 0.5.5` and `json
2.21.0`. `fixed` pins `0.12.2`, `3.4.2`, `0.5.15` and `2.21.2`. Both have
`RUBY VERSION ruby 3.3.6p108`. `no-lock` has only the `Gemfile`.

| Query | All three workspaces |
| --- | --- |
| `all.rql`, `(dependency-evidence)` | No rows, `truncated: true`, `semantic_analysis_partial`: "Ruby selected dependency publication unavailable: static dependency evidence is unavailable for this analyzer" |
| `rubygems.rql`, `:ecosystem rubygems` | Same |
| `range.rql`, `:version-range "<0.12.2"` | Invalid query: "version_ranges requires exactly one supported ecosystem: cargo, rust-toolchain, npm, nuget, go-module or go-toolchain" |

The answer is incomplete, which is correct, but no version gate can be
written.

## Leads

"After the gates" lists what each lead still needs once a release carries the
master fixes. Those needs weren't probed further, because the gates fail first.

| Lead | Advisory | Kind | Outcome | Blocked on (bifrost-dev) | After the gates |
| --- | --- | --- | --- | --- | --- |
| [#362](https://github.com/BrokkAi/bifrost-packs/issues/362) | CVE-2023-36617 `uri` | taint into `URI.parse` (also `URI.split`, `URI::RFC2396_Parser`, `URI::RFC3986_Parser`) | Blocked | #9979/#9336 (singleton binding, fixed on master), #9318, #10005 | A request or network source: `Net::HTTP.get` (the same singleton gate), Rack or Rails (premium packs), or process input (#9335). `uri` is a default gem, so its version comes from the Ruby runtime row unless the lock pins it. |
| [#363](https://github.com/BrokkAi/bifrost-packs/issues/363) | CVE-2024-35176 `rexml` | taint into `REXML::Document.new` | Blocked | #9979/#9336, #9318, #10005 | The same sources as #362. It overlaps the earlier REXML lead #283 (bundled-gem version source). |
| [#364](https://github.com/BrokkAi/bifrost-packs/issues/364) | CVE-2025-58767 `rexml` 3.3.3 to 3.4.1 | taint into `REXML::Document.new` | Blocked | #9979/#9336, #9318, #10005 | As #363. One model and sink can serve #283, #363 and #364, with a separate version gate for each. |
| [#365](https://github.com/BrokkAi/bifrost-packs/issues/365) | CVE-2025-25186 `net-imap` | value flow: a user-chosen host with the deprecated UIDPlusData expansion | Blocked | #9979/#9336, #9318, **#11368** | Host taint into `Net::IMAP.new`. The near miss is the `parser_use_deprecated_uidplus_data: false` keyword or `Net::IMAP.config`, which needs #11368 and config-object value tracking. |
| [#366](https://github.com/BrokkAi/bifrost-packs/issues/366) | CVE-2025-43857 `net-imap` | value flow: no effective `max_response_size` | Blocked | #9979/#9336, #9318, **#11368** | The `max_response_size:` keyword on `Net::IMAP.new` or in config. The near miss also needs the version, because 0.4.x and 0.3.x default to nil. |
| [#367](https://github.com/BrokkAi/bifrost-packs/issues/367) | CVE-2026-42256 `net-imap` | value flow: SCRAM without a `max_iterations` cap | Blocked | #9979/#9336, #9318, **#11368** | `imap.authenticate("SCRAM-SHA-256", user, pass, max_iterations: n)`. Variadic credentials plus a keyword, and summary effects can't reference a variadic tail (seen in the Python session). |
| [#368](https://github.com/BrokkAi/bifrost-packs/issues/368) | CVE-2026-47240 `net-imap` | typestate: a raw string criterion into `search`, `uid_search`, `sort`, `thread` or `fetch` | Blocked | #9979/#9336 (the subject comes from `Net::IMAP.new`), #9318 | Instance calls bind with mapping exact (table above). Their dispatch stays open until `Net::IMAP.new` binds. Server capability negotiation is runtime-only, so that part stays unknown. |
| [#369](https://github.com/BrokkAi/bifrost-packs/issues/369) | CVE-2026-47241 `net-imap` | typestate: a raw criterion with a trailing literal marker | Blocked | #9979/#9336, #9318 | The same sinks as #368, with one version range. One rule and model can serve #368 and #369. |
| [#370](https://github.com/BrokkAi/bifrost-packs/issues/370) | CVE-2026-71847 `json` 2.20.0 to 2.21.1 | typestate: `JSON::ResumableParser` `partial_value` after an incomplete parse | Blocked | #9979/#9336, #9318 | Receiver typing for `JSON::ResumableParser.new` results, which have zero targets on 0.15.1 (see above). The native-extension and CRuby condition needs `ruby.engine` evidence (in #9371). |

## Promotion criteria

1. A Bifrost release cut from master after 2026-11-06, carrying #9375, #9425,
   #9371 and #10010. Rerun `probe/bindings/` and `probe/deps/` first.
2. Then one reviewed `semantic-packs/ruby/` default-gem declaration model for
   `uri`, `rexml`, `net-imap` and `json`, with a version gate for each lead.
   Default gems need the Ruby runtime row unless the lock pins them, so check
   whether model activation or a policy join (#10005) can read that row.
3. The `net-imap` configuration leads (#365 to #367) also need #11368.

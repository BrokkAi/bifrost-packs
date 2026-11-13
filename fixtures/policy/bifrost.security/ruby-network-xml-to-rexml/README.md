# Network XML parsed by an affected REXML release

Qualifies two version-gated Ruby rules against `bifrost.ruby.rexml` 0.1.0:

- `bifrost.security.ruby.network-xml-to-rexml-attribute-value-dos`:
  BrokkAi/bifrost-packs#363 (CVE-2024-35176, rexml before 3.2.7).
- `bifrost.security.ruby.network-xml-to-rexml-repeated-declaration-dos`:
  BrokkAi/bifrost-packs#364 (CVE-2025-58767, rexml 3.3.3 to 3.4.1).

Both report a `Net::HTTP.get` response body (the reviewed
`bifrost.web-network-ruby` source) that reaches formal 0 of
`REXML::Document.new`. The rexml pack declares `REXML::Document.new` in three
member shards, one per Gemfile.lock version split, with the member id naming the
split. `REXML::Document` itself sits in one shared shard under Bifrost's
canonical type id. Each rule's sink selects only its own split's member, so a
locked version on the other side of its fix binds the call to a different record
and the run completes clean. Both rules use `require-model` and are opt-in.

Each case directory is its own workspace with its own `Gemfile.lock`. Run each
one separately.

## Cases

`feed_importer.rb` is the same in every locked case: positives at line 8
(`REXML::Document.new(body)` after `body = Net::HTTP.get(feed_uri)`) and line 12
(the call inline), and a near miss at line 16 that parses the constant
`DEFAULT_FEED`.

- `rexml-3.2.6`: affected by CVE-2024-35176 only.
- `rexml-3.4.1`: affected by CVE-2025-58767 only.
- `rexml-3.4.2`: the fixed-version near miss for both rules.
- `incomplete/unlocked`: a Gemfile without a lock. No shard activates, the call
  stays unbound and both runs are inconclusive, not clean.
- `incomplete/helper` (rexml 3.2.6): the body passes through an unresolved
  `FeedCache.fetch` block, so the CVE-2024-35176 run is inconclusive. The
  CVE-2025-58767 run is complete and clean because 3.2.6 is outside its range.

## Validation

Bifrost `v0.15.2` (`bifrost-v0.15.2-aarch64-apple-darwin.tar.gz`, archive SHA-256 `58c3745bf0f6be04dbf6e3844fb45747ab60189cfe625eb1ab15ee2228859d00`, binary SHA-256 `f06a8760f4099db712d91dcb0acb406589cd84a66ec3ccacaf4d0d6dbc3952dc`, build identity `340cbbdcea3fc565f6ea8066084ed24962c369d3`), with the `packs/v0.13.0` native bundle (`bifrost.public.packs-0.13.0-native.tar.gz`, SHA-256 `92bc425e60dcc42e05630ff45505aa5bef29abb1090caa10f731cc5a6e4226b4`) as `BIFROST_OPEN_SEMANTIC_PACK_BUNDLE`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off` and a fresh `BIFROST_CACHE_DIR` per run. Evaluation date 2026-11-13. The bundle supplies none of the models these cases use: each case directory carries its own copies in `.bifrost/semantic-models`.

| Case | CVE-2024-35176 rule | CVE-2025-58767 rule |
| --- | --- | --- |
| `rexml-3.2.6` | `proven_by_summary`, 2 definite (lines 8, 12) | `complete`, 0 |
| `rexml-3.4.1` | `complete`, 0 | `proven_by_summary`, 2 definite (lines 8, 12) |
| `rexml-3.4.2` | `complete`, 0 | `complete`, 0 |
| `incomplete/unlocked` | `inconclusive (partial_discovery)`, 0 | `inconclusive (partial_discovery)`, 0 |
| `incomplete/helper` | `inconclusive (partial_discovery)`, 0 | `complete`, 0 |

Every finding is `definite` and `complete`. A clean run also carries an
advisory `empty_selection` note: no call bound to that rule's sink member.

Authored hashes: `8052f429d36ce2f2d28521756a0e7395369a56cf2fb1e242548bd6c4bdd81244`
(CVE-2024-35176) and `5632682ec9748240c423944e52c7d65df3ef41fb7dae6396537300e07b3cafbd` (CVE-2025-58767); see
`rules/bifrost.security/manifest.json`.

Run from a case directory:

```console
bifrost --root . --policy-file .bifrost/policies/network-xml-to-rexml-attribute-value-dos.rqlp --policy-file .bifrost/policies/network-xml-to-rexml-repeated-declaration-dos.rqlp --no-builtin-policies --no-incremental --format json --evaluation-date 2026-11-13
```

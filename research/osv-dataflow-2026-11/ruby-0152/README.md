# Ruby CVE leads on Bifrost 0.15.2

Released Bifrost 0.15.2 (build `340cbbdc`) binds model-declared Ruby singleton
calls and activates gem models from Gemfile.lock. That unblocks four Ruby rules,
qualified in `fixtures/policy/bifrost.security/ruby-*`:

| Lead | Rule | Gate |
| --- | --- | --- |
| #363 CVE-2024-35176 | `bifrost.security.ruby.network-xml-to-rexml-attribute-value-dos` | Gemfile.lock rexml <3.2.7 |
| #364 CVE-2025-58767 | `bifrost.security.ruby.network-xml-to-rexml-repeated-declaration-dos` | Gemfile.lock rexml >=3.3.3, <3.4.2 |
| #368 CVE-2026-47240, #369 CVE-2026-47241 | `bifrost.security.ruby.network-input-to-net-imap-raw-arguments` | Gemfile.lock net-imap <0.5.15 or >=0.6.0, <0.6.4 |
| #286 CVE-2017-0903 (install part) | `bifrost.security.ruby.network-input-to-gem-installer` | none (version-independent); the sink is `Gem::Installer#install` |

`generator/genmodels.py` writes the three models in `semantic-packs/ruby/` and
`generator/mkfx.py` stages the fixture workspaces. Both run from the repository
root.

## Model authoring rules found on 0.15.2

- A Ruby constant receiver binds to a model type only through Bifrost's
  canonical type id, `type_declaration_id("rubygems", name)`: a SHA-256 over the
  length-prefixed domain `bifrost.external-declaration.type.v1` and the
  `ecosystem` and `name` fields. Any other id is accepted at load time but the
  call stays `callee_unresolved` (bifrost-dev#12588). The generator computes it.
- The same type id may not appear in two shards of one pack, so each pack puts
  its types in one shard that activates for the union of its ranges and splits
  only the members by version. Member ids are free-form; each names its split,
  so a policy selects the affected declarations by exact member id.
- Summaries are keyed by locator, not member id, so one summaries shard serves
  every split. Complete summaries close effect coverage, so every Net::IMAP
  summary declares `bifrost.network_io`.
- A clean near miss needs a fixed-version shard that declares the same API. With
  no matching shard the call stays unbound and the run is inconclusive.
- Four-segment gem versions read as three segments plus build metadata (0.6.4.1
  equals 0.6.4), and four-segment requirements are rejected. The net-imap
  ranges therefore leave 0.6.4 and 0.6.4.1 outside both shards.

## Limits on 0.15.2

- Only call sources are expressible. Request `params[...]`/`env[...]` reads are
  not call shapes (bifrost-dev#11369).
- Keyword arguments to model members get no target (bifrost-dev#11368), so
  `Net::IMAP.new(host, port: 993, ssl: true)` leaves the run inconclusive.
- An application class that defines a singleton method with the same name as a
  model singleton (for example `def self.at`) makes exact constant-path calls
  such as `Gem::Installer.at(...)` unproven: the run turns inconclusive and its
  findings `possible`. A singleton with a different name has no effect. Not yet
  filed upstream.
- Ruby runtime and default-gem versions are not activation evidence, so the
  CVE-2017-0903 parse-only slice of #286 (RubyGems before 2.6.14) stays out.
- A nested workspace under a Ruby fixture root is read for Ruby load facts even
  when `.bifrostignore` excludes it, so every fixture case is a sibling
  workspace.

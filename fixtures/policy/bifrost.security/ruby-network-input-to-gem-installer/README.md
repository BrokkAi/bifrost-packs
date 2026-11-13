# Network input chooses the gem Gem::Installer installs

Qualifies the version-independent install part of BrokkAi/bifrost-packs#286
(CVE-2017-0903) as `bifrost.security.ruby.network-input-to-gem-installer`.
Installing a gem runs its extension builds and plugins on every RubyGems
release, so a network response that chooses the archive an installer installs
chooses code that runs on the host. The CVE itself, YAML
specification loading before RubyGems 2.6.14, needs RubyGems runtime version
evidence that Bifrost 0.15.2 doesn't have, so the parse-only slice
(`Gem::Package.new`, `Gem::Specification.from_yaml`) isn't covered.

The source is the reviewed `bifrost.web-network-ruby` `Net::HTTP.get`.
`bifrost.ruby.rubygems-installer` 0.1.0 activates in every Ruby workspace
(RubyGems ships with the interpreter) and summarizes `Gem::Installer.at` as
passing its path argument to the installer it returns. Its `Gem::Installer#install`
summary declares possible network I/O at an unknown time, because the gem's own
extension builds and plugins run there. The sink is the receiver
of `Gem::Installer#install`: building an installer without installing is not
reported. The rule uses `require-model` and is opt-in.

Each case directory is its own workspace. Run each one separately.

## Cases

- `install/mirror_agent.rb`: positives at line 8
  (`Gem::Installer.at(gem_path).install` after
  `gem_path = Net::HTTP.get(control_uri)`) and line 13 (`installer.install` on an
  installer built from the inline response). Near misses: line 17 builds an
  installer from the response but doesn't install it, and line 21 installs a
  vendored archive by constant path.
- `incomplete/helper`: the response passes through an unresolved
  `ArchiveCache.store`; inconclusive.
- `incomplete/lookalike`: the `install` sources plus an application class
  `Deploy::Installer` whose own `self.at` receives network input. On Bifrost
  0.15.2 a workspace singleton method with the same name as a model singleton
  makes the exact `Gem::Installer.at` calls unproven, so the run is
  inconclusive and its two findings are `possible`.
  The lookalike call itself is not reported.

## Validation

Bifrost `v0.15.2` (`bifrost-v0.15.2-aarch64-apple-darwin.tar.gz`, archive SHA-256 `58c3745bf0f6be04dbf6e3844fb45747ab60189cfe625eb1ab15ee2228859d00`, binary SHA-256 `f06a8760f4099db712d91dcb0acb406589cd84a66ec3ccacaf4d0d6dbc3952dc`, build identity `340cbbdcea3fc565f6ea8066084ed24962c369d3`), with the `packs/v0.13.0` native bundle (`bifrost.public.packs-0.13.0-native.tar.gz`, SHA-256 `92bc425e60dcc42e05630ff45505aa5bef29abb1090caa10f731cc5a6e4226b4`) as `BIFROST_OPEN_SEMANTIC_PACK_BUNDLE`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off` and a fresh `BIFROST_CACHE_DIR` per run. Evaluation date 2026-11-13. The bundle supplies none of the models these cases use: each case directory carries its own copies in `.bifrost/semantic-models`.

| Case | Completion | Findings |
| --- | --- | --- |
| `install` | `proven_by_summary` | 2 definite (lines 8, 13) |
| `incomplete/helper` | `inconclusive (partial_discovery)` | 0 |
| `incomplete/lookalike` | `inconclusive (partial_discovery)` | 2 possible (lines 8, 13) |

Authored hash `691a4a850d4c4d64318bb5d0c7bee415250215bcea85fa7c455899236ac3ad39`.

Run from a case directory:

```console
bifrost --root . --policy-file .bifrost/policies/network-input-to-gem-installer.rqlp --no-builtin-policies --no-incremental --format json --evaluation-date 2026-11-13
```

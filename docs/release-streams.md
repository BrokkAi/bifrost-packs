# Independent public release streams

Public policy rules and semantic packs have separate identities and version
sequences:

| Stream | Manifest pack ID | Release tag |
| --- | --- | --- |
| Policy rules | `bifrost.public.rules` | `rules/vX.Y.Z` |
| Semantic packs | `bifrost.public.packs` | `packs/vX.Y.Z` |

A rules release does not imply a packs release, and matching version numbers do
not imply the contents were qualified together. Legacy releases keep their
existing manifest schema, engine range, and qualification semantics.

See [release versioning](release-versioning.md) for the independent stream bump
rules and compatibility boundaries.

## Current release status

As of 2026-11-07, the latest published streams are `packs/v0.10.0`, tagged on
`03feb65`, and `rules/v0.10.0`, tagged on `03feb65`. `packs/v0.11.0` and
`rules/v0.11.0` are prepared next. Publish the packs release first, because
the rules release depends on it exactly.

`packs/v0.11.0` is a minor release. It is built by the same released,
checksum-pinned `bifrost-semantic-pack` 0.15.1 as `packs/v0.10.0`, keeps
release index schema 4 and the same semantic-model read schemas, lists 68
packs, and needs Bifrost 0.15.1 or later. It has three kinds of change:

- **Four new native Go packs.** `bifrost.go.stdlib.io-declarations` 1.0.0
  (#244, partial) and `bifrost.go.stdlib.io` 0.1.0, `bifrost.go.stdlib.compress-gzip`
  and `bifrost.go.stdlib.compress-gzip-declarations` 0.2.0 (#320). `io.Copy` has
  no summary, because the semantic-model schema cannot express its write into
  the destination.
- **A tighter consumer requirement (#328).** The 25 Go standard-library packs
  other than `bifrost.go.stdlib.io` declare the Go toolchain range
  `>=1.26.0, <2.0.0` as compatibility and activation selector, because the
  exact-coordinate gate cannot bind a pack with an empty selector. A project
  built with an older Go toolchain, or one whose version Bifrost cannot read,
  no longer gets these models and sees a version near-miss warning. Twenty-one
  packs move to 3.0.0, and `encoding-gob` and its declarations pack move to
  0.2.0. Bifrost 0.15.1 reads these selectors in its dependency-pack
  activation, so the engine minimum does not change. The migration is to build
  with Go 1.26.0 or later. `bifrost.go.stdlib.io` 0.1.0 still has an empty
  selector.
- **Default activation (#327).** Nine packs lose `review_required` and keep
  their versions: `bifrost.typescript-stdlib` 7.0.2 and eight Node packs
  (buffer, child-process and runtime-values, JavaScript and TypeScript). Their
  model content is unchanged, but findings that depend on them can now appear
  without a `.bifrost/packs.json` entry. `bifrost.rust-stdlib` stays
  review-required.

`bifrost.python-stdlib-api-declarations` 0.6.0 and
`bifrost.python-security-sink-summaries` 0.5.0 add the `webbrowser` module
(#323). Source-only or staged, not native: the C# `System.Data` and
`System.Text.RegularExpressions` models (#319), the Node path, url and fs
models (#317), the CodeQL Rust standard-library summaries (#326) and the Rust
`std` module-function remodel in `bifrost.rust-std-sql-taint` (#329).

`rules/v0.11.0` is a minor release. It requires Bifrost 0.15.1 or later and
depends exactly on `packs/v0.11.0`. `bifrost.security` 2.3.0 adds eight
policies. Two C# taint policies are default-on:
`bifrost.security.csharp.regex-pattern-injection` (CVE-2019-0820) and
`bifrost.security.csharp.dataset-read-xml-external-location` (CVE-2020-1147).
Six are opt-in: `go.network-read-all-unbounded` (CVE-2022-30631),
`java.objectinputstream-read-without-filter` (CVE-2026-41586, typestate),
`python.process-input-to-urlopen`, `python.process-input-to-webbrowser-open`,
`javascript.process-input-to-fs-write-path` and
`javascript.process-input-to-legacy-url-parse`. The two C# and the two
JavaScript policies rely on source-only models, so without them the C#
policies report `not_run` and the JavaScript policies report an inconclusive
run with no findings. The Java policy reports every finding as possible and
its runs as inconclusive on 0.15.1 (bifrost-dev#10001). The Python policies
are opt-in because of bifrost-dev#9999 and #9991.

Severity changes (#330, #331) leave detection logic unchanged. Fifty-one
CodeQL-parity quality policies that upstream rates as recommendations move
from warning to note, so a gate that fails on warning no longer fails on
them. Ten that upstream rates as errors move from warning to error, so a gate
that fails on error now fails on them. The packs are
`bifrost.csharp-codeql-quality` 0.5.1 and `bifrost.java-codeql-quality`,
`bifrost.javascript-codeql-quality` and `bifrost.python-codeql-quality` 0.1.2.
The staged `bifrost.rust-codeql-security` catalogs (#326) enable nothing.

The `packs/v0.10.0` and `rules/v0.10.0` notes follow.

`packs/v0.10.0` is a minor release. It adds two native packs,
`bifrost.go.stdlib.encoding-gob-declarations` and
`bifrost.go.stdlib.encoding-gob`. Their summaries leave `Decoder.Decode` and
`DecodeValue` unsummarized, because the semantic-model schema cannot express a
write into the argument (bifrost-dev#9907). `bifrost.go.stdlib.net` 2.1.0 adds
`net.Conn` and `net.Listener` interface summaries. The thirteen Go declaration
packs move to new minors that mark every declared callable
`callable_family_complete` (#213). It is the first packs release built by the
released 0.15.1 producer. Its `bifrost.external.java` production uses
semantic-model schema 22 instead of 21, so it needs Bifrost 0.15.1 or later.
The bundle keeps release index schema 4 and lists 64 packs.

`rules/v0.10.0` is a minor release. It requires Bifrost 0.15.1 or later and
depends exactly on `packs/v0.10.0`. It adds the new `bifrost.rust-generic`
0.1.0 pack (#243): four note-severity review prompts from public Rust bug
fixes, enabled by default. They match calls by name (`output`, `read_dir`,
`remove_file`, `sleep`/`try_recv` and `HOME`/`USERPROFILE` env reads), not by
proven standard-library identity, and need only `structural-match`.
`bifrost.security` 2.2.0 adds two opt-in policies. `bifrost.security.rust.cargo-ssh-git-host-key-unverified`
(CVE-2022-46176) uses the Rust toolchain dependency evidence that 0.15.1
introduced. No capability name covers that evidence, so it declares none, and
Bifrost 0.15.0 rejects it at validation.
`bifrost.security.go.gob-decode-network-input` (CVE-2024-34156) needs the
`packs/v0.10.0` gob and `net` models and 0.15.1's binding of calls through
model-declared interfaces. Its runs that reach `Decoder.Decode` are
inconclusive. The rules smoke test in `pack-release.yml` runs Bifrost 0.15.1.

The `rules/v0.9.1` notes follow. It was a patch release that changes only the
exact packs dependency, from `packs/v0.8.0` to `packs/v0.9.0`. Bifrost 0.15.1
no longer falls back to its embedded packs (bifrost-dev#4438), so the six packs
that only `packs/v0.9.0` ships reach online users only once a rules release
depends on it. Policies, IDs and consumer requirements are unchanged from
`rules/v0.9.0`, which already requires Bifrost 0.15.0, the version
`packs/v0.9.0` needs.

`packs/v0.9.0` (bifrost-dev#4438) is a minor release for two reasons. First, it adds six native packs: Lombok,
Getset, Scala case-class, Python process-inputs and the two Node
runtime-values packs. With them the native bundle contains all 46 packs that
Bifrost's legacy embedded registry provides, so offline installs and
`BIFROST_OPEN_PACKS_DISABLE` users can take every built-in pack from a packs
release. Second, it is the first packs release built by Bifrost 0.15.0: the
released, checksum-pinned `bifrost-semantic-pack` 0.15.0 binary, not a source
build. Its output tightens what a consumer must read. The bundle uses release
index schema 4, and the generated productions use semantic-model schema 19
(`bifrost.external.java`: 21) instead of 17. An engine that reads only index
schema 3 skips this release during selection, so use Bifrost 0.15.0 or later.
Every other job and recipe is unchanged from 0.8.0. The
[generation notes](generation.md#legacy-built-in-packs) describe the six jobs.

`rules/v0.8.0` and `rules/v0.9.0` keep their exact dependency on
`packs/v0.8.0`, so normal acquisition through those rules releases selects
0.8.0, without the six packs. `rules/v0.9.1` moves that dependency.

The 0.8.0 release notes follow. They were prepared as `packs/v0.8.0` and
`rules/v0.8.0` (bifrost-dev#4438). `packs/v0.8.0` is a minor release: it adds
36 native packs that Bifrost previously supplied only through its embedded built-in
registry, so online runs that pin a packs release no longer lose them. The
[generation notes](generation.md#legacy-built-in-packs) list them and the six
built-in packs it kept source-only because its 0.14.0 producer could not
measure rules-only or runtime-value packs. It was published first.

`rules/v0.8.0` requires Bifrost 0.15.0 or later. A consumer engine older than
0.15.0 rejects the release at admission. It was prepared as the patch
`rules/v0.7.1`, which changed only the exact packs dependency to 0.8.0. It was
published as a minor release for two reasons. First, five existing policies now declare
a capability that only Bifrost 0.15.0 advertises (bifrost-dev#8117), so they
require more of a consumer. Second, the C# and security packs gained policies
after `rules/v0.7.0` was tagged.

### Precise capabilities from Bifrost 0.15.0

Bifrost 0.15.0 (build `09a2503c5f7ced1630a9e3c445ead53dfc5925e8`) is the first
release to advertise `resolved-value`, `field-write-value`,
`configuration-absence` and `configuration-code`. Before it, a policy that
used the `(resolved-value ...)` RQL operator could not declare that capability
without being rejected, so it listed only `exact-call-target`.

| Policy | Pack version | Before | Now |
| --- | --- | --- | --- |
| `bifrost.csharp-codeql-quality.call-to-obsolete-method` | 0.4.0 | `exact-call-target` | `exact-call-target`, `resolved-value` |
| `bifrost.csharp-codeql-quality.console-output` | 0.4.0 | `exact-call-target` | `exact-call-target`, `resolved-value` |
| `bifrost.csharp-codeql-quality.use-of-file-upload` | 0.4.0 | `exact-call-target` | `resolved-value` |
| `bifrost.security.csharp.xmldocument-url-resolver` | 2.0.0 | `exact-call-target` | `exact-call-target`, `resolved-value` |
| `bifrost.security.python.insecure-protocol` | 2.0.0 | `exact-call-target` | `exact-call-target`, `resolved-value` |

Each policy's other capabilities are unchanged. `use-of-file-upload` resolves
no call targets, so it no longer lists `exact-call-target`. The other four also
use `call-sites-to` or `resolved-call`, so they keep it. No public policy uses
`field-write-value`, `configuration-absence` or `configuration-code`. The
public configuration rules use only the operators behind `configuration-facts`,
so they keep that name. Policy sources and IDs are unchanged. The
[0.15.0 capability check](qualification/v0150-precise-capabilities.md) records
the engine and the focused outcomes.

The pack bumps follow the consumer-contract rule in
[release versioning](release-versioning.md): a stricter required capability is
a minor bump before 1.0 (`bifrost.csharp-codeql-quality` 0.3.0 → 0.4.0) and a
major bump after it (`bifrost.security` 1.4.1 → 2.0.0). The rules release CI
smoke test now uses the checksum-pinned Linux v0.15.0 binary instead of v0.14.2.

### C# CodeQL ports and Rust security policies for rules 0.9.0

Bifrost 0.15.0 adds C# `comparison`, `binary_expression` and `lock` rows, and
local and parameter reference bindings (bifrost-dev#8308). These made five
CodeQL C# queries expressible. `rules/v0.8.0` was already tagged without them,
so they ship in the minor release `rules/v0.9.0`, and the new policies bump
`bifrost.csharp-codeql-quality` from 0.4.0 to 0.5.0. Like 0.8.0, the release
requires Bifrost 0.15.0 and depends exactly on `packs/v0.8.0`:

| Policy | CodeQL query |
| --- | --- |
| `incomplete-parity-check` | `Likely Bugs/BadCheckOdd.ql` |
| `class-name-comparison` | `Bad Practices/ErroneousClassCompare.ql` |
| `empty-lock-statement` | `Likely Bugs/Statements/EmptyLockStatement.ql` |
| `self-assignment` | `Likely Bugs/SelfAssignment.ql`, locals and parameters only |
| `calls-unmanaged-code` | `Bad Practices/CallsUnmanagedCode.ql` |

`recursive-equals-call` now selects the calls an `Equals` body makes
(bifrost-packs#149), instead of the calls that reach it. Each fixture README
records CodeQL parity, the 0.15.0 run and the known limits.

Pack 0.5.0 also carries bifrost-packs#207. That PR adds `lock-this`,
`nested-if-statements` and `misleading-indentation`, and corrects
`rethrown-exception-variable` and `static-array` against CodeQL's tests.

These queries stay blocked on 0.15.0. StringBuilderInLoop needs a loop-body
entry point. EmptyInterface needs an
interface declaration kind. ConfusingMethodNames needs case folding.
ComplexCondition needs a transitive parent relation. NullArgumentToEquals now
binds in the engine, but the BCL model does not yet declare
`System.Object.Equals(object)`.

`bifrost.security` 2.1.0 adds two opt-in Rust policies (bifrost-packs#113),
so `rules/v0.9.0` carries them too:

| Policy | What it reports |
| --- | --- |
| `rust.unsound-send-sync-impl` (CWE-362) | An `unsafe impl Send` or `Sync` whose stored parameters lack the needed bound |
| `rust.callback-after-invalid-state` (CWE-908, CWE-457, CWE-415) | Caller-supplied code dominated by `set_len`, `assume_init` or a similar invalid-state API, as a panic-safety review warning |

Both declare only capabilities that Bifrost 0.15.0 advertises. The callback
policy matches APIs by name, so it is a review heuristic, and it does not match
unqualified imported pointer APIs (bifrost-dev#6247).

The 0.7.0 release notes follow.

`packs/v0.7.0` is a minor release. `bifrost.python-performance-summaries`
1.1.0 activates on `cpython >=3.10.0, <3.15.0` instead of exactly 3.13.5.
Bifrost derives the toolchain from the `requires-python` lower bound, so the
exact pin left ordinary projects without the reviewed effects, and the Python
performance loop arms stayed structured-open. The summaries, IDs, provenance
and notice are unchanged. Every other job and recipe and the 0.14.0 generator
are unchanged. The C# BCL and System.Web declaration models added since 0.6.1
remain source-only.

`rules/v0.7.0` is a minor release. It adds ten C# CodeQL ports
(`bifrost.csharp-codeql-quality` 0.3.0) and restores the `requests.get` and
`requests.post` name arm of `bifrost.performance.network-call-in-loop`
(`bifrost.code-smells` 4.0.1), whose effect-proven arm alone reported a
complete run with no findings for calls into workspace wrappers. It depends
exactly on `packs/v0.7.0`, which was published first.

Open limits stay explicit: a workspace that passes `sys.modules` to a call
leaves every reviewed standard-library summary unproven (BrokkAi/bifrost-dev#8107),
projects below CPython 3.10 activate no Python standard-library model, and
`json` and `re` performance effects are not native.

The [v0.14.2 release checks](qualification/v0142-public-release.md) record
the previous releases' identities and the exact engine profile's acceptance of
packs 0.6.1.

The original preparation plan remains below as historical context. It records
the planned order before `packs/v0.6.1` was published; its unreleased
`rules/v0.5.2` follow-up is superseded as described above.

## Previous release preparation

Published `packs/v0.6.0`, `rules/v0.5.0`, `packs/v0.5.0`, `rules/v0.4.0`,
`packs/v0.4.0`, `rules/v0.3.1`, `packs/v0.3.0` and `rules/v0.2.1` remain
immutable. Bifrost v0.14.0 rejects
`packs/v0.4.0` because its generated productions use semantic-model schema 16,
not the current schema 17. Their artifact integrity does not establish consumer
behavior or complete analysis. Earlier published streams, including
`packs/v0.2.1` and `rules/v0.1.4`, remain immutable as well.

The proposed patch `rules/v0.5.1` keeps the 238 policy source files, their IDs
and the exact dependency on `bifrost.public.packs@0.6.0`. Twenty-seven
policies in the C#, Java, JavaScript, Python and security packs (each bumped
one patch version) stop requiring synonym capability names that engines
advertised only for compatibility (bifrost-packs#109). Each synonym becomes the
canonical name it stood for, or is dropped when another listed capability
already covers what the policy uses:

| Synonym | Replacement |
| --- | --- |
| `control-flow` | `semantic-control-flow` (JavaScript `control-relations`); `python-cfg` (Python rule steps) |
| `type-hierarchy`, `exception-hierarchy` | `python-class-hierarchy` (Python); dropped for C#, whose caught-type relation belongs to `failure-handler-state` |
| `binding-resolution` | `lexical-environment` |
| `literal-value-matching`, `python-syntax-diagnostics` | dropped; `structural-match` covers value and node-kind matching |
| `expression-kind-facts`, `member-resolution`, `generic-type-facts` | dropped; `language-rule-facts` or `structural-match` covers them |
| `local-value-flow` | dropped; `python-cfg` or `python-call-relations` covers it |
| `exact-value-identity` | dropped; `exact-call-target`, `actual-to-formal-binding` and `semantic-model-provenance` cover it |

Every replacement is advertised by Bifrost v0.14.0, so no policy asks more of
a consumer and admission there is unchanged; an engine that stops advertising
the synonyms keeps admitting these policies. `bifrost.cpp-jsf.av-rule-159`
(`bifrost.cpp-jsf` 0.1.1) now selects the unary member `operator&`, which has
no declared parameters because the implicit object is not one, instead of the
binary member `operator&`. This restores the policy's stated unary address-of
scope and changes its findings; free-function overloads remain out of its
scope.

The published `packs/v0.6.0` is a minor successor to
`packs/v0.5.0`. Its native recipe adds one authored job,
`bifrost.python-performance-summaries` 1.0.0: reviewed CPython 3.13.5 declared
performance effects that the Python arms of the `bifrost.performance` loop
policies read. The pinned producer requires a complete pack envelope around
complete summaries, so the envelope is complete, and one-argument
`pickle.dumps(obj)` and `pickle.loads(data)` summaries sit beside the
full-signature ones because the engine matches summaries by call arity. The
source catalog also extends the CPython 3.13.5 runtime-base model with
`unittest.TestCase`, `MutableMapping` and `threading.Thread` ancestry and adds
declared effects to the CPython golden and Python security-sink summary
sources; the recipe does not select those, so they are not native additions.
Every other job and recipe, and the generator, are unchanged from 0.5.0. The
stream delivers eight reviewed direct result-use model families, two Go
standard-library `os` model outputs, `bifrost.php-builtin` (854 rejects and
partial completeness in a local generation, as in 0.5.0; the CI generation
report remains the release record) and the new performance model, and
preserves the full generated bundle, including schema-8 and schema-17 content.
No complete PHP runtime coverage is claimed (see the
[PHP pack notes](../semantic-packs/php/README.md)).

The recipe uses public generator-only source
`c11a13ffa03ebea154f587b899954e412b5b871e`, version `0.14.0`, with Rust
`1.99.1`. `native-generation.json` pins its source archive and Cargo.lock; the
build receipt must pin the actual generator executable. This source preparation
is not a qualified or published engine release.

Generated schema-8 native content declares actual schema and toolchain
compatibility. The producer rejects an inner engine-version requirement instead
of stripping it; historical schemas retain their original requirements. The
publication guard independently checks the generated payload. Compatibility
neither implies complete analysis in a particular run nor qualifies behavior.

The published minor `rules/v0.5.0` keeps the 238 policy source files and their
IDs and changes the consumer requirements of twenty existing policies. The
Python arms of the ten `bifrost.performance` loop policies now report a call
only when a reviewed model declares that exact operation's effect, so they
require `exact-call-target`, `semantic-model-declared-effects` and
`exhaustive-effect-coverage` (`bifrost.code-smells` 4.0.0); a call with no
exact model stays structured-open instead of matching by name. With Bifrost
0.14.0 and `packs/v0.6.0`, `time.sleep`, `subprocess.run`, `pickle.dumps(obj)`
and `pickle.loads(data)` resolve to declared effects. `json.dumps`,
`json.loads` and `re.compile` stay open because their effects live in source
models that no native recipe delivers, and `list.sort`, buffered reads,
`sqlite3.Cursor.execute` and `HTTPConnection.request` stay open because 0.14.0
does not resolve those calls to an exact target. The ten
`bifrost.effects` selected-boundary policies import their declaration selection
from `.bifrost/effect-boundaries/<language>-network-io.rqlp`, require
`declaration-selection-imports` and are opt-in (`bifrost.effects` 2.0.0): a host
supplies that document and selects them by ID. The release depends exactly on
`bifrost.public.packs@0.6.0`. The retired Go race analysis remains excluded.
Keep separate integrity, compatibility, completeness and runtime behavior
evidence; none of these metadata changes qualify an engine candidate.
The narrow dynamic-evaluation smoke does not qualify the entire policy set.

## Legacy baseline

Historical generator and release records are retained separately from the next
stream's pins.

The published `packs/v0.2.0` release contains 8 native model entries using
schema 8 from public
Bifrost tooling version `0.13.0` at source
`948f6700d2e668ee830aa42abf7ed4151d5bf560`. Its historical source archive, lockfile, Rust toolchain and build receipt
retain their recorded pins; the current generation config selects the successor.
Its source archive pins the authored inputs present at commit
`8711584116169d94475cc8dd4a18caebd5a9e8e4`; it does not contain the later Go,
Rust, Python, or expanded typeshed additions. Its native integrity is separate
from consumer behavior, which remains pending;
inspect actual schemas in the exact archive.

Concurrent legacy releases `rules/v0.1.1` and `packs/v0.1.1` were published
from `28babf267ce4602549588082d5801d78ba549edf`. They retain contract schema 1,
engine range `>=0.12.0, <0.12.1`, and pending qualification. Their manifests and
assets remain immutable. The `rules/v0.1.3` release remains the historical
105-rule, 113-content stream; the published `rules/v0.1.4` release also remains immutable.

The historical native-publication-blocker.json remains attributed to the earlier
public 0.12.0 generator and its eight gated descriptors.

The legacy `rules/v0.1.0` stream contains the exact 49 policies (four native
catalogs) from public Bifrost `v0.11.5`, commit
`4ec4489e850b809c9cc7750e4c450c7560c45de0`. The repository's larger policy
copy remains available for authoring. The legacy `packs/v0.1.0` archive is the
upstream `bifrost-semantic-packs-v0.11.5.tar.gz` (SHA-256
`d16f94892ddd01cf9e1a2e77f4bda48fe09720f9b3bab7d1b41efd6413ebb3b1).
It preserves authored pack versions, generated production versions, and
`partial` completeness. Its release metadata uses the exact legacy engine range
`>=0.11.5, <0.11.6` and legacy qualification rules. Those values and semantics
remain unchanged for v1 manifests.

For new pack artifacts, `semantic_model_read` and `release_index` are the
relevant release-schema axes; the manifest records the exact values found in the
generated content when known. Do not fill in unknown future schema values from
the generator version. Per-content completeness remains explicit, including
`partial`.

The existing release baseline remains available for historical baseline builds and
continues to pin source commits, policy files, and the native archive checksum.
The current rules stream is selected from the content lock; release-building
joins the `content-lock.json` header and its `content-lock/` shards into the
single-file lock, computes its aggregate, and verifies its locked bytes and
archive contents. The archived `content-lock.json` keeps the single-file format,
and `content_origin.lock_sha256` is the digest of that joined lock, so sharding
the authoring lock changes no archive bytes and needs no stream version bump.
Contributors regenerate shards with `scripts/content.py lock`; see
[Locking content](../README.md#locking-content). Manual dispatch stages raw
generation evidence. A stream tag can publish after the exact dependency and
verified-integrity checks; schema-2 behavior may remain pending or limited.
Consumer capability and behavior proof remains required before default
selection or a consumer cutover.

See [the shared contract](../release-contract/README.md) for schema 1 and 2
selection semantics, and [generation](generation.md) for the generator pin,
integrity evidence, and behavioral limits.

Smoke evidence is also retained in `smoke-evidence.zip`, including exact zero-byte logs that GitHub cannot accept as standalone release assets. The ZIP has stable member ordering, timestamps, and permissions. The `rules/v0.1.2` publication attempt passed packaging and dependency verification but failed uploading an empty log; it has no published release.

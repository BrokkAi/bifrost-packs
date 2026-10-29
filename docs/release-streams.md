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

As of 2026-10-29, the latest published streams are `packs/v0.6.1` and
`rules/v0.6.0`. The next releases are prepared as `packs/v0.7.0` and
`rules/v0.7.0` (bifrost-packs#168).

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
exactly on `packs/v0.7.0`, so publish that first.

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

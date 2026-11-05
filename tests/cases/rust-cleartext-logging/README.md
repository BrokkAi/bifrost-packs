# Rust cleartext logging candidate

These Cargo projects exercise
`bifrost.security.rust.cleartext-logging` with the public
`bifrost.rust-std-io-write` and `bifrost.rust-core-logging` model inputs.
The rule is a source candidate; see the qualification results below before
using it as evidence that a program is clean.

- `positive`: sensitive parameter reads and a sensitive field reach prelude
  and explicitly qualified standard print macros. Expected: three findings.
- `near-miss`: parameters whose names indicate encryption, hashing or a path
  are not sensitive-name sources. Expected: zero findings with a bound sink.
- `name-lookalike`: ordinary functions named `println`, `eprintln` and
  `panic_fmt`, a user writer, and a shadowing `println!` macro are not standard
  sinks. A genuine standard macro prints a constant. Expected: zero findings.
- `string-as-str`: an explicitly typed `String` receiver passes its sensitive
  contents through `as_str` to standard output; an encrypted-name control
  uses the same method. The return is stored in a neutral `message` local.
  Expected: one finding for the sensitive input; qualification below records
  the measured certainty and completion.
- `receiver-field`: a newtype-wrapped `self.api_key.inner()` reaches a
  standard print directly and through a neutral local. Expected: two findings;
  an encrypted-field control and an unused sensitive binder must add none.
- [`string-conversions`](string-conversions/README.md): one local-result
  witness per requested conversion, explicit-trait witnesses and a distinct
  same-named trait control. Source models retain standard trait identities;
  unsupported native impl binding is not replaced with inherent methods.
- `barrier-near-miss`: CodeQL's boolean and fieldless-enum barriers prevent
  logging those values from being reported. Expected: zero findings. This is
  an explicit engine-gap witness, not a passing qualification claim.

Install a byte-identical copy of the policy under
`.bifrost/policies/cleartext-logging.rqlp` in each project, and configure the
enabled models as described in the
[core declaration notes](../../../semantic-packs/rust-codeql-parity/README-core-logging.md).
Run the CLI over the whole project:

```sh
bifrost --root CASE --policy --no-builtin-policies \
  --policy-file .bifrost/policies/cleartext-logging.rqlp \
  --evaluation-date 2026-10-15 --fail-on never --format json
```

A nonzero reliability status or an inconclusive completion must be retained
even when the reported findings agree with the expected locations.

## Upstream gate

The gate uses unchanged `test_logging.rs`, `Cargo.lock`, `options.yml` and
`CleartextLogging.expected` from
[`github/codeql` at dd4405c2](https://github.com/github/codeql/tree/dd4405c2c2a8cd5ee7d200e7230ab8dd52e13dc6/rust/ql/test/query-tests/security/CWE-312).
Copy the test to `src/test_logging.rs` in a small Cargo binary project, retain
the lock and options files, and reproduce every `qltest_dependencies` entry
from `options.yml` in `[dependencies]`. The source itself remains unmodified.
Use the same model setup and whole-project policy command.

Compare findings with the `#select` section of `CleartextLogging.expected`,
not the auxiliary edge/node tables. Nineteen expected results use standard
sinks. Thirty-seven use `log` or `log_err`, which require a separate premium
follow-up and are deliberately absent from this public rule. Locations marked
`MISSING` in upstream comments are not expected results.

## Qualification results (2026-10-15)

Fresh validation used a release build of current development Bifrost 0.13.0,
executable SHA-256
`29ce5752eaf9108e3f286b7549d58617756f9143ac08c0189797a46b536f743a`.
Every workspace enables both public models with the configuration in the
[core declaration notes](../../../semantic-packs/rust-codeql-parity/README-core-logging.md).
Complete, exactly bound active summaries require no separate workspace
approval. All runs use fresh caches and the current activation contract.

| Gate | Findings | Run completion |
| --- | --- | --- |
| positive | 3 expected, definite/complete | inconclusive: partial discovery |
| near-miss | 0 | proven by summary |
| name-lookalike | 0 | inconclusive: partial discovery |
| barrier-near-miss | 2 unexpected, definite/complete | inconclusive: partial discovery |
| upstream standard sinks | **19 of 19**, 0 extras; 14 definite/complete, 5 possible/partial | inconclusive: partial discovery and incomplete capabilities |
| String::as_str through a neutral local | 1 expected, possible/partial | proven by summary |
| field receiver directly in print, line 15 | 1 expected, reported definite/complete | proven by summary |
| field receiver through a local, line 20 | 1 expected, possible/partial | proven by summary |

Run completion and individual finding certainty are separate. A run marked
`proven_by_summary` can retain possible findings whose proof is unproven.
The five possible upstream findings are **229, 242, 245, 248 and 251**;
line 229 is now found. The remaining receiver-path proof closure is an engine
gap. All 37 third-party results remain expected premium omissions.
Comparison matches unique overlapping call ranges: multiline I/O calls start
at lines 240 and 243 while CodeQL's selected spans are at 242 and 245. No
finding matches multiple expected rows.

The boolean and fieldless-enum barrier cases still produce two false positives
and require native value-type barriers plus a rule follow-up. Macro operand
evaluation also remains incomplete: the small counterexample
`println!("{}", password.len())` reports a definite sensitive-string flow.
The direct field receiver result shares this current macro-lowering behavior;
proper call evaluation and dispatch within formatting operands still need
qualification. The additional counterexample is separate from the unchanged
upstream oracle, which has zero extra results.

The field-receiver fixture now finds both expected lines. Its previous-model
control gives the same definite direct and possible local findings. No
conversion model alias or selector workaround is introduced. These focused
results do not qualify the actual Vector workspace.

Conversion witnesses and encrypted-name controls run separately; see
[the per-method table](string-conversions/README.md). Native bindings for
Clone, both ToString receivers, ToOwned and From remain unproven with zero
conversion targets, including explicit trait-qualified Clone and From calls.
ToOwned nevertheless produces a definite finding with both current and prior
model sources, so that positive is not evidence that the new trait summary
bound. Zero findings under incomplete discovery do not establish safety.

This candidate is **not behavior-qualified for release**. All 182 source
policy identities were certified separately using the public producer pinned
in `native-generation.json` (0.13.1); it was used only for identities. The rule
authored hash remains
`b7fddb06e44b9823848d5fb0d7142ad47c1f52dbba9f5cd2f101f709c1520545`.
Authoring certification does not establish released-engine coverage. No
release, native recipe change or model/policy byte change is included in this
activation-documentation update.

See the [source role audit](ROLE_AUDIT.md). I/O source version 0.4.0 keeps the
precise borrowed string/byte-slice returns and CodeQL standard trait conversion
models. Generic Into element projections and unmodeled into_bytes remain
explicit omissions. Workspace enablement and summary binding/completeness
remain separate from storing this source catalog.

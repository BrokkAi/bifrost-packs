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
models and reviewed receipts as described in the
[core declaration notes](../../../semantic-packs/rust-codeql-parity/README-core-logging.md).
Run the CLI over the whole project:

```sh
bifrost --root CASE --policy --no-builtin-policies \
  --policy-file .bifrost/policies/cleartext-logging.rqlp \
  --evaluation-date 2026-10-14 --fail-on never --format json
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

Behavioral validation used a development Bifrost 0.13.0 executable with SHA-256
`79ef45ef153a4f113d4cba46e75e0d9ff837804125ca0cf6f4e2a191bf699f4f`,
built with the pending macro, reference-result and binding fixes. The public
CI-pinned 0.13.1 producer was used separately for authoring identities only.
Both model inputs validated and compiled. Reviewed manifest receipts:

- I/O source 0.4.0: `82e103499418fc720cd9b7811fad5c9f4ced365284a330e90b63e7cb5acf82df`.
- Core declarations: `4596d3193525def0f8f6db3f96c0fbd53bb8221aba26bd8e79da47af167a0519`.

| Gate | Findings | Completion |
| --- | --- | --- |
| positive | all 3 expected, definite/complete | inconclusive: partial discovery |
| near-miss | 0 | proven by summary |
| string-as-str through a neutral local | 1 expected, definite/complete | proven by summary |
| receiver-field newtype | 0 of 2 expected | inconclusive: partial discovery |
| name-lookalike | 0 | inconclusive: partial discovery |
| barrier-near-miss | 2 unexpected, definite/complete | inconclusive: partial discovery |
| upstream standard sinks | 18 of 19 expected; 0 extras | inconclusive: partial discovery and incomplete capabilities |

The sole missing upstream standard-sink result is line **229**, the
`Option::expect(format!(...).as_str())` message. Its sink selector retains
unproven dispatch and no complete bindings. Every other expected standard
result is reported as definite/complete. Comparison uses unique overlapping
call ranges: multiline I/O calls start at lines 240 and 243 while CodeQL's
selected method spans are at lines 242 and 245. No finding is matched twice.
All 37 third-party results remain expected premium omissions.

The boolean and fieldless-enum barriers still produce two false positives.
The receiver-field fixture is a development-engine regression: both the direct
`println!("Honeycomb API key: {}", self.api_key.inner())` and local-result
paths are missed, with `inner` reporting invalid-location/no materialized
workspace target. Repeating it with the previous I/O 0.3.1 source and its
review receipt also yields zero. No pack alias or selector workaround is
introduced. Neither result qualifies the actual Vector workspace.

Conversion witnesses and their encrypted-name controls run separately; see
[the per-method table](string-conversions/README.md). Native call bindings for
Clone, both ToString receivers, ToOwned and From remain unproven with zero
conversion targets, including explicit trait-qualified Clone and From calls.
ToOwned's positive nevertheless reports a definite finding with the old model
too, so it is not evidence that the added trait summary bound successfully.
Zero results under incomplete coverage do not establish clean programs.

This candidate is **not behavior-qualified for release**. All 182 source
policy identities were certified using the public producer pinned in
`native-generation.json` (0.13.1). The rule authored hash remains
`b7fddb06e44b9823848d5fb0d7142ad47c1f52dbba9f5cd2f101f709c1520545`.
Authoring certification does not establish runtime coverage or complete
released-engine compatibility. No release or native recipe change is included.

See the [source role audit](ROLE_AUDIT.md) for all included/excluded roles.
Source version 0.3.1 precisely declared borrowed string and byte-slice returns.
Version 0.4.0 adds CodeQL-derived standard trait conversion source models beside
those string-view carriers; no new pack is introduced. Generic Into element
projections and unmodeled into_bytes remain explicitly omitted.

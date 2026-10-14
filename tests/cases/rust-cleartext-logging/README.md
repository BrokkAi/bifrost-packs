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

## Qualification results (2026-10-14)

Behavioral validation used a development Bifrost 0.13.0 executable with SHA-256
`c9d33c6a2e1498e93a58f43c2c207b74531c569a8b3fac43644e53eda1c17e5d`.
The core declaration model compiled without validation errors. Its manifest
receipt is `4596d3193525def0f8f6db3f96c0fbd53bb8221aba26bd8e79da47af167a0519`;
the I/O model receipt is
`ae9de7854a4dc1e314a0fc18746762185946f21106219c95a040c3ba7e9ce8f6`.

| Gate | Findings | Completion |
| --- | --- | --- |
| positive | all 3 expected, definite | inconclusive: partial discovery |
| near-miss | 0 | proven by summary |
| name-lookalike | 0 | inconclusive: partial discovery |
| barrier-near-miss | 2 unexpected, definite | inconclusive: partial discovery |
| upstream standard sinks | 4 of 19 expected; 0 extras | inconclusive: partial discovery and incomplete capabilities |

The upstream standard-sink results found are lines 192, 193, 194 and 195.
Missing lines are 199, 202, 205, 208, 211, 214, 217, 220, 223, 226, 229, 242,
245, 248 and 251. Core panic/assert macros produce `unknown_macro_derived`
call-shape coverage and unavailable formal bindings. `Option::expect` and
locked I/O write calls do not establish complete receiver/call bindings.
The barrier fixture confirms the missing boolean and fieldless-enum barriers.
The shadowing macro also leaves incomplete selector discovery. Empty results
under these incomplete outcomes do not prove safety.

This candidate is **not behavior-qualified for release**. Source authoring
identity verification certified all 182 policy identities with the separate
public CI producer pinned in
`native-generation.json` (0.13.1); those identities do not certify runtime
coverage, and no complete released-engine compatibility claim is made here.

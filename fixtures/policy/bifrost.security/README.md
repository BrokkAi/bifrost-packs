# Public C# and Rust CodeQL security fixtures

The C# fixtures exercise the five public BCL-backed injection policies. The Rust fixture covers the non-HTTPS URL literal rule, which classifies string values structurally and requires no third-party semantic models.

The Rust SAST fixtures cover unsafe marker impl bounds and caller-supplied calls after invalid-state APIs. Their isolated positive and near-miss crates are fresh public sources. See each `expectations.json` and `scripts/rust-sast-gate.py`; unreleased vocabulary requires the integration build, and released-engine qualification is pending.

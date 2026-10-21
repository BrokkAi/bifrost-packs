# callback-after-invalid-state

Fresh Apache-2.0 public fixtures authored for this pack. Engine test fixtures were consulted for vocabulary only; no private fixture source is imported. Run the focused gate with `python3 scripts/rust-sast-gate.py --binary /path/to/bifrost --output /path/to/evidence`.

Each isolated crate has one positive or near-miss in `expectations.json`. Findings must have complete evidence; empty incomplete runs never pass. Fixtures are analysis inputs and must not be executed. Exact engine identity and runtime results belong in the gate evidence and qualification record, not in an engine release claim.

The imported-ptr-read case is expected zero as an accepted known gap: unqualified imported pointer APIs are not matched ([BrokkAi/bifrost-dev#6247](https://github.com/BrokkAi/bifrost-dev/issues/6247)). Fully qualified `std::ptr::read` and `core::ptr::read` are covered; value-receiver `.read()` remains excluded. The benchmark prioritizes the set_len panic-safety shape; a zero result for imported pointer calls is a coverage limitation, not evidence of safety. All qualified pointer, mem and slice API matches are name-based review heuristics.

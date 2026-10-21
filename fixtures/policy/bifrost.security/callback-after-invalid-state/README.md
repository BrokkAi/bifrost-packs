# callback-after-invalid-state

Fresh Apache-2.0 public fixtures authored for this pack. Engine test fixtures were consulted for vocabulary only; no private fixture source is imported. Run the focused gate with `python3 scripts/rust-sast-gate.py --binary /path/to/bifrost --output /path/to/evidence`.

Each isolated crate has one positive or near-miss in `expectations.json`. Findings must have complete evidence; empty incomplete runs never pass. Fixtures are analysis inputs and must not be executed. Exact engine identity and runtime results belong in the gate evidence and qualification record, not in an engine release claim.

The imported-ptr-read case intentionally retains the required positive expectation and currently fails on integration build efd25a06b34efd714f4e6ceac74b30b8114c5c1b. The engine exposes a terminal callee name and receiver but cannot prove whether bare `ptr` names a module or a value; fully qualified `std::ptr::read` and `core::ptr::read` are covered. The raw-receiver-read near miss exercises the requested fallback exclusion. Do not lower the imported-path expectation to hide this coverage gap.

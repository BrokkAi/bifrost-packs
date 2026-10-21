# unsound-send-sync-impl

Fresh Apache-2.0 public fixtures authored for this pack. Engine test fixtures were consulted for vocabulary only; no private fixture source is imported. Run the focused gate with `python3 scripts/rust-sast-gate.py --binary /path/to/bifrost --output /path/to/evidence`.

Each isolated crate has one positive or near-miss in `expectations.json`. Findings must have complete evidence; empty incomplete runs never pass. Fixtures are analysis inputs and must not be executed. Exact engine identity and runtime results belong in the gate evidence and qualification record, not in an engine release claim.

All 14 cases pass on integration build efd25a06b34efd714f4e6ceac74b30b8114c5c1b, with positive findings anchored on the impl header and definite, complete evidence. The required per-parameter message remains blocked: match policies accept static messages and cannot interpolate the parameter and missing bound. See the focused qualification record; released-engine qualification remains pending.

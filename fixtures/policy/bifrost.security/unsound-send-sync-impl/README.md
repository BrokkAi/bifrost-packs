# unsound-send-sync-impl

Fresh Apache-2.0 public fixtures authored for this pack. Engine test fixtures were consulted for vocabulary only; no private fixture source is imported. Run the focused gate with `python3 scripts/rust-sast-gate.py --binary /path/to/bifrost --output /path/to/evidence`.

Each isolated crate has one positive or near-miss in `expectations.json`. Findings must have complete evidence; empty incomplete runs never pass. Fixtures are analysis inputs and must not be executed. Exact engine identity and runtime results belong in the gate evidence and qualification record, not in an engine release claim.

All 17 cases pass on public Bifrost 0.15.0 (build 09a2503c5f7ced1630a9e3c445ead53dfc5925e8); see the focused qualification record. The accepted static message is generic; read the impl header the finding points at to identify the stored type parameter and required marker bound.

The shared-method fixtures cover access classification: methods that read only non-stored metadata fields do not report a Sync impl; Debug through a helper and a shared method in a different file do.

The classifier conservatively counts every read of a field that stores the type parameter. A metadata-only operation on such a field (for example, the alternative Tokio scheduler Inner reading self.buffer.len()) can therefore still report a Sync impl. Distinguishing that case from value access requires a separate engine design decision.

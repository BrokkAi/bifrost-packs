# unsound-send-sync-impl

Fresh Apache-2.0 public fixtures authored for this pack. Engine test fixtures were consulted for vocabulary only; no private fixture source is imported. Run the focused gate with `python3 scripts/rust-sast-gate.py --binary /path/to/bifrost --output /path/to/evidence`.

Each isolated crate has one positive or near-miss in `expectations.json`. Findings must have complete evidence; empty incomplete runs never pass. Fixtures are analysis inputs and must not be executed. Exact engine identity and runtime results belong in the gate evidence and qualification record, not in an engine release claim.

The original 14 cases were qualified on integration build efd25a06b34efd714f4e6ceac74b30b8114c5c1b. That record predates the shared-access refinement; the current 17 cases require requalification with the combined #6385/#6394 engine. The accepted static message is generic; read the impl header the finding points at to identify the stored type parameter and required marker bound. See the focused qualification record; released-engine qualification remains pending.

The #6385 fixtures also exercise shared-method access: metadata-only methods do not report a Sync impl; Debug through a helper and a shared method in a different file do. The engine change depends on #6394 for cross-file method inventory. Requalify with the local combined engine before recording results.

Preliminary #6385 debug validation passes 16 of 17 marker cases and all 20 callback cases. The sole pending case is cross-file-shared-read (one expected finding, zero before #6394). Its expectation is retained. The final combined release-build gate remains required.

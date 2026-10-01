# Node authenticated-decipher finalization probe

This is a bounded, unqualified model attempt for
[`node-crypto-authenticated-decipher-finalization`](../../candidates.md#node-crypto-authenticated-decipher-finalization).
The candidate asks whether provisional bytes returned from a Node
`node:crypto` `createDecipheriv('aes-*-gcm', ...)` `update()` reach a
reviewed publication boundary before `final()` returns successfully on the
same decipher object.

The Node v26.7.0 source-only runtime witness passes the concrete cases: publish
before a tampered-tag `final()` throws; keep bytes private until valid-tag
`final()` succeeds; keep bytes private when `final()` throws; finalize a
different valid decipher before publishing the target's provisional bytes;
exercise an import alias and helper return; exclude a valid AES-CBC operation;
and run a same-spelling workspace-local implementation. The publication
boundary is a local test ledger, and the fixtures do not perform I/O or network
operations. Runtime success verifies the fixture contract only.

Static results do not qualify the candidate. On the recorded Bifrost 0.12.0
build and activation, the exact Node crypto declarations were not materialized.
Six direct factory-shaped calls resolve to the generic unmaterialized external
boundary with partial/truncated target coverage. Method calls remain unknown
and open; call-binding emits 33 typed incomplete diagnostics across 36 rows,
including unknown receiver bindings. A same-name local factory resolves to a
workspace declaration, illustrating why spelling is insufficient. The
discovery-only RQLP selector completes with 41 syntactic findings, including
five in the lookalike fixture; that result is intentionally not treated as a
crypto finding. Exact declaration identity is the stop gate, so no
same-object `update()`/`final()` analysis or final-success dominance result is
claimed.

[`outcomes.json`](outcomes.json) gives per-case supported/incomplete status,
typed diagnostics, exact binary/runtime identity, query arguments, fixture and
query hashes, canonical report hashes, and the observed activation reason.
Raw analyzer reports are retained only as local temporary evidence. The public
summary contains no host-specific absolute paths or private research material.

The discovery-only policy may be replayed with:

```sh
"$BIFROST_012" --root . --no-builtin-policies \
  --policy-file rqlp/discovery-only.rqlp \
  --evaluation-date 2026-10-01 --format json
```

Individual JSON queries use `--root . --query-file queries/<name>.json`.
Run the original fixture witness with `node fixtures/runtime-witness.mjs`.
Check the binary SHA-256 against `outcomes.json` before comparing results.

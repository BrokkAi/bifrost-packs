# TLS verification typestate prototype

This directory records a bounded Python `ssl.SSLContext` query/model probe for
[`python-ssl-client-verification-typestate`](../../candidates.md#python-ssl-client-verification-typestate).
It is a research prototype, not an enabled or qualified rule. Ruby
`Net::HTTP` is covered by the [separate Ruby Net::HTTP investigation](../ruby-net-http/README.md).

[`outcomes/python-ssl-client-verification-typestate.json`](outcomes/python-ssl-client-verification-typestate.json)
contains per-case expectations, result classifications, diagnostics, exact
artifact hashes, and reproducible CLI arguments. Original harmless fixture
functions do not run, import network inputs, or perform TLS. Cases involving a
handshake document an expected connected-client-socket precondition; static
analysis did not establish that a real caller satisfies it.

The 0.12.0 binary finds the call syntax and emits state-event rows. This is
discovery only. Imported `ssl` constructor targets are unmaterialized external
boundaries; calls through the resulting context have unknown receiver dispatch
and incomplete formal binding. The handshake relationship is not proven. A
same-spelling local `SSLContext` class resolves to a source declaration,
demonstrating why callee-name matching cannot establish the stdlib API. No
`.rqlp` policy was written.

The isolated state probe is informative but incomplete for the real constant:
property events with scalar `verify_mode = 0` are complete, while replacing the
scalar with `ssl.CERT_NONE` yields partial property events and a
`flow_state_derivation_incomplete` diagnostic about a field access without a
binding-rooted base. The evidence localizes this difference to qualified
constant handling in this fixture; it does not yet tell us whether or how the
runtime constant should be declared/modelled. State-event rows expose internal
value IDs without a typed SSL member/value identity, and `member_targets` and
`field_write_value` report unsupported/omitted evidence for context field
writes. The prototype therefore remains `incomplete`, with zero findings and
no clean-coverage claim.

Use the repository's exact binary when reproducing:

```sh
"$BIFROST_0_12_0" \
  --root "$PYTHON_FIXTURE_WORKSPACE" \
  --query-file queries/python-call-bindings.json
```

`BIFROST_0_12_0` must name the exact binary whose version and SHA-256 appear in
the outcome JSON. The outcome JSON lists each executed argument set,
fixture/query digest, and raw output digest. Full raw diagnostics remain in
temporary run evidence outside this public research directory.

# Ruby Net::HTTP peer-verification model attempt

This is a bounded, incomplete modeling attempt for catalog candidate
`ruby-net-http-active-peer-verification-disabled`. The contract under study is
CRuby 3.4.0 with shipped default gem `net-http` 0.6.0 and the OpenSSL binding
loaded by that runtime. A report would require declaration-backed Net::HTTP
identity and proof that one client has TLS enabled and effective
`VERIFY_NONE` when its active request starts. `VERIFY_PEER`, unused configuration,
a different active object, and the local `HTTP` lookalike must remain distinct.
No production rule is registered.

The five fixtures are source-only analyzer inputs. **Do not execute the unsafe
positive fixture as a network client.** No fixture was compiled or run. The host
has CRuby 2.6.10p210 with LibreSSL 3.3.6; `net-http` was not present as an
installed gem in `gem list`, so the required Ruby 3.4.0/default-gem/OpenSSL
runtime contract was not exercised. Runtime behavior is therefore unsupported
by this attempt, not inferred from the older host.

## Analyzer result

The exact managed Bifrost 0.12.0 binary parsed and queried the fixtures. The
structural query found source shapes, but did not prove API or session identity:

- `get_declarations_by_location` for `Net::HTTP` at the positive constructor
  returns `unresolvable_import_boundary` (`Net::HTTP` appears to cross an
  unindexed Ruby gem boundary). The `use_ssl=`, `verify_mode=`, `start`, and
  block `get` sites return `unsupported_ruby_receiver`.
- `get_type_by_location` reports `ruby_dynamic_receiver_unsupported` for the
  constructor result and setter/start/request receivers.
- `call_bindings` reports 15 syntactic call rows, all with `selector_exact=false`
  and zero bound actuals; dispatch coverage is open, and the ordinary
  Net::HTTP calls have unresolved callees/unknown targets.
- The state-event query reports `flow_state_axis_unsupported`: Ruby's current
  lowering leaves `binding_events`, reaching/dominance, property
  reaching/dominance, and same-evaluation relations uncovered. It emits partial
  binding events only, which cannot establish same-object property state at the
  active request.
- The local lookalike resolves its own `HTTP.verify_mode` declaration, which is
  useful negative identity evidence; it does not provide a route to prove the
  external Net::HTTP contract.

These are reproduced capability gaps for the exact fixture CLI probe. They do
not say that Ruby or Net::HTTP is universally unsupported, nor that the Ruby
runtime contract is qualified. No RQLP rule was authored: the available query
steps can discover structural candidates, but this probe did not establish a
sound selector or state proof for classification.

## Reproduction

From the repository root, create a temporary workspace with the fixture files
and run the relative commands below with the exact binary path. The stdout JSON
reports and full absolute invocations are retained outside the public checkout
in task-local raw evidence storage; its host paths are intentionally omitted here.

```sh
BIFROST=/path/to/bifrost-0.12.0
# FIXTURE_ROOT is a temporary workspace containing fixtures/ and queries/.
cd "$FIXTURE_ROOT"
"$BIFROST" --root . --query-file queries/ruby-call-bindings.json
"$BIFROST" --root . --query-file queries/ruby-property-assignment-shapes.json
"$BIFROST" --root . --query-file queries/ruby-http-state-events.json
"$BIFROST" --root . --tool get_declarations_by_location --args "{\"references\":[{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":5,\"column\":10},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":5,\"column\":19},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":6,\"column\":8},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":7,\"column\":8},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":8,\"column\":8},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":9,\"column\":17},{\"path\":\"fixtures/near-local-lookalike.rb\",\"line\":23,\"column\":8}]}"
"$BIFROST" --root . --tool get_definitions_by_location --args "{\"references\":[{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":5,\"column\":10},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":5,\"column\":19},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":6,\"column\":8},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":7,\"column\":8},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":8,\"column\":8},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":9,\"column\":17},{\"path\":\"fixtures/near-local-lookalike.rb\",\"line\":23,\"column\":8}]}"
"$BIFROST" --root . --tool get_type_by_location --args "{\"references\":[{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":5,\"column\":10},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":5,\"column\":19},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":6,\"column\":8},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":7,\"column\":8},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":8,\"column\":8},{\"path\":\"fixtures/positive-active-verify-none.rb\",\"line\":9,\"column\":17},{\"path\":\"fixtures/near-local-lookalike.rb\",\"line\":23,\"column\":8}]}"
```

The fixture CLI workspace and repository corpus are different evidence scopes.
The commands above run only the authored fixture workspace; the candidate
catalog is read-only context, not an analyzed source corpus. Hashes of every
fixture and query, candidate source hash, and query-output evidence hashes are in
[`outcome.json`](outcome.json).

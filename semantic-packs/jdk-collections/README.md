# JDK collection-flow models

`bifrost.jdk-collection-flows` carries CSMI `collection-flow` 0.1.0 contracts
for `java.util` containers. With these contracts the engine can track taint
per map key instead of tainting the whole container
([BrokkAi/bifrost-dev#10989](https://github.com/BrokkAi/bifrost-dev/issues/10989)).
Without them, the engine keeps whole-object collection taint. Tracking issue:
[BrokkAi/bifrost-packs#336](https://github.com/BrokkAi/bifrost-packs/issues/336).

The pack is hand-authored from the Java SE API specification. It declares the
modeled members and attaches one `collection_flows` row to each one. When the
pack is active, each declaration composes with the matching declaration in the
JDK artifact, and the engine finds the row through that composed member.

## Coverage

All 12 rows are Keyed rows with `coverage: complete`. They apply to both
`java.util.Map<K, V>` and `java.util.HashMap<K, V>`. The receiver shape is
`keyed{key: K, value: V}`, and `receiverSubstitution` binds `K` and `V` from
the receiver's type arguments.

| Member | Transfers |
| --- | --- |
| `put(K, V)` | parameter 0 → receiver . entry{key: parameter 0} . entry-key; parameter 1 → receiver . entry{key: parameter 0} . entry-value; old receiver . entry{key: parameter 0} . entry-value → result |
| `putIfAbsent(K, V)` | Same transfers as `put` |
| `get(Object)` | receiver . entry{key: parameter 0} . entry-value → result |
| `getOrDefault(Object, V)` | receiver . entry{key: parameter 0} . entry-value → result; parameter 1 → result |
| `remove(Object)` | old receiver . entry{key: parameter 0} . entry-value → result |
| `containsKey(Object)` | none: the boolean result carries no key or value content |

A transfer source is an input root, so it reads the receiver as it was before
the call. That lets `put`, `putIfAbsent` and `remove` return the previous value.

## Limitations

- CSMI collection-flow 0.1 transfers only add content. A row cannot say that
  `remove` deletes an entry or that `put` replaces the previous value. The
  rows are therefore a sound over-approximation: a value stays reachable at its
  key after it is removed or replaced.
- `putIfAbsent` stores only when the key is absent or maps to `null`. The
  profile has no conditional transfer, so the row states the unconditional
  store, the same as `put`.
- Other overloads and members are not modeled, for example `remove(Object,
  Object)`, `putAll`, `compute*`, `merge`, `keySet`, `values`, `entrySet` and
  `forEach`. No member claims `callable_family_complete`.
- List rows (`add(E)`, `add(int, E)`, `remove(int)`, `get(int)`, `set(int, E)`)
  need the CSMI Sequence shape from bifrost-dev#10989 Milestone 3. They are not
  in this pack yet.
- The engine reads these rows only after its Java collection-flow consumer
  lands (bifrost-dev#10989). Until then the pack is inert. It is not in a
  native release recipe.

## Validation

`bifrost-semantic-pack validate`, `lint` and `compile` accept the native
pack (bifrost-dev `3d74223afcb`). The CLI has no native-to-CSMI export
subcommand, so the rows were exported with the engine's
`export_authored_csmi_pack` and checked with `bifrost-semantic-pack
csmi-check`. That check passes structural, semantic and integrity validation,
and the collection-flow profile is structurally valid. It reports
`interpretable: false` only because the CLI checks with no supported
vocabularies. A deliberately broken projection fails with
`semantic.collection_flow_projection_shape`.

At that revision, the generic exporter cannot export this pack unchanged:

- It copies the native `callable` and `receiverSubstitution.declaration` IDs
  as they are, instead of remapping them to the exported CSMI symbols. The
  check used a local exporter patch that remaps both.
- It emits a `named` reference to a type the pack does not declare, such as
  `java.lang.Object` or `boolean`, without defining that symbol. The check
  used a validation-only copy of the pack that also declares those two types.
  The flow rows were unchanged.

Each member carries `receiver: {}`, because the exporter and the CSMI
receiver roots need an instance receiver.

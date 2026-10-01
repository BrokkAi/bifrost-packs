# JNDI LDAP filter boundary prototype

This is an **unqualified diagnostic prototype** for
[`jvm-jndi-filter-escaping`](../../candidates.md#jvm-jndi-filter-escaping)
and [public issue #27](https://github.com/BrokkAi/bifrost-packs/issues/27).
It does not register a security rule or change scanner defaults. The exact
JDK overload and provider proof required for a production rule was not
established by the pinned engine run. The focused upstream blocker is
[Bifrost #3811](https://github.com/BrokkAi/bifrost-dev/issues/3811).

## Contract under test

Oracle's [Java SE 21 `DirContext` API](https://docs.oracle.com/en/java/javase/21/docs/api/java.naming/javax/naming/directory/DirContext.html)
distinguishes `search(Name|String, String filter, SearchControls)` from
`search(Name|String, String filterExpr, Object[] filterArgs, SearchControls)`
and `search(Name|String, Attributes[, String[]])`. The raw `filter` is LDAP
filter grammar. For string-valued substitutions, the `filterArgs` overload
escapes special filter characters. A fixed `(uid={0})` with untrusted input in
`filterArgs[0]` is the close data-only case. This does not prove that every
placeholder grammar position, non-string argument, or JNDI provider has the
same security properties. The structured `Attributes` overload is a distinct
contract, not a raw-filter call.

The fixture pins `com.sun.jndi.ldap.LdapCtxFactory` in its environment, but
that syntax is not analyzer proof that every receiver is backed by that
provider. An authentication claim additionally requires the selected search
result to affect the decision. The fixture's `rawLogin` and
`directInitialDirContext` return `hits.hasMore()` as a candidate decision;
`unrelatedResult` intentionally discards the result. These examples are
independently authored from the public API and perform no network operation
in validation.

## Cases and observations

| Case | Fixture method | Required classification | Pinned observation |
| --- | --- | --- | --- |
| Raw filter used by login | `rawLogin` | Candidate positive only with exact overload, provider, filter flow, and result use | JDK model active; overload/formal proof incomplete |
| Direct concrete JDK receiver | `directInitialDirContext` | Same contract without helper return typing | External dispatch still unproven |
| Alias through helper | `aliasLogin` / `rawSearch` | Candidate positive if interprocedural flow and receiver remain proven | Helper search external binding incomplete |
| Fixed expression plus `filterArgs` | `parameterizedLogin` | Near miss for untrusted value in a fixed assertion value slot | Four-argument overload binding incomplete |
| Structured attributes | `structuredLogin` | Near miss for raw filter grammar | Attributes overload binding incomplete |
| Input does not reach filter | `nonReaching` | Near miss | Input printed; filter fixed |
| Result unused | `unrelatedResult` | Near miss for authentication impact | Result discarded |
| Same-name local class | `lookalike` | Near miss for JNDI identity | Exact local source target and positional binding |

The `discovery-only.rqlp` is deliberately name-based. It finds all eight
`search` calls, including the local lookalike. Its note findings are candidates,
not security findings. The two JSON queries test `call_bindings` and
`dispatch_targets`; their raw output hashes and compact result rows are in
[`outcome.json`](outcome.json). The 0.12.0 run reports
`SignatureApplicability` unavailable, `dispatch_outcome=unproven`, and
`dispatch_coverage=truncated` for the external calls. The active generated
model is partial at these sites. Even where a partial positional map appears,
exact selector proof is absent. The local class resolves exactly. We stopped
before a taint/result-use policy because the first identity and binding gate
failed. No empty set here establishes a clean program.

## Replay

Use the exact Bifrost 0.12.0 macOS arm64 artifact pinned in `outcome.json`.
The ordinary shell `bifrost` on the authoring host was 0.11.4 and was not
used. From this repository root:

```sh
BIFROST_0_12_0=/path/to/pinned/bifrost
javac -d /tmp/jndi-filter-classes research/stdlib/prototypes/jndi-filter-escaping/fixtures/JndiFilterCases.java
"$BIFROST_0_12_0" --root . --query-file research/stdlib/prototypes/jndi-filter-escaping/queries/call-bindings.json
"$BIFROST_0_12_0" --root . --query-file research/stdlib/prototypes/jndi-filter-escaping/queries/dispatch-targets.json
"$BIFROST_0_12_0" --root . --no-builtin-policies --policy-file research/stdlib/prototypes/jndi-filter-escaping/discovery-only.rqlp --format json --evaluation-date 2026-10-01
```

`javac` only validates the fixture syntax. The query and policy commands do
static analysis; they do not connect to LDAP. Requalification needs a current
engine build, exact generated JDK model and provider provenance, complete
actual-to-formal binding, flow through wrappers, security-relevant result use,
and the positive and near-miss matrix above. Unknown, incomplete, unsupported,
cancelled, and budget-exhausted outcomes must remain distinct from clean.

# Missing Override annotation fixture

Original Brokk-authored Java, Apache-2.0. The CodeQL query identity is
`java/missing-override-annotation` at upstream commit
`ae741615f3e178ce61289a651790dc67fcc18e19`; no upstream fixture is copied.

This rule is held until the pack engine pin includes `BrokkAi/bifrost-dev#7465`
(#7179 step C). Older engines report a proven, empty method family for a method
whose only ancestor is an unread JDK type, so the rule would report those
methods as clean. Passing the upstream query's small regression fixture does
not establish coverage of JDK inheritance.

## Expected and observed answers

The CodeQL answer for `Example.java` includes every unannotated overriding or
implementing method at lines 9, 25, 26, 32, 33, 34, 35, 39, 43 and 44. The
observed answers are from a development build of `BrokkAi/bifrost-dev` at
`6749b966cd` (the #7465 head):

| Declaration | Line | CodeQL answer | Observed answer |
| --- | ---: | --- | --- |
| ExpressDelivery.status | 9 | Finding: superclass override | Finding |
| Square.area | 25 | Finding: interface default implementation | Finding |
| Square.perimeter | 26 | Finding: abstract interface implementation | Finding |
| JdkTask.run | 32 | Finding: Runnable implementation | Missed; run inconclusive |
| JdkTask.compareTo | 33 | Finding: Comparable implementation | Missed; run inconclusive |
| JdkTask.toString | 34 | Finding: Object override | Missed; run inconclusive |
| JdkTask.equals | 35 | Finding: Object override | Missed; run inconclusive |
| JdkTask.hashCode with @Override | 36 | No finding: annotated | No finding |
| AuditedDelivery.status | 39 | Finding: superclass override | Finding |
| RetriedDelivery.status() | 43 | Finding: superclass override | Finding |
| RetriedDelivery.status(int) | 44 | Finding: superclass override | Missed |

The run completes as `inconclusive` with reason `partial_discovery`. Its
findings are lines 9, 25, 26, 39 and 43.

- Lines 32 to 35: the engine reads no JDK hierarchy on the default Java route.
  Each member family reports its ancestor side as open, with reason
  `ancestor_external_unindexed` and the unread supertypes (`Runnable`,
  `Comparable`, and `java.lang.Object` for the Object methods). The family
  rows carry that coverage to the run, so the run is inconclusive rather than
  clean. These become findings when the engine provides JDK hierarchy edges
  (`BrokkAi/bifrost-dev#7027`).
- Line 39 is the case the outcome filter used to miss. `AuditedDelivery` also
  implements the unread `Runnable`, so the family of its `status()` is
  incomplete, but its edge to `Delivery.status()` is established.
- Line 44 is missed silently. The engine gives every overload of one name the
  same member id, so the later overloads get no member-family row at all
  (`BrokkAi/bifrost-dev#7505`).

Annotated overrides at lines 10, 29 and 40 are excluded. Line 29 spells the
annotation `@java.lang.Override`; Java's structured decorator adapter
normalizes both annotation forms to the final identifier `Override`. The
annotated hashCode is deliberately a near miss, not a missing expected alert.

Other near misses cover overloads, private methods, static method hiding,
lambdas, method references, enum synthetic methods and the static initializer.
Source method declarations exclude extracted library and generated methods.
The upstream `override` modifier exclusion concerns non-Java constructs; Java
has no such modifier and the policy explicitly selects Java declarations.

## Relation and capability contract

The policy selects forward family edges whose `relation` is in
`[overrides implements]`; it excludes `overridden_by` and `implemented_by`.
Edge rows expose `member_id` for the source method and `target_id` for its
ancestor. A member-family bind bridges `member_declaration_id` to the edge's
`member_id`. It has no outcome filter: an incomplete family keeps its
established edges, and its row carries the family's coverage to the run. All
three binds select only methods without an Override annotation, because an
annotated method cannot be a finding and its open family would otherwise make
the run inconclusive. One group per source method emits one finding even when
more than one selected edge exists. No member-family count is used.

The engine advertises no separate member-family pack capability. The row's
`parameter_type_spellings` capability is an analyzer precision label, not an
advertised pack requirement; the manifest keeps `structural-match`.

## Validation

The rule was validated against a development build of `BrokkAi/bifrost-dev` at
`6749b966cd` (the #7465 head), measure profile. The upstream CodeQL
query-test gate is EXACT: 1 true positive, zero false positives and zero
misses, complete analysis. That upstream fixture has no JDK cases, so the gate
does not remove the hold. The pack manifest's 0.2.0 minor version reflects the
new policy; publication and scanner enablement remain separate.

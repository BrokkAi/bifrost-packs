# Missing Override annotation fixture

Original Brokk-authored Java, Apache-2.0. The CodeQL query identity is
`java/missing-override-annotation` at upstream commit
`ae741615f3e178ce61289a651790dc67fcc18e19`; no upstream fixture is copied.

This rule is held for `BrokkAi/bifrost-dev#7179`. Passing the upstream query's
small regression fixture does not establish coverage of JDK inheritance.

## Expected and observed answers

The CodeQL answer for `Example.java` includes every unannotated overriding or
implementing method at lines 9, 25, 26, 32, 33, 34 and 35:

| Declaration | Line | CodeQL answer | Current engine answer |
| --- | ---: | --- | --- |
| ExpressDelivery.status | 9 | Finding: superclass override | Finding |
| Square.area | 25 | Finding: interface default implementation | Finding |
| Square.perimeter | 26 | Finding: abstract interface implementation | Finding |
| JdkTask.run | 32 | Finding: Runnable implementation | Missed |
| JdkTask.compareTo | 33 | Finding: Comparable implementation | Missed |
| JdkTask.toString | 34 | Finding: Object override | Missed |
| JdkTask.equals | 35 | Finding: Object override | Missed |
| JdkTask.hashCode with @Override | 36 | No finding: annotated | No finding |

The five JDK-backed declarations exercise the engine gap: the four unannotated
methods are missed today; after #7179 the run reports partial for them. The
annotated hashCode is deliberately a near miss, not a missing expected alert.
The pinned engines currently report proven empty families for these JDK
supertypes; the rule has no spelling-based workaround. Do not treat their
current complete outcome as evidence that these methods are clean.

Both pinned engines currently complete with exactly three findings at
`Example.java:9`, `Example.java:25` and `Example.java:26`, with no diagnostics.
The two interface implementations have implements edges, rather than overrides
edges. Annotated overrides at lines 10 and 29 are excluded; line 29 spells the
annotation `@java.lang.Override`. Java's structured decorator adapter normalizes
both annotation forms to the final identifier `Override`.

Other near misses cover overloads, private methods, static method hiding,
lambdas, method references, enum synthetic methods and the static initializer.
Source method declarations exclude extracted library and generated methods.
The upstream `override` modifier exclusion concerns non-Java constructs; Java
has no such modifier and the policy explicitly selects Java declarations.

## Relation and capability contract

The policy selects forward family edges whose `relation` is in
`[overrides implements]`; it excludes `overridden_by` and `implemented_by`.
Edge rows expose `member_id` for the source method and `target_id` for its
ancestor. They do not expose a family `outcome`. A member-family outcome bind
therefore retains `outcome eq proven` and bridges `member_declaration_id` to
the edge's `member_id`. One group per source method emits one finding even
when more than one selected edge exists. No member-family count is used.

The engine advertises no separate member-family pack capability. The row's
`parameter_type_spellings` capability is an analyzer precision label, not an
advertised pack requirement; the manifest keeps `structural-match`.

## Validation

Validated with Bifrost 0.14.2 from source commit `3c62bab569`, executable SHA-256
`f4abcc3ec6a3f2a2ba4754f3925a7f502bd679619cc543175f1433f2b678713b`, and CI's
Bifrost 0.13.1, executable SHA-256
`d1e7a286e10f9e60e9a6f66456ea2ce7c08ae55665d34c379f171d3ec5f00023`.
The release archive and executable were checksum-verified against CI's pin.
The dev build loads the public pack; the release fixture run loads an explicit
policy file because its public pack discovery predates that development route.

Both upstream CodeQL query-test gates remain EXACT: 1 true positive, zero false
positives and zero misses, complete analysis. That upstream fixture has no JDK
cases, so the gate does not remove the #7179 hold. The pack manifest's 0.2.0
minor version reflects the new policy; publication and scanner enablement
remain separate.

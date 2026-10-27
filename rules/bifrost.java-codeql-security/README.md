# Bifrost Java CodeQL security

This rule pack contains generated Java taint endpoints from CodeQL Models-as-Data. Catalog version 1 was generated from `github/codeql` commit `ae741615f3e178ce61289a651790dc67fcc18e19` with engine generator commit `2eda68dc23` and Temurin JDK `21+35` (Java 21; JDK module image SHA-256 `1465b683efd50adb60af815a8554129f8bd1b03807444cc491a5d2800d6f2091`). The pinned regeneration recipe is `scripts/upstream/public/generate-codeql-java-models.sh`.

The JDK run includes all 25 generated source, sink, and barrier catalogs. The servlet run includes only `codeql-servlet-sources-remote`, generated from `javax.servlet:javax.servlet-api:4.0.1` (SHA-256 `83a03dd877d3674576f0da7b90755c8524af099ccf0607fc61aa971535ad7c60`) and `jakarta.servlet:jakarta.servlet-api:6.0.0` (SHA-256 `c034eb1afb158987dbb53a5fea0cadf611c8dae8daadd59c44d9d5ab70129cef`). Servlet sink catalogs are intentionally excluded.

Public servlet source classification: benchmark OWASP Benchmark for Java; required coverage is the `javax.servlet` and `jakarta.servlet` request-source rows in CodeQL Java Models-as-Data. Without these sources, public Java taint rules have no source on servlet applications and cannot pass the benchmark. On 2026-10-27, the repository owner classified servlet request sources as public only; Spring, Micronaut, JAX-RS, and other framework content remains private.

The adjacent generation summaries preserve generator pins, aggregate counts, skip categories, conflicts, and per-catalog identities and hashes. The regeneration script writes complete generator reports only to its caller-supplied scratch directory. Per-catalog gate scope lists are in `fixtures/codeql_gate/java/`.

## Path-injection pilot validation

The opt-in `bifrost.java-codeql-security.path-injection` policy tracks the
`remote` category to both `path-injection` and `path-injection-read` categories,
with `require-model` call handling. Its CodeQL classification is
`java/path-injection` (CWE-22). Register this pack's catalogs with
`BIFROST_POLICY_PACK_ROOT` and stage only the JDK summary pack JSON as workspace
models; the adjacent generation report is provenance, not a semantic model.

The rerun uses CodeQL commit `ae741615f3e178ce61289a651790dc67fcc18e19`,
`security/CWE-022/semmle/tests`, Temurin JDK 21, and engine
`1e8ef7a49af644e5442d6ca6d0c6196aa3591bd0` (measure profile with test-support).
Java taint qualification uses the native trial route
(`BIFROST_TRIAL_NATIVE_JAVA=1`); the default route is recorded separately.
The JDK summary producer is 0.11.0, with receiverless constructor summaries.
The scope union is `fixtures/codeql_gate/java/java-public.json`: 59
catalog-backed obligations and 20 reviewed deferrals (19 framework sinks and
the QL-defined Spring source leading to `SanitizationTests2.java:16`). The
Spring attribution uses the gate's pinned class cache. Attributions are in
`fixtures/codeql_gate/java/attributions/path-injection.json`.

The policy now sanitizes resolved `String.replaceAll` calls whose decoded
literal arguments remove dot, slash and backslash together, in a character
class or alternation, replacing them with an empty string, underscore or
hyphen. A product-surface check retains direct flow, incomplete character
removal and unsafe replacement text, while suppressing the two complete
removals. No source-text fallback is used. Arbitrary replacement regexes,
compile-time constant expressions and multi-call replacement chains are not
covered by this literal recognizer.

CodeQL's branch-sensitive equality, trusted-prefix plus normalization or
traversal checks, blocklist combinations, regex-validation guards and
annotations, and `File.getName` plus traversal checks require conditional
barriers absent from the current policy-local sanitizer transfer contract.
Conditional constructor transfers and the full simple-type barrier family
also remain gaps. Normalization and `File.getName` alone are not sanitizers.

Validation on 2026-10-27 does not establish parity. Native qualification is
`SCOPED-FAIL`, full verdict `FP`: two matched expected alerts
(`TaintedPath.java:16,105`), five extras (`TaintedPath.java:30,51,67,88,122`), and
77 absent expected sites (57 scoped and 20 deferred). All 77 absences are
abstentions under inconclusive analysis, not certified false negatives. The
untraced run finished in 1,376.519 seconds; an initial 900-second traced attempt
timed out before emitting a report and is excluded from those counts.

The default route is `SCOPED-FAIL`, full `EXACT-INCOMPLETE`: zero matched
findings, zero observed extras, and 79 absent sites, all abstentions under
inconclusive analysis (59 scoped and 20 deferred). Both routes complete source
and configuration probes covering all four Java files; the earlier
semantic-model ingestion blocker is resolved. Empty output under incomplete
coverage does not establish zero false positives.

Native output independently confirms exact/exhaustive binding for
`FileInputStream(String)`, where the default route remains unresolved. A full
binding census finds incomplete sink bindings at all 57 catalog-backed
`Test.java` locations, including signature applicability failures for
cast-fed constructors and static calls. Native also leaves the staged servlet
`getParameter` source calls without usable model identity; a real servlet
4.0.1 minimal control does bind its source. The isolated upstream
`TaintedPath.java` fixture reports both expected sites (16 and 105) and five
extras (30, 51, 67, 88, 122). Those extras require the conditional sanitizers
above; they are not classified as true positives. Both expected findings are
complete, but the run remains inconclusive because external call boundaries
remain. The rule stays opt-in and has not reached SCOPED-EXACT or zero extras.

A minimal socket-to-reader chain produces a complete finding with no diagnostics
and `proven_by_summary` run completion. The current strict gate accepts only
`complete` run completion; summary-backed qualification is a separate contract
question from the binding and sanitizer gaps above.

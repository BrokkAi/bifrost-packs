# Bifrost Java CodeQL security

This rule pack contains generated Java taint endpoints from CodeQL Models-as-Data. Catalog version 1 was generated from `github/codeql` commit `ae741615f3e178ce61289a651790dc67fcc18e19` with the `bifrost-semantic-pack` generator from the public Bifrost v0.15.2 release (build `340cbbdcea3fc565f6ea8066084ed24962c369d3`) and Temurin JDK `21+35` (Java 21; JDK module image SHA-256 `1465b683efd50adb60af815a8554129f8bd1b03807444cc491a5d2800d6f2091`). The pinned regeneration recipe is `scripts/upstream/public/generate-codeql-java-models.sh`.

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

The policy also includes conditional sanitizers for basename traversal checks
and trusted-prefix checks on normalized or canonical paths. Conditional
constructor transfers and the full simple-type barrier family remain gaps.
Normalization and `File.getName` alone are not sanitizers.

Validation uses CodeQL commit `ae741615`, the `security/CWE-022` test, the
native route, and engine master `25985e1276`. The scoped result is
`SCOPED-FAIL`: two true positives (`TaintedPath.java:16,105`), four extras
(`TaintedPath.java:30,51,67,88`), and 77 misses. The full suite is `FP` with the
same true positives and extras. Before these sanitizers, there were five
extras; line 122 (`getName` followed by a `".."` check) is now suppressed with
no new misses. The remaining extras have these causes:

- Lines 30 and 67 need two guards on the same value, which is not supported yet.
- Lines 51 and 88 need `Path.startsWith(base + File.separator)`; the native route
does not yet bind the String concatenation argument because its type is not
proven.
- Line 51 also checks a `normalize().toAbsolutePath()` value. This rule does not
treat it as normalized because `toAbsolutePath` can put the working directory
in front of leading `..` parts.

The 77 misses remain abstentions under inconclusive analysis, not certified
false negatives. The rule stays opt-in and has not reached SCOPED-EXACT or zero
extras.

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

### Bifrost 0.15.0 rerun

On 2026-11-02 the same test, scope union and attributions ran on Bifrost
0.15.0 (`fc4a2da2b78c938e811c496b3c21e5b02f415048`) with Temurin JDK 21.0.8
and the gate harness that scores `proven_by_summary` completion. Both routes
remain `SCOPED-FAIL`, full `EXACT-INCOMPLETE`, with run completion
`inconclusive` (partial discovery), so no route passes:

| Route | Binary | TP | Extras | In-scope misses | Deferred |
| --- | --- | ---: | ---: | ---: | ---: |
| Native (`BIFROST_TRIAL_NATIVE_JAVA=1`) | 0.15.0 source, `measure` profile with `test-support` | 51 | 0 | 8 | 20 |
| Default | released v0.15.0 macOS arm64 | 21 | 0 | 38 | 20 |

Cast-fed calls in `Test.java` now bind on the native route (57 misses fell
to 6). The remaining native misses are `Test.java:37,39,69,83,137,138` and
`TaintedPath.java:16,105`. `TaintedPath.java` reports nothing on either
route: the `BufferedReader` constructor call stays unresolved, so the
socket source no longer reaches its sinks. The four earlier extras
(`TaintedPath.java:30,51,67,88`) are therefore absent because that file is
silent, not because the guards were proven; they still need the support
described above. The native run still reports one unresolved call
resolution, on the staged servlet `getParameter` call in `Test.source`. The native route is test-support only and is not in the
released binary.

### Bifrost 0.15.2 rerun

On 2026-11-12 the same test, scope union and attributions ran on the public
v0.15.2 release (macOS arm64, build
`340cbbdcea3fc565f6ea8066084ed24962c369d3`) with Temurin JDK 21.0.8, on the
default route. Both `bifrost.external.java@0.15.2` and
`bifrost.java-codeql-jdk-summaries@1.0.0` activate. The result is
`SCOPED-FAIL`, full `EXACT-INCOMPLETE`, run completion `inconclusive`
(partial discovery): 17 true positives, zero extras, 42 in-scope misses and
20 deferrals. Public v0.15.1 matched 21 sites.

The four lost sites are `Test.java:101, 102, 132, 141`
(`Files.copy`, `Files.newBufferedWriter(Path, Charset)` and
`Files.writeString(Path, CharSequence, Charset)`). On 0.15.2 their sink
selectors report `call_bindings model signature conversion is unavailable:
SignatureApplicability` when the overload family has another
arity-compatible sibling, or when the actuals are casts. This is an engine
regression, BrokkAi/bifrost-dev#12057. The sites are abstentions under the
inconclusive run, not proven negatives.

`TaintedPath.java` is still silent. Its source chain starts at
`sock.getInputStream()`, an instance call on a non-final JDK receiver whose
dispatch stays unproven and open, so the `BufferedReader` constructor's input
is unknown. The staged servlet `getParameter` call in `Test.source` stays
unresolved for the same reason. Both are BrokkAi/bifrost-dev#9998.

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

The pilot uses CodeQL commit `ae741615f3e178ce61289a651790dc67fcc18e19`, the
`security/CWE-022/semmle/tests` upstream directory, Temurin JDK 21, and engine
`39fda1b1c3a23eff4d416a3d33e2757cb17729c8` (measure profile). The committed scope
union is `fixtures/codeql_gate/java/java-public.json`: 59 catalog-backed sites,
one conservatively in-scope QL-defined Spring parameter source, and 19
framework-only sink sites. Reviewed exact endpoint attributions are in
`fixtures/codeql_gate/java/attributions/path-injection.json`. The Spring source
at `SanitizationTests2.java:16` remains an obligation on this gate version.

The pilot cannot model a constant `String.replaceAll` directory-character
replacement: the engine reports that Java structural matching does not support
decoded string-literal values. No source-text matching fallback is used, and
normalization or `File.getName` alone is not treated as sanitization. CodeQL's branch-sensitive equality, prefix, traversal,
blocklist and regex-validation guards, annotation checks, conditional
constructor transfers, full simple-type barriers, broader replacement regexes
and chained replacements remain gaps; this pilot is not a parity claim.

Validation on 2026-10-27 is blocked (`ERROR`), not SCOPED-EXACT. With only the
semantic-pack JSON staged, JDK declarations and summary activation succeed,
but the gate's configuration-coverage probe ingests that JSON as application
configuration and reports its 8 MiB ingestion cap. The raw taint run also
reports incomplete actual-to-formal bindings and unknown call resolution;
zero findings under that coverage is not evidence of zero false positives.
The Java stub compilation is best effort and reports duplicate servlet
classes. These instrument and engine gaps must be resolved before claiming
recall or precision parity. The rule remains opt-in.

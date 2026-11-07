# Bifrost Java CodeQL security catalogs

This catalogs-only rule pack contains generated Java taint endpoints from CodeQL Models-as-Data. Catalog version 1 was generated from `github/codeql` commit `ae741615f3e178ce61289a651790dc67fcc18e19` with engine generator commit `2eda68dc23` and Temurin JDK `21+35` (Java 21; JDK module image SHA-256 `1465b683efd50adb60af815a8554129f8bd1b03807444cc491a5d2800d6f2091`). The pinned regeneration recipe is `scripts/upstream/public/generate-codeql-java-models.sh`.

The JDK run includes all 25 generated source, sink, and barrier catalogs. The servlet run includes only `codeql-servlet-sources-remote`, generated from `javax.servlet:javax.servlet-api:4.0.1` (SHA-256 `83a03dd877d3674576f0da7b90755c8524af099ccf0607fc61aa971535ad7c60`) and `jakarta.servlet:jakarta.servlet-api:6.0.0` (SHA-256 `c034eb1afb158987dbb53a5fea0cadf611c8dae8daadd59c44d9d5ab70129cef`). Servlet sink catalogs are intentionally excluded.

Public servlet source classification: benchmark OWASP Benchmark for Java; required coverage is the `javax.servlet` and `jakarta.servlet` request-source rows in CodeQL Java Models-as-Data. Without these sources, public Java taint rules have no source on servlet applications and cannot pass the benchmark. On 2026-10-27, the repository owner classified servlet request sources as public only; Spring, Micronaut, JAX-RS, and other framework content remains private.

The adjacent generation summaries preserve generator pins, aggregate counts, skip categories, conflicts, and per-catalog identities and hashes. The regeneration script writes complete generator reports only to its caller-supplied scratch directory. Per-catalog gate scope lists are in `fixtures/codeql_gate/java/`.

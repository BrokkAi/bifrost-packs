# Missing Override annotation fixture

Original Brokk-authored Java, Apache-2.0. The CodeQL query identity is
`java/missing-override-annotation` at upstream commit
`ae741615f3e178ce61289a651790dc67fcc18e19`; no upstream fixture is copied.

Expect one finding at `Example.java:9`. Annotated overrides, overloads,
private methods, static method hiding, lambdas, method references, enum
synthetic methods and the static initializer are near misses. Source-only
method declaration selection excludes extracted library and generated methods.
The query's `override` modifier exclusion concerns non-Java source constructs;
Java has no such modifier and the policy explicitly selects Java declarations.
Functional expressions and generated methods are exercised through Java source
constructs that cause a compiler to synthesize methods, rather than invented
Java syntax.

Validated with Bifrost 0.14.2 from engine source commit `3c62bab569`, executable
SHA-256 `f4abcc3ec6a3f2a2ba4754f3925a7f502bd679619cc543175f1433f2b678713b`.
The fixture completed with exactly one finding at `Example.java:9`. The pinned
CodeQL query-test gate was EXACT: 1 true positive, 0 false positives, 0 misses,
complete analysis. The pack manifest advances to 0.2.0 because this adds a
policy; publication and scanner enablement remain separate.

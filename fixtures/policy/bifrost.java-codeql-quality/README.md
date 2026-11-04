# Public Java CodeQL quality fixtures

These fixtures cover the public JV02 declaration, naming, identifier, generic,
and constructor rules plus the JV23 Javadoc rules in
`rules/bifrost.java-codeql-quality`. Each case preserves the engine golden
source's positive and same-shaped near-miss examples.

Every policy retains CodeQL query provenance at commit
`ae741615f3e178ce61289a651790dc67fcc18e19` and requires the unreleased Java
fact and Javadoc support from `BrokkAi/bifrost-dev#4365`. The latest
qualification matrix used engine commit
`14ba3e856807e51d8ab829c00b5a272d81769511`; this content needs the next engine
release containing those Java lanes and structural-facts v44.

The `type-bound-extends-final` fixture includes `T extends String` as a JDK
resolution case. That finding is emitted only when a JDK is active; the
qualification run intentionally unsets `JAVA_HOME`, so it records the
source-declaration findings without treating the JDK case as proved.

The underscore-identifier fixture intentionally preserves the engine's legacy
recovery-shaped declarations. It reports the five known findings but remains
structured-incomplete; that partial result is not a clean result.

Spring, Spring Boot, and Android parity content is intentionally not included;
those framework/platform rules belong to the premium pack.

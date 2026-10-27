# CodeQL Java JDK summaries

`bifrost.java-codeql-jdk-summaries.json` is generated from the CodeQL Java Models-as-Data at commit `ae741615f3e178ce61289a651790dc67fcc18e19`, using Temurin JDK `21+35` and the `codeql-jdk-summaries` generator from Bifrost engine commit `2eda68dc23`. A compact generation summary is adjacent; the pinned recipe writes the full report to its caller-supplied scratch directory.

The pack activates for JDK toolchains `>=17.0.0`. Its declaration IDs are signature-based and do not depend on the JDK feature version; methods absent from a JDK do not match.

The engine must contain BrokkAi/bifrost-dev#7492 before this pack is activated. Older engines read unclassified receiver-to-return transfers as object identity.

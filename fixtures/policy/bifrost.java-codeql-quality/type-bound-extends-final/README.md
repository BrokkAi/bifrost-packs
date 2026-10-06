# Java type-bound-extends-final parity fixture

The source-declared `FinalType` bounds are public positive cases. The
`String` bound is a JDK-resolution case and only fires when a JDK is active;
the public-pack qualification run unsets `JAVA_HOME`, so that case is recorded
as an explicit environment-dependent boundary rather than a clean proof.

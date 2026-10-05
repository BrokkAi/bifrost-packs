# C# call-to-obsolete-method fixture

This fixture mirrors CodeQL `csharp/ql/src/API Abuse/CallToObsoleteMethod.ql`
from commit `ae741615f3e178ce61289a651790dc67fcc18e19`. The engine contract is
an exact source-declared call target carrying the resolved `System.ObsoleteAttribute`;
calls from an obsolete member or type are excluded. The fixture includes
explicit typed-parameter receivers (`service.Old()`) to keep the normal C# call
shape covered. External .NET metadata is outside this fixture and remains
structured-incomplete.

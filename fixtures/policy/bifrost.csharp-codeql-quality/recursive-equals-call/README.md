# C# recursive-equals-call fixture

This fixture mirrors CodeQL `csharp/ql/src/Likely Bugs/RecursiveEquals.ql`
from commit `ae741615f3e178ce61289a651790dc67fcc18e19`. The engine contract is
an exact source-declared call target equal to the enclosing `Equals(object)`
declaration, with the same uncast parameter. A typed overload selected by a
cast is a near miss, as are a different local and an explicit receiver other
than `this`; unresolved external framework overloads are incomplete.

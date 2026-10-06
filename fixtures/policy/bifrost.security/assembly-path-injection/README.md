# C# assembly path injection fixture

The positive public-BCL source reaches `Assembly.LoadFrom`; the sanitized
`Path.GetFileName` path, constant path, and unrelated same-named method are
same-shaped near misses. Provenance is CodeQL
`csharp/ql/src/Security Features/CWE-114/AssemblyPathInjection.ql`
at `ae741615f3e178ce61289a651790dc67fcc18e19`.

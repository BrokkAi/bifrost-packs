# C# XML injection fixture

The positive public-BCL source reaches `XmlWriter.WriteRaw`; the
`SecurityElement.Escape` path, constant text, and unrelated workspace method
are same-shaped near misses. Provenance is CodeQL
`csharp/ql/src/Security Features/CWE-091/XMLInjection.ql` at
`ae741615f3e178ce61289a651790dc67fcc18e19`.

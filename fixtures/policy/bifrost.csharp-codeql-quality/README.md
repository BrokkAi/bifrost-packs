# Public C# CodeQL quality fixtures

These fixtures exercise the nine policies in
`rules/bifrost.csharp-codeql-quality`. Each case contains a positive example
and same-shaped near misses, with the expected structural boundary documented
by the policy's CodeQL query path and pinned commit
`ae741615f3e178ce61289a651790dc67fcc18e19`.

The fixtures require the C# structural facts introduced by the unreleased
Bifrost engine work for epic #4379. The StringBuilder case also activates the
reviewed public BCL model in `semantic-packs/dotnet`; the catch-all case uses
its modeled exception hierarchy as well.

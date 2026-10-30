# Public C# CodeQL quality fixtures

These fixtures exercise the twenty-one policies in
`rules/bifrost.csharp-codeql-quality`. Each case contains a positive example
and same-shaped near misses, with the expected structural boundary documented
by the policy's CodeQL query path and pinned commit
`ae741615f3e178ce61289a651790dc67fcc18e19`.

The fixtures require the C# structural facts introduced by the unreleased
Bifrost engine work for epic #4379. The StringBuilder case also activates the
reviewed public BCL model in `semantic-packs/dotnet`; the catch-all case uses
its modeled exception hierarchy as well. The call-to-gc case resolves
`System.GC.Collect` from whichever declarations are available, the
path-combine case binds calls to its `System.IO.Path.Combine` overloads,
the catch-nullreferenceexception and rethrown-exception-variable cases use
it to resolve caught exception types, and the random-used-once case binds
`System.Random` constructors through it. The console-output case resolves
`System.Console.Out` and `System.Console.Error` through it. The
use-of-html-input-hidden and use-of-file-upload cases install the separate
.NET Framework `bifrost.dotnet.system-web-csharp` model instead. The
empty-catch-block, class-implements-icloneable and too-many-ref-parameters
cases read source syntax only and install no model.

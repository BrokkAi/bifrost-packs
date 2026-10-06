# C# catch-of-all-exceptions parity fixture

This fixture covers CodeQL's `Language Abuse/CatchOfGenericException.ql`.
Bare catches and unfiltered `System.Exception` catches that do not rethrow are
positive cases. A specific external exception, a filter, a bare rethrow, a
caught-variable rethrow, and a source-declared specific exception are near
misses. The fixture installs the reviewed BCL model with declarations for
`System.Exception`, `System.SystemException`, and
`System.InvalidOperationException`, including their `extends` chain, so the
external hierarchy is complete with the BCL model. Without that model, the
external hierarchy remains incomplete-without-metadata rather than becoming a
clean non-match.

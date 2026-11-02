# C# empty-catch-block parity fixture

Mirrors CodeQL `csharp/ql/src/Bad Practices/EmptyCatchBlock.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. The upstream test source keeps
its CodeQL path and an MIT attribution header. The two header lines shift
upstream line numbers by two.

The engine contract reports catch clauses whose body block contains only
whitespace, with or without a caught type or a `when` filter. CodeQL requires
the block to have no statements and no comment inside it. The policy reads
the body form from source: C# failure-handler state also calls a comment-only
body and a body holding only `;` empty, so its `empty` verdict would report
both. Because the caught type is not read, an unmodeled type such as
`IOException` neither needs a model nor makes the run incomplete, and the
fixture installs none.

Near misses in `Probe.cs`: a line comment, a block comment, a statement, a
bare `throw;`, an empty statement `;`, a nested empty block, and an empty
`finally`. The upstream `good()` method keeps a comment-only catch.

## Validation

Bifrost 0.14.2, build identity `073c23790739e33f33abc98338651689eaf8b7c0`,
evaluation date `2026-10-28`, run from this directory with
`BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and `--no-incremental`.
The policy hash is
`b23c07e552175a58f63a5aec3ec84041d29147fa5109f44b397634e7bd3dd471`.

The run is complete with five findings: `Probe.cs:9`, `Probe.cs:15`,
`Probe.cs:21`, `Probe.cs:27` and the upstream expected row
`EmptyCatchBlock.cs:12` (upstream line 10). There are no other findings.

## Known limits

- Only a comment inside the body suppresses a finding. A comment in the
  caught-type parentheses, as in `catch (Exception /* why */) { }`, is
  reported. I have not checked which element CodeQL attaches that comment to.
- A body that holds only a preprocessor block, such as `#if` ... `#endif`
  with an undefined symbol, is not reported. The text inside the block is
  not whitespace, even though the compiled body has no statements.

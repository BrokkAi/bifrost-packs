# C# todo-comment parity fixture

Mirrors CodeQL `csharp/ql/src/Bad Practices/Comments/TodoComments.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. The upstream test sources keep
their CodeQL paths and MIT attribution headers. The two header lines shift
upstream line numbers by two.

The engine contract selects C# comment nodes whose text contains the
case-sensitive markers `TODO` or `FIXME`, or `XXX` not directly preceded by
`=`. This is CodeQL's regular expression without its lookbehind. Line,
block and documentation comments are covered. A block comment is one comment
node, so a block comment with several marked lines is reported once.

Near misses: lowercase `todo` and `fixme`, `=XXX`, and a string literal that
contains `TODO`.

## Validation

Bifrost 0.14.1, build identity `9b3a997bf6218a718223960242053e10d9f8eacb`,
evaluation date `2026-10-27`, run from this directory with
`BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and `--no-incremental`.
The policy hash is
`7767e9b93cb027276c301531c5e5bb8f3dbad4310c909e357ced3342efb28e6d`.

The run is complete with six findings: `Probe.cs:3`, `:6` and `:10`, plus the
three upstream expected rows `TodoComments.cs:6`, `TodoComments.cs:7` and
`TodoCommentsBad.cs:9` (upstream lines 4, 5 and 7). There are no other
findings.

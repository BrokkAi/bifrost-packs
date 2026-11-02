# C# empty-lock-statement parity fixture

Mirrors CodeQL `csharp/ql/src/Likely Bugs/Statements/EmptyLockStatement.ql`
at commit `ae741615f3e178ce61289a651790dc67fcc18e19`. CodeQL has no query
test for this query, so `upstream/` holds the query's own example sources,
`EmptyLockStatement.cs` and `EmptyLockStatementFix.cs`. They keep their
CodeQL paths and MIT attribution headers. The two header lines shift
upstream line numbers by two.

The engine contract reports `lock` statements whose body is a block with no
statements. CodeQL requires `getBlock().(BlockStmt).getNumberOfStmts() = 0`.
Comments do not count as statements, so a comment-only body is reported, as
is a body that holds only `#region` directives. The policy reads the body
form from source, allowing whitespace, line and block comments and
preprocessor directive lines. Block body state does not separate these
shapes on 0.15.0: `(block :body-state empty)` under `lock :body` also
matched bodies with statements. No semantic model is read, so the run needs
no pack.

Near misses in `Probe.cs`: a statement, an empty statement `{ ; }`, a nested
block `{ { } }`, a body that is not a block (`lock (x) ;`), an empty block
that follows a lock, and an outer lock whose body is another lock.

## Validation

Bifrost 0.15.0, build identity `09a2503c5f7ced1630a9e3c445ead53dfc5925e8`,
binary SHA-256
`d9acbc7305ed0390457117c48531c82c5ff0778dab4290f5cc670e692280ae45`
(`bifrost-v0.15.0-aarch64-apple-darwin`), evaluation date `2026-11-02`, run
from this directory with `BIFROST_OPEN_PACKS_DISABLE=1`,
`--no-builtin-policies` and `--no-incremental`. The authored policy hash from
`bifrost policy-source-identity` is
`8782900e2d51fd82b353791511c440498d27a4271f7beb22fa3d820532a28ff9`; its
resolved identity is available with the same hash.

The run is complete with six findings: `Probe.cs:10`, `:15`, `:23`, `:28`
and `:37`, and `EmptyLockStatement.cs:32` (upstream line 30). There are no
other findings.

## CodeQL parity

CodeQL has no `.expected` file for this query. By the query's definition the
upstream example `lock (locker) { }` in `Y()` is its only row; the lock in
`X()` holds statements and `EmptyLockStatementFix.cs` has no lock.

| Upstream row by query semantics | Bifrost finding |
| --- | --- |
| `EmptyLockStatement.cs:30` | `upstream/Likely Bugs/Statements/EmptyLockStatement.cs:32` |

## Known limits

- A body whose only content is inactive preprocessor text, such as
  `#if NEVER` ... `#endif` around a statement, is not reported. CodeQL sees
  no statements there. The inactive text is not whitespace, a comment or a
  directive line.

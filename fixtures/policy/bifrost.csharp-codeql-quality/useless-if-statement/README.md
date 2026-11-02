# C# useless-if-statement parity fixture

Mirrors CodeQL `csharp/ql/src/Useless code/FutileConditional.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. A finding is reported on the
owning `if` statement when its consequence is empty and it has no
alternative or an empty one.

## Known limits

`if (b) { ; }` and `if (b) { { } }` are not reported, although CodeQL's
`emptyStmt` treats them as empty. Tracked in BrokkAi/bifrost-dev#8154.

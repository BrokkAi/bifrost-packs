# Python CodeQL quality upstream fixtures

These isolated fixture roots replay every matching upstream `.expected` case found for the retained rules at CodeQL commit `ae741615f3e178ce61289a651790dc67fcc18e19`. Positive and near-miss Python sources carry per-file source and MIT attribution comments. Each leaf directory has its own policy copy and run instructions.

- `import-and-import-from/01-PyCheckerTests`
- `import-own-module/01-PyCheckerTests`
- `overly-complex-delete/01-general`
- `polluting-import/01-general`
- `unsafe-cyclic-import/01-cyclic-module`
- `unsafe-cyclic-import/02-cyclic-module-annotations-fp`
- `unsafe-cyclic-import/03-false-negative`
- `unsafe-cyclic-import/04-true-negative`
- `useless-class/01-useless`

`syntax-error` and `undefined-placeholder-variable` have no matching upstream query-test directories or `.expected` cases in this pinned checkout.

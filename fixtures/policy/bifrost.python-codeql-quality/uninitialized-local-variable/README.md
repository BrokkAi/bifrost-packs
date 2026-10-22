# Python `uninitialized-local-variable` fixture

Mirrors CodeQL `python/ql/src/Variables/UninitializedLocal.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. The upstream test sources retain
full CodeQL paths and MIT attribution headers. `odasa6800.py` is retained as an
upstream near miss.

Validated with Bifrost 0.13.0, build identity
`dbc1e36370e79f6e1c8984eae7c6bf03b4bcbc66`, evaluation date `2026-10-15`.
The policy hash is
`d50e9e22f51cc165b4f32571da653aab883196073ead2988949c2287942b081c`.

## Upstream CodeQL test gate

Ran from `Variables/undefined` with the workspace-relative policy path,
`BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies`, and
`--no-incremental`. The run was inconclusive (`partial_discovery`,
`capability_incomplete`) with 10 complete findings. Expected: 14; actual
complete matches: 10; complete false positives: 0; complete misses: 0.

Four expected rows remain inconclusive: `UninitializedLocal.py:75` (`u9`),
`UninitializedLocal.py:88` (`u12`), `UninitializedLocal.py:151` (`u19`), and
`odasa3987.py:11` (`var`). They are retained as explicit coverage limits; no
complete result was emitted for these rows.

# Linux credential-drop contract probe

**Outcome: incomplete; no production rule.** This is an original, source-only
attempt to model a narrow Linux/glibc credential-drop sequence. It does not
copy Joern query or fixture text, register a pack model, add a rule, or change
scanner activation.

The candidate profile is: a procedure that intentionally drops a privileged
process's supplementary groups, primary group IDs, and user IDs. The desired
proof must identify the exact external declarations for `setgroups`,
`setgid`, and `setuid`; bind each call's actual arguments and result; prove
the required state-changing calls succeeded before later steps; and prove all
failure paths stop before continuing under an incompletely dropped identity.
A call-name match or source order is discovery only. This profile must not be
inferred from a function name or the mere presence of these calls.

This probe is bounded to the Linux/glibc API surface because `setgroups()` is
not specified by POSIX. The POSIX contract says `setuid()` does not change
supplementary groups. Linux documents that successful `setgroups(0, ...)`
drops all supplementary groups, while its result can fail; Linux `setuid` /
`setgid` behavior also depends on privilege and existing IDs. A future
production model must pin the libc/kernel contract and account for process
versus thread credential behavior.

The source fixtures are analyzer inputs only. None is compiled or executed;
in particular, the apparent credential-changing calls are never run.

## Reproduction

Run from the repository root with the managed Bifrost 0.12.0 binary. The
binary and catalog identities, tool result, and per-file hashes are recorded in
`results/outcome.json`. Query files are diagnostic CodeQuery documents:
shape/binding matches are not API identity, and the call-dispatch query is the
identity gate. Re-run them with `bifrost --root . --query-file <path>` after
copying the fixture directory into the same relative location under an isolated
probe root. Do not use the older Cargo `bifrost` found on `PATH`.

## Model attempt

`model-attempt.json` records the intended exact Linux/glibc identities and
effects as a research proposal, not an installable Bifrost model. Current
catalog discovery exposes no active C POSIX credential model. Until exact
declaration resolution and model activation can be demonstrated on these
fixtures, there is no safe selector or manifest entry to promote.

## Required next evidence

- Exact external dispatch for each API; application-defined same-name functions
  must remain distinct.
- Actual-to-formal argument and result binding for all three calls.
- Same-process credential state across calls, including helper boundaries.
- Guard and control evidence that successful calls dominate each later state
  transition and that every failure path exits before unsafe continuation.
- Original positives plus wrong-order, failure-continues, local-lookalike,
  helper/alias, unrelated-function, and already-safe controls.
- Pinned Linux/glibc contract, active model hashes, and complete scan coverage.

## Research sources

- POSIX Issue 8 specifies that successful `setuid()` changes user IDs according
  to caller privileges and does not change the supplementary group list:
  <https://pubs.opengroup.org/onlinepubs/9799919799/functions/setuid.html>.
- Linux man-pages document `setgroups()`'s success and failure results,
  privilege requirements, Linux-only status, and the glibc/NPTL thread-wide
  credential wrapper:
  <https://man7.org/linux/man-pages/man2/setgroups.2.html>.
- Linux process credentials include real, effective and saved IDs, filesystem
  IDs, supplementary groups, and capability interactions:
  <https://man7.org/linux/man-pages/man7/credentials.7.html>.

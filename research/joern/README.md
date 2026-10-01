# Issue #24 Joern query research

This directory records a pinned source-and-test inventory of the Joern QueryDB
catalog and one bounded Bifrost runtime probe. It contains research evidence,
not installable policy content. No Joern query, test, rule, manifest, or
semantic-pack model was copied or activated.

## Findings

- Joern `CredentialDrop.scala` uses method-name regular expressions and CFG
  dominance; its tests check containing function names. Neither proves exact
  external API identity, successful return values, or credential state.
- Joern `FileOpRace.scala` compares path-argument source text in calls within
  one method. It does not prove filesystem object identity, attacker control,
  or a check/use window.
- The managed Bifrost 0.12.0 probe keeps system-header credential calls at
  `unknown` / open dispatch coverage and leaves call bindings incomplete. It
  resolves same-named application-local controls to their own declarations.
  Guard rows and CFG exit boundaries are available, but credential-state
  events and the association between API success and later state are absent.
- Neither candidate qualifies for a production rule. Empty findings and
  incomplete coverage are not clean results.

## Files

- [`catalog-inventory.md`](catalog-inventory.md): pinned catalog/test inventory,
  candidate semantics, known false-positive/coverage limitations, Apache
  attribution, and selected source/test SHA-256 values.
- [`runtime-qualification.md`](runtime-qualification.md): exact managed engine
  provenance, policy catalog, fixture-query evidence, and owner routing.
- [`prototypes/posix-credential-drop/`](prototypes/posix-credential-drop/):
  original source-only fixtures, a non-installable model proposal, and saved
  CodeQuery documents for replay with the recorded Bifrost binary.
- [`prototypes/posix-credential-drop/results/outcome.json`](prototypes/posix-credential-drop/results/outcome.json): compact results and input digests.

## Source pin and attribution

Upstream is `joernio/joern` at
`af6f9573359ad26c418cbd31ab2ccc8dc32c1019`. The inventory records the Apache
2.0 repository license hash, per-query author metadata, and hashes for the
selected original source and tests. It paraphrases behavior and does not
reproduce upstream query or fixture text.

The prototype targets a narrow Linux/glibc credential-drop profile because
`setgroups()` is not a POSIX interface and `setuid()` alone does not change
supplementary groups. Exact external identity and versioned success/failure
semantics remain unmodeled. See the
[POSIX `setuid()` contract](https://pubs.opengroup.org/onlinepubs/9799919799/functions/setuid.html)
and Linux man-pages for [`setgroups(2)`](https://man7.org/linux/man-pages/man2/setgroups.2.html)
and [process credentials](https://man7.org/linux/man-pages/man7/credentials.7.html).

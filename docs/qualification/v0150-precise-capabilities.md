# Precise capabilities on Bifrost 0.15.0

The [indexed evidence](2026-11-02-v0150-precise-capabilities.json) records the
engine, the archive and executable digests, and each focused outcome measured
on 2026-11-02 (bifrost-dev#8117).

## Engine

| Field | Value |
| --- | --- |
| Version | 0.15.0 |
| Build identity | `09a2503c5f7ced1630a9e3c445ead53dfc5925e8` |
| Validated archive | `bifrost-v0.15.0-aarch64-apple-darwin.tar.gz`, SHA-256 `34295669d86aef268f0134c15f5127b90deac2e31e2f89bd3031ffe05cf097a5` (matches the release `.sha256`) |
| Validated executable | SHA-256 `d9acbc7305ed0390457117c48531c82c5ff0778dab4290f5cc670e692280ae45` |
| CI archive | `bifrost-v0.15.0-x86_64-unknown-linux-gnu.tar.gz`, SHA-256 `1c454241496ed61db2d54e7e631c3663201ac8d4fdcc6ebc72789fe33391ff04` |

`bifrost pack-engine-profile` advertises `configuration-absence`,
`configuration-code`, `field-write-value` and `resolved-value`. No earlier
release advertises them.

## Method

Each policy ran on each fixture workspace in three modes, all with
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off` and `--no-incremental`:

- `workspace`: the fixture's own `.bifrost/policies` copy, with
  `BIFROST_OPEN_PACKS_DISABLE=1` and `--no-builtin-policies`. This is how the
  fixtures were validated on 0.14.2.
- `pack-main`: the policy selected by ID from host-supplied packs
  (`BIFROST_OPEN_POLICY_PACK_ROOT`) at `origin/main` `4f5be38`, which declares
  only `exact-call-target`.
- `pack-new`: the same, from this change's manifests, which declare
  `resolved-value`.

The host-supplied path checks declared capabilities. A manifest copy that
declared the unadvertised name `resolved-value-nope` made
`call-to-obsolete-method` `not_run`, with "this engine does not provide the
`resolved-value-nope` capability". In `pack-new`, no run reported an
unavailable capability.

## Outcomes

All three modes gave the same completion and finding locations in every
case.

| Policy | Fixture | Completion | Findings |
| --- | --- | --- | --- |
| `call-to-obsolete-method` | `call-to-obsolete-method` | complete | 6: `Probe.cs:17`–`19`, `:24`–`26` |
| `console-output` | `console-output` | inconclusive (`partial_discovery`) | 0 |
| `console-output` | `console-output/error-stream` | complete | 2: `ErrorProbe.cs:17`, `:22` |
| `use-of-file-upload` | `use-of-file-upload` | complete | 5, as recorded on 0.14.2 |
| `insecure-protocol` | `python-insecure-protocol` | complete | 14: `main.py:5`–`12`, `upstream/InsecureProtocol.py:7`–`12` |
| `xmldocument-url-resolver` | `xmldocument-url-resolver` | complete | 3: `Probe.cs:12`, `:20`, `:29` |
| `xmldocument-url-resolver` | `xmldocument-url-resolver/incomplete` | inconclusive (`partial_discovery`) | 0, as recorded on 0.14.2 |

Every outcome matches the fixture's earlier record except one: the
`console-output` root fixture. On 0.14.2 that run was complete with ten
findings. On 0.15.0 it is inconclusive in all three modes, so the change comes
from the engine, not from the declarations. The engine reports
`call_relation_analysis_failed`: the incoming call target identity for the
source-declared near miss `Local.Console.WriteLine` is unproven. The
`call-sites-to :proof proven` arm that excludes calls to a source `Console`
type therefore cannot see a complete row set, and no verdict is published.
The engine leaves the run incomplete instead of reporting it clean. Workspaces
with no source-declared `Console` type with `Write` or `WriteLine` members are
not affected; the `error-stream` fixture is one.

All 254 public policy authoring identities match the 0.15.0 authoring CLI
(`scripts/verify-policy-identities.py`). The Python dynamic-evaluation smoke
(`scripts/smoke.py`), which the rules release workflow now runs with the
Linux 0.15.0 binary, completed with one positive and zero near-miss findings.

These checks establish focused behavior, identity and capability admission.
They do not qualify every policy or establish complete analysis in another
workspace.

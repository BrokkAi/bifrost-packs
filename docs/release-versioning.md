# Pack release versioning

Policy-rule and semantic-pack streams are versioned independently from the
Bifrost engine and from one another. A matching version number does not imply a
synchronized engine release, a paired stream release, or shared qualification.

## Choosing a version

Evaluate every included change before tagging and choose the highest bump
required by the set. Reset the patch number on a minor bump, and both lower
numbers on a major bump. Once a stream reaches `1.0.0`, reserve minor releases
for compatible additions:

| Change | Version rule | Hypothetical example |
| --- | --- | --- |
| Fix existing declared behavior, packaging, documentation, or metadata without expanding capabilities or narrowing accepted consumer requirements | Patch | Bug fix: `0.2.0` → `0.2.1` |
| Add policies, integrations, languages, or delivered semantic capabilities | Minor | New policy: `0.2.1` → `0.3.0` |
| Change the consumer contract incompatibly, including an ID or format change, removal, new required schema, or tighter required capability | Minor during `0.x` with an explicit migration; major after `1.0` | `0.3.0` → `0.4.0` during `0.x`; `1.2.0` → `2.0.0` after `1.0` |

Restoring behavior that was already stated can change findings and can be a
patch when consumer requirements stay the same. Deliberately broadening the stated scope is a minor change. A metadata
correction that exposes requirements that were previously missing is
incompatible when it narrows consumer selection, so it follows the consumer
contract rule.

Source-only models do not constitute new native capabilities. Release notes
must distinguish source additions from native additions, and source additions
must be versioned according to the scope actually advertised by the source
artifact. Expanding that advertised source catalog is a minor change. A native integration, language, or semantic capability is a minor
change when it is delivered in the release.

Version selection is independent of qualification and completeness. A version
does not imply that content is enabled, fully qualified, complete for every
security case, or full security coverage. Keep pending, limited, unsupported,
and incomplete outcomes explicit in the release evidence and consumer reports.

Documentation that is not published as a release asset does not by itself
require a release. Existing releases are immutable: do not retag or rewrite an
existing release to correct versioning or documentation. Apply the corrected
guidance to the next release that includes the relevant content.

The examples in this guide are hypothetical and are not claims that those tags
or artifacts have been published.

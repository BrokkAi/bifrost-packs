# Shared pack release contract v1

This directory is the canonical contract for public and private pack repositories.
Premium packaging fetches these files at a full public commit and verifies their
SHA-256 hashes; it does not maintain a second divergent schema.

Every GitHub pack release contains `pack-release.json`, a source or runtime
archive, and archive checksum sidecars. Archive names are
`<pack-id>-<independent-semver>-<role>.<format>` (for example
`bifrost.public-0.1.0-source.tar.gz`). Public source archives include content-lock.json;
premium policy archives retain policy-bundle.json. Native index.json schema 3 is
separate from release metadata schema 1. Older legacy releases without metadata
are invalid for this contract and need explicit historical pinning, not silent
fallback. Releases are not published by this task.

The manifest records the pack repository's immutable source commit, independent
release version, origin lock where relevant, artifact SHA-256/size/role, stable
policy/model identities, authored/resolved policy hashes, language/dependency
metadata, schema requirements, capability contract and qualification evidence.
Schema axes include policy document, RQL, built-in catalog, premium policy bundle,
native semantic read/write, authoring spec, native release index, and runtime.
Empty schema arrays mean that axis is not required by this artifact. A release
version or engine version does not substitute for these requirements.

Engine profiles must provide engine version, exact build identity, model-set
SHA-256, capability contract version 1, supported schema sets and capability set.
Bifrost does not yet advertise this profile; trusted integration tooling must
supply it. Do not invent capabilities from an engine version. Pending source
archives are reviewable only with `--allow-unqualified`; default scan selection
requires qualified policy/native artifacts. Compatibility is not proof of complete
coverage or clean findings.

`release.py select` reads local manifests, validates all candidates, filters engine
range, schemas, required capabilities, stable/prerelease channel and qualification,
then selects highest SemVer. Exact `--version` and/or `--commit` pins narrow it.
Equal-precedence conflicting identities fail. All selected artifact bytes are
verified before writing the scan receipt. The receipt retains engine profile,
release version, source commit, manifest hash and artifact hashes; resolve once
before a scan and retain that receipt throughout it.

```sh
python3 release-contract/release.py select --pack-id bifrost.public.rules \
  --engine-profile /path/to/engine-profile.json --channel stable \
  --cache-dir /path/to/cache --receipt /path/to/scan-pack-receipt.json \
  /path/to/cached/pack-release.json
```

`discover.py` explicitly enumerates **all** GitHub release pages rather than using
GitHub's latest pointer. It verifies repository, channel, annotated/lightweight tag
commit and manifest identity, selects before downloading artifacts, verifies
hashes and saves a cache. Private online discovery requires authenticated `gh`
access; tokens are never included in receipts. `--offline` uses cached candidates
and hash-addressed artifacts with no API/auth requirement. Refresh is explicit.

```sh
python3 release-contract/discover.py --repository BrokkAi/bifrost-packs \
  --visibility public --pack-id bifrost.public --engine-profile engine-profile.json \
  --cache-dir /path/to/cache --receipt scan-pack-receipt.json
```

Typed errors are `no-compatible-release`, `invalid-manifest`,
`unsupported-manifest-schema`, `incompatible-schema`,
`unavailable-credentials/network`, and `integrity-error`. None means an empty or
clean policy set. Cache/manifest integrity is not authentication against an attacker
with cache write access: use trusted repository and cache boundaries. Publication
must verify clean source, tag-to-commit binding, independent release version,
qualified evidence and artifact hashes. Future v0.13 consumer integration remains
in `docs/v013-transition.md`.

The baseline component workflow stages on manual dispatch and publishes only
on explicit `rules/vX.Y.Z` or baseline `packs/v0.1.1` tags. Repository-generated
native releases from `packs/v0.2.0` onward use the separate generation workflow.
See [release streams](../docs/release-streams.md) for the pinned Bifrost release
baselines and dependency resolution. Premium retains its qualified policy ZIP
workflow and stages the same metadata convention. Publish releases only after
the relevant CI and evidence checks pass.
Merge public PR first, then premium PR; the premium contract uses an immutable
public commit and hashes. Later contract changes require an explicit premium pin
update and renewed tests. Engine cutover and native release qualification remain
separate.

Native generation uses `native_generation.py` and `native_release.py` in either
public or private repositories. Generator version/build/checksums are independent
from release compatibility. The generation receipt and both original measurement
records are indexed as checksum-verified sidecar artifacts; they do not qualify
consumer behavior. `bifrost.premium.packs` uses `packs/vX.Y.Z` tags.

# Engine capabilities, pack admission and analysis completion

The engine supplies analysis operations. External packs supply product policies
and semantic content. The engine's supported capability contracts are established
independently of which policies a pack happens to contain; a pack declares the
contracts each policy requires. Copying a pack's requirement names into an engine
profile is not evidence of implemented analysis. The released
[engine profile API](https://github.com/BrokkAi/bifrost/blob/v0.13.0/src/lib.rs)
is an engine declaration, independent of this repository's policy inventory.

The [release producer](../release-contract/release.py) derives the release-level
required capability set as the sorted union of the included content requirements.
The same contract's selector checks schema support, capability-contract version
and missing names before admission. Artifact checks bind the selected source,
manifest and archive bytes. Admission says these declared contracts are available;
it does not say a particular policy finished analyzing a particular workspace.

As described in the [qualification contract](../release-contract/README.md), byte
integrity, behavior qualification and analysis completion remain separate. A
compatible artifact can have pending or limited behavior evidence. Actual results
must still report unsupported partitions, incomplete model/discovery coverage,
budget limits and cancellation. An empty incomplete result is not a clean result.
Engine product rules remain external; the historical `builtin_catalog` schema-axis
name describes a policy-pack manifest format, not a nonzero built-in rule catalog.

## Retired Go race analysis

Go race analysis was intentionally removed. Future rule artifacts therefore omit
`bifrost.correctness.go-data-race` and its source policy. The five requirements used
only by that policy disappear from the producer's union; shared requirements such
as `structural-match` remain. Removing requirements while keeping the rule would
make admission dishonest. Engine race support must not be restored to accommodate
the obsolete artifact.

This is an incompatible removal: the code-smells content version becomes `3.0.0`
and the prepared public rules stream becomes `0.2.0`, following the
[versioning policy](release-versioning.md). Consumers explicitly selecting the
retired policy must remove that selection. Published `rules/v0.1.4` and historical
audit evidence remain immutable. The new source and descriptor do not certify a
fully compatible engine/content tuple or authorize publication. Retained policies
still require their actual contracts and behavior qualification.

## Reproduction

Run the [artifact/admission regression](../tests/test_retired_policy.py):

```sh
python3 -B -m unittest discover -s tests -p 'test_retired_policy.py' -v
```

It builds the actual rules source archive twice, checks identical bytes, checks
the archived pack manifest and lock, verifies each retained content digest and
the archive digest, and checks the exact required-capability union. The test
demonstrates that a profile without the retired requirements can pass capability
admission while missing a retained requirement still fails. Its synthetic test
profile is not an engine advertisement; behavior stays pending. Real engine
capability evidence, dependency resolution, actual execution and publication are
separate obligations. This separation is the reproducible architectural claim;
the regression makes no claim of completed Go race or whole-pack analysis.

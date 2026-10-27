# Public rules 0.6.0 preparation for Bifrost 0.14.2

The [indexed evidence](2026-10-27-v0142-public-release.json) records the exact
published engine archive, executable, build identity, consumer profile, policy
bytes and focused outcomes measured on 2026-10-27. The public release tag commit
and the engine's reported build identity are distinct and are retained separately.

All 240 locked public policy authoring identities match the v0.14.2 authoring
CLI. This checks identity, not execution. The Python dynamic-evaluation smoke
completed with one positive finding and zero near-miss findings. The C#
rethrown-exception-variable and todo-comment fixtures completed with exactly
four and six findings at the previously reviewed locations; their realistic
near misses did not report. The repaired catch-of-all-exceptions fixture
completed with four findings, including the caught-variable rethrow at
`Source.cs:44`. Every focused run completed with no diagnostics.

Reproduce the identity and Python checks with the checksum-verified binary:

```sh
python3 -B scripts/verify-policy-identities.py --binary "$BIFROST_BIN" \
  --engine-version 0.14.2 \
  --build-identity 073c23790739e33f33abc98338651689eaf8b7c0 \
  --output "$EVIDENCE/identities"
python3 -B scripts/smoke.py --binary "$BIFROST_BIN" \
  --output "$EVIDENCE/python-smoke"
```

For each C# case named in the index, copy its complete fixture root, including
the `.bifrost` model inputs, to a fresh directory. Copy the corresponding
`rules/bifrost.csharp-codeql-quality/policies/<case>.rqlp` to
`candidate.rqlp` in that directory. Run:

```sh
BIFROST_OPEN_PACKS_DISABLE=1 BIFROST_SEMANTIC_PACK_DOWNLOAD=off \
  "$BIFROST_BIN" --root "$CASE_ROOT" --no-builtin-policies --no-incremental \
  --policy-file candidate.rqlp --format json --fail-on finding \
  --output "$EVIDENCE/case-report.json"
```

Require the indexed finding locations, complete status and empty report/run
diagnostics; exit 1 is expected because these mixed fixtures contain positives.
Normal cache access is needed to initialize the engine's semantic catalog.
The first sandboxed Python smoke failed on the catalog lock and is not counted
as behavior evidence.

The downloaded packs 0.6.1 release passes the publication guard and resolves
against the actual v0.14.2 profile without qualification overrides. Its native
artifact needs semantic-model schemas 8, 14 and 17, all supported by this engine.
Its recorded behavior status remains pending. No new native recipe or capability
is delivered by this preparation, so the exact dependency remains 0.6.1.

These checks establish focused behavior, identity and format compatibility.
They do not qualify every policy, prove native behavior, or establish complete
analysis in another workspace. Publication CI separately repeats packaging,
integrity and the focused Python smoke on the pinned Linux v0.14.2 binary.

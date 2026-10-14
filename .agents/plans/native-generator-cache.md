# Preserve verified native generator builds after later failures

This plan follows the supplied bifrost-dev `.agents/PLANS.md` standard. Keep its progress, discoveries, decisions and outcomes current. All implementation is in the isolated bifrost-packs worktree `/tmp/bifrost-packs-generator-cache`, branch `dave/native-generator-cache`, based on exact main `9883b3532878fdb4629a5ccc847f042558572aa1`.

## Purpose / Big Picture

The native pack workflow currently compiles a pinned producer executable, then generates and qualifies content. Its combined cache action saves only after the whole job succeeds. A later content failure therefore loses an otherwise successful producer build. Save the completed verified executable before generation, so a later legitimate content repair can reuse that build when every producer build input matches. Reuse never establishes content or release qualification.

## Progress

- [x] Inspect exact main, public repository instructions, receipt contracts and release owner boundaries. The owner approves normal automatic validation of this separate PR, with no manual dispatch, retry, #85 mutation or dependency import.
- [x] Implement an exact build identity and separate cache manifest with strict restore verification. The expected identity is recomputed before recording and verification to detect changed build inputs.
- [x] Replace the producer combined cache action with pinned restore and verified early save steps. Verification checks the copied executable against the unchanged six-field build receipt before saving.
- [x] Prove exact-hit acceptance, changed identity/corruption rejection and execution order, including a later generation failure. All 12 focused tests pass in 10.077 seconds; the harness executes actual checked-in shell bodies with local producer/tool fixtures and action storage.
- [ ] Run complete local Python/content/tool and workflow validation, checkpoint only owned files, and open the separate PR.
- [ ] Inspect current-head hosted checks and integration order; merge only after required checks pass or failures are verified inherited from exact base, and only if merging cannot publish a release.

## Context and Orientation

`.github/workflows/native-packs.yml` builds package `brokk-bifrost-semantic-packs`, binary `bifrost-semantic-pack`, with default features plus `release-tooling` in the release profile. `native-generation.json` pins the public source repository, full commit, archive digest, exact Rust toolchain and Cargo.lock digest. A digest is a SHA-256 fingerprint of exact bytes. `release-contract/native_generation.py` already checks the actual binary against an exact six-field source-build receipt and checks input immutability during generation. `release-contract/native_release.py` compares that six-field receipt exactly; preserve both existing contracts.

The producer cache at `RUNNER_TEMP/generator-cache` holds one executable and `build.json`. Add a separate `cache.json` recording complete build identity, payload digests and origin workflow/run provenance. Its identity must omit pack jobs, recipes, whole pack source commits and release versions, because changes to generated content should not invalidate an unchanged producer build. The producer build recipe itself, toolchain, platform and compiler flags must remain part of the identity.

No source, lockfile, toolchain, model, generation spec, pack version, qualification assertion, release trigger or permission change is in scope. Release owner #85 is independent. Existing main's producer may fail generation; retain and report any such failure rather than importing release fixes.

## Milestones

First implement `release-contract/native_generator_cache.py` using only Python's standard library and the existing native generation validation helpers. Produce a canonical expected identity and versioned exact cache key before restore. Record a manifest only after reading and validating the actual copied executable and six-field receipt. Verify every restored manifest against newly computed expected identity, its identity digest, actual binary/receipt bytes and well-formed origin provenance. Missing, malformed, symlinked, nonexecutable or mismatched payloads must fail closed; an absent or nonexact cache hit must perform the normal source build.

Next update the workflow to install the exact toolchain before computing identity, restore with the pinned `actions/cache/restore` action and no fallback keys, build on a nonexact hit, record and verify completed payloads, and immediately invoke pinned `actions/cache/save` after successful verification of a fresh build. Generate, compare, index, audit and publication checks remain downstream and unchanged. Verify copied bytes, rather than only the original target executable. Specify the build target explicitly and record the actual rustc/cargo identities, runner image/OS/architecture, default features, package/binary/profile, compiler/linker environment and recipe file digests. Use the same computed primary key for restore and save.

Finally add `tests/test_native_generator_cache.py`. Use hand-written fixture binaries and receipts, independent expected values, and execute the actual workflow's shell steps with a hand-written action harness. The harness models exact restore/save, real subprocess step ordering, failed builds and a later generation failure. It must show saved verified payloads survive that later failure and are accepted on the next exact-input attempt, while generation still executes. Tests also change each identity dimension and corrupt each evidence file. Keep tests fast; they must not compile Rust or dispatch workflows.

## Concrete Steps

Run commands from `/tmp/bifrost-packs-generator-cache`:

    python3 -B -m unittest discover -s tests -p 'test_native_generator_cache.py' -v
    python3 -B -m unittest discover -s tests -p 'test_*.py'
    python3 -B -m unittest discover -s tools/tests -p 'test_*.py'
    python3 -B scripts/content.py verify
    python3 -B scripts/verify-native.py
    git diff --check

Use actionlint if available; acquire a reviewed pinned binary in the temporary directory if needed, without changing repository dependencies. Also validate existing shell and JavaScript syntax checks used by content CI. Checkpoint implementation, tests and this living plan with a multiline commit explaining the rationale and observed results. Stage only owned files. Push the source branch normally and create one PR against main, attaching it to this task. Never manually dispatch or rerun validation.

## Validation and Acceptance

An exact input cache accepts the binary only after digest and receipt verification. Changing source/archive, Cargo.lock, actual Rust toolchain, platform/target, feature/profile/flag choices or build recipe rejects reuse. Data-only configuration changes retain the same producer key while still running current-source generation. A failed or partial compilation never reaches save. A successful verified compilation is saved before the generation step; a generation failure retains that saved entry. The next exact-input attempt restores it and still runs generation and all downstream checks. Missing origin or payload evidence and corrupted bytes fail closed.

The ordinary PR will automatically run full validation. A later main-only producer failure is not proof that a new workflow change is sound; establish the exact unchanged producer/config/input relationship and retain its logs. Pending or unrun required checks never permit merge. Publication requires a separate tag trigger, which this task must not create.

## Idempotence and Recovery

The versioned new cache namespace cannot reuse old incomplete entries. Cache writes are immutable and best-effort; eviction, scope restrictions or misses cause a normal compile without permission expansion. Never save unverified partial directories with an unconditional `always()` step. Preserve failures and worktree progress across connection interruptions. Do not alter the user's checkout, owner branches or other temporary directories.

## Surprises & Discoveries

The pinned combined cache action has `post-if: success()`, and its `save-always` input is deprecated. Moving to explicit restore/save is required. The release verifier expects exactly the existing six build receipt fields, so the cache-specific identity belongs in a separate manifest. An earlier native workflow spent 23m45s compiling before a later recipe failure; that is conditional potential savings, not a controlled before/after benchmark.

The first local pass rejected a missing cache manifest with the intended integrity error before file loading. A test had required an I/O exception only; its corrected expectation accepts either explicit fail-closed path. The original log remains `/tmp/native-generator-cache-focused-first.log`. No production gate changed in response. The corrected focused log is `/tmp/native-generator-cache-focused.log`.

## Decision Log

Use exact main as the independent base, confirmed with the release owner. Preserve every main producer/spec pin and default version. Use a separate manifest rather than changing published generation receipts. Hash build recipe bytes rather than the entire pack commit or generation plan so content-only repairs can reuse an unchanged producer. Origin provenance records the original build source and workflow run but does not require a later content commit to equal the origin commit.

## Outcomes & Retrospective

The initial implementation and 12 focused regressions pass. The harness saves a verified producer before a deliberately differing second generation pass fails; a later data-only source commit restores that exact build, preserves its origin and creates fresh two-pass generation evidence with qualification still pending. Failed builds, corrupt exact restores and incomplete evidence never reach save or generation. A partial hit rebuilds and discards stale extra files. Full validation and ordinary PR delivery remain open; no hosted cache hit, release qualification, time saving or merge is yet claimed.

## Interfaces and Dependencies

The new Python module provides identity construction, record and verify functions and CLI commands `identity`, `record` and `verify`. It imports the existing duplicate-key JSON loader, SHA-256 helper, config validator and six-field build attestation validator from `native_generation`. No package dependency, external signing service, permission or credential is added. Workflow tests use a local hand-written action harness and the actual checked-in shell command bodies.

Plan created for the separately authorized cache optimization; changes to its decisions and validation will be recorded here before delivery.

Initial implementation checkpoint: record focused behavior, the preserved first test expectation error and the remaining full-validation/hosted steps.

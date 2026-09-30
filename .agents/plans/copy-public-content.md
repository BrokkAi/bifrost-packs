# Copy public content and establish a shared release contract

## Purpose and plan

Copy reviewed public content from exact source aa291b97e55e48efc931ea89a16068404c3aad3e.
Preserve IDs, hashes, licensing and typed outcomes. Build deterministic source
packaging and a common public/private release contract. Engine defaults, sources,
and releases remain intact. Future v0.13 cutover is documented separately.

## Progress

- [x] Inspected/fetched source and destination, created isolated source snapshot.
- [x] Reviewed source license and baseline classification: public=2254, review=0.
- [x] Copied 293 reviewed public content/fixture/recipe files byte for byte.
- [ ] Verify reproducibility, schema compatibility, selection and typed failures.
- [ ] Prepare premium packaging-only integration with immutable common contract pin.
- [ ] Open ready PRs and inspect terminal exact-head CI.

## Surprises & Discoveries

Semantic content includes separate models and compiled embedded artifacts. Public
JDK fixtures carry GPL-with-Classpath terms. Private assurance suites are excluded.
The installed engine is older than the source catalog, so copying cannot certify
all engine behavior.

## Decision Log

User corrected the initial migration to COPY ONLY: no engine changes or retirement.
Shared contract implementation is canonical here and reused by immutable revision
in premium; no divergent schema copies. Integrity is distinct from qualification.

## Validation and recovery

Run Python tests, compare locked bytes with source, build archives twice, test
corruption/missing files and compatibility filtering. Preserve exact engine/model
identities for any behavior smoke. Roll back destination pins/changes only;
existing engine sources and historical artifacts are untouched.

## Outcomes & Retrospective

Implementation and exact-head CI evidence remain in progress.

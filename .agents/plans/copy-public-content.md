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
- [x] Verified reproducibility, schema compatibility, selection and typed failures (27 public tests).
- [x] Prepared premium packaging-only integration with immutable common contract pin (14 local tests; CI 30 behavior cases).
- [x] Opened public PR #1 and private PR #12; exact-head validation jobs terminal green, publication skipped.

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

293 canonical source files and four upstream license texts are committed with exact hashes. Public PR #1 and premium PR #12 deliver the copy and shared metadata contract. Full public catalog/model qualification, native regeneration/installation, CSMI interoperability and v0.13 consumer changes remain explicitly pending. Engine source checkout is unchanged; no merge/tag/publication occurred. Merge public first, then premium; premium pins common code commit fcd05ac88436485d2277f8ccb459a7baf87b6c45.

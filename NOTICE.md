# Notices and source provenance

Copyright (c) 2026 Brokk, Inc.

The copied paths in `content-lock.json` were reviewed public in the canonical
source at the exact recorded revision. That source's LICENSE.md designates
reviewed public material Apache-2.0. No premium content or private assurance
suites are included. The public source URL is a publication coordinate; the
canonical source revision may not be reachable in the public projection.

Each lock entry's optional `source_revision` records a later reviewed import
and overrides the initial revision for that entry. `source_path` preserves its
original location. These are import provenance, not engine release coordinates
or behavior qualification. Pack source commits bind subsequent authored edits.

Third-party material retains its original terms. Per-file license fields are
provenance labels, not a replacement license grant. Preserve all embedded
headers, `semantic-packs/**/notices/`, and corpus PROVENANCE.md files.

- CodeQL reduced corpus slices: MIT; see `licenses/CodeQL-MIT.txt` and the
  exact upstream revision in `semantic-packs/summary-corpora/pins.json`.
- CodeQL-derived Python quality and security fixture test sources are MIT,
  Copyright (c) GitHub, Inc.,
  from `github/codeql` at
  `ae741615f3e178ce61289a651790dc67fcc18e19`; see
  `licenses/CodeQL-MIT.txt`.
- Joern reduced flow corpus: Apache-2.0, same pinned metadata file.
- OpenJDK source fixtures: GPL-2.0-only WITH Classpath-exception-2.0; see
  `licenses/OpenJDK-*` and the fixture headers. These fixtures were excluded
  from the engine's published Cargo crate. They are included in this source
  repository/source archive only and must remain separate from runtime bundles.
- Rust declaration specifications retain MIT OR Apache-2.0 metadata.
- The authored .NET BCL declaration and summary model retains the .NET
  Foundation and Contributors MIT terms; see licenses/DotNet-Runtime-MIT.txt
  and semantic-packs/dotnet/bifrost.dotnet.bcl-csharp.json.
- Kotlin, Scala, Typeshed, PHPStorm and TypeScript source specifications retain
  their recorded license, pinned input hashes, and notices. Downloaded inputs
  are not vendored here. Node's complete upstream notice is preserved.

The source archive is a mixed-license source distribution, not an Apache-only
relicensing and not an installable native semantic-pack release bundle.

Rust CodeQL parity content records upstream CodeQL query paths at commit ae741615f3e178ce61289a651790dc67fcc18e19. Public Rust semantic models in this source snapshot cover standard-library declarations and flows, are authored by Bifrost, and declare Apache-2.0. No CodeQL query implementation or third-party library source is copied. PostgreSQL and rusqlite SQL models, their rule, and their fixtures are private premium content.

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
- CodeQL QL-class caches under `scripts/upstream/codeql_gate/ql_classes/` are
  MIT, Copyright (c) GitHub, Inc.: node locations and QL class names that the
  pinned CodeQL CLI computed over `github/codeql` query tests at
  `ae741615f3e178ce61289a651790dc67fcc18e19`; see `licenses/CodeQL-MIT.txt`.
- Joern reduced flow corpus: Apache-2.0, same pinned metadata file.
- The JavaScript identifier typo table
  `rules/bifrost.javascript-codeql-quality/data/identifier-typos.txt` is
  Apache-2.0. `tools/aoo_autocorrect_typos.py` builds it from two sources:
  - the en-US AutoCorrect list
    `main/extras/source/autotext/lang/en-US/acor_en-US.dat` of Apache
    OpenOffice at `17d397d7eb7e2935ed88d281ee3068516ad1cd47`. Apache
    OpenOffice, Copyright 2011- The Apache Software Foundation. This product
    includes software developed at The Apache Software Foundation
    (http://www.apache.org/). Portions copyright 2000-2011 Oracle and/or its
    affiliates.
  - `tools/identifier-typos-supplement.txt`, a supplement authored by Brokk,
    Apache-2.0.
- OpenJDK source fixtures: GPL-2.0-only WITH Classpath-exception-2.0; see
  `licenses/OpenJDK-*` and the fixture headers. These fixtures were excluded
  from the engine's published Cargo crate. They are included in this source
  repository/source archive only and must remain separate from runtime bundles.
- Rust declaration specifications retain MIT OR Apache-2.0 metadata.
- The authored .NET BCL declaration and summary model retains the .NET
  Foundation and Contributors MIT terms; see licenses/DotNet-Runtime-MIT.txt
  and semantic-packs/dotnet/bifrost.dotnet.bcl-csharp.json.
- The authored .NET Framework System.Web declaration model records public API
  names and signatures from the .NET Framework 4.8.1 API reference and is MIT;
  see semantic-packs/dotnet/bifrost.dotnet.system-web-csharp.json.
- The authored System.Security.Cryptography.Xml declaration and summary model
  records public SignedXml API names and signatures from the .NET API
  reference and the dotnet/runtime reference assembly, and is MIT; see
  semantic-packs/dotnet/bifrost.dotnet.security-cryptography-xml-csharp.json.
- The authored System.Xml declaration model records public XmlResolver,
  XmlUrlResolver, XmlDocument, XmlTextReader and XmlReaderSettings API names
  and signatures from the .NET API reference and the dotnet/runtime reference
  assembly, and is MIT; see
  semantic-packs/dotnet/bifrost.dotnet.system-xml-csharp.json.
- The authored System.Text.RegularExpressions declaration and summary model
  records public Regex API names and signatures from the .NET API reference
  and the dotnet/runtime reference assembly, and is MIT; see
  semantic-packs/dotnet/bifrost.dotnet.system-text-regularexpressions-csharp.json.
- The authored System.Data declaration and summary model records public
  DataSet and DataTable API names and signatures from the .NET API reference
  and the dotnet/runtime reference assembly, and is MIT; see
  semantic-packs/dotnet/bifrost.dotnet.system-data-csharp.json.
- The authored Go encoding/gob declaration and summary models record public
  API names and signatures from the Go 1.26.0 `encoding/gob` documentation and
  are BSD-3-Clause; see semantic-packs/go/notices/go-1.26.0-BSD-3-Clause.txt
  and semantic-packs/models/go-stdlib-encoding-gob*.json.
- The authored Go compress/gzip and io declaration and summary models record
  public API names and signatures from the Go 1.26.0 `compress/gzip` and `io`
  documentation and are BSD-3-Clause; see
  semantic-packs/go/notices/go-1.26.0-BSD-3-Clause.txt and
  semantic-packs/models/go-stdlib-compress-gzip*.json and
  semantic-packs/models/go-stdlib-io*.json.
- Kotlin, Scala, Typeshed, PHPStorm and TypeScript source specifications retain
  their recorded license, pinned input hashes, and notices. Downloaded inputs
  are not vendored here. Node's complete upstream notice is preserved.

The source archive is a mixed-license source distribution, not an Apache-only
relicensing and not an installable native semantic-pack release bundle.

Rust CodeQL parity content records upstream CodeQL query paths at commit ae741615f3e178ce61289a651790dc67fcc18e19. Public Rust semantic models in this source snapshot cover standard-library declarations and flows, are authored by Bifrost, and declare Apache-2.0. No CodeQL query implementation or third-party library source is copied. PostgreSQL and rusqlite SQL models, their rule, and their fixtures are private premium content.

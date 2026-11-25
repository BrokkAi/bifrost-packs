# C# DataSet.ReadXml external location fixture

Qualifies the version-independent part of the .NET CVE lead
BrokkAi/bifrost-packs#262 (CVE-2020-1147, GHSA-g5vf-38cp-4px9).
`DataSet.ReadXml` and `DataTable.ReadXml` instantiate the column types the XML
names. Microsoft's DataSet and DataTable security guidance says not to read XML
from untrusted input on any version. `ReadXml(String)` opens the file or URL it
is given, so external input that chooses that location chooses the document.
It is reported on every runtime. The CVE's affected-runtime part is not
checked: it needs shared-framework evidence (bifrost-dev#8779).

The sources are `Console.ReadLine` and `Environment.GetEnvironmentVariable`
from `bifrost.dotnet.bcl-csharp` 0.4.0. The sinks are the `fileName` operand of
`DataSet.ReadXml(String)`, `DataSet.ReadXml(String, XmlReadMode)` and
`DataTable.ReadXml(String)` in the reviewed `bifrost.dotnet.system-data-csharp`
0.1.0 model in `.bifrost/semantic-models`. The model also declares the
parameterless constructors and the `WriteXml(String)` members. Its instance
summaries claim `covers_overrides`, so calls through a typed receiver close.

## Cases

- **Positives** (`Probe.cs`): a `DataSet` parameter, a typed `DataSet` local
  with `XmlReadMode.ReadSchema`, and a `DataTable` parameter.
- **Near misses** (`Probe.cs`): a constant resource path, `WriteXml` to an
  external path, and a same-named `Local.DataSet.ReadXml`.
- **Incomplete** (`incomplete/`, one directory per case). `.bifrostignore`
  keeps this workspace out of the parent run.
  - `varlocal`: `var orders = new DataSet(); orders.ReadXml(...)`. The
    receiver of a `var` local is not established, so the sink selector is
    partial (bifrost-dev#8299).
  - `field`: a `DataSet` field receiver. The sink selector is partial
    (bifrost-dev#8299).
  - `reader`: `orders.ReadXml(new StringReader(Console.ReadLine()))`. Neither
    `StringReader` nor the `TextReader` overload is modeled, so call
    resolution is unknown.

## Validation

Bifrost 0.15.1 (`bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`, archive SHA-256
`4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`, which
matches the release digest; binary SHA-256
`78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`; build
identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`), evaluation date
`2026-11-05`. Each run used `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off`, `--no-builtin-policies`,
`--no-incremental` and a fresh `BIFROST_CACHE_DIR`. The authored policy hash
is `f9c163683ea0a156d2dcadf9c64838043202af047d7e15407410694f0d605a28`. Its
resolved identity is workspace-required.

- This directory: `proven_by_summary`, with 3 findings, all definite and
  complete: `Probe.cs:10`, `:16` and `:21`. The near misses produce no finding
  and no diagnostic.
- `incomplete/`: inconclusive (`partial_discovery`). Each case was also run
  alone with `--sources <case>`, and each is inconclusive on its own.
- Without the System.Data model: `not_run`.

## Known limits

- Only the `String` overloads are declared. The `Stream`, `TextReader` and
  `XmlReader` overloads differ from them only by parameter type, and on
  Bifrost 0.15.1 such a family doesn't bind (bifrost-dev#8296). Reading an
  uploaded stream is the more common shape, and it isn't reported. A tainted
  value that reaches one of those overloads through a modeled call would be
  attributed to the `String` member (bifrost-dev#9981). No modeled call here
  turns a `String` into a stream.
- Request input has no selectable C# source yet (bifrost-dev#8307).
- An application that restricts the allowed types (`AppContext` switches or
  `System.Data.DataSetDefaultAllowedTypes`) is still reported. Untrusted XML
  can still exhaust resources with the default types.

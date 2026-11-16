# Public C# and Rust CodeQL security fixtures

The C# fixtures exercise the five public BCL-backed injection policies. The Rust fixture covers the non-HTTPS URL literal rule, which classifies string values structurally and requires no third-party semantic models.

`signedxml-embedded-key-trust` is not a CodeQL port. It qualifies the
version-independent part of the .NET CVE lead BrokkAi/bifrost-packs#154 against
the reviewed `bifrost.dotnet.security-cryptography-xml-csharp` model.

`xmldocument-url-resolver` is not a CodeQL port either. It qualifies the
XmlDocument part of the stdlib candidate
`dotnet-xmlreader-external-dtd-resolution` against the reviewed
`bifrost.dotnet.system-xml-csharp` model.

`regex-pattern-injection` and `dataset-read-xml-external-location` are not
CodeQL ports. They qualify the version-independent parts of the .NET CVE leads
BrokkAi/bifrost-packs#263 (CVE-2019-0820) and #262 (CVE-2020-1147) against the
reviewed `bifrost.dotnet.system-text-regularexpressions-csharp` and
`bifrost.dotnet.system-data-csharp` models.

`go-gob-decode-network-input` is not a CodeQL port. It qualifies the
version-independent part of the Go CVE lead BrokkAi/bifrost-packs#192 against
the reviewed `bifrost.go.stdlib.net` and `bifrost.go.stdlib.encoding-gob`
models.

`go-network-read-all-unbounded` is not a CodeQL port either. It qualifies the
version-independent part of the Go CVE lead BrokkAi/bifrost-packs#252 against
the reviewed `bifrost.go.stdlib.net`, `bifrost.go.stdlib.compress-gzip` and
`bifrost.go.stdlib.io` models.

`java-objectinputstream-read-without-filter` is not a CodeQL port. It
qualifies the version-independent part of the Java CVE lead
BrokkAi/bifrost-packs#301 (CVE-2026-41586) against the generated JDK members
for `java.io.ObjectInputStream`. On Bifrost 0.15.1 every run is inconclusive
and every finding is `possible`; see its `README.md`.

The Rust SAST fixtures cover unsafe marker impl bounds and caller-supplied calls after invalid-state APIs. Their isolated positive and near-miss crates are fresh public sources. See each `expectations.json` and `scripts/rust-sast-gate.py`. All 37 cases pass on public Bifrost 0.15.0; see `docs/qualification/rust-sast.json`.

`cargo-ssh-git-host-key-unverified` is held out of the shipped rules; its
fixtures and qualification moved to `research/rust-cargo-ssh-git/`.

`python-process-input-to-urlopen` and `python-process-input-to-webbrowser-open`
are not CodeQL ports. They qualify the version-independent parts of the Python
CVE leads BrokkAi/bifrost-packs#270 and #272 against the reviewed
`bifrost.python-process-inputs`, `bifrost.python-stdlib-api-declarations` and
`bifrost.python-security-sink-summaries` models.

`python-process-input-to-venv-create` is not a CodeQL port either. It
qualifies the version-independent part of the Python CVE lead
BrokkAi/bifrost-packs#355 (CVE-2024-9287) against the same reviewed models,
which now declare and summarize `venv.create`.

`csharp-webassembly-debugging-affected-version` is not a CodeQL port. It
qualifies the affected-version part of the .NET CVE lead
BrokkAi/bifrost-packs#167 (CVE-2026-96230) against the new
`bifrost.dotnet.aspnetcore-webassembly-server-csharp` and
`bifrost.dotnet.aspnetcore-hosting-csharp` models. The version gate comes from
restored NuGet evidence.

`ruby-network-xml-to-rexml`, `ruby-network-input-to-net-imap` and
`ruby-network-input-to-gem-installer` qualify the Ruby CVE leads
BrokkAi/bifrost-packs#363 and #364 (rexml), #368 and #369 (net-imap), and the
version-independent install part of #286 (RubyGems) against the new
`bifrost.ruby.rexml`, `bifrost.ruby.net-imap` and
`bifrost.ruby.rubygems-installer` models and the reviewed
`bifrost.web-network-ruby` source. The rexml and net-imap gates come from
Gemfile.lock. All of these cases run on Bifrost 0.15.2.

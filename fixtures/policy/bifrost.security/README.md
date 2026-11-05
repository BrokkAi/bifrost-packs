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

`java-objectinputstream-read-without-filter` is not a CodeQL port. It
qualifies the version-independent part of the Java CVE lead
BrokkAi/bifrost-packs#301 (CVE-2026-41586) against the generated JDK members
for `java.io.ObjectInputStream`. On Bifrost 0.15.1 every run is inconclusive
and every finding is `possible`; see its `README.md`.

The Rust SAST fixtures cover unsafe marker impl bounds and caller-supplied calls after invalid-state APIs. Their isolated positive and near-miss crates are fresh public sources. See each `expectations.json` and `scripts/rust-sast-gate.py`. All 37 cases pass on public Bifrost 0.15.0; see `docs/qualification/rust-sast.json`.

`cargo-ssh-git-host-key-unverified` qualifies the Rust CVE lead
BrokkAi/bifrost-packs#60 (CVE-2022-46176). It needs Bifrost 0.15.1 Cargo and
`rust-toolchain` dependency evidence, and no semantic models. Its 10 cases
include five where the toolchain or configuration is unknown, and those must
stay inconclusive. See its `README.md` and
`docs/qualification/rust-cargo-ssh-git.json`.

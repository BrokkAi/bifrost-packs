# Public C# and Rust CodeQL security fixtures

The C# fixtures exercise the five public BCL-backed injection policies. The Rust fixture covers the non-HTTPS URL literal rule, which classifies string values structurally and requires no third-party semantic models.

`signedxml-embedded-key-trust` is not a CodeQL port. It qualifies the
version-independent part of the .NET CVE lead BrokkAi/bifrost-packs#154 against
the reviewed `bifrost.dotnet.security-cryptography-xml-csharp` model.

`xmldocument-url-resolver` is not a CodeQL port either. It qualifies the
XmlDocument part of the stdlib candidate
`dotnet-xmlreader-external-dtd-resolution` against the reviewed
`bifrost.dotnet.system-xml-csharp` model.

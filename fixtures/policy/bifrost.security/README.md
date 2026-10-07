# Public C# CodeQL security fixtures

These fixtures exercise the five C# injection policies added to
`bifrost.security`: XML, XPath, CodeDom code, LDAP filter, and assembly-path
injection. Each source contains a positive path and same-shaped controls for a
constant, an unrelated same-named API, or a reviewed sanitizer where the
policy supports one.

All five policies use the public BCL `System.Environment.GetEnvironmentVariable`
as their external-input source. They deliberately do not depend on ASP.NET,
`System.Web`, SQL client, configuration, cookie, hidden-input, or upload
models. The fixtures require the unreleased Bifrost engine work for epic #4379
and the public BCL model under `semantic-packs/dotnet`.

## Rust CodeQL security fixtures

The public Rust fixture covers the non-HTTPS URL literal rule. It requires no third-party semantic models.

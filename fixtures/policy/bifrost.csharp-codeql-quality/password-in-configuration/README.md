# C# password-in-configuration parity fixture

Mirrors CodeQL `csharp/ql/src/Configuration/PasswordInConfigurationFile.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. The `upstream` directory keeps
the original CodeQL test and its inline alert expectations. `cases/` contains
the positive, near-miss, and adversarial XML cases reviewed for this policy.

The policy reports: XML attributes with a case-insensitive password or pwd name and non-empty decoded value, or whose decoded value contains a password assignment not followed by an empty-value semicolon. Its selector excludes namespace declaration keys because CodeQL models namespace declarations as `XmlNamespace` nodes rather than `XmlAttribute` nodes.

## Adversarial expectations

| Case | password query result |
| --- | --- |
| `direct-case.config` | alert |
| `empty.config` | no alert |
| `terminal.config` | alert |
| `space-semicolon.config` | no alert |
| `substring.config` | alert |
| `namespace.config` | no alert |
| `entities.config` | alert |
| `both.config` | alert |
| `transform.Release.config` | alert |
| `cdata.config` | no alert |
| `namespace-declaration.config` | no alert |
| `namespace-value.config` | no alert |
| `namespace-empty-value.config` | no alert |


Namespace declaration and namespace-value cases must not be reported: CodeQL
models namespace declarations as `XmlNamespace`, while the policy input is
`XmlAttribute`. The policy excludes `xmlns` keys because the engine's XML
configuration facts can expose those declarations in the same attribute family.

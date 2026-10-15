# String conversion flow witnesses

Each positive stores a conversion result in a local before printing it. Each
project also contains an encrypted-name control. The trait-lookalike project
uses a different trait with same-named methods returning a fixed redacted
string; it must not acquire a standard Clone or ToString summary by spelling.

| Project | Positive witness | Upstream model |
| --- | --- | --- |
| `clone-string` | `password.clone()` and explicit `<String as std::clone::Clone>::clone(&password)` | `core.model.yml:87`, value flow |
| `to-string-str` | `password: &str` then `.to_string()` | `alloc.model.yml:53`, taint |
| `to-string-string` | `password: String` then `.to_string()` | `alloc.model.yml:53`, taint |
| `to-owned-str` | `password: &str` then `.to_owned()` | `alloc.model.yml:61`, taint |
| `from-str` | `String::from(password)` and explicit `<String as std::convert::From<&str>>::from(password)` | `core.model.yml:92`, taint |
| `into-string` | `let s: String = password.into()` | Only generic Into element-projection rows exist (`core.model.yml:89-90`); omitted from the model because the summary input/output ports cannot encode them. |
| `into-bytes` | `password.into_bytes()` then debug-print the bytes | No row in the pinned stdlib models; deliberately omitted. |
| `trait-lookalike` | custom `Redacted::clone` / `Redacted::to_string` | Negative control, no standard trait contract applies. |

Upstream sources are MIT, Copyright (c) GitHub, Inc., from
[`github/codeql` at dd4405c2](https://github.com/github/codeql/tree/dd4405c2c2a8cd5ee7d200e7230ab8dd52e13dc6/rust/ql/lib/codeql/rust/frameworks/stdlib).
See `licenses/CodeQL-MIT.txt` and the model provenance. The authored Rust
witnesses are reproduction inputs, not copied upstream test implementations.

The I/O model declares real standard trait members and typed `implements`
edges for the tested String/str owners. Its summaries use the same trait
owners as CodeQL, rather than inventing inherent methods or name-only aliases.
The schema has no summary-target field that distinguishes a concrete trait
implementation. An unresolved impl dispatch must stay incomplete; these
witnesses are not a claim of runtime qualification. Dependent `Self` and
associated `Owned` returns remain unspecified where the schema cannot encode
the concrete substitution accurately; ToString's String return is declared.

The current checkout gate table and exact binary provenance are recorded in
the parent [fixture README](../README.md). Run with both public model receipts
accepted, as described there. A zero finding under incomplete coverage does
not prove the positive or control safe.

## Measured results (2026-10-15)

The development executable and both receipts are identified in the
[parent qualification table](../README.md). Every positive stores its result
in a neutral local. No encrypted-name control added a finding.

| Witness | Found / expected | Finding certainty | Run completion |
| --- | --- | --- | --- |
| String Clone method and explicit trait call | 0 / 2 | no finding | inconclusive: partial discovery |
| str ToString | 0 / 1 | no finding | inconclusive: partial discovery |
| String ToString | 0 / 1 | no finding | inconclusive: partial discovery |
| str ToOwned | 1 / 1 | definite, complete | proven by summary |
| From<&str> for String, normal and explicit trait call | 0 / 2 | no finding | inconclusive: partial discovery |
| String into_bytes (no upstream model) | 0 / 1 | no finding | inconclusive: partial discovery |
| Into<String> (projection omitted) | 0 / 1 | no finding | inconclusive: partial discovery |
| Unrelated Redacted trait lookalikes | 0 / 0 | no finding | inconclusive: partial discovery |

Activated `call_shape`/`call_bindings` queries show all five modeled conversion
families with unproven dispatch, zero targets and incomplete actual/formal
mapping. `dispatch_targets` returns the genuine `_print` sinks but no
conversion target, including the explicit Clone/From trait-qualified forms.
The source format stores trait-owned summaries and typed implements edges;
this tested native engine does not establish their concrete impl binding.
No inherent aliases or spelling-based fallback are added.

The old I/O 0.3.1 model control also finds ToOwned's positive with the same
definite/complete finding and proven-by-summary completion. That result must
not be attributed to the newly authored, natively unbound trait summary.

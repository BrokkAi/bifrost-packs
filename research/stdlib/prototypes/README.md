# Standard-library query modeling attempts

This directory holds a bounded attempt to turn the [research catalog](../candidates.md)
into declaration-backed queries and protocol policies. These artifacts are
experimental contributions. They are explicitly selected diagnostic queries and
fixtures, not registered pack rules or scanner defaults. A discovery query may
complete without proving a security or correctness finding.

The first wave uses Bifrost 0.12.0 on macOS arm64, binary SHA-256
`168cf91d61f7504fbabf77974bfe53cdcc6f41abfbb727b7b152db18a3c4b545`,
and built-in catalog SHA-256
`9d1e4021b68c4dbd8d03c2ab9c10c05578868bd2b38ceae5e9aeca1849ba083e`.
The ordinary shell binary was older and was excluded from these attempts.
Each attempt records its own fixture/query hashes, model activation evidence,
commands, completion, diagnostics, and limitations. This pins the tested engine;
it does not qualify other consumer versions or models.

| Attempt | Contract | Current outcome | Evidence and replay |
| --- | --- | --- | --- |
| Rust initialization | Same MaybeUninit object is still uninitialized on a feasible path reaching assume_init | Incomplete: import and receiver declaration identity | [Rust attempt](rust-maybeuninit/README.md) |
| Python TLS | Effective verification state of the same context reaches an active client handshake | Incomplete: external API identity/binding and qualified-constant state coverage | [Python attempt](stdlib-tls/README.md) |
| Node authenticated decryption | Provisional plaintext reaches a reviewed effect before successful finalization of the same decipher | Incomplete: external API identity/binding; runtime witness passes | [Node attempt](node-aead/README.md) |
| Ruby Net::HTTP | Verification is disabled when the same client starts TLS and sends a request | Incomplete: external receiver identity and Ruby state axes; required runtime unavailable | [Ruby attempt](ruby-net-http/README.md) |

These probes test feasibility before a production query is authored. Discovery
queries deliberately include application lookalikes. The Node discovery RQLP is
an explicit diagnostic root with note severity; it is not an AEAD security rule.
No attempt in this wave has qualified a taint or typestate rule. Downstream
object-state and execution relations remain untested where API identity fails.

Read each attempt's outcome before interpreting results. Missing declarations,
unknown object identity, unresolved callbacks, absent model activation, or missing
success/exception relations stop qualification. A zero-row query under incomplete
coverage is not a safe result. Structural discovery, compiler acceptance,
runtime witnesses, and full analyzer qualification are different evidence tiers.

The fixtures and queries are newly authored for documented public API contracts.
Private implementation, assurance fixtures, research prose and tracker references
are excluded. Artifact storage, release packaging and scanner enablement remain
separate: these experiments do not change the locked policy or semantic-pack
content. Any promotion into `rules/` needs realistic positive/near-miss behavior,
exact identity and binding, complete supported scope, and a separate reviewed
manifest/pack change.

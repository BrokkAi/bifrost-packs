# Copy inventory and dependency boundaries

Canonical source: `aa291b97e55e48efc931ea89a16068404c3aad3e`, tree
`a6cd88202e4fac378c60055a23153d710d3c4a79`. Destination base:
`9a8df215d9b855c0bb589e02a4807759825855e3`. The exact per-path map is
`content-lock.json`; it includes 293 unchanged source files and four pinned
upstream license texts. Baseline-preserving source classification reported 2,254
public, 4,712 private, five generated and zero review paths.

| Layer | Copied | Consumer/tool dependency |
| --- | ---: | --- |
| Policy source/manifests/query/endpoints | 74 | Policy/RQL compiler and semantic locator resolution stay in Bifrost |
| Top-level semantic authored/spec/notices/reports | 79 | Native authoring/verification tool and pinned external inputs |
| Model inputs | 31 | Engine model compiler |
| Embedded native manifests/shards | 90 (42/48) | Engine artifact decoder/catalog/activation |
| Public fixtures | 9 | Engine-owned test harnesses; GPL fixture exclusions retained |
| Public generation/install/corpus recipes | 10 | Exact engine checkout, Cargo or supplied binary; shell/Python/Node/Docker |

Four policy pack identities are retained: `bifrost.code-smells`,
`bifrost.correctness`, `bifrost.security`, `bifrost.effects`. Original manifest
versions and policy authored/resolved hashes remain unchanged. Endpoint/support
files stay adjacent. Directory names do not establish language scope.

Engine CLI policy mode defaults to built-ins; explicit custom `.rqlp` files are
workspace-relative. MCP selection remains explicit. Neither interface discovers
this repository automatically. The built-in catalog is separate from independent
release metadata and native release index; runtime SQLite catalogs are separate
again. No copied file enables itself for scanning.

At the source revision, policy/RQL document schema is 1; built-in policy catalog
schema is 2; native semantic readers accept 2–6 (producer 6); authoring specs are 1;
native release index is 3; runtime model representation is 7. These axes are
independent of both engine and pack release version. Current engine capability
labels are descriptive metadata, so a future consumer needs a versioned,
provenance-bound capability profile. Release selection must not infer those
capabilities merely from engine SemVer.

Root engine tests and semantic authoring CLI tests remain private. Existing
public module tests remain with engine source. Standalone copy checks byte and
packaging identity and focused behavior only; full cross-language qualification
has not been transplanted or claimed. Premium paths, private research, legacy
seeds, customer models and private implementation are excluded.

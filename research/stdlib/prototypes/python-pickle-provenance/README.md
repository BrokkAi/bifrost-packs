# Python pickle provenance attempt

**Outcome: incomplete.** These fixtures and queries are experimental qualification evidence. They are not a production security rule, do not establish a vulnerable application, and do not prove arbitrary-code execution in any application. The public issue covering Python pickle and tarfile remains open; this attempt covers pickle only.

## Scope and public contract

The candidate is Python standard-library pickle reconstruction through load and loads. The contract warns that malicious pickle data can execute code during unpickling and says not to load data that is untrusted or may have been tampered with ([pickle documentation](https://docs.python.org/3.10/library/pickle.html)). It suggests signing when tamper detection is needed; the separate [HMAC API](https://docs.python.org/3.9/library/hmac.html) does not prove this application's key trust or producer relationship. The candidate therefore needs both an exact reconstruction entry point and evidence about the consumed data's origin and integrity. A call alone is not an exploit finding.

The fixtures are independently authored and were analyzed statically. No fixture was run, no pickle payload was deserialized, and no unsafe code was executed. The tarfile hypothesis was not evaluated.

## Fixture and query hashes

| Input | SHA-256 |
| --- | --- |
| fixtures/positive-env-module-alias.py | 247225ee10835ff2b1070ab42e99d04f654270b6b13975a93afb7d6105ad351d |
| fixtures/positive-env-from-import.py | 46f567361c69e6c0d8f4c5a7a16da55a08bde6d116a223b094271fe607dd2ad8 |
| fixtures/positive-stdin-stream.py | 49bdba28a9f8e3d9f255a7aa191787250f046f5dadc35ce51861624d1d304991 |
| fixtures/positive-persisted-file-stream.py | f7518b89a0ed887bff6947a1713681261d18da75d2ddea21e0f01d887287a6a1 |
| fixtures/positive-authentication-different-bytes.py | 0e59aaf2b3fce6fc4270d35bba8248d7f4acff6cccf8a5074fda94e2f13a697d |
| fixtures/near-authenticated-same-bytes.py | d09d55f513ea53af610b45d504827870bdf392f662f91631f77548062065d022 |
| fixtures/near-non-reaching-input.py | f7b8f95f2b820eb09c76975c606f5b4e32dbb99f576b47ba3a0536c928527d91 |
| fixtures/near-safe-json-parser.py | 88a2f9ed3dcb1bce783de5412990ceb712b61594708f21d676590dd50d6b5b6f |
| fixtures/near-local-module-lookalike.py | 7312a8a2c4e748fa87806f48d5d52ff5e77914e3a54342157e60adb0e7dcee2f |
| fixtures/near-shadowed-import-alias.py | 5be6de11d0e0af2e7c5d79709a47afd86fa8efcc4d61850623403cb20487cc65 |
| queries/python-pickle-imports.json | c87290e1522ee8df7c770a3ef77c78fe851cbbf96342d7d08c29238f525c69ac |
| queries/python-pickle-call-bindings.json | 3976422d11c06b40c83d5ea4e179f56569c4a7d0ad16efd1a785a0cfb3ff27d1 |
| rqlp/loader-discovery-only.rqlp | fe9c6a412bc5f0b0793e1cc5ef2402f6a70e1991e24cd39fe83eee8f4d14da6b |
| rqlp/provenance-attempt.rqlp | 093ac1fe8f60d21f2191b88c042d3a38da80d1249c9e1d2455bfbf6910cb77ed |

## Pinned environment

- Repository base: public bifrost-packs main at 8b8fa65cf66fb256eff9983885cb41af8713747d; task branch dave/lit-python-02.
- Consumer: Bifrost 0.12.0, macOS arm64 binary SHA-256 168cf91d61f7504fbabf77974bfe53cdcc6f41abfbb727b7b152db18a3c4b545; printed build identity 676def6c6615002002b1bb9d25211ad1476a5b5d.
- Built-in catalog SHA-256: 9d1e4021b68c4dbd8d03c2ab9c10c05578868bd2b38ceae5e9aeca1849ba083e.
- Runtime on host: CPython 3.9.6, macOS 27 arm64. Its stdlib pickle.py is under the Xcode Python framework and has SHA-256 92fc47af0a718eb7131e0045ce24bf0faa67336b84de2530d9476b963761238f.
- Selected model: bifrost.python-process-inputs@0.1.0, sourced from Python stdlib v3.13.5, with partial completeness; semantic SHA-256 4e3bcaa6982ebded509bd865c7a8795201cd71cf2283346350eb8e0a1fe73e69 and content SHA-256 bfc7c4348b1c2c5821ce15d5fd0b2898292ad7bdde70dee58360b0a36895d3d5. This model provides process-input facts, not a pickle loader declaration. The 3.13.5 model provenance does not match the 3.9.6 host runtime.
- The active workspace reported semantic_packs_ready=true and usage_index_ready=true. Pack selection completeness does not establish declaration or call-binding completeness.



## Fixtures

| Fixture | Intended role |
| --- | --- |
| positive-env-module-alias.py | Environment value encoded to bytes and passed through an imported module alias to loads |
| positive-env-from-import.py | Same source and transform through a direct imported-function alias |
| positive-stdin-stream.py | Stdin buffer passed to load |
| positive-persisted-file-stream.py | Binary file stream passed to load |
| positive-authentication-different-bytes.py | Authenticates one byte string, then unpickles a different environment-derived byte string |
| near-authenticated-same-bytes.py | Verifies a MAC for the same bytes before unpickling; the key and producer trust still need proof |
| near-non-reaching-input.py | Reads environment data but passes a constant pickle byte string |
| near-safe-json-parser.py | Parses environment text with json.loads |
| near-local-module-lookalike.py | Local object named pickle implements its own loads method |
| near-shadowed-import-alias.py | A local value shadows an imported loads alias |

These are designed positive and near-miss shapes, not verified analyzer outcomes. In particular, the same-bytes HMAC fixture is not declared trusted merely because its parameter is named trusted_key.

## Results on the pinned 0.12.0 binary

### Import and call-binding queries

The import query returned 19 Python import syntax nodes with no diagnostics. It proves syntactic imports only.

The call-binding query returned 10 loader-shaped call sites and 10 semantic_analysis_partial diagnostics. Every row had actual_count=1, bound_count=0, selector_exact=false, mapping=incomplete, coverage=unknown, and reason=callee_unresolved. Eight rows had resolved/exhaustive dispatch labels but still lacked complete binding coverage; two rows had unknown/open dispatch. A favorable dispatch label did not supply an exact stdlib declaration or formal-argument mapping.

Definition lookups gave concrete near-miss controls:

- codec.loads and the direct imported alias resolve across the pickle import boundary and are reported unresolvable_import_boundary.
- The same-named local pickle object resolves to its local field declaration.
- A shadowed decode_pickle use is reported as a local variable reference.
- json.loads is also outside the indexed workspace; this is an identity boundary, not evidence that JSON is unsafe.
- The persisted-file fixture's load call crosses the pickle boundary; a separate lookup of its with statement also encountered an unsupported reference shape and conflicting semantic-model declarations.

### Discovery-only RQLP

The note-severity discovery policy completed with four findings and no diagnostics. Its file SHA-256 is fe9c6a412bc5f0b0793e1cc5ef2402f6a70e1991e24cd39fe83eee8f4d14da6b. It only matches syntactic calls whose receiver is spelled pickle and whose method is load or loads. It found the local lookalike, same-bytes HMAC near miss, different-bytes positive, and constant-payload near miss. It missed the module-alias, direct-import-alias, stdin-stream, and persisted-file loader forms.

This result demonstrates why the discovery policy is not a production security rule: it has both false candidates and missed aliases. Its stable research identifier is research.python.pickle-loader-call-discovery.

### Provenance RQLP

The research taint attempt uses os.environ as a source and an exact pickle.loads declaration locator as a sink. Its file SHA-256 is 093ac1fe8f60d21f2191b88c042d3a38da80d1249c9e1d2455bfbf6910cb77ed. The command exited 2. Its single run was inconclusive with partial_discovery, produced zero findings, and included an evaluation_failure diagnostic because call_bindings did not establish complete actual-to-formal coverage for the sink selector. This is not a clean result. The policy also does not yet cover pickle.load stream sources, HMAC validation, trusted producers, or gadget reachability.

## Existing policy and release boundary

The existing policy identifier bifrost.correctness.unsafe-deserialization and its meaning were not changed. The source file rules/bifrost.code-smells/policies/unsafe-deserialization.rqlp has SHA-256 17afe6d2b443d24cbb0d6152dd4ea261b7340a18b909e6a84fd881aed4b3cdb6 in the pinned repository tree. The prototype uses research-only identifiers and is not registered in any manifest. No rule, semantic-pack, release, lock, or scanner-default content was changed.

## Reproduction

Run these from the bifrost-packs repository root with the pinned binary and this directory checked out. The JSON outputs under reports are the captured command results.

    BIFROST_BIN=/Users/dave/Library/Caches/bifrost-agent/binaries/0.12.0/darwin-arm64/bifrost
    ROOT=/Users/dave/.codex/worktrees/lit-python-02/bifrost-packs

    "$BIFROST_BIN" --root "$ROOT" --query-file research/stdlib/prototypes/python-pickle-provenance/queries/python-pickle-imports.json > research/stdlib/prototypes/python-pickle-provenance/reports/python-pickle-imports.json
    "$BIFROST_BIN" --root "$ROOT" --query-file research/stdlib/prototypes/python-pickle-provenance/queries/python-pickle-call-bindings.json > research/stdlib/prototypes/python-pickle-provenance/reports/python-pickle-call-bindings.json
    "$BIFROST_BIN" --root "$ROOT" --sources research/stdlib/prototypes/python-pickle-provenance/fixtures --no-builtin-policies --policy-file research/stdlib/prototypes/python-pickle-provenance/rqlp/loader-discovery-only.rqlp --evaluation-date 2026-10-01 --format json > research/stdlib/prototypes/python-pickle-provenance/reports/python-pickle-discovery-only.json
    "$BIFROST_BIN" --root "$ROOT" --sources research/stdlib/prototypes/python-pickle-provenance/fixtures --no-builtin-policies --policy-file research/stdlib/prototypes/python-pickle-provenance/rqlp/provenance-attempt.rqlp --evaluation-date 2026-10-01 --format json > research/stdlib/prototypes/python-pickle-provenance/reports/python-pickle-provenance-attempt.json

Observed exits: imports 0, call bindings 0 with incomplete rows, discovery 0 with four note findings, provenance 2 with inconclusive partial_discovery.

The captured raw JSON reports are checked in under reports/:

| Report | SHA-256 |
| --- | --- |
| python-pickle-imports.json | 78f38a99f120a1d83e8218ccc5680f4d624d52098117383cbcab6b26756d8478 |
| python-pickle-call-bindings.json | e5b70e8967d019f05d9f8960ad38edb6e9448385ff2f4fb0146bdf3a055fffb9 |
| python-pickle-discovery-only.json | 48a24db37f8c6eab46672ec2b68fdf42ef4a7cde01cf4a352bb8bb3394a952bc |
| python-pickle-provenance-attempt.json | fb4d18ee59ad10082ef3a91b6b870bfea184727c7f153da89dad2dd8f3c490a7 |

The result qualifies only the pinned Bifrost 0.12.0 consumer. No current-master macOS execution was made. The available current PR CI bundle was x86_64 Linux while the host is arm64 macOS, and no Docker daemon was running; no competing Cargo build was started.

## Stop gate

Do not promote either RQLP artifact into a production pack. Requalify against a current exact engine and runtime/model tuple, then prove imported stdlib identity, actual-to-formal argument binding, bytes/stream provenance, same-byte integrity and trusted-key/producer relationship. Keep local lookalikes, alias shadowing, JSON, fixed non-reaching payloads, invalid authentication, incomplete coverage, and unsupported runtime/import states as explicit controls. A generic dangerous-call diagnostic may eventually be justified by the public pickle contract, but the current evidence does not qualify a provenance-aware policy.

# Proposed qualification queue

This is a research-first queue for issue drafting. No qualification or implementation issues were opened by this pass. Recheck current ownership before creating a ticket; use one bounded qualification issue per investigation, then split implementation work only after evidence establishes a supported contract. Rows grouped below still need independent API/language acceptance and non-overlapping file ownership.

The 30 catalog records comprise 20 candidates, three proof-heavy deferrals, one match/configuration lead outside the requested analysis types, five existing-owner/catalog routes, and one exact-identity recheck. All remain unqualified.

Start with Node authenticated plaintext, JDK CipherInputStream, stdlib TLS state, and JNDI filter syntax. These have concrete documented distinctions and useful near misses; this priority is research judgment, not an analyzer-support claim.

| Order | Proposed investigation | Catalog leads |
| --- | --- | --- |
| 1 | Qualify Node authenticated plaintext acceptance | [node-crypto-authenticated-decipher-finalization](candidates.md#node-crypto-authenticated-decipher-finalization) |
| 2 | Qualify JDK authenticated decryption through CipherInputStream | [jvm-aead-cipherinputstream-integrity](candidates.md#jvm-aead-cipherinputstream-integrity) |
| 3 | Qualify stdlib TLS client verification state | [python-ssl-client-verification-typestate](candidates.md#python-ssl-client-verification-typestate), [go-crypto-tls-client-skip-verification](candidates.md#go-crypto-tls-client-skip-verification) |
| 4 | Qualify JNDI LDAP syntax versus filter arguments | [jvm-jndi-filter-escaping](candidates.md#jvm-jndi-filter-escaping) |
| 5 | Qualify implicit multiprocessing object deserialization | [python-multiprocessing-connection-recv-pickle](candidates.md#python-multiprocessing-connection-recv-pickle) |
| 6 | Qualify stdlib archive and filesystem root confinement | [jvm-zip-entry-containment](candidates.md#jvm-zip-entry-containment), [go-archive-extraction-root-confinement](candidates.md#go-archive-extraction-root-confinement), [rust-path-root-containment](candidates.md#rust-path-root-containment) |
| 7 | Qualify database/sql transaction completion | [go-database-sql-tx-terminal](candidates.md#go-database-sql-tx-terminal) |
| 8 | Qualify Rust child-process reaping | [rust-child-reaping](candidates.md#rust-child-reaping) |
| 9 | Qualify Python queue completion accounting | [python-queue-task-accounting](candidates.md#python-queue-task-accounting) |
| 10 | Qualify Python server shutdown thread relation | [python-socketserver-shutdown-thread-state](candidates.md#python-socketserver-shutdown-thread-state) |
| 11 | Qualify explicit runtime code-loading trust boundaries | [python-dynamic-import-untrusted-name](candidates.md#python-dynamic-import-untrusted-name), [rust-explicit-shell-command](candidates.md#rust-explicit-shell-command), [dotnet-processstartinfo-executable-and-shell-boundary](candidates.md#dotnet-processstartinfo-executable-and-shell-boundary) |
| 12 | Qualify Python logging configuration listener verification | [python-logging-config-listener-verification](candidates.md#python-logging-config-listener-verification) |
| 13 | Qualify .NET XML resolver and DTD configuration | [dotnet-xmlreader-external-dtd-resolution](candidates.md#dotnet-xmlreader-external-dtd-resolution) |
| 14 | Qualify explicit Python XInclude resource reads | [python-xinclude-untrusted-href](candidates.md#python-xinclude-untrusted-href) |
| 15 | Qualify PHP paired process and pipe ownership | [php-proc-open-paired-ownership](candidates.md#php-proc-open-paired-ownership) |

## 1. Qualify Node authenticated plaintext acceptance

Start with AES-GCM and one explicitly reviewed publication or storage boundary. Successful final on the same object must dominate the accepting effect; private staging is allowed.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## 2. Qualify JDK authenticated decryption through CipherInputStream

Pin one JDK and crypto provider. Separate the documented risky API/configuration advisory from any stronger witness that unauthenticated bytes actually reach a sensitive consumer.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## 3. Qualify stdlib TLS client verification state

Use independent Python and Go subcontracts. Require active client use with effective verification disabled; unused configuration and proven equivalent verification are near misses. Third-party TLS clients remain outside this group.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## 4. Qualify JNDI LDAP syntax versus filter arguments

Start with the built-in JDK LDAP provider, one raw-filter overload and its bound filterArgs counterpart. No JDBC, third-party directory client or application-name inference.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## 5. Qualify implicit multiprocessing object deserialization

Prove connection origin and peer trust. Contrast recv with recv_bytes and a deployment-owned trusted Pipe; authentication alone does not establish safe serialized objects.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## 6. Qualify stdlib archive and filesystem root confinement

Start with one runtime and an executed ../ or absolute-path write witness. Keep Go os.Root, JDK Path and Rust PathBuf semantics separate, with platform/symlink/race exclusions. Third-party archive packages keep their existing ownership.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## 7. Qualify database/sql transaction completion

Start with successful DB.Begin and defer Rollback, including an early error exit and ownership transfer. Add BeginTx context cancellation only with its exact implicit rollback relation. Reuse lifecycle infrastructure; exclude driver-specific query syntax.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## 8. Qualify Rust child-process reaping

Start with a locally owned Unix Child in a long-running process. Wait success and try_wait Some discharge the obligation; kill and try_wait None do not. Explicit process-lifetime ownership remains distinct.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## 9. Qualify Python queue completion accounting

Start with one bounded worker profile and a corresponding join. Queue-level unfinished counts, delegated acknowledgement, retry and shutdown immediate semantics must be represented; no textual call counting.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## 10. Qualify Python server shutdown thread relation

Start with service_actions calling shutdown on its own serving thread. The near miss is a different controlling thread while serve_forever is active. Stop if cross-thread active-object identity cannot be proven.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## 11. Qualify explicit runtime code-loading trust boundaries

These are independent API subcontracts, not one generic code-execution rule. Select one runtime first. Prove unauthorized module/program selection or explicit shell command-language flow and actual execution. ctypes stays deferred.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## 12. Qualify Python logging configuration listener verification

Use an opt-in untrusted-local-user threat profile. Prove the listener starts and the same bytes pass through a meaningful verify gate; callback presence and localhost binding do not establish trust.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## 13. Qualify .NET XML resolver and DTD configuration

Start with XmlReaderSettings and an explicit external-capable resolver. Preserve secure defaults and parser type/framework version; do not duplicate Java StAX work or confuse expansion DoS with external resource access.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## 14. Qualify explicit Python XInclude resource reads

Require explicit ElementInclude expansion, default-loader selection and the same untrusted href reaching a local read. Ordinary XML parsing is outside this contract.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## 15. Qualify PHP paired process and pipe ownership

Start with a harmless child waiting for EOF. Correlate output pipes with their process resource and show the actual blocking dependency; inherited descriptors are not newly owned pipes.

Acceptance for the qualification issue:

- Pin exact runtime/provider, public API source revision, engine and model identities.
- Prove the catalog's dangerous operand/object/result relationship and applicable execution/exit semantics.
- Execute the stated positive, closest near misses, same-name lookalike, non-reaching data, aliases/wrappers and incomplete-coverage case.
- Retain immutable evidence and a qualified/rejected/incomplete/unsupported outcome.
- Route a minimal capability-gap reproduction to the current engine owner and stop; create an implementation issue only for a passing slice.

## Existing ownership and deferrals

- Node child-process shell and ordinary Go/C/C++ resource-close cases belong to existing security/lifecycle qualification. Add precise API models and fixtures under those owners; do not create a competing leak engine.
- PHP unserialize and Ruby Marshal were already cataloged. Review public runtime ownership under their existing research routes. No premium content or issues were migrated.
- C formatted-output taint needs a current exact-build check of global external declaration identity before any production endpoint.
- GCM nonce reuse needs proven same-key/nonce byte equality and a bounded encryption lifetime. Regex risk needs an engine-specific complexity witness, tainted input and effective work bounds. ctypes needs platform-aware loader provenance. These are deferred, not rejected or supported.
- Legacy PBKDF2 overload defaults are a precise configuration/match lead, outside this taint/typestate wave. Do not invent a universal password-work-factor threshold.

The private ownership audit contains the exact existing tracker references and remains outside this public repository. Re-fetch inventories at execution time; routing does not claim those issues are complete.

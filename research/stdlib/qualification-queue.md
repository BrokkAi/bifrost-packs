# Proposed qualification queue

This is a research-first queue for issue drafting. No qualification or implementation issues were opened by this pass. Recheck current ownership before creating a ticket; use one bounded qualification issue per investigation, then split implementation work only after evidence establishes a supported contract. Rows grouped below still need independent API/language acceptance and non-overlapping file ownership.

The 41 catalog records comprise 24 candidates, six proof-heavy deferrals, one match/configuration lead outside the requested analysis types, nine existing-owner/catalog routes, and one exact-identity recheck. All remain unqualified.

Start with Node authenticated plaintext, JDK CipherInputStream, stdlib TLS state, and JNDI filter syntax. These have concrete documented distinctions and useful near misses; this priority is research judgment, not an analyzer-support claim.

| Order | Proposed investigation | Catalog leads |
| --- | --- | --- |
| 1 | Qualify Node authenticated plaintext acceptance | [node-crypto-authenticated-decipher-finalization](candidates.md#node-crypto-authenticated-decipher-finalization) |
| 2 | Qualify JDK authenticated decryption through CipherInputStream | [jvm-aead-cipherinputstream-integrity](candidates.md#jvm-aead-cipherinputstream-integrity) |
| 3 | Qualify stdlib TLS client verification state | [python-ssl-client-verification-typestate](candidates.md#python-ssl-client-verification-typestate), [go-crypto-tls-client-skip-verification](candidates.md#go-crypto-tls-client-skip-verification), [ruby-net-http-active-peer-verification-disabled](candidates.md#ruby-net-http-active-peer-verification-disabled) |
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
| 16 | Qualify Rust MaybeUninit initialization state | [rust-maybeuninit-initialization-state](candidates.md#rust-maybeuninit-initialization-state) |
| 17 | Qualify Rust Condvar predicate rechecks | [rust-condvar-predicate-recheck](candidates.md#rust-condvar-predicate-recheck) |
| 18 | Qualify Rust buffered-output completion | [rust-bufwriter-drop-hidden-flush-error](candidates.md#rust-bufwriter-drop-hidden-flush-error) |

Ruby Net::HTTP active verification adds an independent Ruby/default-gem
subcontract to group 3. It does not import
Python or Go support. The new Rust groups are ordered for bounded follow-up;
their list position is not a priority ranking over the earlier P1 leads.

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

Use independent Python, Go and Ruby Net::HTTP subcontracts. Require active client use with effective verification disabled; unused configuration and proven equivalent verification are near misses. Pin the Ruby runtime, shipped net-http/OpenSSL versions and active session separately. Third-party TLS clients remain outside this group.

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

## 16. Qualify Rust MaybeUninit initialization state

Start with one local `MaybeUninit<u32>` created by `uninit` and consumed by
`assume_init`, with a corrected same-object `write` case. Require an actual
uninitialized-state witness, not merely failure to discover an initializer.
Keep raw-pointer writes, partial aggregates, FFI out-pointers and type-specific
zeroed validity incomplete until modeled. Do not run undefined-behavior positives
as ordinary executable tests; use a pinned appropriate checking tool if runtime
evidence is needed.

Apply the qualification contract above: pin identities, execute supported
positive/near-miss analysis fixtures, preserve typed outcomes, and route a minimal
capability-gap reproduction to its current owner before proposing implementation.

## 17. Qualify Rust Condvar predicate rechecks

Start with a local mutex-protected queue whose emptiness predicate controls
`Condvar::wait`, followed by consuming an item as though it exists. A spurious
wakeup can leave the queue empty. The near misses are a same-predicate while loop,
`wait_while`, and continuations that safely handle an empty queue. Require exact
guard/predicate identity and post-wake control flow; recheck the current Rust
loop-guard capability before claiming this slice is feasible.

Apply the qualification contract above, including supported analyzer fixtures
and an explicit incomplete/unsupported outcome at any guard or identity gap.

## 18. Qualify Rust buffered-output completion

Use an application-declared output-completion boundary and a writer with proven
pending bytes. Show how a failing underlying write can be hidden by Drop while
the caller returns success. Compare checked `flush`, checked `into_inner` and
intentional `into_parts` recovery. Best-effort output, ownership transfer and an
empty buffer are near misses. This is not a generic missing-close rule or a
durability claim; downstream writer completion and filesystem sync are separate.

Apply the qualification contract above. Explicitly discarded Results reuse the
existing ignored-result owner; this group concerns the implicit Drop error at a
declared completion boundary.

## Existing ownership and deferrals

- Node child-process shell and ordinary Go/C/C++ resource-close cases belong to existing security/lifecycle qualification. Add precise API models and fixtures under those owners; do not create a competing leak engine.
- PHP unserialize and Ruby Marshal were already cataloged. Review public runtime ownership under their existing research routes. No premium content or issues were migrated.
- Ruby Open3 returned-pipe cleanup and Tempfile close/unlink belong under existing Ruby lifecycle qualification. Open3's Process.detach waiter reaps independently; missing wait-thread value retrieval is not a zombie-process finding. Tempfile deletion requires an actual temporary-use obligation; retained or renamed artifacts differ.
- Ruby Psych unsafe-load and Kernel.open pipe-command cases route to existing deserialization and command-execution discovery. Psych safe defaults depend on its exact loaded version; Kernel.open pipe mode is scoped to Ruby 3.4 and excluded on Ruby 4.
- Ruby Open3 paired-pipe deadlock remains deferred until child output volume, effective pipe capacity and blocking read order can be proven. Sequential source order alone is insufficient.
- Rust Unix pre_exec callback safety and process-environment mutation remain deferred. Require executed post-fork callback identity or actual foreign environment-reader concurrency respectively; unused registration, Windows environment mutation and CommandExt::exec need their distinct contracts.
- C formatted-output taint needs a current exact-build check of global external declaration identity before any production endpoint.
- GCM nonce reuse needs proven same-key/nonce byte equality and a bounded encryption lifetime. Regex risk needs an engine-specific complexity witness, tainted input and effective work bounds. ctypes needs platform-aware loader provenance. These are deferred, not rejected or supported.
- Legacy PBKDF2 overload defaults are a precise configuration/match lead, outside this taint/typestate wave. Do not invent a universal password-work-factor threshold.

The private ownership audit contains the exact existing tracker references and remains outside this public repository. Re-fetch inventories at execution time; routing does not claim those issues are complete.

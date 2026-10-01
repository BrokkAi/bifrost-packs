# Standard-library policy research

Reviewed on 2026-10-01 against public packs revision
`bb0eb7158e4b322304af29bdb8f56c697937585c`. Three Luna xhigh subagents
researched Python, JDK/.NET and Go/Node independently. The primary agent reviewed
their contracts and added Rust, C/C++ and PHP/Ruby runtime leads.

The [catalog](candidates.md) and [CSV](candidates.csv) contain research hypotheses,
not runnable policies. [JSON](candidates.json) retains the API identities,
positive and near-miss sketches, source links, prerequisites and stop gates.
The [qualification queue](qualification-queue.md) groups the next investigations.
Priority measures investigation value; it does not certify Bifrost support.

## Scope and ownership

Public scope is a standard runtime's APIs: CPython stdlib, JDK modules, Node
built-ins, Go stdlib, Rust `std`, .NET base class library and PHP/Ruby runtime
APIs. C ISO-library APIs and POSIX/libc extensions are distinguished by their
platform contracts. Kotlin/Scala calls to JDK and TypeScript calls to Node need
their own adapter qualification; shared APIs do not prove language parity.

Third-party packages, drivers, frameworks and customer/application protocols stay
outside this stdlib queue. A standard interface backed by a driver must separate
the interface's documented obligation from driver-specific behavior. Distribution
with an SDK, installation via a package manager, or popularity does not by itself
establish standard-library membership.

The overlap review included current public, premium and engine issue inventories,
public manifests and premium authoring/research inventories. Existing shell/SQL,
Java XML/object-deserialization and generic lifecycle work is routed to its owner.
Runtime APIs already cataloged alongside dependency leads require an ownership
review; they are not new discoveries. A shared weakness family, such as archive
extraction, does not make distinct stdlib and third-party API contracts duplicates.
No existing premium content or issue was moved, copied or closed in this pass.

Public research here is newly authored from linked primary documentation.
Private implementation, fixtures, research prose and issue bodies are excluded.
The private overlap audit is retained outside the public repository. This pass
does not claim exhaustive stdlib coverage; Swift/Foundation and other unlisted
surfaces were not researched, and C++ coverage is limited to libc call sites.

## Qualification contract

For each accepted investigation:

1. Pin the runtime/toolchain, API source revision, Bifrost build and semantic
   pack hashes. A documentation version or retrieval date is a research reference,
   not immutable executable qualification evidence.
2. Prove declaration-backed API identity, dangerous operand or object identity,
   argument/result binding, and the relevant trust/ownership boundary. Similar
   names and favorable dispatch labels are insufficient.
3. Start with one API/version/language contract. Run an original harmless positive,
   realistic close near misses, aliases/wrappers, non-reaching input, unrelated
   same-name APIs and the applicable error/deferred exits.
4. For taint, prove the value reaches the dangerous context. Parsing, hashing,
   escaping, path normalization and constant-time comparison are not universal
   sanitizers. For typestate, correlate the same object/result with the state
   transition and consuming operation; a lexical call order is insufficient.
5. Record `qualified`, `rejected`, `incomplete` or `unsupported` with diagnostic
   evidence. Stop at a resolver, model, binding, flow, alias, concurrency or
   runtime gap, and route the minimal reproduction to the existing engine owner.
   Empty findings under incomplete coverage are not a clean result.
6. Create an implementation issue only for a supported, behavior-tested slice.
   Public/premium content authoring, packaging, scanner selection and hosted
   enablement remain distinct delivery steps.

The catalog was reviewed against the installed Bifrost policy manifest. No taint
or typestate candidate was evaluated through the analyzer in this research pass.
Repository content/native byte-integrity checks and existing unit tests protect
the unchanged pack content; they do not qualify these hypotheses.

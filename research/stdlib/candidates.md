# Standard-library candidate catalog

Every row is research-only and unqualified. The [qualification contract](README.md) defines acceptance. Primary documentation establishes API facts; the proposed policy is our inference. Positives and near misses below are original fixture sketches, not executed results.

| ID | Runtime | Analysis | Priority | Routing |
| --- | --- | --- | --- | --- |
| [python-queue-task-accounting](#python-queue-task-accounting) | python | typestate | P2 | candidate |
| [python-socketserver-shutdown-thread-state](#python-socketserver-shutdown-thread-state) | python | typestate | P2 | candidate |
| [python-xinclude-untrusted-href](#python-xinclude-untrusted-href) | python | taint | P2 | candidate |
| [python-multiprocessing-connection-recv-pickle](#python-multiprocessing-connection-recv-pickle) | python | taint | P1 | candidate |
| [python-logging-config-listener-verification](#python-logging-config-listener-verification) | python | taint + verification gate | P2 | candidate |
| [python-dynamic-import-untrusted-name](#python-dynamic-import-untrusted-name) | python | taint | P2 | candidate |
| [python-ctypes-dynamic-library-load](#python-ctypes-dynamic-library-load) | python | taint | P2 | deferred-proof-heavy |
| [python-ssl-client-verification-typestate](#python-ssl-client-verification-typestate) | python | typestate | P1 | candidate |
| [jvm-zip-entry-containment](#jvm-zip-entry-containment) | JVM (Java; Kotlin/Scala callers of JDK members) | taint | P1 | candidate |
| [jvm-jndi-filter-escaping](#jvm-jndi-filter-escaping) | JVM (Java; Kotlin/Scala callers of JDK members) | taint | P1 | candidate |
| [jvm-aead-cipherinputstream-integrity](#jvm-aead-cipherinputstream-integrity) | JVM (Java; Kotlin/Scala callers of JDK members) | taint + typestate | P1 | candidate |
| [gcm-nonce-reuse-same-key](#gcm-nonce-reuse-same-key) | JVM (Java/Kotlin/Scala) and C#/.NET | relational encryption protocol | P2 | deferred-proof-heavy |
| [dotnet-processstartinfo-executable-and-shell-boundary](#dotnet-processstartinfo-executable-and-shell-boundary) | C#/.NET | taint | P2 | candidate |
| [dotnet-xmlreader-external-dtd-resolution](#dotnet-xmlreader-external-dtd-resolution) | C#/.NET | taint + typestate | P1 | candidate |
| [dotnet-regex-unbounded-backtracking](#dotnet-regex-unbounded-backtracking) | C#/.NET | taint | P2 | deferred-proof-heavy |
| [dotnet-rfc2898-weak-default-parameters](#dotnet-rfc2898-weak-default-parameters) | C#/.NET | match/configuration | P2 | out-of-scope-match-lead |
| [go-database-sql-tx-terminal](#go-database-sql-tx-terminal) | Go | typestate | P2 | candidate |
| [go-crypto-tls-client-skip-verification](#go-crypto-tls-client-skip-verification) | Go | typestate | P1 | candidate |
| [go-archive-extraction-root-confinement](#go-archive-extraction-root-confinement) | Go | taint | P2 | candidate |
| [node-crypto-authenticated-decipher-finalization](#node-crypto-authenticated-decipher-finalization) | JavaScript/TypeScript (Node.js built-ins) | taint + typestate | P1 | candidate |
| [go-net-http-response-body-completion](#go-net-http-response-body-completion) | Go | taint | P2 | existing-owner |
| [node-child-process-shell-boundary](#node-child-process-shell-boundary) | JavaScript/TypeScript (Node.js built-ins) | taint | P2 | existing-owner |
| [rust-child-reaping](#rust-child-reaping) | rust | typestate | P1 | candidate |
| [rust-explicit-shell-command](#rust-explicit-shell-command) | rust | taint | P2 | candidate |
| [rust-path-root-containment](#rust-path-root-containment) | rust | taint | P2 | candidate |
| [c-stdio-format-taint](#c-stdio-format-taint) | c/cpp | taint | P2 | needs-identity-recheck |
| [c-stream-close-protocol](#c-stream-close-protocol) | c/cpp | typestate | P2 | existing-owner |
| [php-proc-open-paired-ownership](#php-proc-open-paired-ownership) | php | typestate | P2 | candidate |
| [php-runtime-deserialization](#php-runtime-deserialization) | php | taint | P2 | existing-catalog-routing |
| [ruby-marshal-untrusted-load](#ruby-marshal-untrusted-load) | ruby | taint | P2 | existing-catalog-routing |
| [rust-maybeuninit-initialization-state](#rust-maybeuninit-initialization-state) | rust | typestate | P1 | candidate |
| [rust-condvar-predicate-recheck](#rust-condvar-predicate-recheck) | rust | typestate | P2 | candidate |
| [rust-bufwriter-drop-hidden-flush-error](#rust-bufwriter-drop-hidden-flush-error) | rust | typestate | P2 | candidate |
| [rust-unix-pre-exec-callback-safety](#rust-unix-pre-exec-callback-safety) | rust | execution-context safety precondition | P2 | deferred-proof-heavy |
| [rust-process-environment-mutation-thread-state](#rust-process-environment-mutation-thread-state) | rust | concurrency safety precondition | P2 | deferred-proof-heavy |
| [ruby-net-http-active-peer-verification-disabled](#ruby-net-http-active-peer-verification-disabled) | ruby | typestate | P1 | candidate |
| [ruby-open3-popen3-paired-pipe-draining](#ruby-open3-popen3-paired-pipe-draining) | ruby | typestate | P2 | deferred-proof-heavy |
| [ruby-open3-popen3-owned-pipe-closure](#ruby-open3-popen3-owned-pipe-closure) | ruby | typestate | P2 | existing-owner |
| [ruby-tempfile-create-unlinked-owner](#ruby-tempfile-create-unlinked-owner) | ruby | typestate | P2 | existing-owner |
| [ruby-kernel-open-pipe-command-taint](#ruby-kernel-open-pipe-command-taint) | ruby | taint | P2 | existing-owner |
| [ruby-psych-unsafe-load-untrusted-yaml](#ruby-psych-unsafe-load-untrusted-yaml) | ruby | taint | P2 | existing-catalog-routing |

## python-queue-task-accounting

**Queue work items need one completion acknowledgement per successful get** (typestate; candidate).

APIs: `queue.Queue.put`, `queue.Queue.get`, `queue.Queue.task_done`, `queue.Queue.join`, `queue.SimpleQueue (excluded: no task_done/join contract)`, `asyncio.Queue.put/get/task_done/join (separate async surface)`.

For each value returned by exact Queue.get()/get_nowait() on the same queue instance, the consumer must eventually mark the work complete with one task_done(), or transfer/requeue responsibility before acknowledging the current item, so a corresponding join() does not remain outstanding. queue.Queue.shutdown(immediate=True), introduced in Python 3.13, intentionally changes join accounting and must not be reported as missing worker acknowledgements. Do not infer correctness from qsize()/empty(). task_done decrements a queue-level count and takes no item argument: a per-item acknowledgement obligation needs an explicit worker-ownership profile and global puts/gets accounting; retries and delegated acknowledgements must be modeled.

Positive fixture sketch:

```text
def worker(q):
    item = q.get()
    process(item)  # if this raises, the unfinished-task count is never decremented
    q.task_done()
# A later q.join() can wait forever.
```

Near-miss fixture sketch:

```text
def worker(q):
    item = q.get()
    try:
        process(item)
    finally:
        q.task_done()
# Alternatively, transfer a failed item to a retry/dead-letter queue before
# acknowledging the current queue's item.
```

Required proof: Exact queue object identity through aliases/arguments; distinguish Queue from SimpleQueue and asyncio.Queue; bind each get to task_done; model try/finally and exception exits; account for requeue/retry and 3.13 shutdown(immediate=True).

Stop gate: Stop if the analyzer cannot preserve queue alias identity, pair get results with acknowledgements, or represent exception and shutdown paths. A textual count of get()/task_done() calls is insufficient. Treat unknown escape or helper ownership as incomplete.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [queue — Synchronized queue class (Python 3.13)](https://docs.python.org/3.13/library/queue.html), [asyncio queues (Python 3.13)](https://docs.python.org/3.13/library/asyncio-queue.html).

## python-socketserver-shutdown-thread-state

**BaseServer.shutdown must stop a running serve_forever loop from another thread** (typestate; candidate).

APIs: `socketserver.BaseServer.serve_forever`, `socketserver.BaseServer.shutdown`, `socketserver.BaseServer.server_close`.

For the same BaseServer object, shutdown() is safe only while serve_forever() is running in a different thread; shutdown() requests stop and waits. server_close() is a distinct cleanup action and is not a substitute for shutdown().

Positive fixture sketch:

```text
class BadServer(socketserver.TCPServer):
    def service_actions(self):
        self.shutdown()  # same thread as serve_forever; documented deadlock

server = BadServer(addr, Handler)
server.serve_forever()
```

Near-miss fixture sketch:

```text
server = socketserver.ThreadingTCPServer(addr, Handler)
thread = threading.Thread(target=server.serve_forever)
thread.start()
server.shutdown()  # controlling thread differs from serve_forever thread
thread.join()
server.server_close()
# The same safe ordering applies when another existing control thread calls shutdown().
```

Required proof: Prove BaseServer instance identity at both methods; know serve_forever execution is active and identify its thread; represent call/thread join ordering and subclasses without assuming all objects share the contract.

Stop gate: Stop if control-flow/thread modeling cannot establish same-instance active serve_forever on another thread. Do not approximate with method-name order or assume shutdown is safe whenever a Thread object exists.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [socketserver — A framework for network servers (Python 3.13)](https://docs.python.org/3.13/library/socketserver.html).

## python-xinclude-untrusted-href

**Untrusted XInclude href can select a local resource through ElementInclude's default loader** (taint; candidate).

APIs: `xml.etree.ElementTree.fromstring`, `xml.etree.ElementTree.parse`, `xml.etree.ElementInclude.include`, `xml.etree.ElementInclude.default_loader`.

Taint must flow from untrusted XML input into an XInclude element's href, through an exact ElementInclude.include() call using the default loader (loader omitted/None), to a local resource read. A custom loader with a proven restrictive policy or a fixed trusted XML document is a control. The documented max_depth bounds recursion but does not establish href trust.

Positive fixture sketch:

```text
root = ET.fromstring(request.body)
ElementInclude.include(root)  # default loader reads include hrefs from disk
```

Near-miss fixture sketch:

```text
root = ET.fromstring(TRUSTED_TEMPLATE)
ElementInclude.include(root, loader=allowlisted_loader)  # custom loader accepts only approved identifiers
```

Required proof: Track parsed XML provenance into element attributes and the href consumed by XInclude; prove default-loader selection versus custom loader; model the path/resource read and any data exposure separately.

Stop gate: Stop if XML node/attribute lineage, default-loader selection, or filesystem effect identity is unavailable. Do not report arbitrary XML parsing, external entity behavior, or an include call with a restrictive custom loader as this finding.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [xml.etree.ElementTree (Python 3.13)](https://docs.python.org/3.13/library/xml.etree.elementtree.html), [XML Processing Modules and security considerations (Python 3.13)](https://docs.python.org/3.13/library/xml.html).

## python-multiprocessing-connection-recv-pickle

**Connection.recv implicitly unpickles messages from a peer** (taint; candidate).

APIs: `multiprocessing.connection.Connection.recv`, `multiprocessing.connection.Connection.recv_bytes`, `multiprocessing.connection.Listener`, `multiprocessing.connection.Client`, `multiprocessing.Pipe`.

An exact Connection.recv() on a connection whose peer is not established as trusted/authenticated performs implicit pickle deserialization. recv_bytes() returns bytes and is not itself the same object-construction sink. Listener/Client authentication configuration and Pipe's process-local context affect trust; do not infer untrustedness merely from the method name. Peer authentication establishes credential possession, not automatically benign payloads; only an explicit trusted-peer contract discharges the object-deserialization trust boundary.

Positive fixture sketch:

```text
conn = listener.accept()  # endpoint can be an untrusted peer unless authenticated
obj = conn.recv()
```

Near-miss fixture sketch:

```text
conn = multiprocessing.Pipe()[0]
obj = conn.recv()  # the docs distinguish Pipe-created connections from other connections;
                   # same method call alone does not prove an untrusted peer
```

Required proof: Resolve Connection receiver identity and origin (Pipe vs Listener/Client); follow authentication-key configuration or an explicit trust profile; model recv's implicit pickle effect separately from recv_bytes.

Stop gate: Stop if connection origin, peer authentication, or trust state cannot be proven. Do not turn every recv() into a finding or rely on a same-named method selector.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [multiprocessing — Process-based parallelism (Python 3.13)](https://docs.python.org/3.13/library/multiprocessing.html), [pickle — Python object serialization (Python 3.13)](https://docs.python.org/3.13/library/pickle.html).

## python-logging-config-listener-verification

**A logging configuration listener needs a verification gate before processing received config** (taint + verification gate; candidate).

APIs: `logging.config.listen`, `logging.config.stopListening`, `logging.config.dictConfig`, `logging.config.fileConfig`.

When a logging.config.listen() thread processes bytes that may be supplied by an untrusted local user, a verify callback should authenticate/decrypt and return accepted bytes or None. Absence of verify is only reportable under an applicable untrusted-local-user threat profile; localhost binding does not mean mutually trusted callers.

Positive fixture sketch:

```text
listener = logging.config.listen(port=9020)  # no verify callback
listener.start()
```

Near-miss fixture sketch:

```text
listener = logging.config.listen(port=9020, verify=verify_signed_config)
listener.start()
```

Required proof: Exact listen target; configuration of verify argument and its callback's result semantics; deployment threat profile for multi-user local access; model configuration processing/evaluation as the dangerous effect.

Stop gate: Stop if call identity or verify-argument binding is incomplete, callback validation cannot be established, or the policy has no applicable local-user threat context. Do not flag all logging configuration or equate localhost with remote exposure.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [logging.config — Logging configuration (Python 3.13)](https://docs.python.org/3.13/library/logging.config.html), [Security Considerations (Python 3.13)](https://docs.python.org/3.13/library/security_warnings.html).

## python-dynamic-import-untrusted-name

**Untrusted module names can reach importlib.import_module and execute selected module initialization** (taint; candidate).

APIs: `importlib.import_module`, `builtins.__import__`, `importlib.util.spec_from_file_location`, `importlib.util.module_from_spec`.

Report only when untrusted data reaches the exact module-name argument of a dynamic import and the selected module executes under the application's authority without a proven allowlist/registry gate. File-based loading is a related but distinct path-and-loader contract.

Positive fixture sketch:

```text
module_name = request.args['plugin']
plugin = importlib.import_module(module_name)
```

Near-miss fixture sketch:

```text
plugin = importlib.import_module(ALLOWED_PLUGINS[request.args['plugin']])  # key is mapped to a fixed allowlist
```

Required proof: Exact dynamic import identity and argument binding; source-to-name propagation; prove an allowlist or dispatch gate's completeness; account for package-relative names, meta_path hooks, import caches, and sys.path provenance.

Stop gate: Stop if module identity/path resolution or allowlist completeness is unknown. Do not infer arbitrary code execution from a constant trusted import or from a name-only `import` match.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [importlib — The implementation of import (Python 3.13)](https://docs.python.org/3.13/library/importlib.html).

## python-ctypes-dynamic-library-load

**Untrusted library names reaching ctypes loaders can load native code into the process** (taint; deferred-proof-heavy).

APIs: `ctypes.CDLL`, `ctypes.PyDLL`, `ctypes.WinDLL`, `ctypes.OleDLL`, `ctypes.cdll.LoadLibrary`, `ctypes.windll.LoadLibrary`.

Taint reaching the exact library-name argument is dangerous only when resolution can select an attacker-controlled or untrusted native library. A constant, trusted absolute path or complete allowlist is a control. Platform search paths, dependent libraries, handles, and preloaded objects alter what name resolution means.

Positive fixture sketch:

```text
library_name = request.args['backend']
lib = ctypes.CDLL(library_name)
```

Near-miss fixture sketch:

```text
lib = ctypes.CDLL('/usr/lib/libtrusted_backend.so')  # fixed deployment-owned path
```

Required proof: Exact ctypes loader identity and formal argument binding; track attacker-controlled name/path; determine whether resolved library location can be influenced; keep platform and loader-search semantics explicit.

Stop gate: Stop if runtime loader resolution, path provenance, or platform scope is unknown. Do not classify every CDLL call or trust a basename-only allowlist as path-safe.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [ctypes — A foreign function library for Python (Python 3.13)](https://docs.python.org/3.13/library/ctypes.html).

## python-ssl-client-verification-typestate

**Client TLS contexts must preserve certificate-chain and hostname verification through wrap_socket** (typestate; candidate).

APIs: `ssl.create_default_context`, `ssl.SSLContext`, `ssl.PROTOCOL_TLS_CLIENT`, `ssl.CERT_REQUIRED`, `ssl.CERT_NONE`, `SSLContext.verify_mode`, `SSLContext.check_hostname`, `SSLContext.wrap_socket`, `SSLContext.wrap_bio`.

For client-side peer authentication, the context at handshake must have certificate verification enabled (CERT_REQUIRED) and hostname checking enabled, and wrap_socket/wrap_bio must supply the intended server_hostname. create_default_context() and PROTOCOL_TLS_CLIENT establish the documented secure baseline; later mutations can invalidate it. Server-side client-certificate authentication is a separate contract.

Positive fixture sketch:

```text
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
sock = ctx.wrap_socket(raw_sock)  # no peer hostname validation
```

Near-miss fixture sketch:

```text
ctx = ssl.create_default_context()
sock = ctx.wrap_socket(raw_sock, server_hostname=host)
```

Required proof: Track exact SSLContext object, constructor/default state, all verify_mode/check_hostname mutations, client versus server use, aliasing and wrap call; use version/OpenSSL scope for any defaults asserted.

Stop gate: Stop if context identity/mutations escape, client/server role is unknown, or handshake call cannot be tied to the configured context. Never report based solely on a protocol constant spelling or a context variable's name. A proven equivalent peer pinning/verification contract before sensitive communication is a separate supported control; do not assume every custom trust scheme is defective. An unused context or wrap with handshake disabled and no later do_handshake/use is a near miss.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [ssl — TLS/SSL wrapper for socket objects (Python 3.13)](https://docs.python.org/3.13/library/ssl.html).

## jvm-zip-entry-containment

**Contain JDK ZIP entry paths before filesystem writes** (taint; candidate).

APIs: `java.util.zip.ZipInputStream.getNextEntry / ZipFile.entries or stream`, `java.util.zip.ZipEntry.getName`, `java.nio.file.Path.resolve/normalize/startsWith`, `java.nio.file.Files.newOutputStream/copy or java.io.FileOutputStream`.

ZipEntry.getName returns the entry name. Before writing, reject rooted paths and establish that the normalized candidate remains beneath the normalized extraction root using Path component semantics, not a string prefix. Lexical normalization alone does not prove safety against symlink or filesystem races.

Positive fixture sketch:

```text
An untrusted ZipInputStream entry named ../../outside.txt is resolved under dest and passed to Files.copy/newOutputStream without checking the resolved path against dest.
```

Near-miss fixture sketch:

```text
Resolve and normalize against an absolute extraction root, reject rooted entries, and require candidate.startsWith(root) as a Path component check before the write. This is only a lexical traversal control; symlink and race cases need separate proof.
```

Required proof: Prove the exact JDK ZIP and filesystem member identities, archive provenance, same entry-name value flowing into the path and write, and the intended extraction root. For Kotlin/Scala, use the resolved JDK member identity rather than a language facade or wrapper name.

Stop gate: Stop if archive entry identity, destination root, path provider/platform semantics, or the actual write cannot be proven. Do not claim symlink-safe extraction from lexical normalize/startsWith alone; preserve incomplete status for symlink and TOCTOU cases.

Ownership: Distinct stdlib archive/path APIs. Sharing a weakness family with third-party archive packages does not establish identical policy ownership.

Sources: [ZipEntry (Java SE 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/zip/ZipEntry.html), [ZipInputStream (Java SE 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/zip/ZipInputStream.html), [Path (Java SE 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Path.html).

## jvm-jndi-filter-escaping

**Keep untrusted values out of JNDI LDAP filter syntax** (taint; candidate).

APIs: `javax.naming.directory.DirContext.search(String|Name, String filter, SearchControls)`, `javax.naming.directory.DirContext.search(String|Name, String filterExpr, Object[] filterArgs, SearchControls)`, `JDK built-in LDAP provider when provider identity is proven`.

The filter is RFC 2254/LDAP filter syntax. The filter-arguments overload substitutes values and performs escaping; string concatenation into the raw filter overload preserves attacker-controlled filter operators.

Positive fixture sketch:

```text
A login directory search builds (uid=<input>) by concatenating request text into the raw filter string, then uses the result set to select an authenticated identity.
```

Near-miss fixture sketch:

```text
Use a fixed filter expression such as (uid={0}) and pass the untrusted value as filterArgs; alternatively construct an attribute match through the structured Attributes overload.
```

Required proof: Prove exact DirContext.search overload identity, taint reaching the filter grammar/value position, and result use in a security-relevant lookup. Prefer the JDK LDAP provider with resolved provider evidence; do not assume every third-party JNDI provider has the same encoding contract.

Stop gate: Stop when call binding/provider identity is unknown, the tainted value is not part of the filter, the argument overload's escaping cannot be established, or the directory result does not affect the claimed security decision. Treat partial provider discovery as incomplete.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [DirContext (Java SE 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.naming/javax/naming/directory/DirContext.html), [JNDI LDAP context search methods and filter arguments](https://docs.oracle.com/javase/jndi/tutorial/ldap/search/search.html), [javax.naming.directory (Java SE 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.naming/javax/naming/directory/package-summary.html).

## jvm-aead-cipherinputstream-integrity

**Do not consume AEAD plaintext through CipherInputStream** (taint + typestate; candidate).

APIs: `javax.crypto.CipherInputStream(InputStream, Cipher)`, `javax.crypto.Cipher.init(DECRYPT_MODE, ...)`, `AEAD cipher identity such as AES/GCM/NoPadding`, `javax.crypto.Cipher.doFinal / AEADBadTagException as the comparison path`.

For AEAD decryption, tag validation is a required success condition. CipherInputStream may catch integrity-check exceptions and not rethrow them; direct Cipher.doFinal reports an AEADBadTagException when the tag does not match.

Positive fixture sketch:

```text
An application decrypts attacker-controlled GCM ciphertext through CipherInputStream and parses, authorizes, or commits data read from the stream without another authenticated-result contract.
```

Near-miss fixture sketch:

```text
Use Cipher directly and make consumption of the returned plaintext control-dependent on doFinal completing normally; reject AEADBadTagException before acting on plaintext.
```

Required proof: Prove exact CipherInputStream and Cipher identities, a decrypt-mode AEAD algorithm, the same Cipher instance, untrusted ciphertext provenance, and a downstream sensitive consumer of bytes returned before an explicit successful authentication result.

Stop gate: Do not generalize to non-AEAD ciphers or infer authentication from an algorithm name fragment. Stop if provider/algorithm mode, ciphertext flow, or the downstream use is unknown; do not treat a swallowed exception as proof that every provider emitted plaintext.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [CipherInputStream (Java SE 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/crypto/CipherInputStream.html), [Cipher (Java SE 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/crypto/Cipher.html), [AEADBadTagException (Java SE 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/crypto/AEADBadTagException.html).

## gcm-nonce-reuse-same-key

**Require fresh GCM nonce values for each encryption under a key** (relational encryption protocol; deferred-proof-heavy).

APIs: `JDK javax.crypto.Cipher.getInstance("AES/GCM/NoPadding") + init(ENCRYPT_MODE, key, GCMParameterSpec) + doFinal`, `.NET System.Security.Cryptography.AesGcm.Encrypt(nonce, plaintext, ciphertext, tag, associatedData)`.

For distinct successful GCM encryptions using the same effective key, nonce/IV byte values must be unique. The rule does not apply to decryptions and must not infer key equality from variable names alone.

Positive fixture sketch:

```text
Two distinct successful encryptions in one pinned process reuse the same effective key and equal fixed nonce bytes. Cross-process restart/counter persistence is deferred until configuration/lifecycle evidence exists.
```

Near-miss fixture sketch:

```text
The same key is retained while each encryption receives a provably distinct nonce from a non-wrapping per-key counter or a separately justified unique-nonce mechanism. A new key per operation also breaks the same-key pair.
```

Required proof: Prove exact AES-GCM encryption mode/API, successful distinct encryption sites, effective key identity/equality, nonce byte-value equality, and control-flow reachability across loops/calls/restarts as applicable. Retain alias and value provenance for arrays/spans and key wrappers.

Stop gate: Stop rather than compare names or assume fresh arrays contain equal/different values. Preserve incomplete when key aliasing, nonce contents, provider-generated IV guarantees, lifecycle scope, or counter reset/wrap behavior is unknown. Do not report decrypt calls or non-GCM modes.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [Java Cryptography Architecture Reference Guide (Java SE 21)](https://docs.oracle.com/en/java/javase/21/security/java-cryptography-architecture-jca-reference-guide.html), [AesGcm.Encrypt (.NET 10 API)](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.aesgcm.encrypt?view=net-10.0).

## dotnet-processstartinfo-executable-and-shell-boundary

**Track ProcessStartInfo executable selection and explicit shell parsing** (taint; candidate).

APIs: `System.Diagnostics.ProcessStartInfo.FileName`, `ProcessStartInfo.Arguments`, `ProcessStartInfo.ArgumentList`, `ProcessStartInfo.UseShellExecute`, `System.Diagnostics.Process.Start`.

FileName selects the application/document to start. ArgumentList builds an escaped command-line representation for the OS; it does not neutralize a later command interpreter. UseShellExecute selects OS-shell launching behavior and varies by target/runtime defaults, so policy decisions must use explicit or resolved state. Attacker-controlled executable selection needs an explicit unauthorized-code/trust boundary; legitimate caller-authorized tool selection is not inherently a violation.

Positive fixture sketch:

```text
Untrusted input selects ProcessStartInfo.FileName, or reaches a command string passed to a proven interpreter such as cmd.exe /c or sh -c before Process.Start. For the latter, trace the interpreter's command-language position, not merely any argument.
```

Near-miss fixture sketch:

```text
A fixed executable receives an ordinary untrusted value as one ArgumentList item with UseShellExecute=false and no explicit interpreter. Do not call shell injection solely because a value contains semicolons or pipes; target-specific argument/option injection is a separate contract.
```

Required proof: Prove exact System.Diagnostics identities, FileName or interpreter identity, UseShellExecute state, argument position, taint flow, and the Process.Start call. Pin .NET target/runtime and platform where shell dispatch or quoting differs.

Stop gate: Stop if executable resolution, UseShellExecute, argument boundaries, platform, or target command grammar is unknown. Never collapse every Arguments/ArgumentList flow into POSIX shell execution; keep target-specific argument injection out of this rule.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [ProcessStartInfo (.NET 10 API)](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo?view=net-10.0), [ProcessStartInfo.ArgumentList (.NET 10 API)](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist?view=net-10.0), [ProcessStartInfo.Arguments (.NET 10 API)](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.arguments?view=net-10.0).

## dotnet-xmlreader-external-dtd-resolution

**Require explicit safe DTD and resolver state for untrusted XML** (taint + typestate; candidate).

APIs: `System.Xml.XmlReaderSettings.DtdProcessing`, `XmlReaderSettings.XmlResolver`, `System.Xml.XmlReader.Create`, `System.Xml.XmlTextReader.DtdProcessing/XmlResolver (separate versioned API)`.

DtdProcessing.Parse enables DTD processing. External resolution requires a resolver capable of opening the referenced resource. DtdProcessing.Prohibit rejects DTDs; XmlResolver=null blocks external resource resolution for XmlReaderSettings. Defaults are type- and framework-version-specific.

Positive fixture sketch:

```text
An attacker-controlled XML document is consumed by an XmlReader created with DtdProcessing.Parse and a resolver that can access external file or network resources; the entity result is read by the application.
```

Near-miss fixture sketch:

```text
Keep DtdProcessing.Prohibit (the XmlReaderSettings default) or use Parse with XmlResolver=null and no alternate resolver path. Do not treat XML that permits inline DTDs but cannot resolve external resources as an XXE finding.
```

Required proof: Prove untrusted XML provenance, the same settings object reaching XmlReader.Create, concrete reader type, effective DtdProcessing and resolver values, runtime/framework version, and actual parser consumption. Separate external entity access from entity-expansion/size DoS.

Stop gate: Stop if parser type, default configuration, target framework, resolver implementation, or external resource reachability is unknown. Do not carry XmlReaderSettings defaults over to XmlTextReader or to third-party XML parsers.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [XmlReaderSettings.DtdProcessing (.NET 10 API)](https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreadersettings.dtdprocessing?view=net-10.0), [XmlReaderSettings.XmlResolver (.NET 10 API)](https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreadersettings.xmlresolver?view=net-10.0), [XmlReader.Create (.NET 10 API)](https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreader.create?view=net-10.0).

## dotnet-regex-unbounded-backtracking

**Bound .NET backtracking regex work on attacker-controlled input** (taint; deferred-proof-heavy).

APIs: `System.Text.RegularExpressions.Regex(String, RegexOptions, TimeSpan)`, `Regex.MatchTimeout`, `Regex.IsMatch/Match/Replace/Split`, `RegexOptions.NonBacktracking where supported`.

A finite timeout bounds one matching operation and throws RegexMatchTimeoutException. Without an explicit or app-wide timeout, matching is infinite by default. NonBacktracking changes engine behavior for its supported syntax subset.

Positive fixture sketch:

```text
A known catastrophic-backtracking expression such as nested ambiguous quantifiers is applied with the backtracking engine to attacker-controlled long near-match text using the default infinite timeout.
```

Near-miss fixture sketch:

```text
Use a finite per-instance/per-call timeout with deliberate timeout handling, or RegexOptions.NonBacktracking for compatible patterns; a bounded input-size contract can also constrain exposure.
```

Required proof: Prove the exact Regex operation and object, pattern structure/engine mode, attacker control of match input, input-size or timeout state, and whether an app-wide timeout is configured.

Stop gate: Stop if the pattern is dynamic/unknown, the selected engine cannot be established, or global timeout configuration is unavailable. Do not report every Regex call without a timeout; require a structural backtracking witness or another defensible risk bound.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [Regex.MatchTimeout (.NET 10 API)](https://learn.microsoft.com/en-us/dotnet/api/system.text.regularexpressions.regex.matchtimeout?view=net-10.0), [Backtracking in .NET regular expressions](https://learn.microsoft.com/en-us/dotnet/standard/base-types/backtracking-in-regular-expressions).

## dotnet-rfc2898-weak-default-parameters

**Reject legacy PBKDF2 constructors with weak implicit defaults** (match/configuration; out-of-scope-match-lead).

APIs: `System.Security.Cryptography.Rfc2898DeriveBytes(string, byte[])`, `Rfc2898DeriveBytes overloads omitting iteration count or HashAlgorithmName`, `Rfc2898DeriveBytes.Pbkdf2 one-shot APIs`.

The legacy defaults are 1000 iterations and HashAlgorithmName.SHA1. SYSLIB0041 marks default-parameter constructors obsolete from .NET 7. .NET 10 additionally obsoletes all instance constructors (SYSLIB0060) because PBKDF2 is intended as a one-shot operation.

Positive fixture sketch:

```text
A password-derived key is created using a default-parameter constructor, or the overload omits the hash/iteration setting and thereby selects the documented legacy defaults.
```

Near-miss fixture sketch:

```text
Use Rfc2898DeriveBytes.Pbkdf2 with explicit salt, work factor, hash algorithm, and output length chosen by the application’s current security policy; do not encode a fixed universal iteration count in the pack.
```

Required proof: Resolve the exact constructor overload and target framework, and establish that its derived bytes are used for a password-based key/verifier. Preserve explicit iteration/hash settings even when below local policy for a configuration-specific finding rather than treating all PBKDF2 as identical.

Stop gate: Stop if overload identity or target framework is unknown. Do not flag explicit parameters solely because they are below an invented universal threshold; require a policy-defined floor or the exact obsolete-default overload.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [SYSLIB0041: Rfc2898DeriveBytes legacy defaults](https://learn.microsoft.com/en-us/dotnet/fundamentals/syslib-diagnostics/syslib0041), [Rfc2898DeriveBytes (.NET 10 API)](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.rfc2898derivebytes?view=net-10.0), [SYSLIB0060: Rfc2898DeriveBytes constructors are obsolete](https://learn.microsoft.com/en-us/dotnet/fundamentals/syslib-diagnostics/syslib0060).

## go-database-sql-tx-terminal

**Complete database/sql transactions on every reachable exit** (typestate; candidate).

APIs: `database/sql.DB.Begin`, `database/sql.DB.BeginTx`, `database/sql.Conn.BeginTx`, `database/sql.Tx.Commit`, `database/sql.Tx.Rollback`.

For each successfully returned *sql.Tx, prove a terminal Commit or Rollback on that same transaction on all paths before ownership leaves the analyzed scope. BeginTx uses its context until terminal completion; cancellation makes database/sql roll back. DB.Begin uses context.Background internally, so there is no equivalent caller context cancellation path. Commit and Rollback both make later Tx operations fail with ErrTxDone.

Positive fixture sketch:

```text
A function calls db.Begin(), performs a write, then returns from an error branch without committing, rolling back, or transferring the transaction to an owner that will finish it.
```

Near-miss fixture sketch:

```text
The function defers tx.Rollback() immediately after BeginTx and commits on success; the deferred rollback after Commit is harmless. A BeginTx path whose exact context is proven cancelled also has an implicit rollback and should not be reported as an unclosed transaction.
```

Required proof: Resolve exact database/sql API identities and *sql.Tx object identity through aliases, parameters, helper returns, and closures; prove the Begin success branch; model defer order, callbacks, panic/exception-equivalent exits, Commit/Rollback, and the exact BeginTx context cancellation relation. Distinguish a transaction transferred to another owner.

Stop gate: Stop if Tx identity, ownership transfer, branch completion, defer execution, or BeginTx cancellation cannot be proven. Do not infer completion from a function named close/finish or from a driver-specific transaction type without exact identity.

Ownership: stdlib database/sql protocol is separate from vendor SQL syntax. Closure/leak components reuse Go lifecycle qualification; transaction/iteration semantics need separate bounded acceptance.

Sources: [Go database/sql package docs, go1.27.1](https://pkg.go.dev/database/sql@go1.27.1), [Go source tag go1.27.1: database/sql/sql.go (BeginTx and Tx lifecycle)](https://raw.githubusercontent.com/golang/go/go1.27.1/src/database/sql/sql.go).

## go-crypto-tls-client-skip-verification

**Track InsecureSkipVerify into active TLS client configurations** (typestate; candidate).

APIs: `crypto/tls.Config.InsecureSkipVerify`, `crypto/tls.Config.VerifyConnection`, `crypto/tls.Config.VerifyPeerCertificate`, `crypto/tls.Client`, `net/http.Transport.TLSClientConfig`, `crypto/tls.Conn.Handshake/HandshakeContext/Read/Write`, `net/http.Client.Do`.

Report only when the exact client-side tls.Config reaching tls.Client or an HTTP Transport has InsecureSkipVerify true and the analyzer can prove no custom verification callback is configured. A configured callback makes the outcome unresolved unless its behavior is itself proven; do not treat mere callback presence as safe. A zero/default false value retains the standard verification path. tls.Client construction and a Transport field assignment alone are not active handshakes; require a correlated executing consumer.

Positive fixture sketch:

```text
A Config with InsecureSkipVerify=true and nil verification callbacks reaches a client Conn that performs Handshake (or a Transport used by Client.Do). The same effective config is used at the handshake.
```

Near-miss fixture sketch:

```text
InsecureSkipVerify is false/default false. If it is true with a custom verification callback, do not suppress a finding merely because the callback exists; classify it as unqualified unless the callback's verification behavior is established. A config or tls.Client wrapper that is built but never performs a handshake/use is also a near miss.
```

Required proof: Resolve exact stdlib field and client-use identities; track Config pointer/copy/Clone identity and writes before handshake; distinguish client from server use; discover callbacks set through helper or mutation paths; account for Transport and tls.Client consumers.

Stop gate: Stop or preserve incomplete status when the final Config value, escape/mutation, client/server role, or callback behavior cannot be resolved. No string matching on field names and no claim that custom verification is correct from callback presence alone.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [Go crypto/tls package docs, go1.27.1](https://pkg.go.dev/crypto/tls@go1.27.1), [Go source tag go1.27.1: crypto/tls/common.go](https://raw.githubusercontent.com/golang/go/go1.27.1/src/crypto/tls/common.go).

## go-archive-extraction-root-confinement

**Confine stdlib archive entry writes to the extraction root** (taint; candidate).

APIs: `archive/tar.Reader.Next`, `archive/tar.Header.Name`, `archive/zip.File.Name`, `archive/zip.File.Open`, `os.OpenRoot`, `os.Root.OpenFile/Create/Mkdir`, `os.OpenInRoot`, `os.OpenFile`, `os.Create`, `filepath.Join`.

Trace an archive entry name to a filesystem write path. Treat direct writes using filepath.Join(root, archiveName) and ordinary os write APIs as potentially escaping; `os.Root` operations on the same root confine `..` and symlinks under their documented threat model. Do not assume tar/zip ErrInsecurePath is enabled, fatal, or validates tar link targets. Lexical filepath.IsLocal/Clean alone does not prove symlink/race safety. Start with a proven ../ escape in raw entries obtained by iterating Reader.File or Reader.Next. Do not treat all dynamic entry names as escaping, or assume Go filepath.Join has another runtime's absolute-component semantics.

Positive fixture sketch:

```text
An extractor takes tar.Header.Name or zip.File.Name and opens filepath.Join(destination, entryName) with os.OpenFile/os.Create without establishing component containment or using an exact destination os.Root.
```

Near-miss fixture sketch:

```text
The extractor opens one os.Root for the destination and writes each entry through that same root's OpenFile/Create/Mkdir methods. A lexical IsLocal check alone is not an equivalent near-miss for symlink or TOCTOU threats. Tar link targets must be analyzed separately from Header.Name.
```

Required proof: Prove exact archive API/member identity and entry-name provenance; track destination root identity and all normalization/validation; understand actual write APIs, symlink/hardlink handling, and return/error paths. Scope os.Root guarantees by GOOS; the Go docs note weaker TOCTOU protection for GOOS=js and do not promise mount-boundary confinement.

Stop gate: Stop if archive metadata provenance, destination root identity, write path, symlink target semantics, or platform behavior is uncertain. Do not claim archive extraction is safe from a GODEBUG flag or lexical path filter alone.

Ownership: Distinct stdlib archive/path APIs. Sharing a weakness family with third-party archive packages does not establish identical policy ownership.

Sources: [Go archive/tar package docs, go1.27.1](https://pkg.go.dev/archive/tar@go1.27.1), [Go archive/zip package docs, go1.27.1](https://pkg.go.dev/archive/zip@go1.27.1), [Go os package docs, go1.27.1](https://pkg.go.dev/os@go1.27.1), [Go blog: Traversal-resistant file APIs (os.Root introduced in Go 1.24)](https://go.dev/blog/osroot).

## node-crypto-authenticated-decipher-finalization

**Do not consume authenticated-decryption plaintext before decipher.final succeeds** (taint + typestate; candidate).

APIs: `node:crypto.createDecipheriv`, `Decipheriv.update`, `Decipheriv.setAAD`, `Decipheriv.setAuthTag`, `Decipheriv.final`.

For authenticated modes documented by Node (GCM, CCM, OCB, chacha20-poly1305), treat update() output as unauthenticated until the exact same Decipheriv instance completes final() successfully; only then allow trusted use. Respect mode-specific ordering: setAuthTag before update for CCM, before final for GCM/OCB/chacha20-poly1305. If final throws, discard all accumulated output. Pure private staging/parsing alone is not an authenticity-bypass finding: require an effect, publication or trusted decision from the provisional bytes. Configure any application-owned consuming boundary explicitly.

Positive fixture sketch:

```text
Plaintext returned by update influences a concrete write/authorization/publication boundary before the same decipher final succeeds; a tampered input later makes final throw after the earlier effect.
```

Near-miss fixture sketch:

```text
Accumulate update output in a private buffer, call final(), and only after it returns successfully parse or publish the concatenated plaintext; discard the buffer on a thrown final(). Non-authenticated modes are outside this contract.
```

Required proof: Resolve exact node:crypto identities and authenticated algorithm mode; track one Decipheriv object and update outputs through aliases, callbacks, and async functions; model setAAD/setAuthTag ordering, final success/throw, and effect sinks. TypeScript wrappers must resolve to the Node built-in API, not a lookalike.

Stop gate: Stop if mode, decipher identity, exception flow, or whether provisional bytes reach a security-sensitive effect cannot be proven. Do not treat any call to final on a different object or a caught final error as authentication success.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [Node.js v24.16.0 crypto API docs](https://nodejs.org/download/release/v24.16.0/docs/api/crypto.html), [Node.js source tag v24.16.0: lib/internal/crypto/cipher.js](https://raw.githubusercontent.com/nodejs/node/v24.16.0/lib/internal/crypto/cipher.js).

## go-net-http-response-body-completion

**Close successful net/http client response bodies on every exit** (taint; existing-owner).

APIs: `net/http.Client.Do/Get/Head/Post`, `net/http.Response.Body`, `io.ReadAll`, `io.Copy`, `io.Copy(io.Discard, body)`, `io.ReadCloser.Close`.

Only treat a response body as caller-owned after the client call returns err == nil. Require close on all exits or a proven ownership transfer. Reading to EOF without Close is insufficient for the documented caller obligation; Close without full reading can still be correct, though connection reuse is not guaranteed. A non-nil Response with non-nil error is limited to redirect failure and its body is already closed.

Positive fixture sketch:

```text
resp, err := client.Do(req); after err is checked nil, an early return from a status/error branch bypasses resp.Body.Close and no helper takes ownership.
```

Near-miss fixture sketch:

```text
defer resp.Body.Close() immediately after the nil-error check, or pass the body to a proven owner that closes it on every path. Closing is still sufficient for the obligation when the caller intentionally does not consume the whole body.
```

Required proof: Resolve exact net/http client call and response/body identity; model err/response pairing, early return, defer, helper ownership transfer, callback/exception paths, and wrappers. Exclude server-side request bodies and request bodies closed by Transport.

Stop gate: Stop if response/body identity or ownership transfer is unresolved. Do not flag all io.ReadAll calls, assume EOF implies Close, or label this a permanent resource leak without lifecycle evidence.

Ownership: stdlib net/http body closure is an API-specific specialization of existing Go lifecycle qualification, distinct from dependency-owned S3 models.

Sources: [Go net/http package docs, go1.27.1](https://pkg.go.dev/net/http@go1.27.1), [Go source tag go1.27.1: net/http/client.go](https://raw.githubusercontent.com/golang/go/go1.27.1/src/net/http/client.go).

## node-child-process-shell-boundary

**Keep dynamic command text away from Node child_process shell APIs** (taint; existing-owner).

APIs: `node:child_process.exec`, `execSync`, `spawn`, `spawnSync`, `execFile`, `execFileSync`, `options.shell`.

Track attacker-controlled command text into an exact shell-interpreting API: exec/execSync or spawn/execFile variants with shell:true. Do not report shell injection solely because tainted data is one argv element with shell disabled. Keep option injection, executable selection, and filesystem path validation as separate contracts.

Positive fixture sketch:

```text
exec('tool --input ' + request.query.value) reaches a child_process.exec call, so shell syntax in the dynamic portion is interpreted by the command shell.
```

Near-miss fixture sketch:

```text
spawn('tool', ['--input', request.query.value], {shell:false}) separates arguments from shell text for this specific sink. It is not automatically safe against option injection or unsafe executable/path selection.
```

Required proof: Use exact Node built-in member identities; propagate taint through template/string operations and options; resolve shell defaults by API/version and explicit options; model aliases and wrapper calls. Do not infer protection from argv alone beyond shell interpretation.

Stop gate: Do not open a duplicate candidate: route to the existing public JS/TS child-process security wave. Stop any rule draft if shell option resolution, built-in identity, or taint flow cannot be proven; do not claim argv prevents option injection.

Ownership: Node shell execution is already in the JavaScript/TypeScript public security wave; contribute precise built-in API cases to that owner.

Sources: [Node.js v24.16.0 child_process API docs](https://nodejs.org/download/release/v24.16.0/docs/api/child_process.html), [Node.js source tag v24.16.0: lib/child_process.js](https://raw.githubusercontent.com/nodejs/node/v24.16.0/lib/child_process.js).

## rust-child-reaping

**Owned std::process::Child must reach a proven reap or ownership transfer** (typestate; candidate).

APIs: `std::process::Command::spawn`, `std::process::Child::{wait,wait_with_output,try_wait,kill}`.

For a successfully spawned, locally owned child in a long-running Unix process, require a successful wait/wait_with_output or try_wait returning Ok(Some(_)) before ownership is discarded. kill alone is not a reap. Model live, reaped and transferred states; do not treat drop as waiting.

Positive fixture sketch:

```text
Spawn a fixed harmless child; an early error path drops the local Child without a wait. A second positive calls kill then drops the handle.
```

Near-miss fixture sketch:

```text
Successful wait; try_wait Ok(Some(_)); helper takes ownership and demonstrably waits; Command::output/status waits internally. try_wait Ok(None) remains positive if abandoned.
```

Required proof: Exact std declarations and successful-result binding; moved ownership, aliases, Result/Option branch predicates, helper summaries, every supported exit. Restrict initial claim to Unix long-running owner procedures.

Stop gate: Stop when native std identity, moves, escape, result polarity or exit partition is unproven. Do not infer universal OS exhaustion or a violation for intentional process-lifetime children.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [Rust 1.98.1 Child](https://doc.rust-lang.org/std/process/struct.Child.html), [Rust 1.98.1 Command](https://doc.rust-lang.org/std/process/struct.Command.html).

## rust-explicit-shell-command

**Untrusted data enters an explicit shell command executed by std::process::Command** (taint; candidate).

APIs: `std::process::Command::{new,arg,args,spawn,status,output}`.

On a pinned Unix platform, prove a Command targeting an explicitly reviewed shell such as /bin/sh receives untrusted shell syntax in its -c command operand and is executed. Generic Command arguments are data, not shell syntax. Windows cmd.exe/batch parsing requires a separate contract.

Positive fixture sketch:

```text
CLI input is formatted into the argument following -c on Command::new("/bin/sh"), then status is called.
```

Near-miss fixture sketch:

```text
Fixed /usr/bin/printf executable with constant format and input as a separate data argument; constructed-but-never-executed shell command; taint confined to an unused variable.
```

Required proof: Command builder identity and mutation order; exact argv slot and shell/executable identity; trusted-boundary configuration for CLI input; source-to-command-string flow and execution correlation.

Stop gate: Stop if final program/argv, shell parsing context, source trust or execution cannot be proven. A data argument can still cause application-specific option injection; this lead makes only a shell-syntax claim.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [Rust 1.98.1 Command argument semantics](https://doc.rust-lang.org/std/process/struct.Command.html).

## rust-path-root-containment

**Untrusted std::path composition reaches a filesystem write outside a declared root** (taint; candidate).

APIs: `std::path::Path::join`, `std::path::PathBuf::push`, `std::fs::{write,File::create,OpenOptions::open}`.

For an application-declared storage root, track untrusted path components through std path composition into an executed write and prove the resulting target can escape the root. Absolute components replace the base; lexical checks do not establish symlink/race safety.

Positive fixture sketch:

```text
A request-derived absolute component is joined to a fixed storage root and passed to fs::write, with no effective containment gate.
```

Near-miss fixture sketch:

```text
The same value is written as file contents to a fixed target; a closed allowlist maps to constant relative names; path construction is unused. Component-aware guarded writes need separately qualified path and symlink assumptions.
```

Required proof: Exact std identity including trait/inherent resolution; path mutation and platform components; declared root/trust boundary; write target binding, guard dominance and filesystem assumptions.

Stop gate: Stop when path semantics, root contract or write reachability is unknown. Neither join nor canonicalize is a universal sanitizer. Record platform, symlink and TOCTOU exclusions.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [Rust 1.98.1 PathBuf composition](https://doc.rust-lang.org/std/path/struct.PathBuf.html), [Rust std fs write](https://doc.rust-lang.org/std/fs/fn.write.html).

## c-stdio-format-taint

**Untrusted bytes reach the format operand of a libc printf-family call** (taint; needs-identity-recheck).

APIs: `printf`, `fprintf`, `sprintf`, `snprintf`, `vprintf`, `vfprintf`, `vsnprintf`.

Track attacker-controlled input into the exact format operand of a reached libc formatted-output function, including wrappers. Data in a constant-format %s argument is a near miss. A bounded destination does not make a tainted format safe.

Positive fixture sketch:

```text
Read external bytes into a buffer and pass it as fprintf(log, input); snprintf(out, n, input) is another positive.
```

Near-miss fixture sketch:

```text
fprintf(log, "%s", input); equivalent constant-format wrapper; attacker input does not reach the format position; workspace function named printf.
```

Required proof: Header-proven global external identity; correct zero-based format positions (printf 0, fprintf/sprintf 1, snprintf 2); varargs/wrapper flow; source buffer memory identity and extent. Separate libc/toolchain/platform profile.

Stop gate: An existing engine investigation reports a global C declaration binding gap; this pass did not reproduce it on a current build. Stop unless exact native identity binds; no name-based endpoint or severity assertion from API presence alone.

Ownership: An open engine investigation reports missing global C declaration binding. Recheck the current exact build before qualification; no spelling fallback.

Sources: [glibc 2.39 formatted output](https://sourceware.org/glibc/manual/2.39/html_node/Formatted-Output-Functions.html), [glibc variadic output](https://sourceware.org/glibc/manual/latest/html_node/Variable-Arguments-Output.html).

## c-stream-close-protocol

**Track FILE ownership and the correct close operation for ordinary and subprocess streams** (typestate; existing-owner).

APIs: `fopen`, `fclose`, `popen`, `pclose`, `fread`, `fwrite`.

After a successful acquisition, distinguish an ordinary FILE stream from a subprocess stream. The former closes via fclose; the latter closes/waits via pclose. Subsequent use or duplicate close on a proven closed alias is a protocol violation. Returning a stream can transfer ownership.

Positive fixture sketch:

```text
Use fwrite through an alias after fclose on an ordinary FILE; abandon a popen stream without pclose on a supported owner exit.
```

Near-miss fixture sketch:

```text
A helper takes ownership and invokes the correct close; acquisition returns null; an unrelated FILE is closed; process termination requires a different lifetime contract.
```

Required proof: Exact external declaration identity; null-result guards; allocation/alias and ownership summaries; normal/error exits; correct release behavior including a close operation that reports an error.

Stop gate: Stop at any exact external identity gap, may-alias/escape, unknown release behavior or unsupported exits. Existing generic lifecycle policy is not proof of libc ownership or subprocess wait semantics.

Ownership: Reuse existing lifecycle specialization under the C/C++ I/O-resource qualification owners. FILE versus subprocess release models belong there.

Sources: [glibc 2.23 close semantics](https://sourceware.org/glibc/manual/2.23/html_node/Closing-Streams.html), [glibc 2.40 subprocess streams](https://sourceware.org/glibc/manual/2.40/html_node/Pipe-to-a-Subprocess.html).

## php-proc-open-paired-ownership

**proc_open process and pipe ownership must be settled in order** (typestate; candidate).

APIs: `proc_open`, `fclose`, `proc_close`.

After successful proc_open, correlate the returned process resource with the output pipes. Track owned pipes and require closure before blocking proc_close where a still-open pipe can prevent child completion. Resource release and pipe release are distinct events; no deadlock claim without a concrete blocking dependency.

Positive fixture sketch:

```text
A fixed harmless child waits for EOF on stdin while the parent calls proc_close with its corresponding write pipe still open.
```

Near-miss fixture sketch:

```text
Parent closes its stdin pipe before proc_close and drains/closes owned output pipes; supplied inherited STDIN/STDOUT resources must not be assumed to be newly owned pipes.
```

Required proof: Exact PHP runtime identities; output-parameter array propagation; per-index pipe/resource pairing; child wait-for-EOF behavior and owned-versus-inherited descriptor classification; error exits.

Stop gate: Stop when descriptor shape, process/pipe correlation or child blocking behavior is unknown. A missing-close advisory is weaker than a proven deadlock.

Ownership: Reviewed against current authoring and issue inventories; distinct stdlib API contract, unless explicitly routed below. Shared risk families remain separate by exact API and runtime.

Sources: [PHP proc_open manual; PHP 7.4+ array-command distinction](https://www.php.net/manual/en/function.proc-open.php).

## php-runtime-deserialization

**Untrusted bytes reach runtime unserialize** (taint; existing-catalog-routing).

APIs: `unserialize`.

Prove untrusted serialized bytes reach the first argument. allowed_classes is not a blanket safety guarantee; use data-only interchange as the close alternative. Authentication of stored bytes must precede deserialization with an exact integrity/trust contract.

Positive fixture sketch:

```text
User-supplied bytes reach unserialize, including an allowed_classes=false variation that must not be declared universally safe.
```

Near-miss fixture sketch:

```text
Data-only JSON decoding with schema validation for this object-deserialization claim; immutable trusted fixture bytes. A hash without a verified secret integrity relationship does not remove taint.
```

Required proof: Exact builtin identity; source trust and byte propagation through storage/decoding; version/options; if modeled, integrity result, same bytes and dominance before use.

Stop gate: Existing research routing: do not open a duplicate qualification ticket. Stop at unresolved trust, builtin identity or effective integrity guard.

Ownership: Already cataloged runtime lead; ownership review before any new issue. No duplicate discovery or content migration claimed.

Sources: [PHP unserialize security warning](https://www.php.net/unserialize).

## ruby-marshal-untrusted-load

**Untrusted bytes reach Ruby Marshal.load/restore** (taint; existing-catalog-routing).

APIs: `Marshal.load`, `Marshal.restore`.

Track untrusted bytes or a stream into runtime object deserialization. Hooks can execute during loading; post-load type checking cannot guard the load itself.

Positive fixture sketch:

```text
Bytes read at an explicit external input boundary reach Marshal.load, then a class check is made afterward.
```

Near-miss fixture sketch:

```text
Trusted immutable test data; data-only parser for this specific object-deserialization claim; unrelated local object method named load.
```

Required proof: Exact runtime module/method identity including aliases; byte/stream provenance, wrapper summaries; trust boundary configuration.

Stop gate: Existing catalog routing: do not open duplicate work. Unknown runtime identity or input trust remains incomplete.

Ownership: Already cataloged runtime lead; ownership review before any new issue. No duplicate discovery or content migration claimed.

Sources: [Ruby 3.4 Marshal security guidance](https://docs.ruby-lang.org/en/3.4/Marshal.html).

## rust-maybeuninit-initialization-state

**Prove MaybeUninit initialization before assuming a T value** (typestate; candidate).

APIs: `std::mem::MaybeUninit::{uninit,new,write,assume_init,assume_init_ref,assume_init_mut,assume_init_read,assume_init_drop}`.

For an exact MaybeUninit<T> created in an uninitialized state, report an assume_init-family operation only when analysis proves that the same object is still uninitialized on a feasible reaching path. A successful write of a valid T or MaybeUninit::new establishes initialization. zeroed is not a generic initializer: all-zero validity and T's other invariants are type-specific. This lead covers missing initialization only; duplicate assume_init_read on non-Copy data is a separate ownership contract.

Positive fixture sketch:

```text
let slot = std::mem::MaybeUninit::<u32>::uninit();
let value = unsafe { slot.assume_init() }; // UB: no value was written
```

Near-miss fixture sketch:

```text
let mut slot = std::mem::MaybeUninit::<u32>::uninit();
slot.write(42);
let value = unsafe { slot.assume_init() }; // the same object was fully initialized
```

Required proof: Resolve exact std declarations and MaybeUninit<T>; track the same object through supported moves and aliases; establish full initialization and T validity at each unsafe consumer; model branches and the successful result of initialization helpers.

Stop gate: Stop if raw-pointer writes, field or array initialization, FFI out-pointers, helper calls, aliases, or type invariants prevent proving the same object's initialized state. Do not infer safety from zeroed or from the presence of any write; preserve unknown as incomplete.

Ownership: Distinct memory-initialization state from generic acquired-resource cleanup. No existing public Rust policy in the reviewed pack proves this object-specific initialization invariant.

Sources: [Rust 1.98.1 MaybeUninit](https://doc.rust-lang.org/std/mem/union.MaybeUninit.html).

## rust-condvar-predicate-recheck

**Recheck the guarded predicate after Condvar::wait returns** (typestate; candidate).

APIs: `std::sync::Condvar::{wait,wait_timeout,wait_while,wait_timeout_while}`, `std::sync::{Mutex,MutexGuard}`.

When code waits because a mutex-protected predicate is false and then consumes state as though the predicate became true, the same predicate must be checked again after every wait return while holding the reacquired guard. Condvar::wait can return spuriously; another waiter can also consume a condition before this thread reacquires the mutex. wait_while and wait_timeout_while repeat the predicate check. This is not a finding for notification waits whose continuation safely handles a false predicate.

Positive fixture sketch:

```text
let mut g = lock.lock().unwrap();
if g.queue.is_empty() { g = cv.wait(g).unwrap(); }
let item = g.queue.pop().unwrap(); // may be empty after wake
```

Near-miss fixture sketch:

```text
let mut g = lock.lock().unwrap();
while g.queue.is_empty() { g = cv.wait(g).unwrap(); }
let item = g.queue.pop().unwrap();
// Condvar::wait_while(g, |state| state.queue.is_empty()) is another guarded form.
```

Required proof: Prove exact Condvar and MutexGuard identities; bind the guard returned by wait; identify the same predicate before waiting and the dependent operation after reacquisition; model loop guards, poisoning exits, and relevant branches.

Stop gate: Stop if the mutex/predicate relationship or post-wake control dependence is unknown. Do not flag every wait call or replace missing Rust guard facts with syntax-only guesses; report incomplete until predicate and guard flow are supported.

Ownership: A distinct predicate/wakeup protocol, separate from generic resource lifecycle and API-name bans. The candidate requires guard and control-flow evidence before any policy claim.

Sources: [Rust 1.98.1 Condvar](https://doc.rust-lang.org/std/sync/struct.Condvar.html).

## rust-bufwriter-drop-hidden-flush-error

**Do not report successful output when BufWriter drop hides a pending flush failure** (typestate; candidate).

APIs: `std::io::BufWriter::{with_capacity,write,write_all,flush,into_inner,into_parts}`, `std::ops::Drop::drop`.

Only for an application-declared output boundary where success promises delivery, report a BufWriter that still has pending bytes when control returns success without a checked completion transition: Drop attempts to flush but ignores any error. A successful checked flush or checked into_inner discharges the pending-output state. into_parts intentionally returns unwritten bytes and is a near miss when that data is retained or retried. This does not imply durable storage; File::sync_all is a separate contract. For a generic underlying buffered writer, into_inner only discharges this BufWriter layer; require the separately declared downstream completion contract. Empty buffers and successful prior flush with no later writes are near misses.

Positive fixture sketch:

```text
fn publish(file: std::fs::File) -> std::io::Result<()> {
    let mut out = std::io::BufWriter::with_capacity(128, file);
    out.write_all(b"record")?;
    Ok(()) // declared publication succeeded; drop may hide a failed flush
}
```

Near-miss fixture sketch:

```text
out.write_all(b"record")?;
out.flush()?; // propagate delivery failure before reporting success
Ok(())
// Checked into_inner is another completion path; into_parts is safe when the returned bytes are handled.
```

Required proof: Resolve the exact BufWriter instance and underlying declared output sink; prove non-empty buffered data at the completion boundary; bind successful write, flush and into_inner outcomes; know the application-declared success/publication boundary and ownership at drop.

Stop gate: Do not report a drop by itself, best-effort output, writers transferred to a caller, or a buffer whose pending state is unknown. Route an explicitly discarded flush/into_inner Result to ignored-result coverage; do not infer durability from flush success.

Ownership: This is the hidden I/O error from Drop at a declared output boundary, not generic unclosed-resource reporting or an explicitly discarded Result. Require an application completion contract before qualifying it.

Sources: [Rust 1.98.1 BufWriter](https://doc.rust-lang.org/std/io/struct.BufWriter.html).

## rust-unix-pre-exec-callback-safety

**Audit operations in Unix CommandExt::pre_exec callbacks** (execution-context safety precondition; deferred-proof-heavy).

APIs: `std::os::unix::process::CommandExt::pre_exec`, `std::process::Command::{spawn,status,output}`, `std::env::{var,var_os}`, `std::sync::Mutex::lock`.

A concern requires the exact pre_exec closure to contain or reach an operation that is not safe in the post-fork child and the same Command to be executed by spawn, status or output on Unix. Registration alone is not a finding. CommandExt::exec does not fork and is outside this contract.

Positive fixture sketch:

```text
use std::os::unix::process::CommandExt;
let mut cmd = std::process::Command::new("helper");
unsafe { cmd.pre_exec(|| { let _ = std::env::var("MODE"); Ok(()) }); }
let _child = cmd.spawn()?;
```

Near-miss fixture sketch:

```text
use std::os::unix::process::CommandExt;
let mut cmd = std::process::Command::new("helper");
unsafe { cmd.pre_exec(|| Ok(())); }
let _child = cmd.spawn()?;
```

Required proof: Prove Unix target, callback identity and body, same Command reaching spawn/status/output, and direct or transitive operation effects against a pinned platform's async-signal-safe contract. Treat multiple registered closures and early error returns accurately.

Stop gate: Defer until closure capture, helper calls, macros, platform function allowlists and post-fork execution are modeled. Do not flag every pre_exec registration; exclude CommandExt::exec because it does not fork.

Ownership: A post-fork callback contract distinct from child reaping and shell syntax. Keep Unix scope and callback execution separate from ordinary Command construction.

Sources: [Rust 1.98.1 Unix CommandExt](https://doc.rust-lang.org/std/os/unix/process/trait.CommandExt.html), [Rust 1.98.1 Command](https://doc.rust-lang.org/std/process/struct.Command.html).

## rust-process-environment-mutation-thread-state

**Process environment mutation has a global concurrency precondition on non-Windows targets** (concurrency safety precondition; deferred-proof-heavy).

APIs: `std::env::{set_var,remove_var,var,var_os}`, `std::thread::{spawn,Builder::spawn,JoinHandle::join}`.

On Windows the documented mutation is sound in multithreaded programs; on non-Windows, soundness requires no other thread concurrently accessing the process environment through functions or global variables outside std::env. A thread merely existing is not enough to prove a violation, while a complete proof must account for opaque standard-library and C-library readers. This remains a platform-wide concurrency precondition, not a taint rule. The exact documented prohibition concerns concurrent access through functions or global variables outside std::env. Do not treat std::env::var_os on another thread alone as a violation witness.

Positive fixture sketch:

```text
On a pinned non-Windows target, a live foreign/native helper thread is proven to read the process environment outside the synchronization used by std::env while the calling thread executes unsafe std::env::set_var. Require a witness of overlapping access; two calls through std::env alone do not establish the documented foreign-reader violation.
```

Near-miss fixture sketch:

```text
The mutation occurs before any other thread starts on a non-Windows target, or occurs on Windows under the documented platform guarantee.
```

Required proof: Pin target OS and Rust edition; establish concurrent read/write overlap across threads and environment-access effects, including relevant standard-library, native-library and global-variable paths.

Stop gate: Defer unless a sound closed-world concurrency and environment-reader proof exists. The 2024 unsafe marker is not itself evidence of misuse, and absence of a visible reader is not proof of safety.

Ownership: No blanket API prohibition proposed. This is a process-global concurrency precondition whose hidden readers make ordinary call-site matching unsound.

Sources: [Rust 1.98.1 std::env::set_var safety](https://doc.rust-lang.org/std/env/fn.set_var.html), [Rust 2024 newly unsafe functions](https://doc.rust-lang.org/stable/edition-guide/rust-2024/newly-unsafe-functions.html).

## ruby-net-http-active-peer-verification-disabled

**Active HTTPS Net::HTTP clients can disable peer verification** (typestate; candidate).

APIs: `Net::HTTP.start(address, use_ssl: true, verify_mode: OpenSSL::SSL::VERIFY_NONE)`, `Net::HTTP#use_ssl=`, `Net::HTTP#verify_mode=`, `Net::HTTP#request`, `Net::HTTP.get_response`, `Net::HTTP#get`.

Scope this hypothesis to CRuby 3.4.0 with the shipped default gem net-http 0.6.0 and OpenSSL bindings resolved by that exact runtime. Report only when the same Net::HTTP instance uses TLS, its effective verify_mode is VERIFY_NONE at connection setup, and an HTTPS request reaches the active session. VERIFY_PEER is a near miss. A custom verification callback or a later configuration override is unresolved unless its effective behavior is proven.

Positive fixture sketch:

```text
http = Net::HTTP.new(host, 443); http.use_ssl = true; http.verify_mode = OpenSSL::SSL::VERIFY_NONE; http.start { |active| active.get('/health') }
```

Near-miss fixture sketch:

```text
Net::HTTP.start(host, use_ssl: true, verify_mode: OpenSSL::SSL::VERIFY_PEER) { |http| http.get('/health') }; also treat an unused configured client as a near miss.
```

Required proof: Resolve exact Net::HTTP object and method identities; track use_ssl and verify_mode writes into the same object through start/request; distinguish construction from an executed TLS session; model effective option defaults and overrides; pin Ruby and default-gem versions.

Stop gate: Stop if configuration writes cannot be associated with the active client/session, if verification callbacks or overrides have unresolved effects, or if request execution cannot be shown. Do not infer disabled verification from HTTPS use, a nil field, or an unqualified method name.

Ownership: Existing runtime network-effect models do not establish this verification protocol. Keep standard-library Net::HTTP acceptance separate from third-party client verification work, and recheck adjacent verification ownership before creating an issue.

Sources: [Net::HTTP Ruby 3.4 API and implementation](https://docs.ruby-lang.org/en/3.4/Net/HTTP.html), [Ruby 3.4 default gem versions](https://docs.ruby-lang.org/en/3.4/NEWS_md.html), [OpenSSL SSLContext verification modes](https://docs.ruby-lang.org/en/3.4/OpenSSL/SSL/SSLContext.html).

## ruby-open3-popen3-paired-pipe-draining

**Open3.popen3 can deadlock when stdout and stderr are drained sequentially** (typestate; deferred-proof-heavy).

APIs: `Open3.popen3(command, *args)`, `Open3.capture3(command, *args)`.

Scope to Ruby 3.4.0 with the exact loaded Open3 implementation pinned. A possible finding requires proof that the child writes enough bytes to one returned pipe to fill its effective OS buffer before it exits or writes the other stream, while the parent waits for the other stream to reach EOF before draining the first. The guarantee is execution and environment dependent; sequential reads alone do not prove a deadlock.

Positive fixture sketch:

```text
Open3.popen3('ruby', '-e', "STDERR.write('x' * 1_000_000); STDOUT.write('done')") do |_stdin, stdout, stderr, _wait_thr|
  stdout.read  # waits for EOF while the child may be blocked on a full stderr pipe
  stderr.read
end
```

Near-miss fixture sketch:

```text
Open3.capture3('ruby', '-e', "STDERR.write('x' * 1_000_000); STDOUT.write('done')") drains stdout and stderr concurrently in its implementation and returns both outputs with process status.
```

Required proof: Prove exact Open3.popen3 result-to-stream identity, child write volume/order and parent blocking read order; pin OS/runtime and pipe behavior for the fixture; distinguish capture3's concurrent readers and bounded output from the raw returned pipes.

Stop gate: Defer if static evidence cannot prove the child can exceed the relevant pipe capacity before the parent drains that stream, or if threads, helpers, callbacks, or alternate reads change the order. Do not report from a lexical stdout.read followed by stderr.read pattern alone.

Ownership: No Ruby public policy or semantic model found for this paired-stream protocol. The contract is distinct from the open Ruby lifecycle work; retain it as deferred until child output volume and blocking order can be proved.

Sources: [Open3 Ruby 3.4 API and pipe deadlock guidance](https://docs.ruby-lang.org/en/3.4/Open3.html), [Process.detach independently reaps children](https://docs.ruby-lang.org/en/3.4/Process.html), [CRuby v3_4_0 Open3 implementation and version-pinned behavior](https://raw.githubusercontent.com/ruby/ruby/v3_4_0/lib/open3.rb), [Ruby v3_4_0 shipped Open3 version](https://github.com/ruby/ruby/blob/v3_4_0/lib/open3/version.rb).

## ruby-open3-popen3-owned-pipe-closure

**Open3.popen3 non-block callers own the returned pipe cleanup** (typestate; existing-owner).

APIs: `Open3.popen3(command, *args)`, `IO#close`, `Process::Waiter#value (status retrieval, not required for reaping)`.

Scope to CRuby 3.4.0 with the exact loaded Open3 implementation pinned. In non-block form, each returned pipe owned by the caller should be closed unless ownership is explicitly transferred. The block form closes the streams and joins the wait thread. Open3's wait thread is established via Process.detach, so wait_thr.value is status retrieval rather than mandatory reaping.

Positive fixture sketch:

```text
stdin, stdout, stderr, _wait_thr = Open3.popen3('worker'); consume(stdout); return # stdin/stdout/stderr are left open on an early exit
```

Near-miss fixture sketch:

```text
Open3.popen3('worker') { |stdin, stdout, stderr, _wait_thr| consume(stdout) } # block cleanup closes streams and joins wait thread; explicit ensure closure also discharges caller-owned streams
```

Required proof: Prove exact Open3 result tuple and stream identities; model aliasing, ensure paths, exceptions, block form and explicit ownership transfer; treat wait_thr.value as status consumption rather than mandatory cleanup.

Stop gate: Route to existing Ruby lifecycle ownership and stop if returned stream identity, exit coverage, or transfer cannot be established. Avoid a new general process/resource leak engine or claims about zombies without direct evidence.

Ownership: Route returned-pipe acquisition and cleanup models to existing Ruby lifecycle qualification. Generic lifecycle discovery does not certify Ruby coverage or this tuple mapping. Process.detach reaps independently; wait thread value retrieves status.

Sources: [Open3 Ruby 3.4 API](https://docs.ruby-lang.org/en/3.4/Open3.html), [CRuby v3_4_0 Open3 implementation: Process.detach, stream close, wait_thread.join](https://raw.githubusercontent.com/ruby/ruby/v3_4_0/lib/open3.rb), [Process.detach independently reaps children](https://docs.ruby-lang.org/en/3.4/Process.html), [Ruby v3_4_0 shipped Open3 version](https://github.com/ruby/ruby/blob/v3_4_0/lib/open3/version.rb).

## ruby-tempfile-create-unlinked-owner

**Tempfile.create without a block leaves a persistent file to its caller** (typestate; existing-owner).

APIs: `Tempfile.create(basename, tmpdir, anonymous: false)`, `Tempfile.create(..., &block)`, `Tempfile.create(..., anonymous: true)`, `Tempfile.new`.

Scope to CRuby 3.4.0 with default gem tempfile 0.3.1. For the default non-block, anonymous:false form, the returned File and path remain caller-owned; close alone does not remove the path. A finding requires evidence the file is intended to be temporary and is no longer needed; an intentionally retained, renamed, or transferred artifact is not a cleanup violation. The block form closes and unlinks; anonymous:true removes before return. Platform-specific anonymous behavior stays version and OS scoped. The deletion obligation applies to a declared temporary-use scope when the file is no longer needed. A deliberately retained file, a successfully renamed output artifact, or transferred ownership is not a missing-unlink finding.

Positive fixture sketch:

```text
A declared temporary-use helper obtains f = Tempfile.create, writes a temporary payload, closes f, and exits with no transfer or rename. File.exist?(f.path) remains true; fixture must pin the intended deletion boundary.
```

Near-miss fixture sketch:

```text
Tempfile.create { |f| write_scratch_data(f) }; f = Tempfile.create; write_scratch_data(f); f.close; File.unlink(f.path); # or explicitly rename/transfer a file intended to persist A successfully renamed or deliberately retained output artifact has a different ownership contract.
```

Required proof: Resolve exact Tempfile.create identity, return value/path identity, anonymous flag, block form and file ownership; model close versus unlink separately, all exits, helper transfer and platform-specific behavior.

Stop gate: Route to Ruby lifecycle ownership; stop if the analyzer cannot track the returned File and path, distinguish close from unlink, model block/anonymous mode and explicit transfer, or prove the path was intended to be transient and no longer needed. Do not diagnose an intentionally retained/renamed artifact or rely on Tempfile.new finalizer timing as proof of prompt deletion.

Ownership: Route close/unlink and invocation-form models to existing Ruby lifecycle qualification. This is an API-specific extension, not a separate lifecycle engine or a production-support claim.

Sources: [Tempfile Ruby 3.4 API](https://docs.ruby-lang.org/en/3.4/Tempfile.html), [Ruby 3.4 Tempfile behavior and default gem versions](https://docs.ruby-lang.org/en/3.4/NEWS_md.html).

## ruby-kernel-open-pipe-command-taint

**A leading pipe makes Ruby 3.4 Kernel.open execute a command** (taint; existing-owner).

APIs: `Kernel.open(path, mode, perm, **opts)`, `File.open(path, mode, perm, **opts) (near-miss identity)`.

Scope only to CRuby 3.4.0 core Kernel.open where the executed string path begins with `|`; Ruby 4.0 is excluded because this mode is removed. Track attacker-controlled command text into the leading-pipe form and an actual call. Ordinary file paths and File.open do not satisfy this contract. For a shell-injection claim, also prove shell-language selection or metacharacter flow under the pinned command-invocation contract; pipe mode alone can invoke an executable directly. Unauthorized executable selection is a separate declared trust boundary.

Positive fixture sketch:

```text
Kernel.open('| /usr/bin/printf %s ' + params[:text]) { |pipe| pipe.read } # An attacker-controlled shell metacharacter in text selects shell interpretation under the pinned invocation rules.
```

Near-miss fixture sketch:

```text
File.open(params[:path]) { |file| file.read }; Kernel.open('report.txt') { |file| file.read } File.open is only a near miss for this command-execution contract; an attacker-selected filesystem path needs its own access policy.
```

Required proof: Resolve Kernel.open versus File.open identity, prove the leading pipe prefix and tainted command text reach an executed call; preserve Ruby version and deprecation/removal scope; distinguish shell command flow from an ordinary filesystem path.

Stop gate: Route to existing Ruby command-execution ownership and stop if call identity, leading-pipe semantics, taint flow, or runtime version is unresolved. Do not duplicate the existing Kernel.system sink family or claim Ruby 4 support.

Ownership: Existing Ruby command-execution discovery owns the shell/executable family. Review this deprecated core API mode under that owner rather than opening a duplicate discovery; no content migration is implied.

Sources: [Kernel Ruby 3.4 API and deprecation](https://docs.ruby-lang.org/en/3.4/Kernel.html), [Ruby 3.4 command injection guidance](https://docs.ruby-lang.org/en/3.4/command_injection_rdoc.html), [Kernel Ruby 4.0 API](https://docs.ruby-lang.org/ja/4.0/method/Kernel/m/open.html).

## ruby-psych-unsafe-load-untrusted-yaml

**Untrusted YAML reaches Psych.unsafe_load object construction** (taint; existing-catalog-routing).

APIs: `Psych.unsafe_load(yaml, **kwargs)`, `Psych.unsafe_load_file(filename, **kwargs)`, `Psych.safe_load(yaml, **kwargs) (near miss)`, `Psych.load(yaml, **kwargs) (safe-load-like in Psych 5.2.2)`.

Scope to CRuby 3.4.0 with shipped default gem psych 5.2.2. Report only when untrusted YAML bytes reach Psych.unsafe_load or unsafe_load_file and deserialization can instantiate an attacker-selected object graph. Do not infer danger from YAML.load in this version, from safe_load with its restricted classes, or from parsing a data-only primitive document. Other Psych versions require separate behavior evidence.

Positive fixture sketch:

```text
yaml = params[:document]; object = Psych.unsafe_load(yaml); authorize(object)
```

Near-miss fixture sketch:

```text
Psych.safe_load(params[:document]); Psych.load(params[:document]) under the pinned Psych 5.2.2 safe-load semantics; trusted fixed YAML fixture into unsafe_load is also a trust-boundary near miss.
```

Required proof: Resolve exact Psych method identity and loaded gem version; prove untrusted byte provenance into the unsafe entrypoint and object-result identity; distinguish safe_load, permitted classes, aliases and primitive-only data; inspect whether the object reaches a security-sensitive use without claiming every YAML document is code execution.

Stop gate: Route to the existing Ruby object-deserialization ownership and stop if the Psych version, exact unsafe method, taint boundary, or constructed-result use cannot be proven. Do not extend Ruby Marshal or blanket-flag YAML.load without version-specific behavior evidence.

Ownership: Ruby object-deserialization and YAML/Psych discovery already have catalog ownership. Review the exact unsafe_load methods and version-specific safe defaults under those routes; this is not a new discovery or a content migration.

Sources: [Psych Ruby 3.4 API](https://docs.ruby-lang.org/en/3.4/Psych.html), [Ruby 3.1 note on Psych 4 safe-load default](https://docs.ruby-lang.org/en/3.4/NEWS/NEWS-3_1_0_md.html), [Ruby 3.4 Psych default gem version](https://docs.ruby-lang.org/en/3.4/NEWS_md.html).

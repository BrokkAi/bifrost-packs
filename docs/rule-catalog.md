# Rule catalog

This catalog lists 108 unique rule IDs from 9 manifest packs.
Supported languages come only from each rule's manifest declaration. Language counts overlap when one policy declares multiple languages. These declarations do not establish tested, enabled, or qualified behavior.

| Policy | Stable ID | Manifest support / query scopes | Category | Severity |
| --- | --- | --- | --- | --- |
| [JPL-C Rule 09: avoid semaphores](../rules/bifrost.c-jpl/policies/avoid-semaphores.rqlp) | `bifrost.c-jpl.avoid-semaphores` | cpp | correctness | note |
| [JPL-C Rule 05: heap allocation outside initialization](../rules/bifrost.c-jpl/policies/heap-memory.rqlp) | `bifrost.c-jpl.heap-memory` | cpp | correctness | note |
| [JPL-C Rule 11: non-local jump](../rules/bifrost.c-jpl/policies/simple-control-flow-jmp.rqlp) | `bifrost.c-jpl.simple-control-flow-jmp` | cpp | correctness | warning |
| [JPL-C Rule 07: delay function](../rules/bifrost.c-jpl/policies/thread-safety.rqlp) | `bifrost.c-jpl.thread-safety` | cpp | correctness | warning |
| [C self-assignment](../rules/bifrost.code-smells/policies/c-self-assignment.rqlp) | `bifrost.correctness.c-self-assignment` | c | correctness | warning |
| [Fixed conditional outcome](../rules/bifrost.code-smells/policies/contradictory-condition.rqlp) | `bifrost.correctness.contradictory-condition` | c, cpp, csharp, go, java, javascript, kotlin, php, python, ruby, rust, scala, typescript | correctness | warning |
| [Database call inside a loop](../rules/bifrost.code-smells/policies/database-call-in-loop.rqlp) | `bifrost.performance.database-call-in-loop` | java, javascript, python, typescript | performance | note |
| [Discarded pure transformation result](../rules/bifrost.code-smells/policies/discarded-pure-result.rqlp) | `bifrost.correctness.discarded-pure-result` | c, cpp, csharp, java, javascript, php, python, ruby, rust, typescript | correctness | warning |
| [Dynamic code evaluation](../rules/bifrost.code-smells/policies/dynamic-evaluation.rqlp) | `bifrost.correctness.dynamic-evaluation` | javascript, python, typescript | correctness | warning |
| [Empty failure handler](../rules/bifrost.code-smells/policies/empty-failure-handler.rqlp) | `bifrost.correctness.empty-failure-handler` | cpp, csharp, go, java, javascript, kotlin, php, python, ruby, rust, scala, typescript | correctness | warning |
| [Expensive operation inside nested loops](../rules/bifrost.code-smells/policies/expensive-operation-in-nested-loop.rqlp) | `bifrost.performance.expensive-operation-in-nested-loop` | java, javascript, python, rust, typescript | performance | note |
| [Failed local swap](../rules/bifrost.code-smells/policies/failed-swap.rqlp) | `bifrost.correctness.failed-swap` | c, cpp, csharp, go, java, javascript, kotlin, php, python, ruby, rust, scala, typescript | correctness | warning |
| [File read inside a loop](../rules/bifrost.code-smells/policies/file-read-in-loop.rqlp) | `bifrost.performance.file-read-in-loop` | java, javascript, python, rust, typescript | performance | note |
| [Go data race](../rules/bifrost.code-smells/policies/go-data-race.rqlp) | `bifrost.correctness.go-data-race` | go | correctness | error |
| [Go nil dereference](../rules/bifrost.code-smells/policies/go-nil-dereference.rqlp) | `bifrost.correctness.go-nil-dereference` | go | correctness | error |
| [Go failure path returns the wrong error](../rules/bifrost.code-smells/policies/go-wrong-error-on-failure-path.rqlp) | `bifrost.correctness.go-wrong-error-on-failure-path` | go | correctness | error |
| [Identical conditional branches](../rules/bifrost.code-smells/policies/identical-conditional-branches.rqlp) | `bifrost.correctness.identical-conditional-branches` | c, cpp, csharp, go, java, javascript, kotlin, php, python, ruby, rust, scala, typescript | correctness | warning |
| [Ignored fallible result](../rules/bifrost.code-smells/policies/ignored-status-result.rqlp) | `bifrost.correctness.ignored-status-result` | c, cpp, csharp, go, java, php, python, ruby, rust | correctness | note |
| [Local self-assignment](../rules/bifrost.code-smells/policies/local-self-assignment.rqlp) | `bifrost.correctness.local-self-assignment` | c, cpp, csharp, go, java, javascript, kotlin, php, python, ruby, rust, scala, typescript | correctness | warning |
| [Loop body never repeats](../rules/bifrost.code-smells/policies/loop-body-never-repeats.rqlp) | `bifrost.correctness.loop-body-never-repeats` | c, cpp, csharp, go, java, javascript, kotlin, php, python, ruby, rust, scala, typescript | correctness | warning |
| [Loop-invariant receiver sorted on every iteration](../rules/bifrost.code-smells/policies/loop-invariant-sort.rqlp) | `bifrost.performance.loop-invariant-sort` | java, javascript, python, rust, typescript | performance | warning |
| [Network request inside a loop](../rules/bifrost.code-smells/policies/network-call-in-loop.rqlp) | `bifrost.performance.network-call-in-loop` | java, javascript, python, rust, typescript | performance | note |
| [Overwritten unread local value](../rules/bifrost.code-smells/policies/overwritten-unread-value.rqlp) | `bifrost.correctness.overwritten-unread-value` | c, cpp, csharp, go, java, javascript, kotlin, php, python, ruby, rust, scala, typescript | correctness | warning |
| [Parsing inside a loop](../rules/bifrost.code-smells/policies/parsing-in-loop.rqlp) | `bifrost.performance.parsing-in-loop` | java, javascript, python, rust, typescript | performance | note |
| [Python absent member](../rules/bifrost.code-smells/policies/python-absent-member.rqlp) | `bifrost.correctness.python-absent-member` | python | correctness | error |
| [Rayon parallelism inside a blocking lazy initializer](../rules/bifrost.code-smells/policies/rayon-in-blocking-lazy-init.rqlp) | `bifrost.correctness.rayon-in-blocking-lazy-init` | rust | correctness | warning |
| [Redundant Boolean return branches](../rules/bifrost.code-smells/policies/redundant-boolean-branches.rqlp) | `bifrost.correctness.redundant-boolean-branches` | c, cpp, csharp, go, java, javascript, kotlin, php, python, ruby, rust, scala, typescript | correctness | warning |
| [Regular-expression compilation inside a loop](../rules/bifrost.code-smells/policies/regex-compile-in-loop.rqlp) | `bifrost.performance.regex-compile-in-loop` | java, javascript, python, rust, typescript | performance | note |
| [Repeated stable branch condition](../rules/bifrost.code-smells/policies/repeated-branch-condition.rqlp) | `bifrost.correctness.repeated-branch-condition` | c, cpp, csharp, go, java, javascript, kotlin, php, python, ruby, rust, scala, typescript | correctness | warning |
| [Input-reachable Rust recursion to review](../rules/bifrost.code-smells/policies/rust-input-recursion-without-bound.rqlp) | `bifrost.correctness.rust-input-recursion-without-bound` | rust | correctness | note |
| [Serialization inside a loop](../rules/bifrost.code-smells/policies/serialization-in-loop.rqlp) | `bifrost.performance.serialization-in-loop` | java, javascript, python, rust, typescript | performance | note |
| [Sleep inside a collection-iteration loop](../rules/bifrost.code-smells/policies/sleep-in-loop.rqlp) | `bifrost.performance.sleep-in-loop` | java, python, rust | performance | note |
| [Subprocess creation inside a loop](../rules/bifrost.code-smells/policies/subprocess-in-loop.rqlp) | `bifrost.performance.subprocess-in-loop` | java, javascript, python, typescript | performance | note |
| [Unreachable statement](../rules/bifrost.code-smells/policies/unreachable-statement.rqlp) | `bifrost.correctness.unreachable-statement` | c, cpp, csharp, go, java, javascript, kotlin, php, python, ruby, rust, scala, typescript | correctness | warning |
| [Unsafe object deserialization](../rules/bifrost.code-smells/policies/unsafe-deserialization.rqlp) | `bifrost.correctness.unsafe-deserialization` | python | correctness | warning |
| [Resource lifecycle](../rules/bifrost.correctness/policies/resource-lifecycle.rqlp) | `bifrost.correctness.resource-lifecycle` | go, java, javascript, kotlin, php, python, rust, scala, typescript | correctness | error |
| [JSF AV Rule 108](../rules/bifrost.cpp-jsf/policies/av-rule-108.rqlp) | `bifrost.cpp-jsf.av-rule-108` | cpp | correctness | warning |
| [JSF AV Rule 110](../rules/bifrost.cpp-jsf/policies/av-rule-110.rqlp) | `bifrost.cpp-jsf.av-rule-110` | cpp | correctness | warning |
| [JSF AV Rule 13](../rules/bifrost.cpp-jsf/policies/av-rule-13.rqlp) | `bifrost.cpp-jsf.av-rule-13` | cpp | correctness | error |
| [JSF AV Rule 14](../rules/bifrost.cpp-jsf/policies/av-rule-14.rqlp) | `bifrost.cpp-jsf.av-rule-14` | cpp | correctness | error |
| [JSF AV Rule 149](../rules/bifrost.cpp-jsf/policies/av-rule-149.rqlp) | `bifrost.cpp-jsf.av-rule-149` | cpp | correctness | note |
| [JSF AV Rule 150](../rules/bifrost.cpp-jsf/policies/av-rule-150.rqlp) | `bifrost.cpp-jsf.av-rule-150` | cpp | correctness | note |
| [JSF AV Rule 159](../rules/bifrost.cpp-jsf/policies/av-rule-159.rqlp) | `bifrost.cpp-jsf.av-rule-159` | cpp | correctness | warning |
| [JSF AV Rule 19](../rules/bifrost.cpp-jsf/policies/av-rule-19.rqlp) | `bifrost.cpp-jsf.av-rule-19` | cpp | correctness | error |
| [JSF AV Rule 208](../rules/bifrost.cpp-jsf/policies/av-rule-208.rqlp) | `bifrost.cpp-jsf.av-rule-208` | cpp | correctness | note |
| [JSF AV Rule 209](../rules/bifrost.cpp-jsf/policies/av-rule-209.rqlp) | `bifrost.cpp-jsf.av-rule-209` | cpp | correctness | note |
| [JSF AV Rule 21](../rules/bifrost.cpp-jsf/policies/av-rule-21.rqlp) | `bifrost.cpp-jsf.av-rule-21` | cpp | correctness | error |
| [JSF AV Rule 22](../rules/bifrost.cpp-jsf/policies/av-rule-22.rqlp) | `bifrost.cpp-jsf.av-rule-22` | cpp | correctness | error |
| [JSF AV Rule 25](../rules/bifrost.cpp-jsf/policies/av-rule-25.rqlp) | `bifrost.cpp-jsf.av-rule-25` | cpp | correctness | error |
| [JSF AV Rule 53.1](../rules/bifrost.cpp-jsf/policies/av-rule-53-1.rqlp) | `bifrost.cpp-jsf.av-rule-53-1` | cpp | correctness | warning |
| [Power of 10 Rule 3: dynamic allocation outside initialization](../rules/bifrost.cpp-power-of-10/policies/dynamic-alloc-after-init.rqlp) | `bifrost.cpp-power-of-10.dynamic-alloc-after-init` | cpp | correctness | note |
| [Power of 10 Rule 1: non-local jump](../rules/bifrost.cpp-power-of-10/policies/use-of-jmp.rqlp) | `bifrost.cpp-power-of-10.use-of-jmp` | cpp | correctness | warning |
| [C# call to obsolete method](../rules/bifrost.csharp-codeql-quality/policies/call-to-obsolete-method.rqlp) | `bifrost.csharp-codeql-quality.call-to-obsolete-method` | csharp | quality | warning |
| [C# catch of all exceptions](../rules/bifrost.csharp-codeql-quality/policies/catch-of-all-exceptions.rqlp) | `bifrost.csharp-codeql-quality.catch-of-all-exceptions` | csharp | quality | warning |
| [C# empty branch and loop blocks](../rules/bifrost.csharp-codeql-quality/policies/empty-block.rqlp) | `bifrost.csharp-codeql-quality.empty-block` | csharp | correctness | warning |
| [C# nested loops reuse variable](../rules/bifrost.csharp-codeql-quality/policies/nested-loops-with-same-variable.rqlp) | `bifrost.csharp-codeql-quality.nested-loops-with-same-variable` | csharp | correctness | warning |
| [C# recursive Equals call](../rules/bifrost.csharp-codeql-quality/policies/recursive-equals-call.rqlp) | `bifrost.csharp-codeql-quality.recursive-equals-call` | csharp | correctness | warning |
| [C# static array](../rules/bifrost.csharp-codeql-quality/policies/static-array.rqlp) | `bifrost.csharp-codeql-quality.static-array` | csharp | quality | warning |
| [C# StringBuilder initialized with a character](../rules/bifrost.csharp-codeql-quality/policies/stringbuilder-initialized-with-character.rqlp) | `bifrost.csharp-codeql-quality.stringbuilder-initialized-with-character` | csharp | correctness | warning |
| [C# use number constant](../rules/bifrost.csharp-codeql-quality/policies/use-number-constant.rqlp) | `bifrost.csharp-codeql-quality.use-number-constant` | csharp | quality | warning |
| [C# useless if statement](../rules/bifrost.csharp-codeql-quality/policies/useless-if-statement.rqlp) | `bifrost.csharp-codeql-quality.useless-if-statement` | csharp | correctness | warning |
| [Selected C# boundary reaches no network effect](../rules/bifrost.effects/policies/csharp/selected-boundary-no-network-io.rqlp) | `bifrost.effects.csharp.selected-boundary-no-network-io` | csharp | effects | error |
| [Selected Go boundary reaches no network effect](../rules/bifrost.effects/policies/go/selected-boundary-no-network-io.rqlp) | `bifrost.effects.go.selected-boundary-no-network-io` | go | effects | error |
| [Selected Java boundary reaches no network effect](../rules/bifrost.effects/policies/java/selected-boundary-no-network-io.rqlp) | `bifrost.effects.java.selected-boundary-no-network-io` | java | effects | error |
| [Selected JavaScript boundary reaches no network effect](../rules/bifrost.effects/policies/javascript/selected-boundary-no-network-io.rqlp) | `bifrost.effects.javascript.selected-boundary-no-network-io` | javascript | effects | error |
| [Selected Kotlin boundary reaches no network effect](../rules/bifrost.effects/policies/kotlin/selected-boundary-no-network-io.rqlp) | `bifrost.effects.kotlin.selected-boundary-no-network-io` | kotlin | effects | error |
| [Selected Python boundary reaches no network effect](../rules/bifrost.effects/policies/python/selected-boundary-no-network-io.rqlp) | `bifrost.effects.python.selected-boundary-no-network-io` | python | effects | error |
| [Selected Ruby boundary reaches no network effect](../rules/bifrost.effects/policies/ruby/selected-boundary-no-network-io.rqlp) | `bifrost.effects.ruby.selected-boundary-no-network-io` | ruby | effects | error |
| [Selected Rust boundary reaches no network effect](../rules/bifrost.effects/policies/rust/selected-boundary-no-network-io.rqlp) | `bifrost.effects.rust.selected-boundary-no-network-io` | rust | effects | error |
| [Selected Scala boundary reaches no network effect](../rules/bifrost.effects/policies/scala/selected-boundary-no-network-io.rqlp) | `bifrost.effects.scala.selected-boundary-no-network-io` | scala | effects | error |
| [Selected TypeScript boundary reaches no network effect](../rules/bifrost.effects/policies/typescript/selected-boundary-no-network-io.rqlp) | `bifrost.effects.typescript.selected-boundary-no-network-io` | typescript | effects | error |
| [Constructor reaches standard library](../rules/bifrost.rust-codeql-quality/policies/rust/ctor-initialization.rqlp) | `bifrost.rust-codeql-quality.ctor-initialization` | rust | quality | error |
| [C# assembly path injection](../rules/bifrost.security/policies/csharp/assembly-path-injection.rqlp) | `bifrost.security.csharp.assembly-path-injection` | csharp | security | error |
| [C# code injection](../rules/bifrost.security/policies/csharp/code-injection.rqlp) | `bifrost.security.csharp.code-injection` | csharp | security | error |
| [C# LDAP injection](../rules/bifrost.security/policies/csharp/ldap-injection.rqlp) | `bifrost.security.csharp.ldap-injection` | csharp | security | error |
| [C# XML injection](../rules/bifrost.security/policies/csharp/xml-injection.rqlp) | `bifrost.security.csharp.xml-injection` | csharp | security | error |
| [C# XPath injection](../rules/bifrost.security/policies/csharp/xpath-injection.rqlp) | `bifrost.security.csharp.xpath-injection` | csharp | security | error |
| [Stored request value requires the configured validator (C)](../rules/bifrost.security/policies/declared-storage/c-store-requires-validation.rqlp) | `bifrost.security.c.store-requires-validation` | c | security | warning |
| [Stored request value reaches SQL (C)](../rules/bifrost.security/policies/declared-storage/c-stored-request-to-sql.rqlp) | `bifrost.security.c.stored-request-to-sql` | c | security | error |
| [Stored request value requires the configured validator (C++)](../rules/bifrost.security/policies/declared-storage/cpp-store-requires-validation.rqlp) | `bifrost.security.cpp.store-requires-validation` | cpp | security | warning |
| [Stored request value reaches SQL (C++)](../rules/bifrost.security/policies/declared-storage/cpp-stored-request-to-sql.rqlp) | `bifrost.security.cpp.stored-request-to-sql` | cpp | security | error |
| [Stored request value requires the configured validator (C#)](../rules/bifrost.security/policies/declared-storage/csharp-store-requires-validation.rqlp) | `bifrost.security.csharp.store-requires-validation` | csharp | security | warning |
| [Stored request value reaches SQL (C#)](../rules/bifrost.security/policies/declared-storage/csharp-stored-request-to-sql.rqlp) | `bifrost.security.csharp.stored-request-to-sql` | csharp | security | error |
| [Stored request value requires the configured validator (Go)](../rules/bifrost.security/policies/declared-storage/go-store-requires-validation.rqlp) | `bifrost.security.go.store-requires-validation` | go | security | warning |
| [Stored request value reaches SQL (Go)](../rules/bifrost.security/policies/declared-storage/go-stored-request-to-sql.rqlp) | `bifrost.security.go.stored-request-to-sql` | go | security | error |
| [Stored request value requires the configured validator (Java)](../rules/bifrost.security/policies/declared-storage/java-store-requires-validation.rqlp) | `bifrost.security.java.store-requires-validation` | java | security | warning |
| [Stored request value reaches JDBC SQL (Java)](../rules/bifrost.security/policies/declared-storage/java-stored-request-to-sql.rqlp) | `bifrost.security.java.stored-request-to-sql` | java | security | error |
| [Stored request value requires the configured validator (JavaScript)](../rules/bifrost.security/policies/declared-storage/javascript-store-requires-validation.rqlp) | `bifrost.security.javascript.store-requires-validation` | javascript | security | warning |
| [Stored request value reaches pg SQL (JavaScript)](../rules/bifrost.security/policies/declared-storage/javascript-stored-request-to-sql.rqlp) | `bifrost.security.javascript.stored-request-to-sql` | javascript | security | error |
| [Stored request value requires the configured validator (Kotlin)](../rules/bifrost.security/policies/declared-storage/kotlin-store-requires-validation.rqlp) | `bifrost.security.kotlin.store-requires-validation` | kotlin | security | warning |
| [Stored request value reaches JDBC SQL (Kotlin)](../rules/bifrost.security/policies/declared-storage/kotlin-stored-request-to-sql.rqlp) | `bifrost.security.kotlin.stored-request-to-sql` | kotlin | security | error |
| [Stored request value requires the configured validator (PHP)](../rules/bifrost.security/policies/declared-storage/php-store-requires-validation.rqlp) | `bifrost.security.php.store-requires-validation` | php | security | warning |
| [Stored request value reaches SQL (PHP)](../rules/bifrost.security/policies/declared-storage/php-stored-request-to-sql.rqlp) | `bifrost.security.php.stored-request-to-sql` | php | security | error |
| [Stored request value requires the configured validator (Python)](../rules/bifrost.security/policies/declared-storage/python-store-requires-validation.rqlp) | `bifrost.security.python.store-requires-validation` | python | security | warning |
| [Stored request value reaches SQLite SQL (Python)](../rules/bifrost.security/policies/declared-storage/python-stored-request-to-sql.rqlp) | `bifrost.security.python.stored-request-to-sql` | python | security | error |
| [Stored request value requires the configured validator (Ruby)](../rules/bifrost.security/policies/declared-storage/ruby-store-requires-validation.rqlp) | `bifrost.security.ruby.store-requires-validation` | ruby | security | warning |
| [Stored request value reaches SQL (Ruby)](../rules/bifrost.security/policies/declared-storage/ruby-stored-request-to-sql.rqlp) | `bifrost.security.ruby.stored-request-to-sql` | ruby | security | error |
| [Stored request value requires the configured validator (Rust)](../rules/bifrost.security/policies/declared-storage/rust-store-requires-validation.rqlp) | `bifrost.security.rust.store-requires-validation` | rust | security | warning |
| [Stored request value reaches SQL (Rust)](../rules/bifrost.security/policies/declared-storage/rust-stored-request-to-sql.rqlp) | `bifrost.security.rust.stored-request-to-sql` | rust | security | error |
| [Stored request value requires the configured validator (Scala)](../rules/bifrost.security/policies/declared-storage/scala-store-requires-validation.rqlp) | `bifrost.security.scala.store-requires-validation` | scala | security | warning |
| [Stored request value reaches JDBC SQL (Scala)](../rules/bifrost.security/policies/declared-storage/scala-stored-request-to-sql.rqlp) | `bifrost.security.scala.stored-request-to-sql` | scala | security | error |
| [Stored request value requires the configured validator (TypeScript)](../rules/bifrost.security/policies/declared-storage/typescript-store-requires-validation.rqlp) | `bifrost.security.typescript.store-requires-validation` | typescript | security | warning |
| [Stored request value reaches pg SQL (TypeScript)](../rules/bifrost.security/policies/declared-storage/typescript-stored-request-to-sql.rqlp) | `bifrost.security.typescript.stored-request-to-sql` | typescript | security | error |
| [Servlet parameter reaches JDBC SQL](../rules/bifrost.security/policies/jvm/servlet-parameter-to-jdbc.rqlp) | `bifrost.security.java.servlet-parameter-to-jdbc` | java | security | error |
| [Environment variable reaches Runtime.exec](../rules/bifrost.security/policies/jvm/system-getenv-to-runtime-exec.rqlp) | `bifrost.security.java.system-getenv-to-runtime-exec` | java | security | error |
| [Process input reaches os.system](../rules/bifrost.security/policies/python/process-input-to-os-system.rqlp) | `bifrost.security.python.process-input-to-os-system` | python | security | error |
| [Non-HTTPS URL literal](../rules/bifrost.security/policies/rust/non-https-url.rqlp) | `bifrost.security.rust.non-https-url` | rust | security | warning |
| [Process input reaches SQL text](../rules/bifrost.security/policies/rust/sql-injection.rqlp) | `bifrost.security.rust.sql-injection` | rust | security | error |

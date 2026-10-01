# Joern QueryDB catalog inventory for issue #24
## Scope and replay
This is a source-and-test inventory of Joern QueryDB at upstream `joernio/joern` commit
`af6f9573359ad26c418cbd31ab2ccc8dc32c1019` (the checkout used was `/private/tmp/issue24-joern-src`;
detached `HEAD`). Replay by checking out that exact revision, then listing
`querydb/src/main/scala/io/joern/scanners/**/*.scala` and
`querydb/src/test/scala/io/joern/scanners/**/*.scala`; the selected-file SHA-256 values below can be
recomputed with `shasum -a 256 <path>` from the checkout root.
The QueryDB README says scanner bundles under `io.joern.scanners` are discovered at runtime, each
query is an `@q` member of a `QueryBundle`, and the tests/examples specify intended query behavior.
Test behavior below is read from source examples and assertions; **no Joern tests were run for this
inventory**. These queries are external leads only: their names, scores, and expected outputs do not
establish Bifrost rule eligibility, completeness, precision, or semantic equivalence.
## Catalog by language and scope
Paths here are relative to `querydb/src/main/scala/io/joern/scanners/` (source) and
`querydb/src/test/scala/io/joern/scanners/` (tests). “No direct test” means no matching behavioral
test class was present in this pinned checkout; it does not mean the query is proven untested in
every build path.
### C / source CPG
- `c/CopyLoops.scala` → `c/CopyLoopTests.scala`
- `c/CredentialDrop.scala` → `c/CredentialDropTests.scala`
- `c/DangerousFunctions.scala` → `c/DangerousFunctionsTests.scala`
- `c/FileOpRace.scala` → `c/FileOpRaceTests.scala`
- `c/HeapBasedOverflow.scala` → `c/HeapBasedOverflowTests.scala`
- `c/IntegerTruncations.scala` → `c/IntegerTruncationsTests.scala`
- `c/Metrics.scala` → `c/MetricsTests.scala`
- `c/MissingLengthCheck.scala` → no direct test found
- `c/NullTermination.scala` → `c/NullTerminationTests.scala`
- `c/RetvalChecks.scala` → `c/RetvalChecksTests.scala`
- `c/SignedLeftShift.scala` → `c/SignedLeftShiftTests.scala`
- `c/SocketApi.scala` → `c/SocketApiTests.scala`
- `c/UseAfterFree.scala` → `c/UseAfterFreeTests.scala`, `c/UseAfterFreeReturnTests.scala`, and
  `c/UseAfterFreePostUsage.scala` (three query methods)
### Ghidra / binary CPG
- `ghidra/DangerousFunctions.scala` → `ghidra/DangerousFunctionsTests.scala`
- `ghidra/UserInputIntoDangerousFunctions.scala` →
  `ghidra/UserInputIntoDangerousFunctionsTests.scala`
Tests use checked-in binary fixtures under `querydb/src/test/resources/testbinaries/`; this is
binary-analysis scope, not a source-C scanner.
### Java / source CPG
- `java/CertificateChecks.scala` → no direct test found
- `java/CrossSiteScripting.scala` → no direct test found
- `java/CryptographyMisuse.scala` → `java/CryptographyMisuseTests.scala`
- `java/DangerousFunctions.scala` → no direct test found
- `java/SQLInjection.scala` → no direct test found
- `java/SpringExpressionLanguageInjection.scala` → no direct test found
`JavaQueryTestSuite` exists, but no `CertificateChecksTests` or other Java suite instantiates these
five unpaired bundles here. `AllBundlesTestSuite` checks query-name uniqueness, not query behavior.
### Kotlin / source CPG
- `kotlin/NetworkCommunication.scala` → `kotlin/NetworkCommunicationTests.scala`
- `kotlin/NetworkProtocols.scala` → `kotlin/NetworkProtocolsTests.scala`
- `kotlin/PathTraversals.scala` → `kotlin/PathTraversalsTests.scala`
### PHP / source CPG
- `php/MagicHash.scala` → `php/MagicHashTests.scala`
- `php/PhpJoern.scala` → `php/PHPJoernTests.scala`
- `php/SQLInjection.scala` → no direct test found
- `php/ShellExec.scala` → no direct test found
- `php/TwigTemplateInjection.scala` → no direct test found
### Android / Java, Kotlin, manifest and framework scope
- `android/ArbitraryFileWrites.scala` → `android/ArbitraryFileWritesJavaTests.scala` and
  `android/ArbitraryFileWritesKotlinTests.scala`
- `android/ExternalStorage.scala` → `android/ExternalStorageTests.scala`
- `android/Intents.scala` → `android/IntentsTests.scala`
- `android/JavaScriptInterface.scala` → `android/JavaScriptInterfaceTests.scala`
- `android/Misconfigurations.scala` → `android/MisconfigurationsTests.scala`
- `android/RootDetection.scala` → `android/RootDetectionTests.scala`
- `android/UnprotectedAppParts.scala` → `android/UnprotectedAppPartsTests.scala`
- `android/UnsafeReflection.scala` → `android/UnsafeReflectionTests.scala`
These use the Android test suite with Kotlin CPG/default jars and include framework/configuration
scope. `c/QueryLangExtensions.scala` is a helper, not a `QueryBundle`; the test-only
`c/QueryWithReachableBy.scala` is not a query-source pair. The source/test pairing above is based on
the pinned tree’s actual filenames and suite constructors, not a claim that every listed query is
otherwise covered.
## Issue #24 shortlist: selectors and test evidence
### C credential-drop checks
Source `querydb/src/main/scala/io/joern/scanners/c/CredentialDrop.scala` defines
`setuid-without-setgid` and `setgid-without-setgroups` (both author metadata `Crew.malte` /
`@maltek`, `setxid` and `default` tags). With `NoResolve`, the first uses case-insensitive
method-name regex `set(res|re|e|)uid`, traverses incoming calls, and keeps calls not dominated by a
`set(res|re|e|)?gid` call. The second analogously selects `set(res|re|e|)gid` not dominated by
`setgroups`. These are name/CFG-dominance checks, not resolution-proven identity or a model of
privilege transitions across callees/paths.
`CredentialDropTests.scala` expects `bad1` and `bad3` for user changes, and `bad2` for group
changes; the embedded `good` case calls `setgroups`, then `setresgid`, then `setresuid`. The test
compares containing method names of matched call evidence.
### C file-operation path race
Source `FileOpRace.scala` declares exact call-name selectors and path argument indexes: index 1 for
`access`, `chdir`, `chmod`, `chown`, `creat`, `fopen`, `lchown`, `lstat`, `mkdir`, `mkfifo`,
`mknod`, `open`, `readlink`, `rmdir`, `stat`, and `unlink`; index 2 for `faccessat`, `fchmodat`,
`fstatat`, `mkdirat`, `mkfifoat`, `mknodat`, `openat`, `readlinkat`, and `unlinkat`; indexes 2 and 4
for `linkat` and `renameat`; and indexes 1 and 2 for `link` and `rename`. It discards literal
arguments, examines other selected calls in the same method AST, and reports when selected argument
`.code` strings are equal. It does not establish alias identity, an exploitable scheduling
window/order, or filesystem semantics; text equality can miss aliases and can conflate distinct
expressions.
`FileOpRaceTests.scala` expects only `insecure_race` from `chmod(path, 0)` plus `rename(path, ...)`;
the handle-based `fopen`/`fchown(fileno(...))` example is the negative case. Query author metadata
is `@maltek`.
### C heap-based overflow
`HeapBasedOverflow.scala` (`@fabsx00`) selects `malloc` calls whose first argument is an arithmetic
expression, then `memcpy` calls where argument 1 is reachable from that allocation, the destination
is the assignment target, and `memcpy` argument 3 has different source text from `malloc` argument
1. It uses `NoSemantics` and `NoResolve`; this is not arithmetic range/size proof, and different
expressions are not necessarily unequal sizes. The in-source comment says it adapts an old Joern
query for VLC CVE-2014-9626.
`HeapBasedOverflowTests.scala` expects the evidence expression `memcpy(dst, src, len + 7)` for a
`malloc(len + 8)` example. The negative examples use a matching `len + 8` copy and a `some_size`
expression. These demonstrate source-text cases, not general heap-bound reasoning.
### C use-after-free bundle
`UseAfterFree.scala` contains three independently tested queries. `free-field-no-reassign`
(`@fabsx00`) examines `free` arguments that are field accesses rooted in a method parameter,
excludes selected whole-structure `free`/`memset`/`bzero` cases, and checks reachability to the
method return. `UseAfterFreeTests.scala` expects `bad` and excludes `good`, where the early-return
path clears the field to `NULL` before it is reassigned.
`free-returned-value` (`@maltek`) looks for pointer-like output parameters assigned a
local/identifier and an identifier it treats as freed on a dominating path.
`UseAfterFreeReturnTests.scala` expects only `bad`; the source’s own examples call `good1` and
`good2` safe, and explicitly label `bad_not_covered` as uncovered (freeing the output field itself).
`free-follows-value-reuse` (`@maltek`) looks for a one-argument method named like `(.*_)?free`, then
uses CFG post-dominance and identifier source text, with post-dominating assignments removed.
`UseAfterFreePostUsage.scala` expects both `bad` **and `false_positive`**; the query’s own examples
label a nested early return as `false_negative`. This fixture is direct evidence that the result is
a lead with known precision/coverage limits, not a general UAF detector.
### C dangerous-function and format checks
`DangerousFunctions.scala` has seven query methods. `gets`, `scanf`, `strcat|strncat`,
`strcpy|strncpy`, `strtok`, and `getwd` select calls via case-insensitive method-name regexes; those
checks do not inspect argument safety. `argvUsedInPrintf` selects `printf` when argument 1 is not a
literal and `sprintf|vsprintf` when argument 2 is not a literal. Thus the format query tests
“non-literal format position,” not attacker-controlled provenance. Query author metadata is
`@tuxology` for the first six methods and `@ursachec` for `getwd`.
`DangerousFunctionsTests.scala` expects containing methods `insecure_gets`; `insecure_printf` and
`insecure_sprintf`; `insecure_scanf`; both `insecure_strcat` and `insecure_strncat`; both
`insecure_strcpy` and `insecure_strncpy`; `insecure_strtok`; and `insecure_getwd`. It does not
include a `vsprintf` fixture. Call-name matching, including safe variants of the named functions, is
not a proof of vulnerability. Format/memory overlap belongs with issue #12’s owner; this inventory
does not define a duplicate rule batch.
### C `strncpy` null termination
`NullTermination.scala` (`@fabsx00`) selects `strncpy` calls whose destination is reachable from a
`malloc` size expression whose source text equals the copy count, then looks in that method for an
array-access assignment on that destination whose source is a literal matching `.*0.*`; it reports
when none is found. The check does not establish runtime lengths or path-sensitive termination, and
the literal test is textual. `NullTerminationTests.scala` expects method `bad` only; the examples
mark a `malloc(asize + 1)` buffer and an explicit `ptr[asize - 1] = '\0'` as safe.
### C unchecked return values
`RetvalChecks.scala` (`@fabsx00`) selects calls to case-insensitive method names `read|recv|malloc`,
then applies the helper in `c/QueryLangExtensions.scala`. That helper excludes a call if its source
text occurs in a control-structure condition, if the call’s assignment-target code intersects any
identifier/call code in a condition in the same method, or if the call is under a return. The
assignment check is by code/name sets, not dataflow identity or a condition-specific proof.
`RetvalChecksTests.scala` expects both `unchecked_read` **and `checks_something_else`**; in the
latter, `read` assigns `nbytes` but the condition checks `foo`. This is a concrete
false-positive-shaped expected result. Embedded examples also include a correctly checked
assignment, an immediate condition, and a direct return. Treat the selector as a lead, not a
checked-result contract.
### Java certificate validation
`java/CertificateChecks.scala` (`@maltek`) applies `nameExact` to the validator names and
`signatureExact` to the signature list separately; it does not constrain declaring type or preserve
name/signature pairs. The listed signatures are `HostnameVerifier.verify(String, SSLSession):
boolean` plus four three-argument `X509ExtendedTrustManager.checkClientTrusted` /
`checkServerTrusted` overloads taking `Socket` or `SSLEngine`. It skips a CFG prologue only when
nodes are identifiers referring to locals or assignments whose arguments satisfy the same predicate,
then accepts a literal `1` followed only by return nodes **or any `Return` node**. The
implementation does not inspect a return node’s value in that second case, and the signatures omit
the two-argument `X509TrustManager` overloads. Despite the description about a positive-only
validator, this selector is broader than that description.
No `CertificateChecksTests.scala` or other direct certificate behavioral test is present, and the
bundle contains no `CodeExamples` field. The catalog’s Java test harness is not itself evidence that
this query was exercised. TLS overlap (including Kotlin `NetworkCommunication`) is routed to issue
#15’s owner; do not create a duplicate TLS rule batch here.
## Attribution and license provenance
The pinned checkout’s repository-level `LICENSE` has SHA-256
`2e50a6169977b8c7bb3c3fb39e13b4502c0a5f00c79716647bee12731f50c4ce`. It contains Apache License 2.0
terms; its appendix boilerplate includes `Copyright 2020-2023 The Joern Project` and `Copyright 2019
ShiftLeft, Inc.`, followed by an MIT-license notice section for components bundled by Apache
TinkerPop. The selected Scala query and test files have no per-file copyright/SPDX header. The
query-level author attribution is the `Crew` metadata recorded above; do not substitute the
top-level commit author for those query authors. This checkout is shallow, so its path history does
not provide source-specific authorship beyond the pinned snapshot and explicit query metadata.
Android-specific/framework scope is listed for ownership visibility only and routes to premium/other
owners; it is outside this issue #24 C/Java shortlist. Store this document as research, not copied
query code or a qualified policy.
## SHA-256 manifest for selected issue #24 items
Hashes were computed from the pinned checkout with `shasum -a 256`. All paths below are relative to
that checkout root. The license hash is included for attribution/replay.
| Item | SHA-256 |
|---|---|
| `LICENSE` | `2e50a6169977b8c7bb3c3fb39e13b4502c0a5f00c79716647bee12731f50c4ce` |
| `querydb/README.md` | `886fd5a6216b1a9a72e15597b206adf639b1fabf53054448790f8cceb0530ea3` |
| `querydb/src/main/scala/io/joern/scanners/Crew.scala` | `a3bfe705298b110a210d485f20efa4a36f19de6b9cbcf3071f88379414cbd4b3` |
| `querydb/src/main/scala/io/joern/scanners/QueryTags.scala` | `60a1396196b5e4e9f2c6589f2913d266e4dd73d44f38fbdacac4dfbd2cb4638b` |
| `querydb/src/main/scala/io/joern/scanners/c/QueryLangExtensions.scala` | `ce459ada6a6b1a26f909d5a14a8f9310d5231acf95499771ea9733a72716fc37` |
| `querydb/src/test/scala/io/joern/suites/AllBundlesTestSuite.scala` | `1bbec7a776725b4eb0e228410fe95741e302bd8f4e338b2712dfbe4c62752654` |
| `querydb/src/test/scala/io/joern/suites/CQueryTestSuite.scala` | `828b1368d9686885bb6771305aa8740ce1b9c8fb4de05286c125b918ae35983c` |
| `querydb/src/test/scala/io/joern/suites/JavaQueryTestSuite.scala` | `4ff94171cebea61ca94525f87dd0fdb55840184f76e006dac8b5a3d30db93258` |
| `querydb/src/main/scala/io/joern/scanners/c/CredentialDrop.scala` | `5e299c7a346287598d89f49673c44e70049a2cd52aa175cd104d45b015b0b271` |
| `querydb/src/test/scala/io/joern/scanners/c/CredentialDropTests.scala` | `494a40717e2b5585f67695b5925b0d7c2f6c0b19ce57db5937acb1c872d28211` |
| `querydb/src/main/scala/io/joern/scanners/c/FileOpRace.scala` | `01225d0ebfa3cca99a1e420fcac2d2fc36765663f527e66ef6b2e47db2938b84` |
| `querydb/src/test/scala/io/joern/scanners/c/FileOpRaceTests.scala` | `7501ef04892a89a401a14bd8ac2a5861a28c187f92287a03b11803d1808cc2fb` |
| `querydb/src/main/scala/io/joern/scanners/c/HeapBasedOverflow.scala` | `bd9725084a88beb98e90eff7d18ffd6c39b6f168668c882dde74e979b1bd4504` |
| `querydb/src/test/scala/io/joern/scanners/c/HeapBasedOverflowTests.scala` | `5efe8e0580d291bdaa93282f9375d9fe087dd1a94f4afd0bcdbec68e5efe796e` |
| `querydb/src/main/scala/io/joern/scanners/c/UseAfterFree.scala` | `6e4577fcd662481554a290fc9cb9c2bc1f6be4915af9ff5bd7e35b14bc25e026` |
| `querydb/src/test/scala/io/joern/scanners/c/UseAfterFreeTests.scala` | `4bf76f0de102020034bbe09659daca9d84fe52e72371cbbabd36f6153e78f038` |
| `querydb/src/test/scala/io/joern/scanners/c/UseAfterFreeReturnTests.scala` | `df4ee0b7d5a02054061dd826d27adb4768d9771cfc129b45cb1f905de0be7fd9` |
| `querydb/src/test/scala/io/joern/scanners/c/UseAfterFreePostUsage.scala` | `e5c028f838f93284effb8e405e7ca1b958a5cb2d708cbdde9eb355455e84483a` |
| `querydb/src/main/scala/io/joern/scanners/c/DangerousFunctions.scala` | `e367df6417ed7bffd27540e156261ce2ce721022e381e8f758660961e8ff2640` |
| `querydb/src/test/scala/io/joern/scanners/c/DangerousFunctionsTests.scala` | `8e43f968765440351ac0a4c0df7d9710707c9a4fdd08b76ea7f4b35b563a5fd2` |
| `querydb/src/main/scala/io/joern/scanners/c/NullTermination.scala` | `145299acbaa3751b6b845e6a66b5c2b8ec433af95f68bfde1a8438a3b8c60acd` |
| `querydb/src/test/scala/io/joern/scanners/c/NullTerminationTests.scala` | `780e18adcbf0e1479827a0ed6dd87eff32007157fd0a5875863eb2254f0d04ee` |
| `querydb/src/main/scala/io/joern/scanners/c/RetvalChecks.scala` | `fd765289ee6f03810930f9f2f8519875ec605555e106f774dd115df9674d0e11` |
| `querydb/src/test/scala/io/joern/scanners/c/RetvalChecksTests.scala` | `74312ca015686159cce438a9a2ce7556e0dfdc0617fdd3ef8f995e28d9350043` |
| `querydb/src/main/scala/io/joern/scanners/java/CertificateChecks.scala` | `4cb7886d4a668667280661b29976ae67aa04c4b06bfd6756d5dce37c5b8601e9` |

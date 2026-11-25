# Java OSV data-flow leads on Bifrost 0.15.1

**Outcome: 1 of 10 leads ships, as an opt-in rule that is always
inconclusive on 0.15.1. 7 are blocked by the engine, and 2 are premium.** This
batch picked 10 new `[Java] CVE-` leads from the OSV Maven feed whose
theoretical policy is a taint or typestate policy. Eight model a JDK contract
(open placement). The CVE is in a Maven library, and the policy models the
version-independent JDK misuse behind it, as #192 did for gob. Two model a
Maven library's own contract (premium placement).

| Lead | Advisory | Policy | Outcome |
| --- | --- | --- | --- |
| [#300](https://github.com/BrokkAi/bifrost-packs/issues/300) | CVE-2022-46337 (Derby) | request input → raw `DirContext.search` filter (taint) | Blocked: [bifrost-dev#9998](https://github.com/BrokkAi/bifrost-dev/issues/9998) |
| [#301](https://github.com/BrokkAi/bifrost-packs/issues/301) | CVE-2026-41586 (fabric-sdk-java) | `readObject` before `setObjectInputFilter` (typestate) | **Implemented**: `bifrost.security.java.objectinputstream-read-without-filter`. Possible findings only: [#10001](https://github.com/BrokkAi/bifrost-dev/issues/10001), [#9431](https://github.com/BrokkAi/bifrost-dev/issues/9431) |
| [#302](https://github.com/BrokkAi/bifrost-packs/issues/302) | CVE-2026-40859 (Camel HTTP) | HTTP response body → `ObjectInputStream` (taint) | Blocked: #9998 |
| [#303](https://github.com/BrokkAi/bifrost-packs/issues/303) | CVE-2025-70952 (pf4j) | ZIP entry name → file write without containment (taint) | Blocked: #9998, [#10000](https://github.com/BrokkAi/bifrost-dev/issues/10000) |
| [#304](https://github.com/BrokkAi/bifrost-packs/issues/304) | CVE-2026-50632 (CXF) | untrusted name → `Context.lookup` (taint) | Blocked: #9998 |
| [#305](https://github.com/BrokkAi/bifrost-packs/issues/305) | CVE-2026-45367 (HAPI FHIR) | request input → `Pattern.compile` (taint) | Blocked: #9998 (sinks bind; source doesn't) |
| [#306](https://github.com/BrokkAi/bifrost-packs/issues/306) | CVE-2026-54082 (veraPDF) | default `DocumentBuilderFactory` → `parse` (typestate) | Blocked: #9998, #9431 |
| [#307](https://github.com/BrokkAi/bifrost-packs/issues/307) | CVE-2026-40047 (Camel Docling) | request input → `ProcessBuilder` argument list (taint) | Blocked: #9998, #10000 |
| [premium #469](https://github.com/BrokkAi/bifrost-premium-packs/issues/469) | CVE-2026-21452 (msgpack-core) | untrusted bytes → `MessageUnpacker` on affected versions | Premium, not implemented here. The version gate needs [bifrost-dev#9325](https://github.com/BrokkAi/bifrost-dev/issues/9325) |
| [premium #470](https://github.com/BrokkAi/bifrost-premium-packs/issues/470) | CVE-2026-28208 (junrar) | untrusted archive → `Junrar.extract` on affected versions | Premium, not implemented here (#9325) |

[`outcomes.json`](outcomes.json) records the engine identity, the input
hashes, the dispatch table and every policy run. The files under `probe/` are
research inputs, not registered pack content.

## Selection

Source: `https://osv-vulnerabilities.storage.googleapis.com/Maven/all.zip`,
downloaded on 2026-11-05. Advisories were filtered for JDK data-flow roots
(XML parsers, Java serialization, JNDI, archive entry names, `java.util.regex`,
`ProcessBuilder`, LDAP filters) and deduplicated against the 50 existing
`[Java] CVE-` titles in both repositories. The selection skipped
pure version-match or config-match advisories, and advisories about a
library's own internals that application code can't reach.

## Engine

Official `v0.15.1` release, the latest on 2026-11-05 (v0.15.2 was not out):
`bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`, archive SHA-256
`4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c` (matches the
release `.sha256`), binary SHA-256
`78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`, build
identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`. Host JDK Temurin 21.0.8.
Environment `BIFROST_OPEN_PACKS_DISABLE=1`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`,
`BIFROST_WORKSPACE_SEMANTIC_MODELS=on`, and a fresh `BIFROST_CACHE_DIR` per
run. The JDK members bind to the generated `bifrost.external.java` model built
from the host JDK. The `bifrost.jdk` pack from `packs/v0.10.0` is not needed
for that.

## Shared findings

1. **JDK call binding.** `probe/bind/Calls.java` makes every call these leads
   need. Constructors with a single same-arity overload, statics and `final`
   methods resolve (`resolved, exhaustive, 1`): `new ObjectInputStream(in)`,
   `ois.readObject()`, `setObjectInputFilter`, `Pattern.compile`,
   `Pattern.matches`, `System.getenv`, `new InitialContext()`,
   `DocumentBuilderFactory.newInstance()`. Every other instance call is
   `unproven, open`. That includes `DirContext.search`, `Context.lookup`,
   `URLConnection.getInputStream`, `ZipEntry.getName`, `Path.resolve`,
   `DocumentBuilder.parse` and `ProcessBuilder.start`. It also includes calls on
   the final classes `String` (`matches`) and `Pattern` (`matcher`). Filed as
   [bifrost-dev#9998](https://github.com/BrokkAi/bifrost-dev/issues/9998), which
   cites the closed #7473, #3811 and #2714.
2. **The shipped servlet-to-JDBC rule binds no source on 0.15.1.**
   `probe/servlet-jdbc-baseline` runs the unchanged
   `bifrost.security.java.servlet-parameter-to-jdbc` rule on a two-line
   positive. It runs with the four `framework-decls` models, a `pom.xml` that
   declares `javax.servlet-api` 4.0.1, and that jar in `~/.m2`. The result is
   inconclusive, 0 findings, `bound no source endpoint`. Every Java lead that
   starts at a request parameter is blocked by this (#9998).
3. **Overloaded constructors claim exhaustive coverage with no target.**
   `new File(dir, name)`, `new FileOutputStream(f)`, `new ProcessBuilder(list)`,
   `new XMLDecoder(in)` and `new Hashtable<>()` are `resolved, exhaustive, 0`.
   Filed as [bifrost-dev#10000](https://github.com/BrokkAi/bifrost-dev/issues/10000).
4. **JDK typestate stays possible.** The #301 typestate binds its subject and
   both events exactly. Its three findings are still `possible`
   (`typestate-external-call`), and the run is `inconclusive` with no
   diagnostic. Reviewed summaries for the three members change nothing.
   Filed as [bifrost-dev#10001](https://github.com/BrokkAi/bifrost-dev/issues/10001)
   (related: #9431).
5. **No Maven dependency evidence.** `(dependency-evidence :ecosystem maven)`
   and `:ecosystem jvm` return no rows. bifrost-dev#9325 is closed, but the
   gap reproduces on the release. A comment there asks whether the fix is in
   v0.15.2.
6. **A malformed workspace model fails silently.** An array type with a
   `nullable` key in a hand-authored `javax.naming` declaration turned every
   JDK binding, including `System.getenv`, into `unknown`, with no diagnostic.
   Filed as [bifrost-dev#10002](https://github.com/BrokkAi/bifrost-dev/issues/10002).
   Even with the type fixed, the hand-authored `DirContext.search`
   declaration didn't take over from the generated target. So no
   `javax.naming` model ships.

## The shipped rule

`rules/bifrost.security/policies/jvm/objectinputstream-read-without-filter.rqlp`
is opt-in. Its fixture is
`fixtures/policy/bifrost.security/java-objectinputstream-read-without-filter`,
and its README lists the cases and the per-JDK results. The selectors use the
generated member IDs. Those IDs are the same on Temurin 17.0.16 and 21.0.8. On
Temurin 25.0.1 the constructor gets 0 targets, and the run reports it. No
semantic model ships with the rule, because the summaries that were tried had
no effect.

## Reproduction

```sh
BIFROST=/path/to/bifrost-v0.15.1/bifrost python3 -I research/osv-dataflow-2026-11/java/probe/run.py
```

`run.py` copies each probe root, the four `semantic-packs/framework-decls`
models and the shipped fixture into a temporary directory. It checks the build
identity and prints the dispatch table and every policy run as JSON. It needs
the `javax.servlet-api` 4.0.1 jar in `~/.m2` to match the servlet results.

## Promotion criteria

- #300, #304, #305, #307: rerun once #9998 lands. The servlet-to-JDBC
  baseline must bind its source first. #305's sinks already bind, so it should
  qualify first.
- #302, #303: also need #9998 for `URLConnection`, `ZipEntry` and `Path`
  members. #303 and #307 need #10000 for the constructor overloads.
- #301: becomes definite once #10001 and #9431 land. Rerun the fixture and
  update its expected certainty.
- #306: needs #9998, then a typestate that hands the factory state to the
  builder and a guard on the literal feature name.
- Premium #469, #470: need Maven dependency evidence (#9325) and library call
  targets. They belong in bifrost-premium-packs.

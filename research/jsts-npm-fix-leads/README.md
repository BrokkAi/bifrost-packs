# JavaScript and TypeScript npm fix-history leads

Rule leads mined on 2026-11-25 from public fix commits and GitHub security
advisories of expressjs/express and its dependencies (pillarjs/send,
expressjs/serve-static, expressjs/body-parser, pillarjs/path-to-regexp,
jshttp/cookie), axios/axios, node-fetch/node-fetch, auth0/node-jsonwebtoken,
websockets/ws, expressjs/multer, lodash/lodash and mde/ejs. The leads also use
follow-redirects/follow-redirects, isaacs/node-tar, minimistjs/minimist,
handlebars-lang/handlebars.js, Leonidas-from-XIV/node-xml2js, panva/jose and
nodejs/undici. The window is roughly 2019 to November 2026, plus two 2018
lodash merge fixes that the later CVE-2019-10744 fix builds on. Each lead is
filed as one issue, except the zlib lead, which is the version-independent part
of the existing #291 and is listed under it. The issues hold the theoretical policy, the qualification
cases and the required capabilities. They are research candidates, not rules,
and nothing here was run through an analyzer.

Kinds: **(a)** a pattern inside the library that a general JavaScript or
TypeScript rule should catch anywhere; **(b)** a misuse of the library by its
callers, which needs a semantic model of that library. No third-party npm
semantic model exists in this repository yet. Each (b) lead would add the first
model for its package, and whether that model is open or premium is an
open-core classification decision (see #393).

Pure protocol and parser bugs were left out because no static rule could
plausibly express them. Examples are undici request and response smuggling
(CVE-2026-1525) and its CRLF and header-parsing fixes, ws frame-length handling
and its uninitialized `close()` buffer (CVE-2026-45736), qs `stringify` crashes,
node-tar PAX and GNU header arithmetic (CVE-2026-53655, CVE-2026-59874), and
multer's busboy error and cleanup races. Two families were left out on purpose.
The 2026 axios prototype-pollution "gadget" advisories (for example
CVE-2026-42033 and CVE-2026-101905) need a polluted `Object.prototype` as a
precondition, and no static source can express that. Cache-poisoning and
cross-user disclosure in undici's cache interceptor (for example CVE-2026-85152)
depend on shared-cache semantics. Advisories with no public fix commit were also
dropped, among them express CVE-2024-9266 and CVE-2024-10491 and path-to-regexp
CVE-2026-4867 and CVE-2026-4923.

The Node core packs ship six JavaScript taint and boundary rules (five
`process-input-to-*` rules and `selected-boundary-no-network-io`). There are
also the declared-storage rules and the lexical
`bifrost.correctness.dynamic-evaluation`. TypeScript has only the declared-storage
and boundary rules. All sources are keyed `process.argv` reads. No reviewed
model exists for an HTTP request (`req`), for `JSON.parse`, for the `RegExp` or
`Function` constructors, or for `zlib`.

| Issue | Package | Fix commit(s) | Kind | Policy | Existing rule |
| --- | --- | --- | --- | --- | --- |
| #465 | lodash | [3469357c](https://github.com/lodash/lodash/commit/3469357cff396a26c363f8c1b5a91dde28ba4b1c), [879aaa93](https://github.com/lodash/lodash/commit/879aaa93132d78c2f8d20c60279da9f8b21576d6) | a (+b) | taint | none (`dynamic-evaluation` and `process-input-to-vm-code` are adjacent) |
| #466 | lodash | [c84fe827](https://github.com/lodash/lodash/commit/c84fe82760fb2d3e03a63379b297a1cc1a2fce12) | b | taint | none |
| #467 | lodash | [edadd452](https://github.com/lodash/lodash/commit/edadd452146f7e4bad4ea684e955708931d84d81), [fe8d32ed](https://github.com/lodash/lodash/commit/fe8d32eda854377349a4f922ab7655c8e5df9a0b) | b | taint | none |
| #468 | lodash, axios | lodash [90e6199a](https://github.com/lodash/lodash/commit/90e6199a161b6445b01454517b40ef65ebecd2ad), [1f8ea077](https://github.com/lodash/lodash/commit/1f8ea07746963a535385a5befc19fa687a627d2b); axios [28c72158](https://github.com/axios/axios/commit/28c721588c7a77e7503d0a434e016f852c597b57) | a + b | taint via summary (gap) | none |
| #469 | minimist, xml2js | minimist [38a4d1ca](https://github.com/minimistjs/minimist/commit/38a4d1caead72ef99e824bb420a2528eec03d9ab), [c2b98197](https://github.com/minimistjs/minimist/commit/c2b981977fa834b223b408cfb860f933c9811e4d); xml2js [581b19a6](https://github.com/Leonidas-from-XIV/node-xml2js/commit/581b19a62d88f8a3c068b5a45f4542c2d6a495a5) | a (+b) | taint (gap) | none |
| #470 | handlebars, ejs | handlebars [b6d3de71](https://github.com/handlebars-lang/handlebars.js/commit/b6d3de7123eebba603e321f04afdbae608e8fea8), [d5413781](https://github.com/handlebars-lang/handlebars.js/commit/d54137810a49939fd2ad01a91a34e182ece4528e) | b | taint | none (`process-input-to-vm-code` is adjacent) |
| #471 | ejs | [15ee6985](https://github.com/mde/ejs/commit/15ee698583c98dadc456639d6245580d17a24baf), [e469741d](https://github.com/mde/ejs/commit/e469741dca7df2eb400199e1cdb74621e3f89aa5) | a + b | taint (gap) | none (`dynamic-evaluation` is adjacent) |
| #472 | jsonwebtoken | [e1fa9dcc](https://github.com/auth0/node-jsonwebtoken/commit/e1fa9dcc12054a8681db4e6373da1b30cf7016e3) | b | configuration (gap) | none |
| #473 | express | [0867302d](https://github.com/expressjs/express/commit/0867302ddbde0e9463d0564fea5861feb708c2dd) | b (+a) | taint (gap) | none (#393 open-redirect item is adjacent) |
| #474 | send, serve-static, express | send [ae4f2989](https://github.com/pillarjs/send/commit/ae4f2989491b392ae2ef3b0015a019770ae65d35); serve-static [0c11fad1](https://github.com/expressjs/serve-static/commit/0c11fad159898cdc69fd9ab63269b72468ecaf6b); express [54271f69](https://github.com/expressjs/express/commit/54271f69b511fea198471e6ff3400ab805d6b553) | a | taint + sanitizer context (gap) | none |
| #475 | lodash, axios, node-fetch, ws | lodash [c4847ebe](https://github.com/lodash/lodash/commit/c4847ebe7d14540bb28a8b932a9ce1b9ecbfee1a); axios [5b457116](https://github.com/axios/axios/commit/5b457116e31db0e88fede6c428e969e87f290929); node-fetch [28802387](https://github.com/node-fetch/node-fetch/commit/28802387292baee467e042e168d92597b5bbbe3d); ws [00c425ec](https://github.com/websockets/ws/commit/00c425ec77993773d823f018f64a5c44e17023ff) | a | structural regex + taint | none (`bifrost.security.python.polynomial-redos` is the Python counterpart) |
| #476 | path-to-regexp (express) | [29b96b4a](https://github.com/pillarjs/path-to-regexp/commit/29b96b4a1de52824e1ca0f49a701183cc4ed476f), [f01c26a0](https://github.com/pillarjs/path-to-regexp/commit/f01c26a013b1889f0c217c643964513acf17f6a4) | b | version-gated structural | none |
| #477 | follow-redirects | [080a76d0](https://github.com/follow-redirects/follow-redirects/commit/080a76d0e125b37bf81717368a61d5dc37aa56c8) | a | taint | none (`bifrost.security.csharp.regex-pattern-injection` is the C# counterpart) |
| #478 | axios, undici | axios [fb8eec21](https://github.com/axios/axios/commit/fb8eec214ce7744b5ca787f2c3b8339b2f54b00f), [6b6b605e](https://github.com/axios/axios/commit/6b6b605eaf73852fb2dae033f1e786155959de3a); undici [124f7ebf](https://github.com/nodejs/undici/commit/124f7ebf705366b2e1844dff721928d270f87895) | b | taint | none (#291 covers global `fetch`; Python `process-input-to-urlopen` is the counterpart) |
| #479 | node-fetch, follow-redirects, axios | node-fetch [5c32f002](https://github.com/node-fetch/node-fetch/commit/5c32f002fdd65b1c6a8f1e3620210813d45c7e60); follow-redirects [8b347cbc](https://github.com/follow-redirects/follow-redirects/commit/8b347cbcef7c7b72a6e9be20f5710c17d6163c22), [c4f847f8](https://github.com/follow-redirects/follow-redirects/commit/c4f847f85176991f95ab9c88af63b1294de8649b); axios [afca61a0](https://github.com/axios/axios/commit/afca61a070728e717203c2bc21e7b589b59b858b) | a + b | typestate (gap) | none |
| #480 | follow-redirects | [7a6567e1](https://github.com/follow-redirects/follow-redirects/commit/7a6567e16dfa9ad18a70bfe91784c28653fbf19d) | a | taint + structural (gap) | `process-input-to-legacy-url-parse` |
| #481 | ws | [2b2abd45](https://github.com/websockets/ws/commit/2b2abd458a1b647d0b6033bd62a619c36189839a) | b | configuration (gap) | none |
| #482 | multer, body-parser | multer [73c1759f](https://github.com/expressjs/multer/commit/73c1759fa93b87366bc6dbd7abe1b80ddff7d27c); body-parser [b2695c44](https://github.com/expressjs/body-parser/commit/b2695c4450f06ba3b0ccf48d872a229bb41c9bce) | a + b | taint + configuration (gap) | none |
| #483 | tar | [1f036ca2](https://github.com/isaacs/node-tar/commit/1f036ca23f64a547bdd6c79c1a44bc62e8115da4), [340eb285](https://github.com/isaacs/node-tar/commit/340eb285b6d986e91969a1170d7fe9b0face405e) | a + b | taint (gap) | `process-input-to-fs-write-path` (adjacent) |
| #291 | jose, undici | jose [1b91d88d](https://github.com/panva/jose/commit/1b91d88d2f8233f3477a5f4579aa5f8057b2ee8b); undici [b04e3cbb](https://github.com/nodejs/undici/commit/b04e3cbb569c1596f86c108e9b52c79d8475dcb3) | a | taint | none (#291 is adjacent) |
| #484 | cookie (express) | [e1004284](https://github.com/jshttp/cookie/commit/e10042845354fea83bd8f34af72475eed1dadf5c) | b | taint | none |

## Pre-images to check with the shipped rules

These are the pre-fix files and lines where a run of the shipped rules (engine
0.15.4) is most informative. The first four rows belong to a lead that names an
existing or adjacent rule. The Expectation column says whether that rule should
fire or is expected to miss; an expected miss is the gap the lead records, not a
regression. The last four rows have no rule and give a baseline for
qualification.

| Issue | Repository @ pre-fix commit | File and lines | Expectation |
| --- | --- | --- | --- |
| #480 | follow-redirects/follow-redirects @ `05629af696588b90d64e738bc2e809a97a5f92fc` | `index.js` L496-L508 | `process-input-to-legacy-url-parse` miss expected (the URL is a function parameter, not `process.argv`) |
| #465 | lodash/lodash @ `ded9bc66583ed0b4e3b7dc906206d40757b4a90a` | `lodash.js` L14893-L14895 | `dynamic-evaluation` probable miss (`Function` is bound lexically at L1413 as `context.Function`) |
| #471 | mde/ejs @ `c120527315e159ee48570f73936691f33113ec25` | `lib/ejs.js` L660-L662 | `dynamic-evaluation`: check. The bare `Function` reference at L660 may match the identifier arm. The call at L662 goes through the alias `ctor` |
| #483 | isaacs/node-tar @ `1b94260e87b3eacad801314ce4d5759716c46058` | `lib/unpack.js` L225-L234 | `process-input-to-fs-write-path` miss expected (the path comes from a parsed archive entry) |
| #466 | lodash/lodash @ `e7b28ea6cb17b4ca021e7c9d66218c8c89782f32` | `lodash.js` L3978-L4006 | no rule |
| #475 | axios/axios @ `5bc9ea24dda14e74def0b8ae9cdb3fa1a0c77773` | `lib/utils.js` L187-L189 | no rule (Python `polynomial-redos` only) |
| #477 | follow-redirects/follow-redirects @ `0c23a223067201c368035e82954c11eb2578a33b` | `index.js` L118-L120, L703-L705 | no rule |
| #478 | axios/axios @ `98120457559e573024862e2925d56295a965ad7e` | `lib/adapters/http.js` L230-L232 | no rule |

## Feasibility on Bifrost 0.15.4

Each issue's own feasibility was judged against the pinned authoring CLI.
Three findings come from probes run on 2026-11-25 (Bifrost 0.15.4, build
identity `ea8da845e8d702206a9acc0c6f28d8bd18fa71c0`):

- A sink-only declaration of a member of a third-party module
  (`require("lodash")`) binds `:proof declared` by module name, with no
  lockfile. So the lodash, ejs and Handlebars sinks are expressible now. They
  wait on the open-core placement decision for third-party npm models (#393).
- `new RegExp(x)` does not bind to a declared `globalThis.RegExp` member
  (`predeclared_symbol_reference`). Only the call form `RegExp(x)` binds.
- The released `bifrost.web-network-javascript` model declares only
  `fetch(input, init)`, so `fetch(url)` does not bind. Adding a second pack
  with the one-argument form makes every `fetch` call ambiguous.

| Issue | Feasibility |
| --- | --- |
| #465 | now for the template-string sink (`_.template(string)`, argument 0); needs a third-party lodash model (placement decision pending) |
| #466 | now; needs a third-party lodash model (placement decision pending) |
| #467 | now; needs a third-party lodash model (placement decision pending) |
| #468 | partial |
| #469 | partial |
| #470 | now; needs third-party ejs and Handlebars models (placement decision pending) |
| #471 | blocked for the realistic caller (`res.render(view, req.query)`): no express request model exists, and the sink is a property of the data object (`settings["view options"]`, `outputFunctionName`) |
| #472 | blocked (the rule is "`jwt.verify` called without an `algorithms` option", or with `"none"` in it; options-object property constraints on a call are not available) |
| #473 | partial |
| #474 | partial |
| #475 | partial |
| #476 | blocked (needs `pkg:npm/path-to-regexp` version evidence for the transitive Express dependency, plus a structural analysis of route-string literals) |
| #477 | partial: `RegExp(x)` binds, `new RegExp(x)` does not |
| #478 | partial: axios and undici need third-party models (placement decision pending); global `fetch(url)` does not bind |
| #479 | blocked |
| #480 | partial |
| #481 | blocked (options-object property constraints on a constructor call are not available: `new WebSocketServer({ maxPayload: 0 })`, an absent `maxFragments` on ws versions with no default, or a missing `maxPayload` on a client `new WebSocket(url)`) |
| #482 | partial |
| #483 | partial |
| #291 | Implemented: `bifrost.security.javascript.file-content-to-unbounded-decompression` |
| #484 | partial |

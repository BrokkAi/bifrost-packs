# Python HTTP client fix-history leads

Rule leads mined on 2026-11-24 from public fix commits and GitHub security
advisories of psf/requests, urllib3/urllib3, aio-libs/aiohttp, encode/httpx,
encode/httpcore, python-hyper/h11, getsentry/responses and ranaroussi/yfinance.
The window is roughly September 2023 to November 2026. Each lead is filed as one
issue. The issues hold the theoretical policy, the qualification cases and the
required capabilities. They are research candidates, not rules, and nothing here
was run through an analyzer.

Kinds: **(a)** a pattern inside the library that a general Python rule should
catch anywhere; **(b)** a misuse of the library by its callers, which needs a
semantic model of that library.

Pure protocol-parser bugs were left out because no static rule could plausibly
express them. Examples are h11 chunk-footer validation (CVE-2025-43859), aiohttp
llhttp and pure-Python parser smuggling, and WebSocket frame-size arithmetic.
httpcore and h11 contributed no lead of their own.

| Issue | Package | Fix commit(s) | Kind | Policy | Existing rule |
| --- | --- | --- | --- | --- | --- |
| #422 | urllib3, aiohttp, requests | urllib3 [5ec0de49](https://github.com/urllib3/urllib3/commit/5ec0de499b9166ca71c65ab04f2a7e4eb0d66fcc), [01cd60b5](https://github.com/urllib3/urllib3/commit/01cd60b539f808a65e9c5aa93db1c48292432176); aiohttp [5351c980](https://github.com/aio-libs/aiohttp/commit/5351c980dcec7ad385730efdf4e1f4338b24fdb6) | a | taint + typestate | none |
| #423 | urllib3, requests | [644124ec](https://github.com/urllib3/urllib3/commit/644124ecd0b6e417c527191f866daa05a5a2056d), [accff72e](https://github.com/urllib3/urllib3/commit/accff72ecc2f6cf5a76d9570198a93ac7c90270e), [5ec0de49](https://github.com/urllib3/urllib3/commit/5ec0de499b9166ca71c65ab04f2a7e4eb0d66fcc); requests [74ea7cf7](https://github.com/psf/requests/commit/74ea7cf7a6a27a4eeb2ae24e162bcc942a6706d5) | b | version-gated taint | none |
| #424 | aiohttp | [5351c980](https://github.com/aio-libs/aiohttp/commit/5351c980dcec7ad385730efdf4e1f4338b24fdb6), [f54c4085](https://github.com/aio-libs/aiohttp/commit/f54c40851b0d6c4bbdab97ba518a223adda32478), [38d16060](https://github.com/aio-libs/aiohttp/commit/38d16060037e1bfcd6d677abababa3c2a4bb58fa) | b | version-gated taint | none |
| #425 | requests | [96ba401c](https://github.com/psf/requests/commit/96ba401c1296ab1dda74a2365ef36d88f7d144ef) | a (+b) | taint | none (`incomplete-url-substring-sanitization` is adjacent) |
| #426 | requests | [c0813a2d](https://github.com/psf/requests/commit/c0813a2d910ea6b4f8438b91d315b8d181302356) | b | typestate | none |
| #427 | requests, httpx, aiohttp, urllib3 | httpx [89599a9](https://github.com/encode/httpx/commit/89599a9541af14bcf906fc4ed58ccbdf403802ba) | b | configuration | none (`insecure-protocol` covers versions only) |
| #428 | yfinance, requests, aiohttp | yfinance [929557f](https://github.com/ranaroussi/yfinance/commit/929557ffdc448a3239b7f6e45e3e8a662289d1a8), [03a18ae](https://github.com/ranaroussi/yfinance/commit/03a18ae779df41f7234444c121850ab128fbd0f5), [f4ddf5c](https://github.com/ranaroussi/yfinance/commit/f4ddf5caa166d3d381d330c1e31a25e3f5b6e065); aiohttp [1e94b3e8](https://github.com/aio-libs/aiohttp/commit/1e94b3e82cbfcc24a1dca914db53c69096744451) | a | structural dataflow | none |
| #429 | aiohttp, urllib3 | aiohttp [bf88077e](https://github.com/aio-libs/aiohttp/commit/bf88077ebb14f4c29924b8e8904cba20c55c28b8), [9a6ada97](https://github.com/aio-libs/aiohttp/commit/9a6ada97e2c6cf1ce31727c6c9fcea17c21f6f06); urllib3 [e18a0d1a](https://github.com/urllib3/urllib3/commit/e18a0d1a159210a5b64354a435b6e5437c80e0d6) | a | taint | none |
| #430 | aiohttp | [e4ae01c2](https://github.com/aio-libs/aiohttp/commit/e4ae01c2077d2cfa116aa82e4ff6866857f7c466), [1e86b777](https://github.com/aio-libs/aiohttp/commit/1e86b777e61cf4eefc7d92fa57fa19dcc676013b), [9a6ada97](https://github.com/aio-libs/aiohttp/commit/9a6ada97e2c6cf1ce31727c6c9fcea17c21f6f06), [bf88077e](https://github.com/aio-libs/aiohttp/commit/bf88077ebb14f4c29924b8e8904cba20c55c28b8) | b | version-gated taint | none |
| #431 | requests | [bc7dd0fc](https://github.com/psf/requests/commit/bc7dd0fc4d56e808bcdd85ac2d797b3107c89259) | a | structural regex | none |
| #432 | aiohttp | [c7b7a044](https://github.com/aio-libs/aiohttp/commit/c7b7a044f88c71cefda95ec75cdcfaa4792b3b96), [32677f2a](https://github.com/aio-libs/aiohttp/commit/32677f2adfd907420c078dda6b79225c6f4ebce0) | a | taint | none |
| #433 | aiohttp | [bc1319ec](https://github.com/aio-libs/aiohttp/commit/bc1319ec3cbff9438a758951a30907b072561259) | a | taint + structural | none (`side-effect-in-assert` is adjacent) |
| #434 | aiohttp | [a4b038ad](https://github.com/aio-libs/aiohttp/commit/a4b038adbd44bf88c68ddcc14d500b350eae47f6), [bcf0a36e](https://github.com/aio-libs/aiohttp/commit/bcf0a36e296d4311ce61df4966ab7ff3cb6635fa), [c7cf1e45](https://github.com/aio-libs/aiohttp/commit/c7cf1e45a33b604833705758aecb15352b4407ed), [c6ac0e44](https://github.com/aio-libs/aiohttp/commit/c6ac0e44c3c573ff9616f4a6a532992538b31e43) | a | taint (gap) | `polynomial-redos` |
| #435 | urllib3, aiohttp | urllib3 [c19571de](https://github.com/urllib3/urllib3/commit/c19571de34c47de3a766541b041637ba5f716ed7), [24d7b67e](https://github.com/urllib3/urllib3/commit/24d7b67eac89f94e11003424bcf0d8f7b72222a8); aiohttp [2b920c39](https://github.com/aio-libs/aiohttp/commit/2b920c39002cee0ec5b402581779bbaaf7c9138a) | a | taint | none (`xml-bomb` is adjacent) |
| #436 | aiohttp | [615fec3d](https://github.com/aio-libs/aiohttp/commit/615fec3d4f088f30d2ee72cad760152e92aa1c53) | a (+b) | taint | none |
| #437 | urllib3, aiohttp | urllib3 [13f0bfd5](https://github.com/urllib3/urllib3/commit/13f0bfd55e4468fe1ea9c6f809d3a87b0f93ebab), [c284372e](https://github.com/urllib3/urllib3/commit/c284372e2e11639b4554d50bf6d1a5b1750c0df0); aiohttp [9dd8eaf4](https://github.com/aio-libs/aiohttp/commit/9dd8eaf4e31f1237ef2c1574a8c82a739fca5805) | a | taint | none |
| #438 | aiohttp | [c4d77c35](https://github.com/aio-libs/aiohttp/commit/c4d77c3533122be353b8afca8e8675e3b4cbda98), [b1f6c87b](https://github.com/aio-libs/aiohttp/commit/b1f6c87b2bd3bd80f2b6c22ff46e11d00921e412) | a | taint + structural | none |
| #439 | aiohttp, urllib3 (+ requests, httpx callers) | aiohttp [182198fc](https://github.com/aio-libs/aiohttp/commit/182198fccae2d71b857a0f26b18e7317fd6cff4f), [a5e3747d](https://github.com/aio-libs/aiohttp/commit/a5e3747d3a2440e59a86914cf287cfba5ab91104), [4416d89e](https://github.com/aio-libs/aiohttp/commit/4416d89e73f4a09339eb08fabef3fa010ec9184f); urllib3 [a164d79c](https://github.com/urllib3/urllib3/commit/a164d79c8cf760f222daa2dc7f67d0e1ca7fb17c) | a + b | typestate (gap) | `resource-lifecycle` |
| #440 | aiohttp | [1c335944](https://github.com/aio-libs/aiohttp/commit/1c335944d6a8b1298baf179b7c0b3069f10c514b), [0ae2aa07](https://github.com/aio-libs/aiohttp/commit/0ae2aa076c84573df83fc1fdc39eec0f5862fe3d), [ce2e9758](https://github.com/aio-libs/aiohttp/commit/ce2e9758814527589b10759a20783fb03b98339f) | a (+b) | taint | none |
| #441 | aiohttp | [dcf40f30](https://github.com/aio-libs/aiohttp/commit/dcf40f30637e8752c76781cf6703b5a236749a00) | b | taint via summary (gap) | `unsafe-deserialization` |
| #442 | aiohttp | [47558a30](https://github.com/aio-libs/aiohttp/commit/47558a30c88e31cc3b5ff3b57f6127e7984c80bc) | a | taint (gap) | `overly-permissive-file` |
| #443 | requests | [66d21cb0](https://github.com/psf/requests/commit/66d21cb07bd6255b1280291c4fafb71803cdb3b7) | a | structural dataflow (gap) | `insecure-temporary-file` |
| #444 | urllib3, responses, aiohttp | urllib3 [8afb98b3](https://github.com/urllib3/urllib3/commit/8afb98b3cede2ac14f7d20b3d9ac290cf57fa72d); responses [a19add7](https://github.com/getsentry/responses/commit/a19add7777d7d0c64eeb364f6cc9de624c33f4f8); aiohttp [1857e6df](https://github.com/aio-libs/aiohttp/commit/1857e6df6e9efce10dcf08a4ee26a366add2e443) | a | alias dataflow | none (`modification-of-default-value` is adjacent) |
| #445 | urllib3 | [f05b1329](https://github.com/urllib3/urllib3/commit/f05b1329126d5be6de501f9d1e3e36738bc08857) | b | version-gated configuration | none |

## Pre-images to check with the shipped rules

These are the pre-fix files and lines where a run of the shipped rules (engine
0.15.4, rules 0.17.0, packs 0.16.0) is most informative. The first four have an
existing rule that should fire. The rest have no rule, so they give a baseline
for qualification.

| Issue | Repository @ pre-fix commit | File and lines | Expectation |
| --- | --- | --- | --- |
| #434 | aio-libs/aiohttp @ `b2b2bce03c17521dc454cdd4a6e19ab0a08bce6b` | `aiohttp/client_reqrep.py` L500 | `polynomial-redos` should fire (literal pattern) |
| #434 | aio-libs/aiohttp @ `6963ee0befec1502b6bb7b4db6c72d044c08f4fa` | `aiohttp/web_urldispatcher.py` L845-L846 | probable miss (pattern built at run time) |
| #441 | aio-libs/aiohttp @ `4f12a6641e3db60aa35c60c9db61b45c89176c00` | `aiohttp/cookiejar.py` L119-L122 | `unsafe-deserialization` should fire on the direct `pickle.load` |
| #443 | psf/requests @ `8b9bc8fc0f63be84602387913c4b689f19efd028` | `src/requests/utils.py` L285-L290 | probable miss in `insecure-temporary-file` |
| #439 | aio-libs/aiohttp @ `0c4b1c74cd7bffb544dacb4a4d8793f80fd4ad32` | `aiohttp/connector.py` L1103-L1124 | miss expected (no Python acquisition family) |
| #439 | urllib3/urllib3 @ `089176c179a8173188bda92ab5eef796b12f57fc` | `src/urllib3/http2/probe.py` L36-L49 | miss expected |
| #422 | urllib3/urllib3 @ `2bdcc44d1e163fb5cc48a8662425e35e15adfe6a` | `src/urllib3/connectionpool.py` L891-L915 | no rule |
| #425 | psf/requests @ `7341690e842a23cf18ded0abd9229765fa88c4e2` | `src/requests/utils.py` L239-L245 | no rule |
| #435 | urllib3/urllib3 @ `816fcf04528bc0f89672e13398eb813dcc892490` | `src/urllib3/response.py` L60-L86 | no rule |

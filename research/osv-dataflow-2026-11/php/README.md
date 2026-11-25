# PHP OSV data-flow leads on Bifrost 0.15.1

**Outcome: 10 new `[PHP] CVE-` data-flow leads are filed, and none ships as a rule
on Bifrost 0.15.1.** Eight are PHP runtime leads (bifrost-packs #309–#316). Two
are Composer leads (bifrost-premium-packs #471, #472), placed in premium and not
implemented here.

With research declarations standing in for the missing pack flag, five runtime
leads give a definite, proven finding on their positive case, with clean near
misses: #309, #310, #311 (string command), #315 and #316. The production
`bifrost.php-builtin` pack refuses every one of them. The three PHP fixes that
would unblock them all merged in bifrost-dev on 2026-11-03, but none is in the
public v0.15.1 release:

- bifrost-dev#9337 (fixed by bifrost-dev PR 9372): `php-builtin` marks global
  functions `callable_family_complete`. The public v0.15.1 source has neither
  the PR's producer change nor its golden fixtures. packs/v0.10.0 still ships
  `php-builtin` 2026.9.4, whose shard has no `callable_family_complete` record
  (0 of 4,992).
- bifrost-dev#9330 (PR 9455): element reads, binary operators and `??`.
- bifrost-dev#9331 (PR 9470): string interpolation.

So the PHP rows are expected to move only on v0.15.2. The probe also found two
new engine gaps. Both are filed:

- bifrost-dev#9992: array literals drop their elements, and the run still
  reports **complete**. This is a false clean result, not a typed gap.
- bifrost-dev#9993: there's no selector for a stream fetch by the options of its
  `stream_context_create` context.

Five leads also need bundled extensions that the pinned stub slice doesn't
declare. That's a change in this repository: #318.

Files under `probe/` are research inputs, not registered pack content. They
change no locked policy or semantic-pack content, and they are not release
inputs.

## Engine

- Official `v0.15.1`, `bifrost-v0.15.1-universal-apple-darwin.tar.gz`,
  downloaded with `gh release download v0.15.1 --repo BrokkAi/bifrost`.
  Archive SHA-256 `d7ca6901787455bdabf18ec9c36453032a9be354180e54b5ff183b1e4bf83038`,
  which matches the release `.sha256`. Binary SHA-256
  `00b279126297d5e9f7805390799493e915eaf4a2d5940dc3e755138a577a6df9`.
- Production packs: `packs/v0.10.0`, `bifrost.public.packs-0.10.0-native.tar.gz`,
  SHA-256 `3f39f9f5ec2d028e293a238ff796260101915e50963a44a93c812d9d02860945`
  (matches its `.sha256`). It holds `bifrost.php-builtin` 2026.9.4, shard
  `e8e6ad9cb51904b193e71ef5c0402e602ce2c6c42846a4c90e2386c441e7e392`.
- Evaluation date: 2026-11-05.

## Recheck of the 0.15.0 PHP blockers

| Issue | Upstream state | 0.15.1 result |
| --- | --- | --- |
| bifrost-dev#9337 | closed 2026-11-03 (PR 9372) | Still refused. With `php-builtin` selected, `_php_global_.file_get_contents` and `_php_global_.unserialize` are `not_run`, `qualified-call-locator-partial`. Adding research declarations makes the locator `qualified-call-locator-ambiguous` instead. |
| bifrost-dev#9330 | closed (PR 9455) | Still reproduces. `$_GET['url']`, `?? ''`, `'x' . $_GET['url']`, and an unrelated `$_GET` read beside a constant sink are all `inconclusive` ("procedure semantics … unknown"). `==`, `===`, `!==` and `?:` do the same. PR 9455 says binary operators now flow and only `?:`, `match`, `&&` and `\|\|` keep the join gap. |
| bifrost-dev#9331 | closed (PR 9470) | Still reproduces: `"x{$_GET['url']}"` is inconclusive. |
| bifrost-dev#9328, #9329 | closed | Not probed again. Every slice here fails on #9337 or #9330 first. |
| bifrost-dev#9332 | open | Not relevant: no vendor calls. |

## Probe

`tools/build_probe.py` writes `probe/`. `tools/run_probe.py` runs it.
`probe/.bifrost/semantic-models/bifrost.research.php-osv-dataflow-probe.json`
declares eleven builtins under the `_php_global_` type id that `php-builtin`
uses. Each is `callable_family_complete`, with complete receiverless summaries.
`filter_var`, `parse_url`, `stream_context_create` and `fread` transfer
argument 0 to the result. This is research only. Don't copy it into
`semantic-packs/`: the stub producer owns declarations of the pinned slice.

Request input comes from a workspace `request_param()` function, not
`$_GET[...]`. That way each probe measures its own lead's sink and transfer,
apart from bifrost-dev#9330. Each lead has one taint policy
(`:mode may`, `:unmodeled require-model`).

```sh
python3 research/osv-dataflow-2026-11/php/tools/build_probe.py
python3 research/osv-dataflow-2026-11/php/tools/run_probe.py "$BIFROST" "$OUT"
python3 research/osv-dataflow-2026-11/php/tools/run_probe.py "$BIFROST" "$OUT" \
  --production "$PACKS/bifrost-semantic-packs" filter-var-url-fetch/positive-filtered-value
```

Without `--production`, the runner sets `BIFROST_OPEN_PACKS_DISABLE=1`. With
it, the runner supplies the bundle, writes `.php-version` `8.3.0` so
`php-builtin` activates, and drops the research declaration shard. Each
production case takes three to seven minutes.

### Research declarations, open packs disabled

| Case | Completion | Findings |
| --- | --- | --- |
| `filter-var-url-fetch/positive-filtered-value` | proven_by_summary | `app.php:11` definite, proven |
| `filter-var-url-fetch/positive` (`if (filter_var(...) === false) return false;`) | inconclusive: procedure semantics unknown (the `===`, bifrost-dev#9330) | `app.php:14` definite, proven |
| `filter-var-url-fetch/near-miss-constant` | proven_by_summary | none |
| `filter-var-url-fetch/unknown-unmodeled-trim` | inconclusive: `trim` unmodeled | none |
| `libxml-noent-untrusted-xml/positive` | proven_by_summary | `app.php:10` definite, proven |
| `libxml-noent-untrusted-xml/near-miss-default-options`, `near-miss-nonet` | complete, no sink selected | none |
| `libxml-noent-untrusted-xml/unknown-flag-union` (`LIBXML_NOENT \| LIBXML_DTDLOAD`) | **complete, no sink selected** | none: see below |
| `proc-open-array-command/positive-string` | proven_by_summary | `app.php:12` definite, proven |
| `proc-open-array-command/positive-array` (`['convert', $name, 'out.png']`) | **proven_by_summary** | **none** (bifrost-dev#9992) |
| `proc-open-array-command/near-miss-constant` | proven_by_summary | none |
| `proc-open-array-command/unknown-unmodeled-escape` | inconclusive: `escapeshellarg` unmodeled | none |
| `http-context-header/positive` (`['http' => ['header' => $header]]`) | **proven_by_summary** | **none** (bifrost-dev#9992) |
| `http-context-header/near-miss-constant-header` | proven_by_summary | none |
| `http-context-header/near-miss-method-only` | inconclusive: `?:` join gap | none |
| `http-proxy-fulluri/positive` | proven_by_summary | `app.php:11` definite, proven |
| `http-proxy-fulluri/near-miss-no-proxy` | proven_by_summary | `app.php:11`, the same finding (bifrost-dev#9993) |
| `fsockopen-host-after-check/positive` | inconclusive: `!==` (bifrost-dev#9330) | `app.php:15` definite, proven |
| `fsockopen-host-after-check/near-miss-constant` | proven_by_summary | none |
| `fsockopen-host-after-check/unknown-unmodeled-strtolower` | inconclusive: `strtolower` unmodeled | none |
| `openssl-pkcs1-network-ciphertext/positive-default-padding`, `positive-explicit-pkcs1` | proven_by_summary | `app.php:8` definite, proven |
| `openssl-pkcs1-network-ciphertext/near-miss-oaep` | complete, no sink selected | none |
| `libxml-remote-url-load/positive` | proven_by_summary | `app.php:10` definite, proven |
| `libxml-remote-url-load/near-miss-constant` | proven_by_summary | none |

The `unknown-flag-union` row is a selector limit in this probe, not an engine
result. `:args [... (name "LIBXML_NOENT")]` matches only the bare constant, so a
flag union selects no sink, and the empty result says nothing. A shipped #310
rule needs a selector for "the options operand includes `LIBXML_NOENT`". It
also needs an unknown answer when the operand is computed. Until it has both,
it must not treat a non-match as clean. The same applies to
`OPENSSL_PKCS1_PADDING` passed through a variable.

### Production `php-builtin`, research summaries only

Each lead's main positive case, with `php-builtin` 2026.9.4 selected through
`.php-version` `8.3.0`. Every case is `not_run`, with exit code 2 and no findings.

| Case | Refusal |
| --- | --- |
| `filter-var-url-fetch/positive-filtered-value` | `qualified-call-locator-partial`: `_php_global_.file_get_contents` (bifrost-dev#9337) |
| `proc-open-array-command/positive-string` | `qualified-call-locator-partial`: `_php_global_.proc_open` (bifrost-dev#9337) |
| `http-context-header/positive` | `qualified-call-locator-partial`: `_php_global_.stream_context_create` (bifrost-dev#9337) |
| `http-proxy-fulluri/positive` | `qualified-call-locator-partial`: `_php_global_.file_get_contents` (bifrost-dev#9337) |
| `fsockopen-host-after-check/positive` | `qualified-call-locator-partial`: `_php_global_.fsockopen` (bifrost-dev#9337) |
| `libxml-noent-untrusted-xml/positive` | `qualified-call-locator-zero`: `_php_global_.simplexml_load_string` has no identity (#318) |
| `libxml-remote-url-load/positive` | `qualified-call-locator-zero`: `_php_global_.simplexml_load_file` has no identity (#318) |
| `openssl-pkcs1-network-ciphertext/positive-default-padding` | `qualified-call-locator-zero`: `_php_global_.openssl_private_decrypt` has no identity (#318). Its `stream_socket_client` source is in the slice, so bifrost-dev#9337 also applies. |

These refusals are explicit. None of them is a clean result.

### Array literals (bifrost-dev#9992)

`probe/engine-array-literal/` needs no models. A `src()` result reaches a
workspace `sink(mixed $s)`:

| Body | Completion | Findings |
| --- | --- | --- |
| `sink($u)` (control) | complete | 1 |
| `sink([$u])`, `sink(['k' => $u])`, `sink(['http' => ['header' => $u]])`, `$a = [$u]; sink($a[0])` | **complete** | **0** |
| `$a = []; $a[] = $u; sink($a)` | inconclusive: `index_memory` unsupported | 1 |
| `sink(['k' => 'v'])` (near miss) | complete | 0 |

Run it from that directory with
`--policy-file .bifrost/policies/array-literal.rqlp --sources <case>`, with
open packs disabled.

## Per-lead outcomes

| Lead | Outcome | Blockers | Notes |
| --- | --- | --- | --- |
| #309 CVE-2024-5458 `filter_var` URL then fetch | Blocked by engine | bifrost-dev#9337, bifrost-dev#9330, #318 | The version-independent slice works with research declarations. `filter_var` isn't in the stub slice. The affected-version part needs runtime evidence (not probed). |
| #310 CVE-2023-3823 `LIBXML_NOENT` on untrusted XML | Blocked by engine | bifrost-dev#9337, bifrost-dev#9330, #318 | The bare-flag slice works. Flag unions need an operand selector and an unknown fallback. `DOMDocument::loadXML` (class binding, bifrost-dev#9329) not probed. |
| #311 CVE-2024-1874 `proc_open` command | Blocked by engine | bifrost-dev#9992, bifrost-dev#9337, bifrost-dev#9330 | The string command works. The CVE's array form silently loses the flow. Windows target evidence not probed. |
| #312 CVE-2025-1736 http context `header` | Blocked by engine | bifrost-dev#9992, bifrost-dev#9993, bifrost-dev#9337, bifrost-dev#9330 | The nested option element is dropped and the run says complete. |
| #313 CVE-2024-11234 proxy and `request_fulluri` | Blocked by engine | bifrost-dev#9993, bifrost-dev#9337, bifrost-dev#9330 | The URL flow works, but no selector can tell a proxied context from a plain one. |
| #314 CVE-2025-1220 host to `fsockopen` | Blocked by engine | bifrost-dev#9337, bifrost-dev#9330, bifrost-dev#9331 | The flow is found, but the `!==` guard leaves the run inconclusive on 0.15.1. |
| #315 CVE-2024-2408 PKCS#1 v1.5 decrypt | Blocked by engine | bifrost-dev#9337, #318 | Network bytes reach `openssl_private_decrypt`. Default and explicit PKCS#1 padding work, and OAEP is clean. The OpenSSL build is deployment knowledge, so the CVE part stays review. |
| #316 CVE-2025-1219 URL to `simplexml_load_file` | Blocked by engine | bifrost-dev#9330, #318 | The flow works. SimpleXML isn't in the stub slice, and the request source needs bifrost-dev#9330. |
| premium #471 CVE-2026-45071 DomCrawler `addXmlContent` | Premium, not implemented here | none | Composer package. |
| premium #472 CVE-2026-84372 Predis aggregate pipelines | Premium, not implemented here | none | Composer package. |

## Promotion criteria

1. A release containing bifrost-dev PRs 9372, 9455 and 9470 (expected
   v0.15.2), and a `php-builtin` pack regenerated with its producer. Then rerun
   the `--production` cases. Use `$_GET[...]` sources in place of
   `request_param()`.
2. #318 with reviewed summaries for `filter_var`, the SimpleXML and DOM loaders,
   and `openssl_private_decrypt`, like `semantic-packs/web-network/php/`.
3. bifrost-dev#9992 for #311 and #312. bifrost-dev#9993 for #312 and #313.
4. Then model rules on
   `rules/bifrost.security/policies/go/gob-decode-network-input.rqlp` for the
   version-independent slices of #309, #310, #315 and #316, with
   `:unmodeled require-model` and these positive, near-miss and unknown
   fixtures. Release selection stays separate.

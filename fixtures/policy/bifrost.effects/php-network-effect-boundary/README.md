# PHP network-effect boundary (`curl_exec`)

Fixtures for `bifrost.effects.php.selected-boundary-no-network-io`, the PHP row
of the network-effect boundary family (BrokkAi/bifrost-dev#3387, row #3460).
Each case directory is a workspace: its `.bifrost/policies/` copy is the
shipped specialization with the declaration selection configured to the
namespace function `App\total`, and its `.bifrost/semantic-models/` copy is
`semantic-packs/web-network/php/bifrost.web-network-php.json` byte for byte.

The reviewed model declares `bifrost.network_io` on the cURL builtin
`curl_exec` at written arity one, as a member of PHP's global-namespace
scaffold (`_php_global_.curl_exec`), and declares `curl_init` effect-free so a
handle allocation does not leave coverage open. The call site binds that
identity through PHP's own function lookup, never by spelling: an unqualified
call tries the caller's namespace first and reaches the global builtin only
when the workspace declares no function of that name there.

Validated with Bifrost 0.14.0, build identity
`0b40d26b2722d9f3e467abf4afb89eda1b98de09` (engine `origin/master`
`ac496ec1b7ec1062e2827d6bb5ef6d672592c272` plus test-only changes), debug
binary SHA-256
`5f6fe05c233c8b9e63f96e0067f872ded9484f2259f691d6a573432d29357968`.
Configured policy hash:
`eb42e51256d1489dda8cdb35c109137c0e6f9d1a6c9b58090ef8fecc6c11451c`.

```bash
bifrost --root fixtures/policy/bifrost.effects/php-network-effect-boundary/<case> \
  --no-builtin-policies \
  --policy-file .bifrost/policies/selected-boundary-no-network-io.rqlp \
  --format json
```

| Case | Exit | Completion | Findings | Witness |
| --- | --- | --- | --- | --- |
| `finding` | 1 | complete | 1, `PriceCalculator.php:10` | `App.total -> App.record -> App.deliver -> _php_global_.curl_exec/1` |
| `direct` | 1 | complete | 1, `PriceCalculator.php:8` | `App.total -> _php_global_.curl_exec/1` (written `\curl_exec`) |
| `recursion` | 1 | complete | 1, `PriceCalculator.php:6` | `App.total -> App.accumulate -> App.record -> App.deliver -> _php_global_.curl_exec/1` |
| `corrected` | 0 | complete | 0 | the caller owns the transfer; the boundary reaches only `sum_lines` |
| `near-miss-namespaced-curl-exec` | 0 | complete | 0 | `curl_exec` resolves to the userland `App\curl_exec` |
| `near-miss-uncalled-helper` | 0 | complete | 0 | `deliver` reaches the builtin, but nothing selected calls it |
| `unresolved` | 2 | inconclusive (`capability_incomplete`) | 0 | `\Vendor\Billing\dispatch` has no definition and no model |

The corrected verdict depends on exhaustive coverage. Out-of-tree probes on
the same binary: the `finding` tree without the model, a `curl_exec` call
written at arity two, and the `corrected` tree with its loop replaced by the
unmodeled builtins `array_sum(array_column(...))` each end inconclusive
(exit 2) with no finding. A second activated pack that also publishes the
`_php_global_` scaffold does not change the `finding` result.

<?php
// The reviewed external boundary. `curl_exec` is written unqualified inside
// `namespace App`, and the workspace declares no `App\curl_exec`, so PHP's
// own function lookup falls back to the global builtin. The activated model
// declares the network effect on that exact global identity at written arity
// one; `curl_init` is declared effect-free, since it only allocates a handle.
namespace App;

function deliver(string $orderId): string|bool
{
    $handle = curl_init('https://example.test/audit?order=' . $orderId);
    return curl_exec($handle);
}

<?php
// The direct positive: the selected boundary itself performs the transfer.
// The call is written fully qualified, `\curl_exec`, which names the global
// builtin without PHP's namespace fallback; it binds the same reviewed
// identity as the unqualified spelling in the cross-file tree.
namespace App;

function total(array $order, \CurlHandle $audit): int
{
    \curl_exec($audit);
    $total = 0;
    foreach ($order['lines'] as $line) {
        $total += $line['amount'];
    }
    return $total;
}
